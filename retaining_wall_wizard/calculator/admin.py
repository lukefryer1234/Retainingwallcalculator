from django.contrib import admin
from .models import SoilType, SurchargeLoad, WallMaterial

@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the SoilType model.
    """
    list_display = ('name', 'phi_k_min', 'phi_k_max', 'c_k_min', 'c_k_max')
    search_fields = ('name',)

@admin.register(SurchargeLoad)
class SurchargeLoadAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the SurchargeLoad model.
    """
    list_display = ('name', 'pressure')
    search_fields = ('name',)

@admin.register(WallMaterial)
class WallMaterialAdmin(admin.ModelAdmin):
    """
    Custom admin configuration for the WallMaterial model.
    """
    list_display = ('name', 'unit_weight_min', 'unit_weight_max')
    search_fields = ('name',)
