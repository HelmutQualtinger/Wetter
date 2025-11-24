from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
GEODATA_DATABASE = "geodata"

# Create SQLAlchemy engine for the geodata database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{GEODATA_DATABASE}")

print(f"Connecting to {GEODATA_DATABASE} database on beker.club...")

try:
    with engine.connect() as connection:
        # Drop the all_towns table if it exists
        connection.execute(text("DROP TABLE IF EXISTS all_towns"))
        connection.commit()
        print("✓ Table 'all_towns' deleted if it existed.")

        # Create the all_towns table
        create_table_sql = """
        CREATE TABLE all_towns (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            town VARCHAR(255),
            state VARCHAR(255),
            longitude FLOAT,
            latitude FLOAT,
            inhabitants INT,
            country VARCHAR(50)
        )
        """
        connection.execute(text(create_table_sql))
        connection.commit()
        print("✓ Table 'all_towns' created successfully.")

        # Insert data from austrian_towns_new
        insert_austrian_sql = """
        INSERT INTO all_towns (town, state, longitude, latitude, inhabitants, country)
        SELECT 
            town,
            federal_state AS state,
            longitude,
            latitude,
            inhabitants,
            'AT' AS country
        FROM 
            austrian_towns_new;
        """
        connection.execute(text(insert_austrian_sql))
        connection.commit()
        print("✓ Data from 'austrian_towns_new' inserted into 'all_towns'.")

        # Insert data from swiss_towns
        insert_swiss_sql = """
                INSERT INTO all_towns (town, state, longitude, latitude, inhabitants, country)
                SELECT
                    town,
                    canton AS state,
                    longitude,
                    latitude,
                    inhabitants,
                    'CH' AS country
                FROM
                    swiss_towns_new;        """
        connection.execute(text(insert_swiss_sql))
        connection.commit()
        print("✓ Data from 'swiss_towns' inserted into 'all_towns'.")

        # Verify insertion and content
        print("\nSample data from 'all_towns' (first 10 rows):")
        result = connection.execute(text("SELECT * FROM all_towns LIMIT 10"))
        
        # Fetch column names
        column_names = result.keys()
        print(column_names)
        
        for row in result:
            print(row)
        
        print(f"\nTotal rows in 'all_towns': {connection.execute(text('SELECT COUNT(*) FROM all_towns')).scalar()}")

except Exception as e:
    print(f"✗ Error: {e}")
