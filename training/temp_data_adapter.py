from typing import List, Iterator, Tuple
from pathlib import Path
import json

def weekify(days: List[float]) -> float:
    return sum(days) / 7

def get_temperature_data_historical_forecast(json_file_path: str | Path) -> Iterator[Tuple[List[float], List[float], List[float]]]:
    """
    Process temperature data from JSON:
    1. Use daily temperature data
    2. Create 2-year chunks of daily data (730 days)
    3. For each chunk, yield:
       - the 2-year historical data
       - the next 8 days (including today)
       - the next 12 weeks from today (84 days)

    Args:
        json_file_path: Path to the JSON file with temperature data

    Yields:
        Tuple of (2-year chunk of daily temperatures, 
                 next 8 days' temperatures including today,
                 next 12 weeks' temperatures from today)
    """
    # Load the JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Extract the temperature readings
    temperatures = data[0]["codes"][0]["dataPerTimeInterval"][0]["data"][0]

    # Define constants
    DAYS_IN_TWO_YEARS = 730
    DAYS_IN_PREDICTION = 8  # Including today + 7 more days
    DAYS_IN_12_WEEKS = 84   # 12 weeks * 7 days

    # Yield 2-year chunks with the next 8 days and next 12 weeks
    for i in range(len(temperatures) - DAYS_IN_TWO_YEARS - DAYS_IN_12_WEEKS + 1):
        two_year_data = temperatures[i:i+DAYS_IN_TWO_YEARS]
        next_week_with_today = temperatures[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_PREDICTION]
        next_12_weeks = temperatures[i+DAYS_IN_TWO_YEARS:i+DAYS_IN_TWO_YEARS+DAYS_IN_12_WEEKS]
        yield (two_year_data, next_week_with_today, next_12_weeks)


if __name__ == "__main__":
    # Path to the JSON file
    json_path = r"c:\Users\alber\Desktop\starthack_bibo\training\max_temp.json"

    # Test the function
    data_generator = get_temperature_data_historical_forecast(json_path)

    # Get the first few examples to verify it works
    for i, (two_year_data, next_days, next_12_weeks) in enumerate(data_generator):
        print(f"Example {i+1}:")
        print(f"Two-year data length: {len(two_year_data)} days")
        print(f"First day temperature: {two_year_data[0]:.2f}°C")
        print(f"Last day temperature: {two_year_data[-1]:.2f}°C")
        
        print(f"Next 8 days' temperatures (including today):")
        for j, temp in enumerate(next_days):
            if j == 0:
                print(f"  Today: {temp:.2f}°C")
            else:
                print(f"  Day +{j}: {temp:.2f}°C")
        
        print(f"Next 12 weeks' temperatures (total {len(next_12_weeks)} days):")
        print(f"  First day: {next_12_weeks[0]:.2f}°C")
        print(f"  Last day: {next_12_weeks[-1]:.2f}°C")
        print(f"  Weekly averages:")
        for week in range(12):
            week_data = next_12_weeks[week*7:week*7+7]
            if len(week_data) == 7:  # Make sure we have a full week
                avg = weekify(week_data)
                print(f"    Week {week+1}: {avg:.2f}°C")
        print("-" * 50)

        # Just show a few examples
        if i >= 2:
            break

    # Calculate total number of data points available
    data_generator = get_temperature_data_historical_forecast(json_path)
    total_examples = sum(1 for _ in data_generator)
    print(f"Total number of 2-year chunks available: {total_examples}")
