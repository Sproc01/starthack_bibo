from typing import List, Iterator, Tuple
from pathlib import Path
import sqlite3
import numpy as np
from risk_calculator import riskCalculator, droughtRiskCalculator

def get_meteoblue_data_historical_forecast_from_sqlite(
    db_path: str | Path,
    column_names: List[str] | str,
) -> Iterator[Tuple[List[List[float]] | List[float], List[List[float]] | List[float], List[List[float]] | List[float]]]:
    """
    Process meteoblue data from SQLite database:
    1. Use daily measurement data from the specified columns
    2. Create 2-year chunks of daily data (730 days)
    3. For each chunk, yield:
       - the 2-year historical data for each column
       - the next 8 days (including today) for each column
       - the next 12 weeks from today (85 days including today) for each column

    Args:
        db_path: Path to the SQLite database file
        column_names: List of column names or a single column name to retrieve data from

    Yields:
        If single column requested:
            Tuple of (2-year chunk of daily measurements,
                     next 8 days' measurements including today,
                     next 12 weeks' measurements from today (including today))
        If multiple columns requested:
            Tuple of (list of 2-year chunks for each column,
                     list of next 8 days for each column,
                     list of next 12 weeks for each column)
    """
    # Handle single column case for backward compatibility
    single_column = isinstance(column_names, str)
    if single_column:
        column_names = [column_names]

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Define constants
    DAYS_IN_TWO_YEARS = 730
    DAYS_IN_PREDICTION = 8  # Including today + 7 more days
    DAYS_IN_12_WEEKS = 85   # 12 weeks * 7 days + today

    # Query to get all measurements for the specified columns
    column_str = ", ".join(column_names)
    query = f"""
    SELECT {column_str}
    FROM bibo_data
    """

    cursor.execute(query)
    all_measurements = cursor.fetchall()

    # Transpose data structure to group by column
    column_measurements = []
    for col_idx in range(len(column_names)):
        column_measurements.append([row[col_idx] for row in all_measurements])

    # Yield 2-year chunks with the next 8 days and next 12 weeks for all columns
    for i in range(len(column_measurements[0]) - DAYS_IN_TWO_YEARS - DAYS_IN_12_WEEKS + 1):
        two_year_data = []
        next_week_with_today = []
        next_12_weeks = []

        for col_measurements in column_measurements:
            two_year_data.append(col_measurements[i:i+DAYS_IN_TWO_YEARS])
            next_week_with_today.append(col_measurements[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_PREDICTION])
            next_12_weeks.append(col_measurements[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_12_WEEKS])

        # If only one column was requested, return flat lists for backward compatibility
        if single_column:
            yield (two_year_data[0], next_week_with_today[0], next_12_weeks[0])
        else:
            yield (two_year_data, next_week_with_today, next_12_weeks)

    conn.close()


def get_temperature_data_from_sqlite(
    db_path: str | Path,
) -> Iterator[Tuple[List[float], List[float], List[float], List[float], List[float], List[float]]]:
    """
    Process meteoblue temperature data from SQLite database:
    Retrieves both temp_min and temp_max for historical and forecast data

    Args:
        db_path: Path to the SQLite database file

    Yields:
        Tuple of (2-year chunk of temp_max, 2-year chunk of temp_min,
                 next 8 days' temp_max, next 8 days' temp_min,
                 next 12 weeks' temp_max, next 12 weeks' temp_min)
    """
    # Use the generic function to get both temperature columns at once
    for two_year_data, next_week_data, next_12_weeks_data in get_meteoblue_data_historical_forecast_from_sqlite(
        db_path, ["temp_max", "temp_min"]
    ):
        # Extract data for temp_max (index 0) and temp_min (index 1)
        two_year_tmax = two_year_data[0]
        two_year_tmin = two_year_data[1]
        next_week_tmax = next_week_data[0]
        next_week_tmin = next_week_data[1]
        next_12_weeks_tmax = next_12_weeks_data[0]
        next_12_weeks_tmin = next_12_weeks_data[1]

        yield (
            two_year_tmax, two_year_tmin,
            next_week_tmax, next_week_tmin,
            next_12_weeks_tmax, next_12_weeks_tmin
        )


