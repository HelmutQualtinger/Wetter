import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine

# Austrian towns data
austria_towns_data = [
    {"town": "Wien", "federal_state": "Wien", "longitude": 16.37208, "latitude": 48.20817, "inhabitants": 2028289},
    {"town": "Graz", "federal_state": "Steiermark", "longitude": 15.43950, "latitude": 47.07071, "inhabitants": 305314},
    {"town": "Linz", "federal_state": "Oberösterreich", "longitude": 14.28611, "latitude": 48.30694, "inhabitants": 213557},
    {"town": "Salzburg", "federal_state": "Salzburg", "longitude": 13.05501, "latitude": 47.80949, "inhabitants": 157659},
    {"town": "Innsbruck", "federal_state": "Tirol", "longitude": 11.40410, "latitude": 47.26921, "inhabitants": 132499},
    {"town": "Klagenfurt am Wörthersee", "federal_state": "Kärnten", "longitude": 14.30777, "latitude": 46.62618, "inhabitants": 105256},
    {"town": "Villach", "federal_state": "Kärnten", "longitude": 13.85079, "latitude": 46.61030, "inhabitants": 65749},
    {"town": "Wels", "federal_state": "Oberösterreich", "longitude": 14.03224, "latitude": 48.16582, "inhabitants": 65482},
    {"town": "Sankt Pölten", "federal_state": "Niederösterreich", "longitude": 15.64262, "latitude": 48.20357, "inhabitants": 59767},
    {"town": "Dornbirn", "federal_state": "Vorarlberg", "longitude": 9.74609, "latitude": 47.41305, "inhabitants": 52108},
    {"town": "Wiener Neustadt", "federal_state": "Niederösterreich", "longitude": 16.23617, "latitude": 47.81364, "inhabitants": 49156},
    {"town": "Steyr", "federal_state": "Oberösterreich", "longitude": 14.41900, "latitude": 48.03869, "inhabitants": 38036},
    {"town": "Feldkirch", "federal_state": "Vorarlberg", "longitude": 9.60331, "latitude": 47.24037, "inhabitants": 36708},
    {"town": "Bregenz", "federal_state": "Vorarlberg", "longitude": 9.74800, "latitude": 47.50500, "inhabitants": 29476},
    {"town": "Leonding", "federal_state": "Oberösterreich", "longitude": 14.25280, "latitude": 48.28095, "inhabitants": 29244},
    {"town": "Klosterneuburg", "federal_state": "Niederösterreich", "longitude": 16.33115, "latitude": 48.30095, "inhabitants": 28152},
    {"town": "Baden bei Wien", "federal_state": "Niederösterreich", "longitude": 16.23056, "latitude": 47.99972, "inhabitants": 25931},
    {"town": "Wolfsberg", "federal_state": "Kärnten", "longitude": 14.84944, "latitude": 46.84056, "inhabitants": 24961},
    {"town": "Krems an der Donau", "federal_state": "Niederösterreich", "longitude": 15.61667, "latitude": 48.41667, "inhabitants": 25473},
    {"town": "Traun", "federal_state": "Oberösterreich", "longitude": 14.23384, "latitude": 48.22180, "inhabitants": 25345},
    {"town": "Amstetten", "federal_state": "Niederösterreich", "longitude": 14.87250, "latitude": 48.12637, "inhabitants": 24008},
    {"town": "Lustenau", "federal_state": "Vorarlberg", "longitude": 9.65703, "latitude": 47.43012, "inhabitants": 24603},
    {"town": "Leoben", "federal_state": "Steiermark", "longitude": 15.09560, "latitude": 47.37987, "inhabitants": 24561},
    {"town": "Kapfenberg", "federal_state": "Steiermark", "longitude": 15.29034, "latitude": 47.44476, "inhabitants": 21907},
    {"town": "Hallein", "federal_state": "Salzburg", "longitude": 13.09972, "latitude": 47.68333, "inhabitants": 21654},
    {"town": "Schwechat", "federal_state": "Niederösterreich", "longitude": 16.46972, "latitude": 48.12639, "inhabitants": 21243},
    {"town": "Mödling", "federal_state": "Niederösterreich", "longitude": 16.29228, "latitude": 48.08643, "inhabitants": 20662},
    {"town": "Kufstein", "federal_state": "Tirol", "longitude": 12.17000, "latitude": 47.58472, "inhabitants": 20212},
    {"town": "Traiskirchen", "federal_state": "Niederösterreich", "longitude": 16.26972, "latitude": 48.01139, "inhabitants": 18925},
    {"town": "Ansfelden", "federal_state": "Oberösterreich", "longitude": 14.25833, "latitude": 48.21667, "inhabitants": 18271},
    {"town": "Braunau am Inn", "federal_state": "Oberösterreich", "longitude": 13.04611, "latitude": 48.25556, "inhabitants": 17604},
    {"town": "Stockerau", "federal_state": "Niederösterreich", "longitude": 16.21583, "latitude": 48.38556, "inhabitants": 17210},
    {"town": "Saalfelden am Steinernen Meer", "federal_state": "Salzburg", "longitude": 12.69889, "latitude": 47.42750, "inhabitants": 17299},
    {"town": "Tulln an der Donau", "federal_state": "Niederösterreich", "longitude": 16.06472, "latitude": 48.33139, "inhabitants": 16951},
    {"town": "Hohenems", "federal_state": "Vorarlberg", "longitude": 9.68472, "latitude": 47.36556, "inhabitants": 17432},
    {"town": "Telfs", "federal_state": "Tirol", "longitude": 11.07222, "latitude": 47.30833, "inhabitants": 16439},
    {"town": "Eisenstadt", "federal_state": "Burgenland", "longitude": 16.52667, "latitude": 47.84639, "inhabitants": 16118},
    {"town": "Bruck an der Mur", "federal_state": "Steiermark", "longitude": 15.27583, "latitude": 47.41667, "inhabitants": 15735},
    {"town": "Spittal an der Drau", "federal_state": "Kärnten", "longitude": 13.49889, "latitude": 46.79917, "inhabitants": 15341},
    {"town": "Bludenz", "federal_state": "Vorarlberg", "longitude": 9.82472, "latitude": 47.15750, "inhabitants": 15102},
    {"town": "Perchtoldsdorf", "federal_state": "Niederösterreich", "longitude": 16.27000, "latitude": 48.11056, "inhabitants": 14960},
    {"town": "Marchtrenk", "federal_state": "Oberösterreich", "longitude": 14.11111, "latitude": 48.19083, "inhabitants": 14815},
    {"town": "Schwaz", "federal_state": "Tirol", "longitude": 11.70639, "latitude": 47.34639, "inhabitants": 14480},
    {"town": "Wörgl", "federal_state": "Tirol", "longitude": 12.06528, "latitude": 47.48556, "inhabitants": 14412},
    {"town": "Hall in Tirol", "federal_state": "Tirol", "longitude": 11.52028, "latitude": 47.27639, "inhabitants": 14698},
    {"town": "Ternitz", "federal_state": "Niederösterreich", "longitude": 16.04167, "latitude": 47.71806, "inhabitants": 14697},
    {"town": "Feldkirchen in Kärnten", "federal_state": "Kärnten", "longitude": 14.10361, "latitude": 46.72667, "inhabitants": 14528},
    {"town": "Bad Ischl", "federal_state": "Oberösterreich", "longitude": 13.62111, "latitude": 47.71139, "inhabitants": 14107},
    {"town": "Hard", "federal_state": "Vorarlberg", "longitude": 9.70000, "latitude": 47.48333, "inhabitants": 13639},
    {"town": "Feldbach", "federal_state": "Steiermark", "longitude": 15.88333, "latitude": 46.95000, "inhabitants": 13495},
    {"town": "Gmunden", "federal_state": "Oberösterreich", "longitude": 13.79944, "latitude": 47.91861, "inhabitants": 13231},
    {"town": "Leibnitz", "federal_state": "Steiermark", "longitude": 15.53333, "latitude": 46.78333, "inhabitants": 13517},
    {"town": "Vöcklabruck", "federal_state": "Oberösterreich", "longitude": 13.64861, "latitude": 48.00000, "inhabitants": 12989},
    {"town": "Neunkirchen", "federal_state": "Niederösterreich", "longitude": 15.96667, "latitude": 47.71667, "inhabitants": 12940},
    {"town": "Ried im Innkreis", "federal_state": "Oberösterreich", "longitude": 13.48833, "latitude": 48.21139, "inhabitants": 12766},
    {"town": "Hollabrunn", "federal_state": "Niederösterreich", "longitude": 16.08056, "latitude": 48.55528, "inhabitants": 12514},
    {"town": "Bad Vöslau", "federal_state": "Niederösterreich", "longitude": 16.21667, "latitude": 47.96667, "inhabitants": 12478},
    {"town": "Götzis", "federal_state": "Vorarlberg", "longitude": 9.63750, "latitude": 47.32806, "inhabitants": 12405},
    {"town": "Brunn am Gebirge", "federal_state": "Niederösterreich", "longitude": 16.28333, "latitude": 48.08333, "inhabitants": 12310},
    {"town": "Gänserndorf", "federal_state": "Niederösterreich", "longitude": 16.71667, "latitude": 48.33333, "inhabitants": 12285},
    {"town": "Enns", "federal_state": "Oberösterreich", "longitude": 14.47972, "latitude": 48.21306, "inhabitants": 12184},
    {"town": "Rankweil", "federal_state": "Vorarlberg", "longitude": 9.63917, "latitude": 47.27278, "inhabitants": 12157},
    {"town": "Groß-Enzersdorf", "federal_state": "Niederösterreich", "longitude": 16.58333, "latitude": 48.20000, "inhabitants": 12088},
    {"town": "Mistelbach", "federal_state": "Niederösterreich", "longitude": 16.56667, "latitude": 48.56667, "inhabitants": 12044},
    {"town": "Ebreichsdorf", "federal_state": "Niederösterreich", "longitude": 16.40000, "latitude": 47.95000, "inhabitants": 12003},
    {"town": "Lienz", "federal_state": "Tirol", "longitude": 12.76250, "latitude": 46.83167, "inhabitants": 12107},
    {"town": "Weiz", "federal_state": "Steiermark", "longitude": 15.61667, "latitude": 47.21667, "inhabitants": 12116},
    {"town": "Seekirchen am Wallersee", "federal_state": "Salzburg", "longitude": 13.13333, "latitude": 47.91667, "inhabitants": 11708},
    {"town": "Deutschlandsberg", "federal_state": "Steiermark", "longitude": 15.21667, "latitude": 46.81667, "inhabitants": 11757},
    {"town": "Sankt Johann im Pongau", "federal_state": "Salzburg", "longitude": 13.27972, "latitude": 47.34972, "inhabitants": 11643},
    {"town": "Gleisdorf", "federal_state": "Steiermark", "longitude": 15.70000, "latitude": 47.10000, "inhabitants": 11533},
    {"town": "Imst", "federal_state": "Tirol", "longitude": 10.73806, "latitude": 47.25139, "inhabitants": 11183},
    {"town": "Trofaiach", "federal_state": "Steiermark", "longitude": 15.01667, "latitude": 47.43333, "inhabitants": 11030},
    {"town": "Waidhofen an der Ybbs", "federal_state": "Niederösterreich", "longitude": 14.78333, "latitude": 47.98333, "inhabitants": 11062},
    {"town": "Bischofshofen", "federal_state": "Salzburg", "longitude": 13.41667, "latitude": 47.41667, "inhabitants": 10743},
    {"town": "Zwettl", "federal_state": "Niederösterreich", "longitude": 15.16667, "latitude": 48.60000, "inhabitants": 10771},
    {"town": "Lauterach", "federal_state": "Vorarlberg", "longitude": 9.72778, "latitude": 47.45750, "inhabitants": 10568},
    {"town": "Fürstenfeld", "federal_state": "Steiermark", "longitude": 16.08333, "latitude": 47.05000, "inhabitants": 10391},
    {"town": "Zell am See", "federal_state": "Salzburg", "longitude": 12.79639, "latitude": 47.32389, "inhabitants": 10227},
    {"town": "Altmünster", "federal_state": "Oberösterreich", "longitude": 13.75000, "latitude": 47.88333, "inhabitants": 9998},
    {"town": "Purkersdorf", "federal_state": "Niederösterreich", "longitude": 16.18333, "latitude": 48.20000, "inhabitants": 9970},
    {"town": "Sierning", "federal_state": "Oberösterreich", "longitude": 14.26250, "latitude": 48.00333, "inhabitants": 9867},
    {"town": "Sankt Johann in Tirol", "federal_state": "Tirol", "longitude": 12.43750, "latitude": 47.51667, "inhabitants": 9891},
    {"town": "Köflach", "federal_state": "Steiermark", "longitude": 15.10000, "latitude": 47.01667, "inhabitants": 9489},
    {"town": "Völkermarkt", "federal_state": "Kärnten", "longitude": 14.63667, "latitude": 46.59667, "inhabitants": 10902},
    {"town": "Knittelfeld", "federal_state": "Steiermark", "longitude": 14.81667, "latitude": 47.21667, "inhabitants": 12570},
    {"town": "Voitsberg", "federal_state": "Steiermark", "longitude": 15.15000, "latitude": 47.04167, "inhabitants": 9547},
    {"town": "Judenburg", "federal_state": "Steiermark", "longitude": 14.66667, "latitude": 47.16667, "inhabitants": 9607},
    {"town": "Laakirchen", "federal_state": "Oberösterreich", "longitude": 13.81667, "latitude": 47.98333, "inhabitants": 9766},
]

