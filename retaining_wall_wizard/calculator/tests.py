from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import SoilType, SurchargeLoad
from .services import calculate_retaining_wall_design


class CalculationServiceTests(TestCase):
    """
    Unit tests for the engineering calculation service.
    """
    @classmethod
    def setUpTestData(cls):
        # This data is created by migration 0002, but we recreate it
        # here to make tests independent of the migration being run.
        cls.good_soil = SoilType.objects.create(
            name="Test Sandy Gravel",
            angle_of_internal_friction=35,
            soil_density=18
        )
        cls.poor_soil = SoilType.objects.create(
            name="Test Wet Clay",
            angle_of_internal_friction=20,
            soil_density=20
        )
        cls.heavy_load = SurchargeLoad.objects.create(
            name="Test Driveway",
            pressure=10
        )
        cls.no_load = SurchargeLoad.objects.create(
            name="Test Garden",
            pressure=0
        )

    def test_design_passes_with_good_conditions(self):
        """
        Test a standard scenario that should result in a passing design.
        """
        wall_height = 1.2  # m
        results = calculate_retaining_wall_design(wall_height, self.good_soil, self.no_load)

        self.assertEqual(results['status'], 'OK')
        self.assertGreater(results['calculations']['safety_factor_overturning'], 2.0)
        self.assertGreater(results['calculations']['safety_factor_sliding'], 1.5)
        self.assertLess(results['calculations']['max_bearing_pressure_kPa'], 100)

    def test_design_fails_on_overturning(self):
        """
        Test a scenario with a high wall and poor soil that should fail on overturning.
        """
        wall_height = 2.2 # m (high wall)
        # Use a soil with a low friction angle to generate high pressure
        overturning_soil = SoilType.objects.create(
            name="Test Silty Sand",
            angle_of_internal_friction=25, # Low angle to force failure
            soil_density=19
        )
        results = calculate_retaining_wall_design(wall_height, overturning_soil, self.heavy_load)

        self.assertEqual(results['status'], 'FAIL', "The design should fail with these inputs.")
        self.assertLess(
            results['calculations']['safety_factor_overturning'], 2.0,
            "The safety factor for overturning should be less than 2.0"
        )

    def test_design_fails_on_sliding(self):
        """
        Test a scenario with poor soil and a heavy load that should fail on sliding.
        Note: Sliding failures are harder to trigger with the simplified friction model.
        This test checks that the calculation is happening, but may need adjustment
        with a more advanced model. A very high surcharge on poor soil should do it.
        """
        wall_height = 1.5 # m
        # Create a very high surcharge to force a sliding failure
        extreme_load = SurchargeLoad.objects.create(name="Extreme", pressure=25)
        results = calculate_retaining_wall_design(wall_height, self.poor_soil, extreme_load)

        # With the simple rules, overturning or bearing might fail first.
        # The key is to check that the safety factors are below the required values.
        self.assertEqual(results['status'], 'FAIL')
        self.assertLess(results['calculations']['safety_factor_sliding'], 1.5)

    def test_design_fails_on_bearing_pressure(self):
        """
        Test a scenario with a high wall on poor soil that should exceed bearing capacity.
        """
        wall_height = 2.0 # m
        # Create a very poor soil to ensure high bearing pressure
        very_poor_soil = SoilType.objects.create(name="Swamp", angle_of_internal_friction=15, soil_density=18)
        results = calculate_retaining_wall_design(wall_height, very_poor_soil, self.heavy_load)

        self.assertEqual(results['status'], 'FAIL')
        self.assertGreater(results['calculations']['max_bearing_pressure_kPa'], 100)


class RetainingWallAPITests(TestCase):
    """
    Integration tests for the /api/calculate/ endpoint.
    """
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.calculate_url = reverse('calculate')
        cls.soil_type = SoilType.objects.create(
            name="API Test Soil",
            angle_of_internal_friction=35,
            soil_density=18
        )
        cls.heavy_surcharge_load = SurchargeLoad.objects.create(
            name="API Test Heavy Load",
            pressure=10
        )
        cls.no_surcharge_load = SurchargeLoad.objects.create(
            name="API Test No Load",
            pressure=0
        )
        cls.valid_payload = {
            "wall_height": 1.2,
            "soil_type_id": cls.soil_type.id,
            "surcharge_load_id": cls.no_surcharge_load.id, # Using no_surcharge_load for success case
            "is_adjacent_to_highway": False,
            "is_within_3_7m_of_street": False,
            "special_area_check": True
        }

    def test_api_success_with_valid_data(self):
        """
        Ensure the API returns 200 OK and a valid design for good input.
        """
        response = self.client.post(self.calculate_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('regulatory_gateway', response.data)
        self.assertIn('engineering_design', response.data)
        self.assertEqual(response.data['regulatory_gateway'][0]['level'], 'GREEN')
        self.assertEqual(response.data['engineering_design']['status'], 'OK')

    def test_api_returns_400_for_invalid_data(self):
        """
        Ensure the API returns 400 Bad Request for missing or invalid data.
        """
        payload = self.valid_payload.copy()
        payload.pop('wall_height') # Make payload invalid
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('wall_height', response.data)

    def test_api_returns_404_for_invalid_id(self):
        """
        Ensure the API returns 404 Not Found for a non-existent soil type id.
        """
        payload = self.valid_payload.copy()
        payload['soil_type_id'] = 999 # an ID that does not exist
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, 404)

    def test_regulatory_gateway_red_flag_for_height(self):
        """
        Test that the gateway returns a RED flag for a wall over 2.0m.
        """
        payload = self.valid_payload.copy()
        payload['wall_height'] = 2.1
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['regulatory_gateway'][0]['level'], 'RED')
        self.assertIn('over 2m high', response.data['regulatory_gateway'][0]['message'])

    def test_regulatory_gateway_red_flag_for_highway(self):
        """
        Test that the gateway returns a RED flag for a wall over 1.0m next to a highway.
        """
        payload = self.valid_payload.copy()
        payload['wall_height'] = 1.1
        payload['is_adjacent_to_highway'] = True
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['regulatory_gateway'][0]['level'], 'RED')
        self.assertIn('over 1m high and next to a highway', response.data['regulatory_gateway'][0]['message'])

    def test_special_area_check_validation(self):
        """
        Test that the serializer validation for special_area_check works.
        """
        payload = self.valid_payload.copy()
        payload['special_area_check'] = False
        response = self.client.post(self.calculate_url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('special_area_check', response.data)
