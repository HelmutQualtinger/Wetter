import mysql.connector
import plotly.express as px
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection parameters
db_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': 'geodata'
}

# Connect to MySQL database
conn = mysql.connector.connect(**db_config)

# Query to get unique Austrian towns
query = """
SELECT DISTINCT town, latitude, longitude
FROM austrian_towns_new
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
""" # Changed column name from 'town' to 'town_name'

# Load data into a DataFrame
df = pd.read_sql_query(query, conn)
conn.close()

# Count towns per location (for choropleth intensity)
df['town_count'] = 1
town_counts = df.groupby(['latitude', 'longitude']).agg({
    'town': 'first',
    'town_count': 'count'
}).reset_index()

# Create the map
fig = px.scatter_geo(
    town_counts,
    lat='latitude',
    lon='longitude',
    size='town_count',
    hover_name='town',
    hover_data={'latitude': True, 'longitude': True, 'town_count': True},
    title='Austrian Towns Distribution',
    projection='natural earth',
    color='town_count',
    color_continuous_scale='Viridis'
)

# Focus on Austria
fig.update_geos(
    center=dict(lat=47.5, lon=13.5),
    projection_scale=20,
    visible=True,
    showcountries=True,
    countrycolor="DarkSlateGrey"
)

# Update layout
fig.update_layout(
    height=700,
    title_x=0.5,
    geo=dict(
        scope='europe',
        showland=True, # Show land areas
        landcolor='rgb(230, 230, 230)', # Light grey for land
    )
)

# Show the map
fig.show()

print(f"Total unique towns displayed: {len(df)}")
print(f"Towns with multiple locations: {len(town_counts[town_counts['town_count'] > 1])}")