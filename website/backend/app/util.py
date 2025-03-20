import threading
import torch
import pandas as pd
import sqlite3

import config as c


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
        self.temp_stress_model = None
        self.drought_stress_model = None
        self._load_resources()

    def _load_resources(self):
        weather_db = sqlite3.connect(c.HISTORICAL_WHEATER_DB_PATH)

        self.historical_weather_df = pd.read_sql("SELECT * FROM bibo_data", weather_db)
        self.historical_weather_df["date"] = pd.to_datetime(self.historical_weather_df["date"])

        weather_db.close()

        # Load the PyTorch models
        self.temp_stress_model = torch.load(c.TEMP_STRESS_MODEL_PATH)
        self.temp_stress_model.eval()

        self.drought_stress_model = torch.load(c.DROUGHT_STRESS_MODEL_PATH)
        self.drought_stress_model.eval()

    def get_historical_weather_df(self):
        return self.historical_weather_df

    def get_temp_stress_model(self):
        return self.temp_stress_model

    def get_drought_stress_model(self):
        return self.drought_stress_model
