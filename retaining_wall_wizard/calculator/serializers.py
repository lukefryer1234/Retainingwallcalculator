from rest_framework import serializers
from .models import SoilType, WallMaterial, SurchargeLoad

class SoilTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilType
        fields = '__all__'

class WallMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = WallMaterial
        fields = '__all__'

class SurchargeLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurchargeLoad
        fields = '__all__'

class CalculationInputSerializer(serializers.Serializer):
    retained_height = serializers.FloatField(min_value=0.1, max_value=10.0)
    wall_material_id = serializers.PrimaryKeyRelatedField(queryset=WallMaterial.objects.all(), label="Wall Material")

    # Wall Dimensions
    stem_thickness = serializers.FloatField(min_value=0.1, max_value=5.0)
    base_width = serializers.FloatField(min_value=0.1, max_value=10.0)
    base_thickness = serializers.FloatField(default=0.3, min_value=0.1, max_value=5.0)
    toe_length = serializers.FloatField(min_value=0.0, max_value=10.0)
    heel_length = serializers.FloatField(min_value=0.0, max_value=10.0)

    # Soil Types
    retained_soil_type_id = serializers.PrimaryKeyRelatedField(queryset=SoilType.objects.all(), label="Retained Soil Type")
    foundation_soil_type_id = serializers.PrimaryKeyRelatedField(queryset=SoilType.objects.all(), label="Foundation Soil Type")

    # Ground Profile
    ground_slope_angle = serializers.FloatField(default=0, min_value=0, max_value=45)
    # Groundwater
    water_table_height = serializers.FloatField(default=0, min_value=0)
    # Surcharge
    surcharge_load = serializers.FloatField(default=0, min_value=0)

    def validate(self, data):
        if not (data['toe_length'] + data['heel_length'] <= data['base_width']):
            raise serializers.ValidationError("The sum of toe and heel length must be less than or equal to the base width.")
        if data['water_table_height'] > data['retained_height']:
            raise serializers.ValidationError("Water table height cannot be greater than the retained height.")
        return data
