from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config as c
from retrieve_forecast import retrieve_all_forecast_data

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/forecast")
async def get_forecast():
    today = datetime.today().strftime("%Y-%m-%d")
    df = retrieve_all_forecast_data(c.SORRISO_LATITUDE, c.SORRISO_LONGITUDE)
