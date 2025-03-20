import torch
import pandas as pd
from datetime import datetime, timedelta

from util import GlobalResources


def get_historical_weather_last_days(num_days: int) -> pd.DataFrame:
    resources = GlobalResources()
    historical_df = resources.get_historical_weather_df()

    current_date = datetime.now()
    date_n_days_ago = current_date - timedelta(days=num_days)

    return historical_df.loc[historical_df["date"] >= date_n_days_ago]


# TODO
async def predict_temperature_stress(forecast_df: pd.DataFrame) -> torch.Tensor:
    # Get historical data
    historical_data = get_historical_weather_last_days(365 * 2)
    combined_data = pd.concat([historical_data, forecast_df], ignore_index=True)

    resources = GlobalResources()
    temp_stress_model = resources.get_temp_stress_model()

    # Extract features required by the model
    feature_columns = ["temp_max", "temp_min", "temp_avg"]

    if not all(col in combined_data.columns for col in feature_columns):
        raise KeyError(f"Missing required columns in input data: {feature_columns}")

    features = combined_data[feature_columns].to_numpy()
    features_tensor = torch.from_numpy(features).float()

    # Ensure tensor is on the same device as the model
    device = next(temp_stress_model.parameters()).device
    features_tensor = features_tensor.to(device)

    # Predict temperature stress
    with torch.no_grad():
        stress_predictions = temp_stress_model(features_tensor)

    return stress_predictions
