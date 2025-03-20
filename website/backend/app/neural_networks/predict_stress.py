import torch
import math
import pandas as pd
from datetime import datetime, timedelta

import config as c
from util.util import GlobalResources
from util.timed_cache import TimedCache, cached, CacheCategory


@cached(TimedCache(), category=CacheCategory.DB_DATA, ttl_seconds=12 * 3600)
def get_historical_weather_last_days(num_days: int) -> pd.DataFrame:
    resources = GlobalResources()
    historical_df = resources.get_historical_weather_df()

    current_date = datetime.strptime("2024/12/12 00:00:00", "%Y/%m/%d %H:%M:%S") # datetime.now() # TODO
    date_n_days_ago = current_date - timedelta(days=num_days)

    return historical_df.loc[historical_df["date"] > date_n_days_ago][:num_days]#TODO


# TODO
@cached(TimedCache(), category=CacheCategory.TEMP_STRESS_PREDICTION, ttl_seconds=12 * 3600)
def predict_temperature_stress(crop: str, forecast_df: pd.DataFrame) -> torch.Tensor:
    # Get historical data
    historical_data = get_historical_weather_last_days(c.NUM_DAYS_TEMP_STRESS_PREDICTION+8)
    combined_data = historical_data# pd.concat([historical_data, forecast_df], ignore_index=True) # TODO

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

    stress_data = {}
    for week in range(1, 13):
        start_index = (week - 1) * 3
        end_index = start_index + 3

        if end_index <= len(stress_predictions):
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


# TODO
@cached(TimedCache(), category=CacheCategory.DROUGHT_STRESS_PREDICTION, ttl_seconds=12 * 3600)
def predict_drought_stress(forecast_df: pd.DataFrame) -> torch.Tensor:
    # Get historical data
    historical_data = get_historical_weather_last_days(c.NUM_DAYS_DROUGHT_STRESS_PREDICTION)

    # Sum evaporation and precipitation in the whole considered historical period
    h_sum_columns = historical_data.filter(regex="_sum$").sum()
    # Average soil moisture and temperature in the whole considered historical period
    h_avg_columns = historical_data.filter(regex="_avg$").mean()
    # Historical data
    historical_data_parameters = pd.concat([h_sum_columns, h_avg_columns]).tolist()

    # Sum evaporation and precipitation in the forecast period
    f_sum_columns = forecast_df.filter(regex="_sum$").sum()
    # Average soil moisture and temperature in the forecast period
    f_avg_columns = forecast_df.filter(regex="_avg$").mean()
    # Forecast data
    forecast_data_parameters = pd.concat([f_sum_columns, f_avg_columns]).tolist()

    resources = GlobalResources()
    drought_stress_model = resources.get_drought_stress_model()

    # TODO
    features = combined_data[feature_columns].to_numpy()
    features_tensor = torch.from_numpy(features).float()

    # Ensure tensor is on the same device as the model
    device = next(drought_stress_model.parameters()).device
    features_tensor = features_tensor.to(device)

    # Predict temperature stress
    with torch.no_grad():
        stress_predictions = drought_stress_model(features_tensor)

    return stress_predictions
