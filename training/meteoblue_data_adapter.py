from typing import List, Iterator, Tuple
from pathlib import Path
import json

def weekify(days: List[float]) -> float:
    return sum(days) / 7

def get_meteoblue_data_historical_forecast(json_file_path: str | Path, data_name: str = "temperature") -> Iterator[Tuple[List[float], List[float], List[float]]]:
    """
    Process meteoblue data from JSON:
    1. Use daily measurement data
    2. Create 2-year chunks of daily data (730 days)
    3. For each chunk, yield:
       - the 2-year historical data
       - the next 8 days (including today)
       - the next 12 weeks from today (85 days including today)

    Args:
        json_file_path: Path to the JSON file with meteoblue data
        data_name: Type of meteoblue data being processed (e.g., "temperature", "humidity")

    Yields:
        Tuple of (2-year chunk of daily measurements,
                 next 8 days' measurements including today,
                 next 12 weeks' measurements from today (including today))
    """
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Extract the measurement readings
    measurements = data[0]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Define constants
    DAYS_IN_TWO_YEARS = 730
    DAYS_IN_PREDICTION = 8  # Including today + 7 more days
    DAYS_IN_12_WEEKS = 85   # 12 weeks * 7 days + today

    # Yield 2-year chunks with the next 8 days and next 12 weeks
    for i in range(len(measurements) - DAYS_IN_TWO_YEARS - DAYS_IN_12_WEEKS + 1):
        two_year_data = measurements[i:i+DAYS_IN_TWO_YEARS]
        next_week_with_today = measurements[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_PREDICTION]
        next_12_weeks = measurements[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_12_WEEKS]
        yield (two_year_data, next_week_with_today, next_12_weeks)


if __name__ == "__main__":
    # Path to the JSON file
    json_path = Path(__file__).parent / "dataset" / "temp_max.json"

    # Get the first few examples to verify it works
    for i, (two_year_data, next_days, next_12_weeks) in enumerate(get_meteoblue_data_historical_forecast(json_path)):
        print(f"Example {i+1}:")
        print(f"Two-year data length: {len(two_year_data)} days")
        print(f"First day: {two_year_data[0]:.2f}")
        print(f"Last day: {two_year_data[-1]:.2f}")

        print(f"Next 8 days (including today):")
        for j, value in enumerate(next_days):
            if j == 0:
                print(f"  Today: {value:.2f}")
            else:
                print(f"  Day +{j}: {value:.2f}")

        print(f"Next 12 weeks (total {len(next_12_weeks)} days):")
        print(f"  First day: {next_12_weeks[0]:.2f}")
        print(f"  Last day: {next_12_weeks[-1]:.2f}")
        print(f"  Weekly averages:")
        for week in range(12):
            week_data = next_12_weeks[week*7:week*7+7]
            if len(week_data) == 7:  # Make sure we have a full week
                avg = weekify(week_data)
                print(f"    Week {week+1}: {avg:.2f}")
        print("-" * 50)

        # Just show a few examples
        if i >= 2:
            break

    # Calculate total number of data points available
    total_examples = sum(1 for _ in get_meteoblue_data_historical_forecast(json_path))
    print(f"Total number of 2-year chunks available: {total_examples}")
