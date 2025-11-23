import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "geodata"

# Read the weather data
csv_file = "austria_towns_current_weather.csv"
df = pd.read_csv(csv_file)

print(f"Loading weather data from {csv_file}...")
print(f"Records to save: {len(df)}")

# Create database connection
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

# Save to database
table_name = "austria_towns_current_weather"

try:
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"\n✓ Successfully saved {len(df)} records to MySQL")
    print(f"  Table: {table_name}")
    print(f"  Database: {MYSQL_DATABASE}")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
except Exception as e:
    print(f"\n✗ Error saving to database: {e}")
