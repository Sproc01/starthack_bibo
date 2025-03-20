import torch
import requests
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

import crops
import config as c
from neural_networks.neural_network_temp_stress import NN_temp_stress
from neural_networks.neural_network_drought_stress import NN_drought_stress
from util.util import SingletonMeta


def fetch_historical_weather_data(start_date: str, end_date: str):
    payload = {
        "units": {"temperature": "C", "velocity": "km/h", "length": "metric", "energy": "watts"},
        "geometry": {
            "type": "MultiPoint",
            "coordinates": [[c.SORRISO_LONGITUDE, c.SORRISO_LATITUDE]],
            "locationNames": [c.SORRISO_NAME],
            "mode": "preferLandWithMatchingElevation",
        },
        "format": "json",
        "timeIntervals": [f"{start_date}T+01:00/{end_date}T+01:00"],
        "timeIntervalsAlignment": "none",
        "queries": [
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 11, "level": "2 m above gnd", "aggregation": "mean"}],  # Average Temperature
            },
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 11, "level": "2 m above gnd", "aggregation": "max"}],  # Max Temperature
            },
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 11, "level": "2 m above gnd", "aggregation": "min"}],  # Min Temperature
            },
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 61, "level": "sfc", "aggregation": "sum"}],  # Rainfall sum
            },
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 144, "level": "0-7 cm down", "aggregation": "mean"}],  # Average soil moisture
            },
            {
                "domain": "ERA5T",
                "gapFillDomain": "NEMSGLOBAL",
                "timeResolution": "daily",
                "codes": [{"code": 260, "level": "2 m above gnd", "aggregation": "sum"}],  # Evaporation sum
            },
        ],
    }

    headers = {"content-type": "application/json"}
    querystring = {"apikey": c.HISTORICAL_API_KEY}
    response = requests.post(c.HISTORICAL_API_URL, json=payload, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    response_data = response.json()

    # Extract time intervals (dates)
    dates = [
        datetime.strptime(date.split("T")[0], "%Y%m%d").strftime("%Y-%m-%d")
        for date in response_data[0]["timeIntervals"][0]
    ]

    # Extract average temperatures
    avg_temps = response_data[0]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Extract max temperatures
    max_temps = response_data[1]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Extract min temperatures
    min_temps = response_data[2]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Extract rainfall sum
    rainfall_sum = response_data[3]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Extract soil moisture average
    soil_moisture_avg = response_data[4]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Extract evaporation sum
    evaporation_sum = response_data[5]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    new_weather_data_df = pd.DataFrame(
        {
            "date": dates,
            "evaporation_sum": evaporation_sum,
            "rainfall_sum": rainfall_sum,
            "soil_moisture_avg": soil_moisture_avg,
            "temp_avg": avg_temps,
            "temp_max": max_temps,
            "temp_min": min_temps,
        }
    )
    new_weather_data_df["date"] = pd.to_datetime(new_weather_data_df["date"])

    return new_weather_data_df


class GlobalResources(metaclass=SingletonMeta):
    def __init__(self):
        self.historical_weather_df = None
        self.temp_stress_models = {}
        self.drought_stress_model = None
        self._update_database()
        self._load_resources()

    def _update_database(self):
        try:
            weather_db = sqlite3.connect(c.HISTORICAL_WEATHER_DB_PATH)
            historical_weather_df = pd.read_sql("SELECT * FROM historical_weather_data", weather_db)
            historical_weather_df["date"] = pd.to_datetime(historical_weather_df["date"], format="mixed")

            # Find the latest date in the database
            latest_date = historical_weather_df["date"].max().strftime(c.METEOBLUE_DATE_FORMAT)

            # Calculate the date range (ends included) for the API request (fill with data until yesterday)
            start_date = (datetime.strptime(latest_date, c.METEOBLUE_DATE_FORMAT) + timedelta(days=1)).strftime(
                c.METEOBLUE_DATE_FORMAT
            )
            end_date = (datetime.now() - timedelta(days=1)).strftime(c.METEOBLUE_DATE_FORMAT)

            # Database is already up-to-date
            if datetime.strptime(start_date, c.METEOBLUE_DATE_FORMAT) > datetime.strptime(
                end_date, c.METEOBLUE_DATE_FORMAT
            ):
                weather_db.close()
                return

            new_weather_data_df = fetch_historical_weather_data(start_date, end_date)
            new_weather_data_df.to_sql("historical_weather_data", weather_db, if_exists="append", index=False)

            database_to_df = pd.read_sql("SELECT * FROM historical_weather_data", weather_db)
            database_to_df["date"] = pd.to_datetime(database_to_df["date"])  # Ensure consistent date format

            # Remove duplicates and write back
            database_to_df.sort_values("date").drop_duplicates(subset=["date"]).to_sql(
                "historical_weather_data", weather_db, if_exists="replace", index=False
            )

            weather_db.close()

        except Exception as e:
            print(f"Error updating weather database: {str(e)}")
            # Make sure to close the database connection in case of error
            if "weather_db" in locals():
                weather_db.close()

    def _load_resources(self):
        weather_db = sqlite3.connect(c.HISTORICAL_WEATHER_DB_PATH)

        self.historical_weather_df = pd.read_sql("SELECT * FROM historical_weather_data", weather_db)
        self.historical_weather_df["date"] = pd.to_datetime(self.historical_weather_df["date"], format="ISO8601")

        weather_db.close()

        # Load the PyTorch models
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        for crop in crops.CROPS:
            model = NN_temp_stress(c.TEMP_STRESS_INPUT_SIZE, c.TEMP_STRESS_OUTPUT_SIZE, device).to(device)
            model_state_dict = torch.load(c.TEMP_STRESS_MODEL_PATH_TEMPLATE.format(crop), map_location=device)
            model.load_state_dict(model_state_dict)
            model.eval()
            self.temp_stress_models[crop] = model

        d_model = NN_drought_stress(c.DROUGHT_STRESS_INPUT_SIZE, c.DROUGHT_STRESS_OUTPUT_SIZE, device).to(device)
        d_model_state_dict = torch.load(c.DROUGHT_STRESS_MODEL_PATH_TEMPLATE, map_location=device)
        d_model.load_state_dict(d_model_state_dict)
        d_model.eval()
        self.drought_stress_model = d_model

    def get_historical_weather_df(self):
        return self.historical_weather_df

    def get_temp_stress_model(self, crop: str):
        return self.temp_stress_models[crop]

    def get_drought_stress_model(self):
        return self.drought_stress_model
