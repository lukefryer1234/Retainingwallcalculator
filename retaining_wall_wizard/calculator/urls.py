from django.urls import path
from .views import (
    RetainingWallCalculatorView,
    SoilTypeListAPIView,
    SurchargeLoadListView,
    WallMaterialListAPIView,
    GeneratePDFView
)

urlpatterns = [
    path('calculate/', RetainingWallCalculatorView.as_view(), name='calculate'),
    path('soil-types/', SoilTypeListAPIView.as_view(), name='soil-types-list'),
    path('wall-materials/', WallMaterialListAPIView.as_view(), name='wall-materials-list'),
    path('surcharge-loads/', SurchargeLoadListView.as_view(), name='surcharge-loads-list'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate-pdf'),
]
