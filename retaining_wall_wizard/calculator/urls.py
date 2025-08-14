from django.urls import path
from .views import RetainingWallCalculatorView

urlpatterns = [
    path('calculate/', RetainingWallCalculatorView.as_view(), name='calculate'),
]
