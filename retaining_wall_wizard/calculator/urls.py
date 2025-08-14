from django.urls import path
from .views import RetainingWallCalculatorView, SoilTypeListView, SurchargeLoadListView

urlpatterns = [
    path('calculate/', RetainingWallCalculatorView.as_view(), name='calculate'),
    path('soil-types/', SoilTypeListView.as_view(), name='soil-types-list'),
    path('surcharge-loads/', SurchargeLoadListView.as_view(), name='surcharge-loads-list'),
]
