import httpx
import asyncio
import pandas as pd
from datetime import datetime
from fastapi import HTTPException
from enum import Enum

import config as c
from util.timed_cache import TimedCache, cached, CacheCategory


class MeasureLabel(Enum):
    TEMP_MAX = "TempSurface_DailyMax (C)"
    TEMP_MIN = "TempSurface_DailyMin (C)"
    TEMP_AVG = "TempAir_DailyAvg (C)"
    RAINFALL_SUM = "Precip_DailySum (mm)"
    EVAPORATION_SUM = "Referenceevapotranspiration_DailySum (mm)"
    SOIL_MOISTURE_AVG = "Soilmoisture_0to10cm_DailyAvg (vol%)"


async def retrieve_forecast_label(latitude: float, longitude: float, start_date: str, measure_label: MeasureLabel):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                c.FORECAST_API_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "startDate": start_date,
                    "supplier": c.FORECAST_SUPPLIER,
                    "measureLabel": measure_label,
                    "top": c.FORECAST_DAYS,
                    "format": "json",
                },
                headers={"accept": "*/*", "ApiKey": c.FORECAST_API_KEY},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))


@cached(TimedCache(), category=CacheCategory.WEATHER_FORECAST, ttl_seconds=3600)
async def retrieve_all_forecast_data(latitude: float, longitude: float, start_date: str):
    retrieve_tasks = []

    # Create tasks for each measure label
    for label in MeasureLabel:
        task = retrieve_forecast_label(latitude, longitude, start_date, label.value)
        retrieve_tasks.append(task)

    # Wait for all API calls to complete
    results = await asyncio.gather(*retrieve_tasks)

    forecast_by_date = {}

    for i, result in enumerate(results):
        measure_label = list(MeasureLabel)[i].name.lower()

        if result:
            for item in result:
                date = datetime.strptime(item["date"], "%Y/%m/%d %H:%M:%S")

                if date not in forecast_by_date:
                    forecast_by_date[date] = {"date": date}

                forecast_by_date[date][measure_label] = float(item["dailyValue"])

                if measure_label == "soil_moisture_avg":
                    forecast_by_date[date][measure_label] /= 100  # The retrieved data is in %

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(forecast_by_date.values()))

    return df
