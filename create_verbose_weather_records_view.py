from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

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
        # Drop the verbose_weather_records view if it exists
        connection.execute(text("DROP VIEW IF EXISTS verbose_weather_records"))
        connection.commit()
        print("✓ View 'verbose_weather_records' deleted if it existed.")

        # Create the verbose_weather_records view
        create_view_sql = """
        CREATE VIEW verbose_weather_records AS
        SELECT
            wr.*,
            wwc.description AS weather_description
        FROM
            weather_records wr
        JOIN
            wmo_weather_codes wwc ON wr.weather_code = wwc.code;
        """
        connection.execute(text(create_view_sql))
        connection.commit()
        print("✓ View 'verbose_weather_records' created successfully.")

        # Verify the view by selecting a few rows
        print("\nSample data from 'verbose_weather_records':")
        result = connection.execute(text("SELECT * FROM verbose_weather_records LIMIT 5"))
        
        # Fetch column names
        column_names = result.keys()
        print(column_names) # Print column names for verification
        
        for row in result:
            print(row)

except Exception as e:
    print(f"✗ Error: {e}")
