from django.db import models

class SoilType(models.Model):
    """
    Represents a type of soil with its engineering properties.
    """
    name = models.CharField(max_length=255, help_text="User-friendly name for the soil type (e.g., 'Sandy Gravel (Good Drainage)')")
    angle_of_internal_friction = models.FloatField(help_text="Angle of internal friction (phi) in degrees")
    soil_density = models.FloatField(help_text="Density of the soil (gamma) in kN/m^3")

    def __str__(self):
        return self.name

class SurchargeLoad(models.Model):
    """
    Represents a type of surcharge load on the land above the wall.
    """
    name = models.CharField(max_length=255, help_text="User-friendly name for the surcharge load (e.g., 'Flat Garden/Lawn (Light Load)')")
    pressure = models.FloatField(help_text="Equivalent uniform pressure (q) in kN/m^2")

    def __str__(self):
        return self.name
