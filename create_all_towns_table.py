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
            CASE
                WHEN federal_state = 'Burgenland' THEN 'B'
                WHEN federal_state = 'Kärnten' THEN 'K'
                WHEN federal_state = 'Niederösterreich' THEN 'NÖ'
                WHEN federal_state = 'Oberösterreich' THEN 'OÖ'
                WHEN federal_state = 'Salzburg' THEN 'S'
                WHEN federal_state = 'Steiermark' THEN 'ST'
                WHEN federal_state = 'Tirol' THEN 'T'
                WHEN federal_state = 'Vorarlberg' THEN 'V'
                WHEN federal_state = 'Wien' THEN 'W'
                ELSE federal_state
            END AS state,
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

        # Insert data from german_towns_new
        insert_german_sql = """
        INSERT INTO all_towns (town, state, longitude, latitude, inhabitants, country)
        SELECT 
            town,
            CASE
                WHEN federal_state = 'Baden-Württemberg' THEN 'BW'
                WHEN federal_state = 'Bavaria' THEN 'BY'
                WHEN federal_state = 'Berlin' THEN 'BE'
                WHEN federal_state = 'Brandenburg' THEN 'BB'
                WHEN federal_state = 'Bremen' THEN 'HB'
                WHEN federal_state = 'Hamburg' THEN 'HH'
                WHEN federal_state = 'Hesse' THEN 'HE'
                WHEN federal_state = 'Mecklenburg-Vorpommern' THEN 'MV'
                WHEN federal_state = 'Lower Saxony' THEN 'NI'
                WHEN federal_state = 'North Rhine-Westphalia' THEN 'NW'
                WHEN federal_state = 'Rhineland-Palatinate' THEN 'RP'
                WHEN federal_state = 'Saarland' THEN 'SL'
                WHEN federal_state = 'Saxony' THEN 'SN'
                WHEN federal_state = 'Saxony-Anhalt' THEN 'ST'
                WHEN federal_state = 'Schleswig-Holstein' THEN 'SH'
                WHEN federal_state = 'Thuringia' THEN 'TH'
                ELSE federal_state
            END AS state,
            longitude,
            latitude,
            inhabitants,
            'DE' AS country
        FROM 
            german_towns_new;
        """
        connection.execute(text(insert_german_sql))
        connection.commit()
        print("✓ Data from 'german_towns_new' inserted into 'all_towns'.")

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
