import os
import json
import sqlite3
import glob

# Define the dataset directory
dataset_dir = "c:/Users/alber/Desktop/starthack_bibo/training/dataset"

# Function to extract time intervals (days) from a JSON file
def extract_time_intervals(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        try:
            # Access time intervals through the correct path
            return data[0]["timeIntervals"][0]
        except (KeyError, IndexError) as e:
            print(f"Error extracting time intervals from {json_file}: {e}")

# Function to extract data measurements from a JSON file
def extract_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    try:
        return data[0]["codes"][0]["dataPerTimeInterval"][0]["data"][0]
    except (KeyError, IndexError) as e:
        print(f"Error extracting data from {json_file}: {e}")
        return []

# Create SQLite database
def create_database(time_intervals, data_files):
    # Connect to SQLite database (it will be created if it doesn't exist)
    db_path = 'c:/Users/alber/Desktop/starthack_bibo/stress_buster_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table with a column for each data file
    columns = ["day TEXT PRIMARY KEY"]
    for data_file in data_files:
        data_name = os.path.basename(data_file).replace('.json', '')
        columns.append(f"{data_name} REAL")

    create_table_sql = f"CREATE TABLE IF NOT EXISTS bibo_data ({', '.join(columns)})"
    cursor.execute(create_table_sql)

    # Prepare all days data
    for i, day in enumerate(time_intervals):
        # Start with the day value
        row_values = [day]
        column_names = ["day"]

        # Add data from each file for this day
        for data_file in data_files:
            data_name = os.path.basename(data_file).replace('.json', '')
            column_names.append(data_name)

            data = extract_data(data_file)
            data_value = data[i] if i < len(data) else None
            row_values.append(data_value)

        # Create placeholders for the SQL query
        placeholders = ','.join(['?'] * len(row_values))

        # Insert the row
        insert_sql = f"INSERT OR REPLACE INTO bibo_data ({', '.join(column_names)}) VALUES ({placeholders})"
        cursor.execute(insert_sql, row_values)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Database created successfully at {os.path.abspath(db_path)}")

def main():
    # Find all JSON files in the dataset directory
    data_files = glob.glob(os.path.join(dataset_dir, "*.json"))

    if not data_files:
        print(f"No JSON files found in {dataset_dir}")
        return

    # Extract time intervals from the first JSON file (assuming they're the same across files)
    time_intervals = extract_time_intervals(data_files[0])

    if not time_intervals:
        print("No time intervals found in the JSON files")
        return

    print(f"Found {len(data_files)} data files and {len(time_intervals)} time intervals")

    # Create the database
    create_database(time_intervals, data_files)

if __name__ == "__main__":
    main()
