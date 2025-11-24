import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pymysql # Use pymysql as the MySQL driver

load_dotenv()

# MySQL connection details from environment variables
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306) # Default MySQL port

def import_swiss_towns_to_db():
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('swiss_towns.csv')

    # Create a connection string for MySQL using pymysql
    db_connection_str = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/geodata'
    db_connection = create_engine(db_connection_str)

    # Write the data to a new table named 'swiss_towns_new' in the 'geodata' database
    # If the table already exists, it will be replaced
    df.to_sql('swiss_towns_new', db_connection, if_exists='replace', index=False)

    print("Swiss towns data imported successfully into 'swiss_towns_new' table in 'geodata' database.")

    # No need to explicitly close connection with sqlalchemy engine in this context
    # The engine manages the connections

if __name__ == "__main__":
    import_swiss_towns_to_db()