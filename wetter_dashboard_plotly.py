import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL connection details
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "OpenMeteo" # Confirmed database name

# Create SQLAlchemy engine
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
engine = create_engine(DATABASE_URL)

# --- Data Loading Functions ---
def get_all_locations():
    """Fetches all unique federal_states and towns from the verbose_weather_records view."""
    try:
        query = "SELECT DISTINCT federal_state, town FROM verbose_weather_records ORDER BY federal_state, town"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return pd.DataFrame(columns=['federal_state', 'town'])

def get_latest_weather_data(federal_state: str, town: str):
    """Fetches the latest weather record for a given federal_state and town."""
    try:
        # Assuming 'recorded_at' is the primary time key
        query = f"""
            SELECT * FROM verbose_weather_records
            WHERE federal_state = '{federal_state}' AND town = '{town}'
            ORDER BY recorded_at DESC
            LIMIT 1
        """
        df = pd.read_sql(query, engine)
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        print(f"Error fetching weather data for {town}, {federal_state}: {e}")
        return None

# --- Initialize Dash App ---
app = dash.Dash(__name__)
server = app.server # This is needed for deployment later

# --- Get initial data for dropdowns ---
all_locations_df = get_all_locations()
states = sorted(all_locations_df['federal_state'].unique().tolist()) if not all_locations_df.empty else []

# --- App Layout ---
app.layout = html.Div([
    html.H1("Wetter-Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Bundesland auswählen:"),
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'label': s, 'value': s} for s in states],
                placeholder="Wähle ein Bundesland",
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'margin-right': '2%'}),

        html.Div([
            html.Label("Ort auswählen:"),
            dcc.Dropdown(
                id='town-dropdown',
                options=[], # Will be populated by callback
                placeholder="Wähle einen Ort",
                clearable=False
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'padding': '20px'}),

    html.Div(id='weather-output', children=[
        html.Div([
            dcc.Graph(id='gauge-temperature', style={'display': 'inline-block', 'width': '25%'}),
            dcc.Graph(id='gauge-humidity', style={'display': 'inline-block', 'width': '25%'}),
            dcc.Graph(id='gauge-wind-speed', style={'display': 'inline-block', 'width': '25%'}),
            dcc.Graph(id='gauge-pressure', style={'display': 'inline-block', 'width': '25%'}),
        ], style={'textAlign': 'center'}),
        html.Div([
            dcc.Graph(id='windrose-chart', style={'width': '50%', 'display': 'inline-block'}),
            html.Div(id='weather-description-card', children=[
                html.H3("Wetterbeschreibung", style={'textAlign': 'center'}),
                html.P(id='weather-description', style={'textAlign': 'center', 'fontSize': '1.2em'}),
                html.P(id='last-updated', style={'textAlign': 'center', 'fontSize': '0.9em', 'color': 'gray'})
            ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'borderRadius': '5px', 'margin-left': '5%'})
        ], style={'textAlign': 'center', 'marginTop': '20px'})
    ])
])

# --- Callbacks ---
@app.callback(
    Output('town-dropdown', 'options'),
    Output('town-dropdown', 'value'), # Reset town selection when state changes
    Input('state-dropdown', 'value')
)
def set_town_options(selected_federal_state):
    if selected_federal_state:
        towns = all_locations_df[all_locations_df['federal_state'] == selected_federal_state]['town'].unique()
        return [{'label': t, 'value': t} for t in sorted(towns)], None # Reset value
    return [], None

@app.callback(
    Output('gauge-temperature', 'figure'),
    Output('gauge-humidity', 'figure'),
    Output('gauge-wind-speed', 'figure'),
    Output('gauge-pressure', 'figure'),
    Output('windrose-chart', 'figure'),
    Output('weather-description', 'children'),
    Output('last-updated', 'children'),
    Input('state-dropdown', 'value'),
    Input('town-dropdown', 'value')
)
def update_weather_visuals(selected_federal_state, selected_town):
    # Initialize empty figures and default text
    empty_fig = go.Figure()
    empty_description = "Bitte wählen Sie ein Bundesland und einen Ort."
    empty_updated_text = ""

    if not selected_federal_state or not selected_town:
        return (empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                empty_description, empty_updated_text)

    weather_data = get_latest_weather_data(selected_federal_state, selected_town)

    if weather_data is None:
        return (empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
                "Keine Wetterdaten für diesen Ort verfügbar.", empty_updated_text)

    # --- Gauges ---
    temp_c = weather_data.get('temperature_2m')
    humidity_percent = weather_data.get('relative_humidity_2m')
    wind_speed_kmh = weather_data.get('wind_speed_10m')
    pressure_hpa = weather_data.get('pressure_msl')

    gauge_temp = create_gauge("Temperatur (°C)", temp_c, -20, 40, '°C')
    gauge_humidity = create_gauge("Luftfeuchtigkeit (%)", humidity_percent, 0, 100, '%')
    gauge_wind_speed = create_gauge("Windgeschwindigkeit (km/h)", wind_speed_kmh, 0, 100, 'km/h')
    gauge_pressure = create_gauge("Luftdruck (hPa)", pressure_hpa, 950, 1050, 'hPa')

    # --- Windrose ---
    wind_direction = weather_data.get('wind_direction_10m')
    wind_speed = weather_data.get('wind_speed_10m')

    windrose_fig = go.Figure()
    if wind_direction is not None and wind_speed is not None:
        wind_data_for_rose = pd.DataFrame({
            "direction": [wind_direction],
            "strength": [wind_speed]
        })
        windrose_fig = px.bar_polar(
            wind_data_for_rose,
            r="strength",
            theta="direction",
            color="strength",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Windrose"
        )
        windrose_fig.update_layout(polar_radialaxis_ticks=" ", polar_angularaxis_line_color="black")


    # --- Weather Description and Last Updated ---
    weather_desc = weather_data.get('weather_description', 'N/A')
    last_updated_ts = weather_data.get('recorded_at')
    last_updated_text = f"Zuletzt aktualisiert: {pd.to_datetime(last_updated_ts).strftime('%d.%m.%Y %H:%M')}" if last_updated_ts else ""


    return (gauge_temp, gauge_humidity, gauge_wind_speed, gauge_pressure,
            windrose_fig, weather_desc, last_updated_text)

def create_gauge(title, value, min_val, max_val, unit):
    """Helper function to create a Plotly Gauge figure."""
    if value is None:
        value = 0 # Default to 0 if no value
        title = f"{title} (N/A)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, min_val + (max_val-min_val)*0.2], 'color': 'cyan'},
                {'range': [min_val + (max_val-min_val)*0.2, min_val + (max_val-min_val)*0.8], 'color': 'lightgray'},
                {'range': [min_val + (max_val-min_val)*0.8, max_val], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value}}
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    return fig


if __name__ == '__main__':
    app.run(debug=True, port=8050)
