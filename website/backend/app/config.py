import os
from dotenv import load_dotenv

# Env
load_dotenv()
FORECAST_API_KEY = os.getenv("FORECAST_API_KEY")
HISTORICAL_API_KEY = os.getenv("HISTORICAL_API_KEY")

# Forecast
FORECAST_API_URL = "https://services.cehub.syngenta-ais.com/api/Forecast/ShortRangeForecastDaily"
FORECAST_SUPPLIER = "Meteoblue"
FORECAST_DAYS = 8  # Today and a week after

# Historical data
HISTORICAL_API_URL = "http://my.meteoblue.com/dataset/query"
METEOBLUE_DATE_FORMAT = "%Y-%m-%d"

# Position
SORRISO_LATITUDE = -12.5471531
SORRISO_LONGITUDE = -55.7319178
SORRISO_NAME = "Sorriso"

# Uvicorn
HOST = "0.0.0.0"
PORT = 8123
DEBUG_MODE = True

# Resources
HISTORICAL_WEATHER_DB_PATH = "./resources/stress_buster_historical_data.db"
TEMP_STRESS_MODEL_PATH_TEMPLATE = "./resources/temp_stress_models/temp_stress_model_{}.pth"
DROUGHT_STRESS_MODEL_PATH_TEMPLATE = "./resources/drought_stress_models/drought_stress_model_{}.pth"

# Neural networks
TEMP_STRESS_INPUT_SIZE = 1476  # Min and max temperatures for 2 years + 8 days
TEMP_STRESS_OUTPUT_SIZE = 36  # 3 temperature stress for 12 weeks

# Prediction
NUM_DAYS_TEMP_STRESS_PREDICTION = 2 * 365
NUM_DAYS_DROUGHT_STRESS_PREDICTION = 90
