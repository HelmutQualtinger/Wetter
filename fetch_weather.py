import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings for geodata
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
GEODATA_DATABASE = "geodata"
GEODATA_TABLE = "austrian_towns_new"

# Create SQLAlchemy engine for the geodata database
geodata_engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{GEODATA_DATABASE}")

print(f"Fetching towns from database {GEODATA_DATABASE}.{GEODATA_TABLE}...")

try:
    # Read towns data from the database
    df = pd.read_sql_table(GEODATA_TABLE, con=geodata_engine)
    
    # Optional: sort by population descending (as in generate_towns.py and original fetch_weather.py)
    df = df.sort_values("inhabitants", ascending=False).reset_index(drop=True)
    
    # Add rank column

    
    print(f"✓ Successfully fetched {len(df)} towns from the database.")
    
except Exception as e:
    print(f"✗ Error fetching towns from database: {e}")
    exit() # Exit if we can't get town data

# Open Meteo API endpoint for current weather
API_URL = "https://api.open-meteo.com/v1/forecast"

# Current weather parameters
CURRENT_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "is_day",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "weather_code",
    "cloud_cover",
    "pressure_msl",
    "surface_pressure"
]

# Prepare coordinates as comma-separated strings
latitudes = ",".join(df["latitude"].astype(str))
longitudes = ",".join(df["longitude"].astype(str))

# Make API request
params = {
    "latitude": latitudes,
    "longitude": longitudes,
    "current": ",".join(CURRENT_PARAMS),
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh"
}

print(f"Fetching current weather for {len(df)} towns...")
print(f"API URL: {API_URL}")

try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract current weather for each location
    # API returns a list where each item has location info + current weather
    weather_data = []
    # Open-Meteo returns a single dictionary if only one location, or a list of dictionaries for multiple locations
    if isinstance(data, dict) and 'latitude' in data: # Single location response
        # Extract current weather data
        current = data.get("current", {})
        # Add time and timezone info from the response
        current["time"] = data.get("current_units", {}).get("time", "")
        current["timezone"] = data.get("timezone", "")
        weather_data.append(current)
    elif isinstance(data, list): # Multiple locations response
        for location_data in data:
            current = location_data.get("current", {})
            current["time"] = location_data.get("current_units", {}).get("time", "")
            current["timezone"] = location_data.get("timezone", "")
            weather_data.append(current)
    else:
        print("✗ Unexpected API response format.")
        exit()


    # Create a dataframe from the weather data
    weather_df = pd.DataFrame(weather_data)

    # Combine with original dataframe
    result_df = pd.concat([df.reset_index(drop=True), weather_df.reset_index(drop=True)], axis=1)

    # Add timestamp columns
    now = datetime.now()
    result_df['recorded_at'] = now.isoformat()
    result_df['recorded_date'] = now.strftime('%Y-%m-%d')
    result_df['recorded_time'] = now.strftime('%H:%M:%S')

    # Display the results
    print(f"\n✓ Successfully fetched weather for {len(result_df)} towns")
    print(f"Timestamp: {now.isoformat()}")
    if len(data) > 0:
        if isinstance(data, dict):
            print(f"Timezone: {data.get('timezone', 'N/A')}")
        elif isinstance(data, list):
            print(f"Timezone: {data[0].get('timezone', 'N/A')}")

    # Show sample data
    print("\n" + "="*100)
    print("SAMPLE DATA (first 5 towns):")
    print("="*100)
    sample_cols = ["rank", "town", "federal_state", "temperature_2m", "relative_humidity_2m",
                   "apparent_temperature", "wind_speed_10m", "weather_code", "cloud_cover"]
    print(result_df[sample_cols].head())

    # Show all columns available
    print("\n" + "="*100)
    print("ALL AVAILABLE WEATHER COLUMNS:")
    print("="*100)
    weather_cols = [col for col in result_df.columns if col not in df.columns]
    print(weather_cols)

    # Save to CSV
    csv_filename = "austria_towns_current_weather.csv"
    result_df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"✓ Saved to {csv_filename}")

    # Save to OpenMeteo database
    OPENMETEO_DATABASE = "OpenMeteo" # This is the database for weather records
    openmeteo_engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{OPENMETEO_DATABASE}")

    table_name = "weather_records"
    result_df.to_sql(table_name, con=openmeteo_engine, if_exists='append', index=False)
    print(f"✓ Saved to MySQL database {OPENMETEO_DATABASE}.{table_name}")

    # Display full weather data for first town as example
    print("\n" + "="*100)
    print(f"DETAILED WEATHER FOR: {result_df.loc[0, 'town']}")
    print("="*100)
    print(f"Recorded at: {result_df.loc[0, 'recorded_at']}")
    for col in weather_cols:
        print(f"{col}: {result_df.loc[0, col]}")

except requests.exceptions.RequestException as e:
    print(f"✗ Error fetching data from Open-Meteo API: {e}")
except Exception as e:
    print(f"✗ Error processing data: {e}")