# Create DataFrame
df = pd.DataFrame(austria_towns_data)
df = df.sort_values("inhabitants", ascending=False).reset_index(drop=True)
df.insert(0, "rank", range(1, len(df) + 1))

# Open Meteo API endpoint
API_URL = "https://api.open-meteo.com/v1/forecast"

# Current weather parameters
CURRENT_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "is_day",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "weather_code",
    "cloud_cover",
    "pressure_msl",
    "surface_pressure"
]

# Prepare coordinates
latitudes = ",".join(df["latitude"].astype(str))
longitudes = ",".join(df["longitude"].astype(str))

# Fetch weather
params = {
    "latitude": latitudes,
    "longitude": longitudes,
    "current": ",".join(CURRENT_PARAMS),
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh"
}

print("Fetching current weather from Open Meteo...")
print(f"Timestamp: {datetime.now().isoformat()}")

try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract weather data
    weather_data = []
    for location_data in data:
        current = location_data.get("current", {})
        current["timezone"] = location_data.get("timezone", "")
        weather_data.append(current)

    # Create weather dataframe
    weather_df = pd.DataFrame(weather_data)

    # Combine with town data
    result_df = pd.concat([df.reset_index(drop=True), weather_df.reset_index(drop=True)], axis=1)

    # Add timestamp column with current date and time
    now = datetime.now()
    result_df['recorded_at'] = now.isoformat()
    result_df['recorded_date'] = now.strftime('%Y-%m-%d')
    result_df['recorded_time'] = now.strftime('%H:%M:%S')

    # MySQL connection
    import os
    from dotenv import load_dotenv

    load_dotenv() # Load environment variables from .env

    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
    MYSQL_DATABASE = "OpenMeteo"

    engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

    # Append to weather_records table (keep historical data)
    table_name = "weather_records"
    result_df.to_sql(table_name, con=engine, if_exists='append', index=False)

    print(f"\n✓ Successfully stored {len(result_df)} weather records")
    print(f"  Table: {table_name}")
    print(f"  Database: {MYSQL_DATABASE}")
    print(f"  Host: {MYSQL_HOST}")
    print(f"  Recorded at: {now.isoformat()}")

    # Show sample
    print("\n" + "="*100)
    print("SAMPLE DATA (first 3 towns):")
    print("="*100)
    cols = ["rank", "town", "temperature_2m", "relative_humidity_2m", "weather_code", "recorded_at"]
    print(result_df[cols].head(3).to_string())

except Exception as e:
    print(f"✗ Error: {e}")
