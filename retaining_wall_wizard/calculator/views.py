from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import SoilType, SurchargeLoad
from .serializers import CalculationInputSerializer, SoilTypeSerializer, SurchargeLoadSerializer
from .services import calculate_retaining_wall_design


class SoilTypeListView(generics.ListAPIView):
    """
    Read-only endpoint to list all available soil types.
    """
    queryset = SoilType.objects.all()
    serializer_class = SoilTypeSerializer


class SurchargeLoadListView(generics.ListAPIView):
    """
    Read-only endpoint to list all available surcharge loads.
    """
    queryset = SurchargeLoad.objects.all()
    serializer_class = SurchargeLoadSerializer


class RetainingWallCalculatorView(APIView):
    """
    API View for the Retaining Wall Calculator.
    Accepts user inputs, performs regulatory checks, runs engineering
    calculations, and returns the final design specifications.
    """
    def post(self, request, *args, **kwargs):
        serializer = CalculationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        wall_height = validated_data['wall_height']

        # --- Step 1: The Regulatory Gateway ---
        flags = []
        if wall_height > 1.0 and validated_data['is_adjacent_to_highway']:
            flags.append({
                "level": "RED",
                "message": "STOP: Planning Permission is likely required as the wall is over 1m high and next to a highway. Consult Powys County Council."
            })

        if wall_height > 2.0:
            flags.append({
                "level": "RED",
                "message": "STOP: Planning Permission is likely required as the wall is over 2m high. Consult Powys County Council."
            })

        if wall_height > 1.5:
            flags.append({
                "level": "ORANGE",
                "message": "CAUTION: Building Regulations approval is likely required as the wall is retaining over 1.5m of earth. The calculations provided are for guidance only and must be verified by a structural engineer."
            })

        if wall_height > 1.37 and validated_data['is_within_3_7m_of_street']:
             flags.append({
                "level": "ORANGE",
                "message": "CAUTION: Approval under the Highways Act 1980 is likely required. Consult Powys County Council's highways department."
            })

        if not flags:
            flags.append({
                "level": "GREEN",
                "message": "Good to Go! Your project appears to fall within permitted development. Let's design it."
            })

        # --- Step 2 & 3: Wall & Soil Specification & Design ---
        try:
            soil_type = SoilType.objects.get(pk=validated_data['soil_type_id'])
            surcharge_load = SurchargeLoad.objects.get(pk=validated_data['surcharge_load_id'])
        except (SoilType.DoesNotExist, SurchargeLoad.DoesNotExist):
            return Response(
                {"error": "Invalid soil_type_id or surcharge_load_id."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Call the engineering calculation service
        design_results = calculate_retaining_wall_design(
            wall_height=wall_height,
            soil=soil_type,
            surcharge=surcharge_load
        )

        # Combine regulatory flags and design results into a single response
        final_response = {
            "regulatory_gateway": flags,
            "engineering_design": design_results
        }

        return Response(final_response, status=status.HTTP_200_OK)