def get_meteobluedata_with_risk(
    db_path: str | Path,
    crop_type: str,
    column_name: str
) -> Iterator[Tuple[List[float], List[float], Tuple[float, float, float]]]:
    """
    Calculates stress risk for the forecasted 12-week period using temperature data

    Args:
        db_path: Path to the SQLite database file
        crop_type: Type of crop for risk calculation
        column_name: Column to retrieve data from

    Yields:
        Tuple of (2-year chunk of daily measurements,
                 next 8 days' measurements including today,
                 risk values (heat_risk, frost_risk, night_risk) for the 12-week period)
    """
    # Get temperature datasets for risk calculation
    if column_name in ["temp_max", "temp_min"]:
        for (two_year_tmax, two_year_tmin,
             next_week_tmax, next_week_tmin,
             next_12_weeks_tmax, next_12_weeks_tmin) in get_temperature_data_from_sqlite(db_path):

            # Calculate stress risk using both temp_max and temp_min for the 12-week forecast period only
            heat_risk, frost_risk, night_risk = riskCalculator(next_12_weeks_tmax, next_12_weeks_tmin, crop_type)
            risk_values = (heat_risk, frost_risk, night_risk)

            # Return the column that was requested in the function call without next_12_weeks
            if column_name == "temp_min":
                yield (two_year_tmin, next_week_tmin, risk_values)
            else:
                yield (two_year_tmax, next_week_tmax, risk_values)
    else:
        print("Non-temperature columns are not supported for risk calculation")
        # For non-temperature columns, use the original implementation
        for two_year_data, next_week_with_today, next_12_weeks in get_meteoblue_data_historical_forecast_from_sqlite(
            db_path, column_name
        ):
            # No risk calculation for non-temperature data
            risk_values = (0.0, 0.0, 0.0)

            # Yield data without next_12_weeks
            yield (two_year_data, next_week_with_today, risk_values)


def get_meteobluedata_with_risk_numpy(
    db_path: str | Path,
    crop_type: str
) -> Iterator[np.ndarray]:
    """
    Retrieves temperature data and risk values organized in a 3D numpy array:
    - Dimension 1: [historical_data, forecast_data, risk_values]
    - Dimension 2: Time points or samples
    - Dimension 3: For historical and forecast data: [temp_min, temp_max]

    Args:
        db_path: Path to the SQLite database file
        crop_type: Type of crop for risk calculation

    Yields:
        3D numpy array with the organized temperature and risk data
    """
    # Get all temperature data
    for (two_year_tmax, two_year_tmin,
         next_week_tmax, next_week_tmin,
         next_12_weeks_tmax, next_12_weeks_tmin) in get_temperature_data_from_sqlite(db_path):

        # Calculate risk values
        heat_risk, frost_risk, night_risk = riskCalculator(next_12_weeks_tmax, next_12_weeks_tmin, crop_type)

        # Stack min and max temperatures for historical data
        historical_data = np.column_stack((two_year_tmin, two_year_tmax))  # Shape: (730, 2)

        # Stack min and max temperatures for forecast data
        forecast_data = np.column_stack((next_week_tmin, next_week_tmax))  # Shape: (8, 2)

        # Create risk values array (no third dimension)
        risk_data = np.array([heat_risk, frost_risk, night_risk])  # Shape: (3,)

        yield historical_data, forecast_data, risk_data

