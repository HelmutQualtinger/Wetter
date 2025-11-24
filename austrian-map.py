import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- Configuration ---
# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
GEODATA_DATABASE = "geodata"

# GeoJSON file path
GEOJSON_PATH = "geo_data/austria_federal_states.geojson"
OUTPUT_HTML_PATH = "austrian-map.html"

# Mapping from full federal state names (from GeoJSON) to abbreviations (from DB)
state_abbreviations = {
    'Burgenland': 'B',
    'Kärnten': 'K',
    'Niederösterreich': 'NÖ',
    'Oberösterreich': 'OÖ',
    'Salzburg': 'S',
    'Steiermark': 'ST',
    'Tirol': 'T',
    'Vorarlberg': 'V',
    'Wien': 'W'
}

def create_austrian_map():
    # 1. Database connection
    try:
        engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{GEODATA_DATABASE}")
        print(f"Connecting to {GEODATA_DATABASE} database on {MYSQL_HOST}...")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    # 2. Fetch town data (for choropleth)
    try:
        with engine.connect() as connection:!!
            query = """
            SELECT state, COUNT(town) as town_count
            FROM all_towns
            WHERE country = 'AT'
            GROUP BY state
            """
            df_town_counts = pd.read_sql(text(query), connection)
        print("✓ Austrian town data for choropleth fetched successfully.")
        print(df_town_counts)
    except Exception as e:
        print(f"Error fetching choropleth town data: {e}")
        return

    # 2.1 Fetch individual town data (for scatter plot)
    try:
        with engine.connect() as connection:
            query_towns = """
            SELECT town, latitude, longitude, federal_state, inhabitants
            FROM austria_top100_towns
            ORDER BY inhabitants DESC
            """
            df_towns = pd.read_sql(text(query_towns), connection)
            df_towns['wikipedia_url'] = df_towns['town'].apply(lambda x: f"https://en.wikipedia.org/wiki/{x.replace(' ', '_')}")
        print("✓ Individual Austrian town data fetched successfully.")
    except Exception as e:
        print(f"Error fetching individual town data: {e}")
        return


    # 3. Load GeoJSON
    try:
        with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        print(f"✓ GeoJSON data loaded from {GEOJSON_PATH}.")
    except FileNotFoundError:
        print(f"Error: GeoJSON file not found at {GEOJSON_PATH}. Please ensure it exists.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode GeoJSON file at {GEOJSON_PATH}. Check file validity.")
        return

    # 4. Process GeoJSON to add abbreviations and prepare for plotting
    for feature in geojson_data['features']:
        full_state_name = feature['properties'].get('BL') # 'BL' is the federal state name
        if full_state_name and full_state_name in state_abbreviations:
            feature['properties']['state_abbr'] = state_abbreviations[full_state_name]
        else:
            # Handle cases where state name might not be found or mapped
            feature['properties']['state_abbr'] = None
            print(f"Warning: Could not map federal state '{full_state_name}' to an abbreviation.")

    # Remove features that couldn't be mapped (optional, but good for clean data)
    geojson_data['features'] = [f for f in geojson_data['features'] if f['properties']['state_abbr']]

    # 5. Create Plotly Choropleth Map
    fig = px.choropleth_mapbox(
        df_town_counts,
        geojson=geojson_data,
        locations="state",  # Column in df_town_counts that matches the GeoJSON featureidkey
        color="town_count",  # Data to color the map regions
        featureidkey="properties.state_abbr",  # Path to the ID in GeoJSON features
        color_continuous_scale="Viridis",
        mapbox_style="open-street-map",
        zoom=50,
        center={"lat": 47.5, "lon": 14.5},  # Approximate center of Austria
        opacity=0.5, # Opacity for the choropleth layer
        labels={'town_count': 'Number of Towns', 'state': 'Federal State'},
        hover_name="state",
        hover_data={"town_count": True, "state": False} # Show town count on hover, hide state abbr
    )

    fig.update_layout(
        title_text="Number of Towns per Federal State in Austria",
        margin={"r":0,"t":50,"l":0,"b":0}
    )

    # Add town markers
    fig.add_trace(go.Scattermap(
        lat=df_towns["latitude"],
        lon=df_towns["longitude"],
        mode="markers+text",
        marker=go.scattermap.Marker(
            size=10, # Fixed marker size
            color="red",
            opacity=0.7
        ),
        text=df_towns["town"], # Show only town name
        textposition="top center",
        textfont=dict(
            size=9,
            color="black"
        ),
        customdata=df_towns[['inhabitants', 'latitude', 'longitude', 'wikipedia_url']],
        hovertemplate="<b>%{text}</b><br>" +
                      "Inhabitants: %{customdata[0]:,}<br>" +
                      "Latitude: %{customdata[1]:.2f}<br>" +
                      "Longitude: %{customdata[2]:.2f}<extra></extra>",
        hoverinfo="text",
        name="Towns"

    ))

    fig.update_layout(map_style="open-street-map")

    # Define the JavaScript code to open Wikipedia page on click
    js_code = """
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var plotDiv = document.querySelector('.plotly-graph-div');
            if (plotDiv) {
                plotDiv.on('plotly_click', function(data) {
                    if (data.points.length > 0) {
                        var point = data.points[0];
                        var wikipediaUrl = point.customdata[3]; // URL is at index 3 in customdata
                        if (wikipediaUrl) {
                            window.open(wikipediaUrl, '_blank');
                        }
                    }
                });
            }
        });
    </script>
    """

    # Remove fig.show() as we are explicitly opening the modified HTML

    fig.show() # Commented out as per instruction

    # 6. Save the map as an HTML file with the injected JavaScript
    fig.write_html(OUTPUT_HTML_PATH, post_script=js_code, full_html=True)
    print(f"✓ Map saved to {OUTPUT_HTML_PATH} with click handler.")
    

if __name__ == "__main__":
    create_austrian_map() # open in browser
