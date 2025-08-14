from rest_framework import serializers

class CalculationInputSerializer(serializers.Serializer):
    """
    Serializer for the input data required for the retaining wall calculation.
    """
    wall_height = serializers.FloatField(min_value=0.3, max_value=2.5)
    soil_type_id = serializers.IntegerField()
    surcharge_load_id = serializers.IntegerField()
    # The following fields are for the regulatory gateway checks
    is_adjacent_to_highway = serializers.BooleanField()
    is_within_3_7m_of_street = serializers.BooleanField()
    special_area_check = serializers.BooleanField()

    def validate_special_area_check(self, value):
        """
        Check that the user has confirmed they are not in a special area.
        """
        if not value:
            raise serializers.ValidationError("You must confirm the property is not in a special area to proceed.")
        return value


class SoilTypeSerializer(serializers.Serializer):
    """
    Serializer for the SoilType model, exposing id and name.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class SurchargeLoadSerializer(serializers.Serializer):
    """
    Serializer for the SurchargeLoad model, exposing id and name.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
