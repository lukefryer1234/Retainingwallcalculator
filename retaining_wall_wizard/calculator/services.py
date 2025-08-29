import math
from .models import SoilType, WallMaterial

PARTIAL_FACTORS_DA1 = {
    'DA1/1': { 'gamma_G': 1.35, 'gamma_G_fav': 1.00, 'gamma_Q': 1.50, 'gamma_phi': 1.00, 'gamma_c': 1.00 },
    'DA1/2': { 'gamma_G': 1.00, 'gamma_G_fav': 1.00, 'gamma_Q': 1.30, 'gamma_phi': 1.25, 'gamma_c': 1.25 }
}
WATER_UNIT_WEIGHT = 9.81
LARGE_NUMBER = 99999.0

def _get_characteristic_values(validated_data):
    retained_soil = validated_data['retained_soil_type_id']
    foundation_soil = validated_data['foundation_soil_type_id']
    wall_material = validated_data['wall_material_id']
    return {
        'H': validated_data['retained_height'], 'B': validated_data['base_width'],
        't_base': validated_data['base_thickness'], 't_stem': validated_data['stem_thickness'],
        'B_toe': validated_data['toe_length'], 'B_heel': validated_data['heel_length'],
        'beta': math.radians(validated_data['ground_slope_angle']), 'Hw': validated_data['water_table_height'],
        'q': validated_data['surcharge_load'],
        'gamma_wall': (wall_material.unit_weight_min + wall_material.unit_weight_max) / 2,
        'gamma_retained': (retained_soil.unit_weight_dry_min + retained_soil.unit_weight_dry_max) / 2,
        'gamma_sat_retained': (retained_soil.unit_weight_saturated_min + retained_soil.unit_weight_saturated_max) / 2,
        'phi_k_retained': math.radians((retained_soil.phi_k_min + retained_soil.phi_k_max) / 2),
        'c_k_retained': (retained_soil.c_k_min + retained_soil.c_k_max) / 2,
        'phi_k_foundation': math.radians((foundation_soil.phi_k_min + foundation_soil.phi_k_max) / 2),
    }

def _calculate_earth_pressure_coeff(phi, beta):
    if beta > 0 and math.cos(beta)**2 < math.cos(phi)**2: return LARGE_NUMBER
    if beta == 0: return math.tan(math.radians(45) - phi / 2) ** 2
    cos_beta = math.cos(beta)
    term_under_sqrt = cos_beta**2 - math.cos(phi)**2
    if term_under_sqrt < 0: return LARGE_NUMBER
    numerator = cos_beta - math.sqrt(term_under_sqrt)
    denominator = cos_beta + math.sqrt(term_under_sqrt)
    if denominator == 0: return LARGE_NUMBER
    return cos_beta * (numerator / denominator)

def _perform_uls_checks(data, combination):
    factors = PARTIAL_FACTORS_DA1[combination]
    phi_d = math.atan(math.tan(data['phi_k_retained']) / factors['gamma_phi'])
    Ka_d = _calculate_earth_pressure_coeff(phi_d, data['beta'])

    H_total = data['H'] + data['t_base']
    Pa_k = 0.5 * data['gamma_retained'] * H_total**2 * Ka_d
    Pq_k = data['q'] * H_total * Ka_d

    W_stem = data['t_stem'] * data['H'] * data['gamma_wall']
    W_base = data['B'] * data['t_base'] * data['gamma_wall']
    W_soil = data['B_heel'] * data['H'] * data['gamma_retained']

    MOT_d = (Pa_k * (H_total/3) * factors['gamma_G']) + (Pq_k * (H_total/2) * factors['gamma_Q'])
    MR_d = (W_stem * (data['B_toe'] + data['t_stem']/2) * factors['gamma_G_fav']) + \
           (W_base * (data['B']/2) * factors['gamma_G_fav']) + \
           (W_soil * (data['B'] - data['B_heel']/2) * factors['gamma_G_fav'])

    Fslide_d = (Pa_k * factors['gamma_G']) + (Pq_k * factors['gamma_Q'])
    Fvertical_d = (W_stem + W_base + W_soil) * factors['gamma_G_fav']

    phi_d_foundation = math.atan(math.tan(data['phi_k_foundation']) / factors['gamma_phi'])
    Fresist_d = Fvertical_d * math.tan(phi_d_foundation)

    overturning_ok = MR_d >= MOT_d
    sliding_ok = Fresist_d >= Fslide_d

    if Fvertical_d <= 0:
        eccentricity = LARGE_NUMBER
        qmax_d = LARGE_NUMBER
    else:
        eccentricity = (data['B'] / 2) - ((MR_d - MOT_d) / Fvertical_d)
        if abs(eccentricity) <= data['B'] / 6:
            qmax_d = (Fvertical_d / data['B']) * (1 + 6 * abs(eccentricity) / data['B'])
        else:
            denominator = 3 * (data['B']/2 - abs(eccentricity))
            qmax_d = (2 * Fvertical_d) / denominator if denominator > 0 else LARGE_NUMBER

    bearing_ok = qmax_d <= 100

    return {
        "overturning_moment_d": round(MOT_d, 2), "restoring_moment_d": round(MR_d, 2), "overturning_ok": overturning_ok,
        "sliding_force_d": round(Fslide_d, 2), "resisting_force_d": round(Fresist_d, 2), "sliding_ok": sliding_ok,
        "max_bearing_pressure_d": round(qmax_d, 2), "bearing_ok": bearing_ok, "eccentricity": round(eccentricity, 3),
    }

def run_eurocode_7_calculation(validated_data):
    char_values = _get_characteristic_values(validated_data)
    results_da1_1 = _perform_uls_checks(char_values, 'DA1/1')
    results_da1_2 = _perform_uls_checks(char_values, 'DA1/2')

    overall_status = all([results_da1_1['overturning_ok'], results_da1_1['sliding_ok'], results_da1_1['bearing_ok'],
                          results_da1_2['overturning_ok'], results_da1_2['sliding_ok'], results_da1_2['bearing_ok']])

    serializable_inputs = validated_data.copy()
    serializable_inputs['wall_material_id'] = serializable_inputs['wall_material_id'].id
    serializable_inputs['retained_soil_type_id'] = serializable_inputs['retained_soil_type_id'].id
    serializable_inputs['foundation_soil_type_id'] = serializable_inputs['foundation_soil_type_id'].id

    return {
        "inputs": serializable_inputs,
        "characteristic_values": {k: round(v, 2) if isinstance(v, float) else v for k, v in char_values.items()},
        "results_DA1_1": results_da1_1, "results_DA1_2": results_da1_2, "overall_status": "PASS" if overall_status else "FAIL",
        "warnings": ["Bearing capacity check is simplified.", "Hydrostatic pressure is not yet implemented."]
    }
