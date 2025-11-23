from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT")) # Convert port to integer

# Connect to MySQL server (without specifying a database)
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}")

print("Connecting to MySQL server...")

try:
    with engine.connect() as connection:
        # Create the database
        connection.execute(text("CREATE DATABASE IF NOT EXISTS OpenMeteo"))
        connection.commit()
        print("✓ Database 'OpenMeteo' created successfully on beker.club")

        # Show all databases
        result = connection.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result]
        print(f"\nAvailable databases:")
        for db in sorted(databases):
            print(f"  - {db}")

except Exception as e:
    print(f"✗ Error creating database: {e}")
