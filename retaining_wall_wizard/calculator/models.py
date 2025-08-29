from django.db import models

class SoilType(models.Model):
    """
    Represents a type of soil with its engineering properties based on BSCS.
    Values are typical characteristic values for UK soils as per the design guide.
    """
    name = models.CharField(max_length=255, unique=True, help_text="British Soil Classification System name (e.g., 'Well-graded Gravel (GW)')")
    notes = models.TextField(blank=True, help_text="Notes on soil characteristics (e.g., 'Free-draining, high strength')")

    # Unit Weight (gamma) in kN/m^3
    unit_weight_dry_min = models.FloatField(help_text="Typical minimum dry unit weight (kN/m^3)")
    unit_weight_dry_max = models.FloatField(help_text="Typical maximum dry unit weight (kN/m^3)")
    unit_weight_saturated_min = models.FloatField(help_text="Typical minimum saturated unit weight (kN/m^3)")
    unit_weight_saturated_max = models.FloatField(help_text="Typical maximum saturated unit weight (kN/m^3)")

    # Angle of Shearing Resistance (phi') in degrees
    phi_k_min = models.FloatField(help_text="Characteristic minimum angle of shearing resistance (phi_k') in degrees")
    phi_k_max = models.FloatField(help_text="Characteristic maximum angle of shearing resistance (phi_k') in degrees")

    # Effective Cohesion (c') in kPa
    c_k_min = models.FloatField(help_text="Characteristic minimum effective cohesion (c_k') in kPa")
    c_k_max = models.FloatField(help_text="Characteristic maximum effective cohesion (c_k') in kPa")

    def __str__(self):
        return self.name

class WallMaterial(models.Model):
    """
    Represents a type of construction material for the retaining wall.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Name of the construction material (e.g., 'Mass / Reinforced Concrete')")
    unit_weight_min = models.FloatField(help_text="Typical minimum unit weight (gamma) in kN/m^3")
    unit_weight_max = models.FloatField(help_text="Typical maximum unit weight (gamma) in kN/m^3")

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
