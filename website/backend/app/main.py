import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


import config as c
from retrieve_forecast import retrieve_all_forecast_data

# TODO
app = FastAPI(title="Syngenta", description="Syngenta", version="1.0.0")

# TODO
# CORS configuration
origins = [
    "http://localhost:3000",  # For local development
    # Add production domains here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# API routes
@app.get("/api/forecast", tags=["Forecast"])
async def get_forecast():
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        lat = c.SORRISO_LATITUDE
        lon = c.SORRISO_LONGITUDE

        df = await retrieve_all_forecast_data(lat, lon, today)

        # Convert dataframe to dict and return as JSON
        forecast_data = df.to_dict(orient="records") if df is not None else []

        return {
            "timestamp": datetime.now().isoformat(),
            "coordinates": {"latitude": lat, "longitude": lon},
            "forecast": forecast_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve forecast data: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host=c.HOST, port=c.PORT, reload=c.DEBUG_MODE)
