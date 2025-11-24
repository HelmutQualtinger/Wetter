from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# Import WMO weather codes
from WMO_weather_code import WMO_WEATHER_CODE_DE

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "OpenMeteo"

# Create SQLAlchemy engine for the OpenMeteo database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

print(f"Connecting to {MYSQL_DATABASE} database on beker.club...")

try:
    with engine.connect() as connection:
        # Drop the wmo_weather_codes table if it exists
        connection.execute(text("DROP TABLE IF EXISTS wmo_weather_codes"))
        connection.commit()
        print("✓ Table 'wmo_weather_codes' deleted if it existed.")

        # Create the wmo_weather_codes table
        create_table_sql = """
        CREATE TABLE wmo_weather_codes (
            code INT PRIMARY KEY,
            description VARCHAR(255)
        )
        """
        connection.execute(text(create_table_sql))
        connection.commit()
        print("✓ Table 'wmo_weather_codes' created successfully.")

        # Insert data from WMO_WEATHER_CODE_DE
        print("Inserting WMO weather codes...")
        for code, description in WMO_WEATHER_CODE_DE.items():
            insert_sql = text("INSERT INTO wmo_weather_codes (code, description) VALUES (:code, :description)")
            connection.execute(insert_sql, {"code": code, "description": description})
        connection.commit()
        print(f"✓ Successfully inserted {len(WMO_WEATHER_CODE_DE)} WMO weather codes.")

        # Verify insertion
        result = connection.execute(text("SELECT * FROM wmo_weather_codes LIMIT 5"))
        print("\nSample data from 'wmo_weather_codes':")
        for row in result:
            print(f"  Code: {row.code}, Description: {row.description}")

except Exception as e:
    print(f"✗ Error: {e}")
