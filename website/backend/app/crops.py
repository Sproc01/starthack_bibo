CROPS = ["soybean", "corn", "cotton", "rice", "wheat"]

CROPS_TEMPERATURE_THRESHOLDS = {
    "soybean": {
        "temp_max_optimum": 32,
        "temp_max_limit": 45,
        "temp_min_optimum": 22,
        "temp_min_limit": 28,
        "temp_min_no_frost": 4,
        "temp_min_frost": -3,
    },
    "corn": {
        "temp_max_optimum": 33,
        "temp_max_limit": 44,
        "temp_min_optimum": 22,
        "temp_min_limit": 28,
        "temp_min_no_frost": 4,
        "temp_min_frost": -3,
    },
    "cotton": {
        "temp_max_optimum": 32,
        "temp_max_limit": 38,
        "temp_min_optimum": 20,
        "temp_min_limit": 25,
        "temp_min_no_frost": 4,
        "temp_min_frost": -3,
    },
    "rice": {
        "temp_max_optimum": 32,
        "temp_max_limit": 38,
        "temp_min_optimum": 22,
        "temp_min_limit": 28,
        "temp_min_no_frost": -float("inf"),
        "temp_min_frost": -float("inf"),
    },
    "wheat": {
        "temp_max_optimum": 25,
        "temp_max_limit": 32,
        "temp_min_optimum": 15,
        "temp_min_limit": 20,
        "temp_min_no_frost": -float("inf"),
        "temp_min_frost": -float("inf"),
    },
}


def get_avg_diurnal_heat_stress(max_temp_days, crop_type):
    threshold_values = CROPS_TEMPERATURE_THRESHOLDS[crop_type]
    avg_diurnal_heat_stress = 0
    for max_temp in max_temp_days:
        if max_temp <= threshold_values["temp_max_optimum"]:
            avg_diurnal_heat_stress += 0
        elif max_temp < threshold_values["temp_max_limit"]:
            avg_diurnal_heat_stress += (
                9
                * (max_temp - threshold_values["temp_max_optimum"])
                / (threshold_values["temp_max_limit"] - threshold_values["temp_max_optimum"])
            )
        else:
            avg_diurnal_heat_stress += 9
    return avg_diurnal_heat_stress / len(max_temp_days)


def get_avg_nighttime_heat_stress(min_temp_days, crop_type):
    threshold_values = CROPS_TEMPERATURE_THRESHOLDS[crop_type]
    avg_night_heat_stress = 0
    for min_temp in min_temp_days:
        if min_temp >= threshold_values["temp_min_no_frost"]:
            avg_night_heat_stress += 0
        elif min_temp < threshold_values["temp_min_frost"]:
            avg_night_heat_stress += (
                9
                * abs(threshold_values["temp_min_frost"] - min_temp)
                / abs(threshold_values["temp_min_frost"] - threshold_values["temp_min_no_frost"])
            )
        else:
            avg_night_heat_stress += 9
    return avg_night_heat_stress / len(min_temp_days)


def get_avg_frost_stress(min_temp_days, crop_type):
    threshold_values = CROPS_TEMPERATURE_THRESHOLDS[crop_type]
    avg_frost_stress = 0
    for min_temp in min_temp_days:
        if min_temp < threshold_values["temp_min_optimum"]:
            avg_frost_stress += 0
        elif min_temp < threshold_values["temp_min_limit"]:
            avg_frost_stress += (
                9
                * (min_temp - threshold_values["temp_min_optimum"])
                / (threshold_values["temp_min_limit"] - threshold_values["temp_min_optimum"])
            )
        else:
            avg_frost_stress += 9
    return avg_frost_stress / len(min_temp_days)


def get_drought_risk(rainfall_sum, evaporation_sum, soil_moisture_avg, temp_avg):
    return (rainfall_sum - evaporation_sum) + soil_moisture_avg / temp_avg
