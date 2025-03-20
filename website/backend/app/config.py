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
