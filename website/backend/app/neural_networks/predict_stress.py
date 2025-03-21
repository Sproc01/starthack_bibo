import torch
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import config as c
from util.load_resources import GlobalResources
from util.timed_cache import TimedCache, cached, CacheCategory


@cached(TimedCache(), category=CacheCategory.DB_DATA, ttl_seconds=12 * 3600)
def get_historical_weather_last_days(num_days: int) -> pd.DataFrame:
    resources = GlobalResources()
    historical_df = resources.get_historical_weather_df()

    current_date = datetime.now()
    date_n_days_ago = current_date - timedelta(days=(num_days + 1))  # All dates start at midnight

    return historical_df.loc[historical_df["date"] >= date_n_days_ago]


@cached(TimedCache(), category=CacheCategory.TEMP_STRESS_PREDICTION, ttl_seconds=12 * 3600)
def predict_temperature_stress(crop: str, forecast_df: pd.DataFrame) -> torch.Tensor:
    # Get historical data
    historical_data = get_historical_weather_last_days(c.NUM_DAYS_TEMP_STRESS_PREDICTION)
    combined_data = pd.concat([historical_data, forecast_df], ignore_index=True)

    resources = GlobalResources()
    temp_stress_model = resources.get_temp_stress_model(crop)

    # Extract features required by the model
    feature_columns = ["temp_max", "temp_min"]
    features = combined_data[feature_columns].to_numpy()
    features_tensor = torch.tensor(features, dtype=torch.float32)
    features_tensor_flat = features_tensor.reshape(-1)  # Alternate max and min

    # Ensure tensor is on the same device as the model
    device = next(temp_stress_model.parameters()).device
    features_tensor_flat = features_tensor_flat.to(device)

    # Predict temperature stress
    with torch.no_grad():
        stress_predictions = temp_stress_model(features_tensor_flat)

    # The output tensor contains 3 values of stress for each of the 12 following weeks
    stress_data = {}
    for week in range(1, 13):
        start_index = (week - 1) * 3
        end_index = start_index + 3

        week_data = stress_predictions[start_index:end_index]
        avg_diurnal_stress = math.floor(week_data[0].item() * 10)
        avg_frost_stress = math.floor(week_data[1].item() * 10)
        avg_nighttime_stress = math.floor(week_data[2].item() * 10)

        stress_data[f"week_{week}"] = {
            "avg_diurnal_stress": avg_diurnal_stress,
            "avg_frost_stress": avg_frost_stress,
            "avg_nighttime_stress": avg_nighttime_stress,
        }

    return stress_data


@cached(TimedCache(), category=CacheCategory.DROUGHT_STRESS_PREDICTION, ttl_seconds=12 * 3600)
def predict_drought_stress(forecast_df: pd.DataFrame) -> torch.Tensor:
    f_evaporation_sum = forecast_df["evaporation_sum"].sum()
    f_rainfall_sum = forecast_df["rainfall_sum"].sum()
    f_soil_moisture_avg = forecast_df["soil_moisture_avg"].mean()
    f_temp_avg = forecast_df["temp_avg"].mean()

    forecast_data_parameters = [f_evaporation_sum, f_rainfall_sum, f_soil_moisture_avg, f_temp_avg]

    # Get historical data
    historical_data = get_historical_weather_last_days(c.NUM_DAYS_DROUGHT_STRESS_PREDICTION)

    h_evaporation_sum = historical_data["evaporation_sum"].sum()
    h_rainfall_sum = historical_data["rainfall_sum"].sum()
    h_soil_moisture_avg = historical_data["soil_moisture_avg"].mean()
    h_temp_avg = historical_data["temp_avg"].mean()

    historical_data_parameters = [h_evaporation_sum, h_rainfall_sum, h_soil_moisture_avg, h_temp_avg]

    resources = GlobalResources()
    drought_stress_model = resources.get_drought_stress_model()

    features = np.array([forecast_data_parameters + historical_data_parameters])
    features_tensor = torch.from_numpy(features).float()

    # Ensure tensor is on the same device as the model
    device = next(drought_stress_model.parameters()).device
    features_tensor = features_tensor.to(device)

    # Predict temperature stress
    with torch.no_grad():
        stress_predictions = drought_stress_model(features_tensor)

    # The output tensor contains 1 value for the drought index for each of the 12 following weeks
    stress_data = {}
    for week in range(1, 13):
        week_index = week - 1

        drought_stress = math.floor(stress_predictions[0][week_index] * 10)

        stress_data[f"week_{week}"] = {
            "drought_stress": drought_stress,
        }

    return stress_data
