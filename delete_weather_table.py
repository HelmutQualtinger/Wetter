from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "geodata"

# Connect to MySQL database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

print(f"Connecting to {MYSQL_DATABASE} database on beker.club...")

try:
    with engine.connect() as connection:
        # Drop the weather table
        connection.execute(text("DROP TABLE IF EXISTS austria_towns_current_weather"))
        connection.commit()
        print("✓ Table 'austria_towns_current_weather' deleted successfully from geodata database")

        # Show remaining tables
        result = connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"\nRemaining tables in '{MYSQL_DATABASE}':")
        for table in sorted(tables):
            print(f"  - {table}")

except Exception as e:
    print(f"✗ Error deleting table: {e}")
