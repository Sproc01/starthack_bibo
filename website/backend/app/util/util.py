import threading
import torch
import pandas as pd
import sqlite3

import crops
import config as c
from neural_networks.neural_network_risk import NN_risk


# Thread-safe singleton metaclass
class SingletonMeta(type):
    _instances = {}
    _lock = threading.RLock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class GlobalResources(metaclass=SingletonMeta):
    def __init__(self):
        self.historical_weather_df = None
        self.temp_stress_models = {}
        self.drought_stress_models = {}
        self._load_resources()

    def _load_resources(self):
        weather_db = sqlite3.connect(c.HISTORICAL_WHEATER_DB_PATH)

        self.historical_weather_df = pd.read_sql("SELECT * FROM historical_weather_data", weather_db)
        self.historical_weather_df["date"] = pd.to_datetime(self.historical_weather_df["date"])

        weather_db.close()

        # Load the PyTorch models
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        for crop in crops.CROPS:
            model = NN_risk(c.TEMP_STRESS_INPUT_SIZE, c.TEMP_STRESS_OUTPUT_SIZE, device).to(device)
            model_state_dict = torch.load(c.TEMP_STRESS_MODEL_PATH_TEMPLATE.format(crop), map_location=device)
            model.load_state_dict(model_state_dict)
            model.eval()
            self.temp_stress_models[crop] = model

            # TODO
            # model = torch.load(c.DROUGHT_STRESS_MODEL_PATH_TEMPLATE.format(crop), map_location=device)
            # model.to(device)
            # model.eval()
            # self.drought_stress_models[crop] = model

    def get_historical_weather_df(self):
        return self.historical_weather_df

    def get_temp_stress_model(self, crop: str):
        return self.temp_stress_models[crop]

    def get_drought_stress_model(self, crop: str):
        return self.drought_stress_models[crop]
