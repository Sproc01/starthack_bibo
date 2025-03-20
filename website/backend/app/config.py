import os
from dotenv import load_dotenv

# Env
load_dotenv()
FORECAST_API_KEY = os.getenv("FORECAST_API_KEY")

# Forecast
FORECAST_API_URL = "https://services.cehub.syngenta-ais.com/api/Forecast/ShortRangeForecastDaily"
FORECAST_SUPPLIER = "Meteoblue"
FORECAST_DAYS = 8  # Today and a week after

# Position
SORRISO_LATITUDE = -12.5471531
SORRISO_LONGITUDE = -55.7319178

# Uvicorn
HOST = "0.0.0.0"
PORT = 8123
DEBUG_MODE = True

# Resources
HISTORICAL_WHEATER_DB_PATH = "./resources/stress_buster_historical_data.db"
TEMP_STRESS_MODEL_PATH = "./resources"
DROUGHT_STRESS_MODEL_PATH = "./resources"
