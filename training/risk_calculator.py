OPT_VALUES_TEMP = {
    'SoyBean':{
        'TMaxOptimum': 32,
        'TMaxLimit': 45,
        'TMinOptimum': 22,
        'TMinLimit': 28,
        'TMinNoFrost': 4,
        'TMinFrost': -3
    },
    'Corn':{
        'TMaxOptimum': 33,
        'TMaxLimit': 44,
        'TMinOptimum': 22,
        'TMinLimit': 28,
        'TMinNoFrost': 4,
        'TMinFrost': -3
    },
    'Cotton':{
        'TMaxOptimum': 32,
        'TMaxLimit': 38,
        'TMinOptimum': 20,
        'TMinLimit': 25,
        'TMinNoFrost': 4,
        'TMinFrost': -3
    },
    'Rice':{
        'TMaxOptimum': 32,
        'TMaxLimit': 38,
        'TMinOptimum': 22,
        'TMinLimit': 28,
        'TMinNoFrost': -float('inf'),
        'TMinFrost': -float('inf')
    },
    'Wheat':{
        'TMaxOptimum': 25,
        'TMaxLimit': 32,
        'TMinOptimum': 15,
        'TMinLimit': 20,
        'TMinNoFrost': -float('inf'),
        'TMinFrost': -float('inf')
    }
}

def calculate_diurnal_heat_stress_risk(days_max, crop_type):
    opt_values = OPT_VALUES_TEMP[crop_type]
    avg_risk_heat = 0
    for day_max in days_max:
        if day_max <= opt_values['TMaxOptimum']:
            avg_risk_heat += 0
        elif day_max < opt_values['TMaxLimit']:
            avg_risk_heat += 9 * (day_max - opt_values['TMaxOptimum']) / (opt_values['TMaxLimit'] - opt_values['TMaxOptimum'])
        else:
            avg_risk_heat += 9
    return avg_risk_heat / len(days_max)

def calculate_notturnal_heat_stress_risk(days_min, crop_type):
    opt_values = OPT_VALUES_TEMP[crop_type]
    avg_night_risk = 0
    for day_min in days_min:
        if day_min >= opt_values['TMinNoFrost']:
            avg_night_risk += 0
        elif day_min < opt_values['TMinFrost']:
            avg_night_risk += 9 * abs(opt_values['TMinFrost'] - day_min) / abs(opt_values['TMinFrost'] - opt_values['TMinNoFrost'])
        else:
            avg_night_risk += 9
    return avg_night_risk / len(days_min)

def calculate_frost_risk(days_min, crop_type):
    opt_values = OPT_VALUES_TEMP[crop_type]
    avg_risk_frost = 0
    for day_min in days_min:
        if day_min < opt_values['TMinOptimum']:
            avg_risk_frost += 0
        elif day_min < opt_values['TMinLimit']:
            avg_risk_frost += 9 * (day_min - opt_values['TMinOptimum']) / (opt_values['TMinLimit'] - opt_values['TMinOptimum'])
        else:
            avg_risk_frost += 9
    return avg_risk_frost / len(days_min)

def riskCalculator(days_max, days_min, crop_type):
    heat_risk = calculate_diurnal_heat_stress_risk(days_max, crop_type)
    frost_risk = calculate_frost_risk(days_min, crop_type)
    night_risk = calculate_notturnal_heat_stress_risk(days_min, crop_type)
    return heat_risk, frost_risk, night_risk

def droughtRiskCalculator(cumulative_precipitation, cumulative_evapotranspiration, soil_moistrue, avg_temp):
    return (cumulative_precipitation - cumulative_evapotranspiration) + soil_moistrue / avg_temp