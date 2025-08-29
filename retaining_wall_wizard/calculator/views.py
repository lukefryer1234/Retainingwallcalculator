from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import SoilType, SurchargeLoad, WallMaterial
from .serializers import SoilTypeSerializer, SurchargeLoadSerializer, WallMaterialSerializer, CalculationInputSerializer
from .services import run_eurocode_7_calculation

class SoilTypeListAPIView(generics.ListAPIView):
    """
    Read-only endpoint to list all available soil types.
    """
    queryset = SoilType.objects.all()
    serializer_class = SoilTypeSerializer

class WallMaterialListAPIView(generics.ListAPIView):
    """
    Read-only endpoint to list all available wall materials.
    """
    queryset = WallMaterial.objects.all()
    serializer_class = WallMaterialSerializer

class SurchargeLoadListView(generics.ListAPIView):
    """
    Read-only endpoint to list all available surcharge loads.
    """
    queryset = SurchargeLoad.objects.all()
    serializer_class = SurchargeLoadSerializer

class RetainingWallCalculatorView(APIView):
    """
    API View for the Retaining Wall Calculator.
    """
    def post(self, request, *args, **kwargs):
        serializer = CalculationInputSerializer(data=request.data)
        if serializer.is_valid():
            results = run_eurocode_7_calculation(serializer.validated_data)
            return Response(results, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GeneratePDFView(APIView):
    """
    API View to generate a PDF report from calculation data.
    This will need to be updated later to work with the new calculation output.
    """
    def post(self, request, *args, **kwargs):
        # This view is temporarily disabled until the new calculation service is built.
        return Response(
            {"message": "PDF generation is temporarily disabled and will be updated with the new calculation engine."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
