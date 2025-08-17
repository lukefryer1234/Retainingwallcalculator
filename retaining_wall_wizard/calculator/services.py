import math
from rest_framework.response import Response
from rest_framework import status
from .models import SoilType, SurchargeLoad
from .serializers import CalculationInputSerializer


# --- Constants based on project brief & standard practice ---
# Safety Factors
SF_OVERTURNING = 2.0
SF_SLIDING = 1.5
# Assumed soil bearing capacity (kN/m^2) for typical firm ground
SOIL_BEARING_CAPACITY = 100
# Density of concrete (kN/m^3)
CONCRETE_DENSITY = 24
# Friction coefficient between concrete base and soil (can be simplified as tan(phi))
BASE_FRICTION_COEFFICIENT_FACTOR = 0.7  # Typically 0.5 to 0.7 of tan(phi)

# Material properties (can be expanded later)
BLOCK_WIDTH = 0.215 # Standard 215mm block depth becomes the wall stem thickness

def calculate_retaining_wall_design(wall_height, soil, surcharge):
    """
    Performs the core engineering calculations for a retaining wall.

    Args:
        wall_height (float): The height of the wall in meters (H).
        soil (SoilType): The SoilType object with its properties.
        surcharge (SurchargeLoad): The SurchargeLoad object with its properties.

    Returns:
        dict: A dictionary containing the calculated design specifications,
              safety factors, and a status indicating success or failure.
    """
    # --- Input parameters from data models ---
    H = wall_height
    phi_deg = soil.angle_of_internal_friction
    gamma = soil.soil_density
    q = surcharge.pressure

    phi_rad = math.radians(phi_deg)

    # --- 1. Calculate Lateral Earth Pressure (Rankine Theory) ---
    Ka = math.tan(math.radians(45 - phi_deg / 2)) ** 2

    # Force from soil pressure (Pa) and its point of action
    Pa = 0.5 * Ka * gamma * H**2
    h_Pa = H / 3

    # Force from surcharge pressure (Ps) and its point of action
    Ps = q * Ka * H
    h_Ps = H / 2

    # --- 2. Initial Design Assumptions (based on project brief) ---
    # Foundation dimensions
    foundation_width = H * 0.5
    # A standard cantilever design where stem is in the middle third
    toe_length = foundation_width / 3
    heel_length = foundation_width - toe_length - BLOCK_WIDTH

    foundation_depth = max(0.3, H / 4)

    # --- 3. Calculate Forces and Moments for Stability Analysis ---
    # Weights (per meter length of wall)
    W_stem = BLOCK_WIDTH * H * CONCRETE_DENSITY
    W_base = foundation_width * foundation_depth * CONCRETE_DENSITY
    # Weight of the soil on the heel of the foundation
    W_soil_on_heel = heel_length * H * gamma if heel_length > 0 else 0

    # Horizontal (Sliding) Forces
    total_sliding_force = Pa + Ps

    # Vertical Forces for Resistance
    total_vertical_force = W_stem + W_base + W_soil_on_heel

    # Resisting Force against Sliding
    base_friction_coeff = math.tan(phi_rad) * BASE_FRICTION_COEFFICIENT_FACTOR
    sliding_resistance_force = total_vertical_force * base_friction_coeff

    # Moments (calculated about the toe of the foundation)
    # Overturning Moments
    overturning_moment = (Pa * h_Pa) + (Ps * h_Ps)

    # Resisting (Stabilising) Moments
    M_stem = W_stem * (toe_length + BLOCK_WIDTH / 2)
    M_base = W_base * (foundation_width / 2)
    M_soil_on_heel = W_soil_on_heel * (foundation_width - heel_length / 2) if heel_length > 0 else 0
    resisting_moment = M_stem + M_base + M_soil_on_heel

    # --- 4. Check Safety Factors and Bearing Pressure ---
    sf_overturning = resisting_moment / overturning_moment if overturning_moment > 0 else float('inf')
    sf_sliding = sliding_resistance_force / total_sliding_force if total_sliding_force > 0 else float('inf')

    # Bearing Pressure
    # Calculate eccentricity
    if total_vertical_force > 0:
        moment_arm_of_vertical_force = (resisting_moment - overturning_moment) / total_vertical_force
        eccentricity = (foundation_width / 2) - moment_arm_of_vertical_force
    else:
        eccentricity = 0


    # Check if eccentricity is within the middle third (kern)
    is_in_middle_third = abs(eccentricity) <= (foundation_width / 6)

    # Calculate max and min bearing pressure
    if total_vertical_force > 0:
        if is_in_middle_third:
            pressure_at_toe = (total_vertical_force / foundation_width) * (1 + 6 * eccentricity / foundation_width)
        else:
            # Outside middle third, implies tension and uplift at the heel
            pressure_at_toe = (2 * total_vertical_force) / (3 * ((foundation_width / 2) - eccentricity)) if ((foundation_width / 2) - eccentricity) > 0 else float('inf')
    else:
        pressure_at_toe = 0


    max_bearing_pressure = pressure_at_toe

    # --- 5. Determine Design Status ---
    design_is_ok = (
        sf_overturning >= SF_OVERTURNING and
        sf_sliding >= SF_SLIDING and
        max_bearing_pressure <= SOIL_BEARING_CAPACITY
    )

    # --- 6. Compile Results ---
    # These are simplified outputs based on the brief
    results = {
        "status": "OK" if design_is_ok else "FAIL",
        "inputs": {
            "wall_height": H,
            "soil_type": soil.name,
            "surcharge_load": surcharge.name,
        },
        "design_specifications": {
            "foundation_width": round(foundation_width, 2),
            "foundation_depth": round(foundation_depth, 2),
            "concrete_mix": "C20/25 mix",
            "vertical_rebar_size": "12mm high-tensile rebar",
            "vertical_rebar_spacing": "Every 400mm / in every other block core",
            "horizontal_rebar": "Add 'bed-joint' reinforcement every two courses",
            "concrete_infill": "All hollow blocks must be filled with C20/25 concrete",
            "drainage_pipe": "110mm perforated land drain is essential",
            "drainage_aggregate": "Backfill with 300mm of clean drainage aggregate (e.g., 20mm gravel)",
            "weep_holes": "Add 75mm weep holes every 1.5m",
        },
        "calculations": {
            "safety_factor_overturning": round(sf_overturning, 2),
            "safety_factor_sliding": round(sf_sliding, 2),
            "max_bearing_pressure_kPa": round(max_bearing_pressure, 2),
            "eccentricity_mm": round(eccentricity * 1000, 1),
            "is_in_middle_third": is_in_middle_third,
        },
        "required_sf": {
            "overturning": SF_OVERTURNING,
            "sliding": SF_SLIDING,
            "bearing_capacity_kPa": SOIL_BEARING_CAPACITY,
        }
    }
    return results


def process_retaining_wall_request(request_data):
    """
    A unified service to handle a request, validate it, and return all results.
    Returns a tuple of (result_data, error_response).
    If successful, error_response will be None.
    If an error occurs, result_data will be None.
    """
    serializer = CalculationInputSerializer(data=request_data)
    if not serializer.is_valid():
        return None, Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data

    try:
        soil_type = SoilType.objects.get(pk=validated_data['soil_type_id'])
        surcharge_load = SurchargeLoad.objects.get(pk=validated_data['surcharge_load_id'])
    except (SoilType.DoesNotExist, SurchargeLoad.DoesNotExist):
        return None, Response(
            {"error": "Invalid soil_type_id or surcharge_load_id."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Engineering calculations
    engineering_design = calculate_retaining_wall_design(
        wall_height=validated_data['wall_height'],
        soil=soil_type,
        surcharge=surcharge_load
    )

    # Regulatory gateway checks
    flags = []
    wall_height = validated_data['wall_height']
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
            "message": "Good to Go! Your project appears to fall within permitted development."
        })

    # Compile the final response data
    final_data = {
        "regulatory_gateway": flags,
        "engineering_design": engineering_design
    }

    return final_data, None
