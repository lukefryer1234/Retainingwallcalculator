from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import SoilType, SurchargeLoad
from .serializers import SoilTypeSerializer, SurchargeLoadSerializer
# Note the change in imports from services
from .services import process_retaining_wall_request


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
    Uses the unified service to process the request.
    """
    def post(self, request, *args, **kwargs):
        result_data, error_response = process_retaining_wall_request(request.data)
        if error_response:
            return error_response
        return Response(result_data, status=status.HTTP_200_OK)


class GeneratePDFView(APIView):
    """
    API View to generate a PDF report from calculation data.
    Uses the unified service to process the request.
    """
    def post(self, request, *args, **kwargs):
        result_data, error_response = process_retaining_wall_request(request.data)
        if error_response:
            # We can't generate a PDF from an error, so return the JSON error
            return error_response

        # Render the HTML template with the context from the service
        html_string = render_to_string('pdf_template.html', result_data)
        pdf_file = HTML(string=html_string).write_pdf()

        # Create the HTTP response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="retaining_wall_report.pdf"'
        return response