def get_last30_days_sum(db_path: str | Path) -> tuple[List[float], List[float], List[float], List[float]]:
    """
    Recupera e somma i valori di evaporation_sum, rainfall_sum, soil_moisture_avg e temp_avg
    per gli ultimi 30 giorni dalla tabella bibo_data del database SQLite.

    Args:
        db_path: Path al file del database SQLite.
    
    Returns:
        Una tupla contenente le somme nell'ordine:
        (evaporation_sum, rainfall_sum, soil_moisture_avg, temp_avg)
    """
    # Connessione al database SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Seleziona gli ultimi 30 record ordinati in base al rowid (si assume che rowid più alto corrisponda a date recenti)
    query = """
    SELECT evaporation_sum, rainfall_sum, soil_moisture_avg, temp_avg
    FROM bibo_data
    ORDER BY rowid ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # Inizializza le somme
    evaporation_total = 0.0
    rainfall_total = 0.0
    soil_moisture_total = 0.0
    temp_total = 0.0

    sum_evaporation_past = []
    sum_rainfall_past = []
    sum_soil_moisture_past = []
    sum_temp_past = []
    forecast = []
    sum_evaporation_present = []
    sum_rainfall_present = []
    sum_soil_moisture_present = []
    sum_temp_present = []

    val = 0
    # Somma ogni colonna (gestendo eventuali valori None)
    for i in range(23, len(rows)-84, 7):
        prediction = []
        for j in range(0, 23):
            row = rows[i-j]
            evaporation_total += row[0] if row[0] is not None else 0.0
            rainfall_total += row[1] if row[1] is not None else 0.0
            soil_moisture_total += row[2] if row[2] is not None else 0.0
            temp_total += row[3] if row[3] is not None else 0.0
        sum_evaporation_past.append(evaporation_total)
        sum_rainfall_past.append(rainfall_total)
        sum_soil_moisture_past.append(soil_moisture_total)
        sum_temp_past.append(temp_total)
        evaporation_total = 0.0
        rainfall_total = 0.0
        soil_moisture_total = 0.0
        temp_total = 0.0
        for j in range(0, 7):
            row = rows[i+j]
            evaporation_total += row[0] if row[0] is not None else 0.0
            rainfall_total += row[1] if row[1] is not None else 0.0
            soil_moisture_total += row[2] if row[2] is not None else 0.0
            temp_total += row[3] if row[3] is not None else 0.0
        sum_evaporation_present.append(evaporation_total)
        sum_rainfall_present.append(rainfall_total)
        sum_soil_moisture_present.append(soil_moisture_total)
        sum_temp_present.append(temp_total)

        for j in range(7, 85):
            row = rows[j+i]
            evaporation_total += row[0] if row[0] is not None else 0.0
            rainfall_total += row[1] if row[1] is not None else 0.0
            soil_moisture_total += row[2] if row[2] is not None else 0.0
            temp_total += row[3] if row[3] is not None else 0.0
            risk = droughtRiskCalculator(evaporation_total, rainfall_total, soil_moisture_total, temp_total)
            if risk > 1:
                val += 0
            elif risk == 1:
                val += 0.5
            else:
                val += 1
            if j % 7 == 0:
                prediction.append(val/7)
                val = 0
        forecast.append(prediction)
        prediction = []


    return sum_evaporation_past, sum_rainfall_past, sum_soil_moisture_past, sum_temp_past, sum_evaporation_present, sum_rainfall_present, sum_soil_moisture_present, sum_temp_present, forecast


if __name__ == "__main__":
    db_path = "stress_buster_data.db"
    # Get the last 30 days sum
    res = get_last30_days_sum(db_path)
    print(res[0][0])
    print(res[1][0])
    print(res[2][0])
    print(res[3][0])
    print(res[4][0])

    #try:
        # Get the first few examples to verify it works
    #     for i, (two_year_data, next_days, risk_values) in enumerate(
    #         get_meteobluedata_with_risk(
    #             db_path,
    #             "Corn",
    #             "temp_max"
    #         )
    #     ):
    #         print(f"Example {i+1}:")
    #         print(f"Two-year data length: {len(two_year_data)} days")
    #         print(f"First day: {two_year_data[0]:.2f}")
    #         print(f"Last day: {two_year_data[-1]:.2f}")

    #         print(f"Next 8 days (including today):")
    #         for j, value in enumerate(next_days):
    #             if j == 0:
    #                 print(f"  Today: {value:.2f}")
    #             else:
    #                 print(f"  Day +{j}: {value:.2f}")

    #         print(f"Risk values: Heat risk: {risk_values[0]:.2f}, Frost risk: {risk_values[1]:.2f}, Night risk: {risk_values[2]:.2f}")

    #         # Just show one example
    #         if i >= 0:
    #             break

    #     # Calculate total number of data points available
    #     total_examples = sum(1 for _ in get_meteobluedata_with_risk(
    #         db_path,
    #         "Corn",
    #         "temp_max"
    #     ))
    #     print(f"Total number of 2-year chunks available from SQLite: {total_examples}")

    #     # Test the numpy version
    #     # TODO not completely working
    #     print("Testing numpy-based temperature data retrieval:")
    #     for i, data_array in enumerate(get_meteobluedata_with_risk_numpy(db_path, "Corn")):
    #         historical_data = data_array[0]  # Shape: (730, 2)
    #         forecast_data = data_array[1]    # Shape: (8, 2)
    #         risk_values = data_array[2]      # Shape: (3,)

    #         print(f"Example {i+1}:")
    #         print(f"Historical data shape: {historical_data.shape}")
    #         print(f"First day min/max: {historical_data[0][0]:.2f}/{historical_data[0][1]:.2f}")
    #         print(f"Last day min/max: {historical_data[-1][0]:.2f}/{historical_data[-1][1]::.2f}")

    #         print(f"Forecast data shape: {forecast_data.shape}")
    #         print(f"Today min/max: {forecast_data[0][0]:.2f}/{forecast_data[0][1]:.2f}")

    #         print(f"Risk values: {risk_values}")
    #         print(f"Heat risk: {risk_values[0]:.2f}, Frost risk: {risk_values[1]:.2f}, Night risk: {risk_values[2]:.2f}")

    #         # Just show one example
    #         if i >= 0:
    #             break

    #     total_examples = sum(1 for _ in get_meteobluedata_with_risk_numpy(db_path, "Corn"))
    #     print(f"Total number of 3D arrays available: {total_examples}")

    # except Exception as e:
    #     print(f"Error testing function: {e}")

