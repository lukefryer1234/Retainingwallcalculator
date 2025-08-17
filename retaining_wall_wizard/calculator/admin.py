from django.contrib import admin
from .models import SoilType, SurchargeLoad

@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the SoilType model.
    """
    list_display = ('name', 'angle_of_internal_friction', 'soil_density')
    search_fields = ('name',)

@admin.register(SurchargeLoad)
class SurchargeLoadAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the SurchargeLoad model.
    """
    list_display = ('name', 'pressure')
    search_fields = ('name',)
