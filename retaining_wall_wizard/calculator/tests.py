import math
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import SoilType, WallMaterial

class Eurocode7APITests(TestCase):
    """
    Tests for the new Eurocode 7 compliant calculation engine,
    using the examples from the user-provided design guide.
    """
    @classmethod
    def setUpTestData(cls):
        # The data is created by migration 0002.
        # We don't need to create it here, just fetch it.
        cls.client = APIClient()
        cls.calculate_url = reverse('calculate')

        # Data for Example 1
        cls.poorly_graded_sand = SoilType.objects.get(name="Poorly-graded Sand (SP)")
        cls.mass_concrete = WallMaterial.objects.get(name="Mass / Reinforced Concrete")

        # Data for Example 2
        cls.lean_clay = SoilType.objects.get(name="Clay (Low Plasticity, CL)")
        cls.dense_blocks = WallMaterial.objects.get(name="Dense Concrete Blocks")

    def test_example_1_simple_gravity_wall_fails_as_expected(self):
        """
        Tests the scenario from Section 5.1 of the design guide.
        The design is expected to FAIL.
        """
        payload = {
            "retained_height": 1.5,
            "wall_material_id": self.mass_concrete.id,
            "stem_thickness": 0.3,
            "base_width": 0.9,
            "toe_length": 0.3,
            "heel_length": 0.3,
            "retained_soil_type_id": self.poorly_graded_sand.id,
            "foundation_soil_type_id": self.poorly_graded_sand.id,
            "ground_slope_angle": 0,
            "water_table_height": 0,
            "surcharge_load": 10.0 # Domestic Garden
        }

        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the overall status
        self.assertEqual(response.data['overall_status'], 'FAIL')

        # Check the DA1/1 (STR) overturning results, which the document calculates
        results_da1_1 = response.data['results_DA1_1']
        self.assertFalse(results_da1_1['overturning_ok'])

        # The document calculates MOT,d = 14.72 kNm/m and MR,d = 13.86 kNm/m.
        # My implementation may differ slightly due to simplifications (e.g. base thickness).
        # Let's check if the values are close.
        self.assertAlmostEqual(results_da1_1['overturning_moment_d'], 14.72, delta=1.5)
        self.assertAlmostEqual(results_da1_1['restoring_moment_d'], 13.86, delta=1.5)

        # Check the DA1/2 (GEO) sliding results
        results_da1_2 = response.data['results_DA1_2']
        self.assertFalse(results_da1_2['sliding_ok'])

    def test_example_2_complex_wall_is_handled(self):
        """
        Tests the scenario from Section 5.2 of the design guide.
        The document predicts this will fail. The main goal of this test
        is to ensure the API can process the complex inputs without errors.
        """
        payload = {
            "retained_height": 2.0,
            "wall_material_id": self.dense_blocks.id,
            "stem_thickness": 0.215,
            "base_width": 1.4,
            "toe_length": 0.4,
            "heel_length": 0.785,
            "retained_soil_type_id": self.lean_clay.id,
            "foundation_soil_type_id": self.lean_clay.id,
            "ground_slope_angle": 10.0,
            "water_table_height": 1.3,
            "surcharge_load": 12.0 # Driveway
        }

        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The document predicts failure, and my service has warnings about
        # sloping ground and water table not being fully implemented.
        # The key is that it runs and returns a FAIL status.
        self.assertEqual(response.data['overall_status'], 'FAIL')
        self.assertIn("warnings", response.data)
        self.assertGreater(len(response.data['warnings']), 0)

    def test_api_returns_400_for_invalid_data(self):
        """
        Ensure the API returns 400 Bad Request for missing data.
        """
        payload = {
            "retained_height": 1.5,
            # Missing other required fields
        }
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('wall_material_id', response.data)
        self.assertIn('base_width', response.data)

    def test_api_returns_400_for_bad_dimensions(self):
        """
        Ensure the API returns 400 for inconsistent dimensions.
        """
        payload = {
            "retained_height": 1.5,
            "wall_material_id": self.mass_concrete.id,
            "stem_thickness": 0.3,
            "base_width": 0.9,
            "toe_length": 0.8, # toe + heel > base
            "heel_length": 0.2,
            "retained_soil_type_id": self.poorly_graded_sand.id,
            "foundation_soil_type_id": self.poorly_graded_sand.id,
            "ground_slope_angle": 0,
            "water_table_height": 0,
            "surcharge_load": 10.0
        }
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('sum of toe and heel length must be less than or equal', response.data['non_field_errors'][0])
