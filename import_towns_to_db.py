import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
GEODATA_DATABASE = "geodata"
TABLE_NAME = "austrian_towns_new"

# Create SQLAlchemy engine for the geodata database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{GEODATA_DATABASE}")

print(f"Reading austria_towns.csv...")
try:
    # Read the CSV file
    df = pd.read_csv("austria_towns.csv")
    print(f"✓ Successfully read {len(df)} rows from austria_towns.csv")

    # Display sample data
    print("\nSample data:")
    print(df.head())

    # Add ran
    # k column
    df = df.sort_values("inhabitants", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))

    # Import to MySQL database
    print(f"\n✓ Importing data to {GEODATA_DATABASE}.{TABLE_NAME}...")
    df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)
    print(f"✓ Successfully imported {len(df)} rows to {GEODATA_DATABASE}.{TABLE_NAME}")

except FileNotFoundError:
    print("✗ Error: austria_towns.csv not found")
    exit()
except Exception as e:
    print(f"✗ Error: {e}")
    exit()
