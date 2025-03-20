def RiskCalculator(days_max, days_min, opt_values):
    avg_risk_heat = 0
    avg_risk_frost = 0
    avg_night_risk = 0
    for i in range(len(days_max)):
        if days_max[i] < opt_values['TMaxOptimum']:
            avg_risk_heat += 0
        elif days_max[i] < opt_values['TMaxLimit']:
            avg_risk_heat += 9 * (days_max[i] - opt_values['TMaxOptimum']) / ( opt_values['TMaxLimit'] - opt_values['TMaxOptimum'])
        else:
            avg_risk_heat += 9

        if days_min[i] < opt_values['TMinOptimum']:
            avg_risk_frost += 0
        elif days_min[i] < opt_values['TMinLimit']:
            avg_risk_frost += 9 * (days_min[i] - opt_values['TMinOptimum']) / ( opt_values['TMinLimit'] - opt_values['TMinOptimum'])
        else:
            avg_risk_frost += 9

        if days_min[i] >= opt_values['TMinNoFrost']:
            avg_night_risk += 0
        elif days_min[i] < opt_values['TMinFrost']:
            avg_night_risk += 9 * abs(opt_values['TMinFrost'] - days_min[i]) / abs(opt_values['TMinFrost'] - opt_values['TMinNoFrost'])
        else:
            avg_night_risk += 9

    return avg_risk_heat/len(days_max), avg_risk_frost/len(days_min), avg_night_risk/len(days_min)