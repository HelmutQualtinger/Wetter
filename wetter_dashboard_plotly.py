import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "OpenMeteo" # The database for weather records

# Create SQLAlchemy engine for the OpenMeteo database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

# Daten aus der SQLite-Datenbank laden
def load_data():
    """Lädt die neuesten Wetterdaten für jeden Ort aus der Datenbank."""
    try:
        # Use the global engine created earlier
        query = """
        SELECT * FROM (
            SELECT *,
                   ROW_NUMBER() OVER(PARTITION BY town ORDER BY recorded_at DESC) as rn
            FROM verbose_weather_records
        ) AS subquery
        WHERE rn = 1;
        """
        df = pd.read_sql_query(query, engine) # Use the global engine
        return df
    except Exception as e:
        print(f"Fehler beim Laden der Daten aus MySQL: {e}")
        # Erstellt ein leeres DataFrame mit den erwarteten Spalten bei einem Fehler
        return pd.DataFrame(columns=[
            'location_name', 'federal_state', 'timestamp', 'temperature_2m', 'relative_humidity_2m',
            'apparent_temperature', 'is_day', 'precipitation', 'rain', 'snowfall',
            'cloud_cover', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m',
            'wind_gusts_10m', 'weather_code_description', 'weather_code_image'
        ])

# Daten initial laden
df = load_data()
bundeslaender = sorted(df['federal_state'].unique().tolist())

# Initialisiert die Dash-App
app = dash.Dash(__name__)
app.title = "Wetter-Dashboard"

# App-Layout
app.layout = html.Div(style={'backgroundColor': '#111111', 'color': '#7FDBFF', 'font-family': 'sans-serif'}, children=[
    html.H1(
        children='Wetter-Dashboard Österreich',
        style={'textAlign': 'center', 'padding': '10px', 'marginBottom': '5px', 'fontSize': '24px'}
    ),

    # Dropdowns für die Auswahl
    html.Div([
        html.Div([
            html.Label('Bundesland', style={'fontSize': '12px', 'marginBottom': '2px', 'display': 'block'}),
            dcc.Dropdown(
                id='state-dropdown',
                style={'color': 'black', 'fontSize': '13px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '3px', 'marginRight': '2%'}),

        html.Div([
            html.Label('Ort', style={'fontSize': '12px', 'marginBottom': '2px', 'display': 'block'}),
            dcc.Dropdown(id='city-dropdown', style={'color': 'black', 'fontSize': '13px'})
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '3px'})
    ], style={'marginBottom': '5px'}),

    # Container für die Visualisierungen
    html.Div(id='weather-output', style={'padding': '20px'}),
])

# Callback zur Initialisierung des Bundesland-Dropdowns
@app.callback(
    Output('state-dropdown', 'options'),
    Output('state-dropdown', 'value'),
    Input('state-dropdown', 'id'),
    prevent_initial_call=False
)
def initialize_state_dropdown(_):
    options = [{'label': b, 'value': b} for b in bundeslaender]
    initial_value = bundeslaender[0] if len(bundeslaender) > 0 else None
    return options, initial_value

# Callback zur Aktualisierung des Städte-Dropdowns basierend auf dem Bundesland
@app.callback(
    Output('city-dropdown', 'options'),
    Input('state-dropdown', 'value')
)
def set_cities_options(selected_state):
    if selected_state is None:
        return []
    filtered_df = df[df['federal_state'] == selected_state]
    cities = sorted(filtered_df['town'].unique())
    return [{'label': c, 'value': c} for c in cities]

# Callback zur Aktualisierung der Wettervisualisierungen basierend auf der Stadtauswahl
@app.callback(
    Output('weather-output', 'children'),
    Input('city-dropdown', 'value')
)
def update_weather_dashboard(selected_city):
    if selected_city is None:
        return html.Div("Bitte wählen Sie einen Ort aus.", style={'textAlign': 'center', 'padding': '50px'})

    city_data = df[df['town'] == selected_city].iloc[0]

    # --- Gauges ---
    def create_gauge(value, title, unit, value_range, colors, bar_color):
        min_val, max_val = value_range

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={
                'text': title,
                'font': {'size': 16, 'color': '#FFFFFF', 'family': 'Arial Black'}
            },
            number={
                'font': {'size': 44, 'color': '#FFFFFF', 'family': 'Arial Black'},
                'suffix': f" {unit}",
                'valueformat': '.1f'
            },
            gauge={
                'axis': {
                    'range': [min_val, max_val],
                    'tickwidth': 3,
                    'tickcolor': '#FFFFFF',
                    'ticklen': 12,
                    'tickfont': {'size': 11, 'color': '#FFFFFF', 'family': 'Arial'}
                },
                'bar': {
                    'color': '#FFD700',
                    'thickness': 1.0,
                    'line': {'color': '#FFFFFF', 'width': 3}
                },
                'bgcolor': 'rgba(50,50,80,0.4)',
                'borderwidth': 6,
                'bordercolor': '#00D9FF',
                'steps': colors,
                'threshold': {
                    'line': {'color': '#FFFFFF', 'width': 4},
                    'thickness': 1.0,
                    'value': value
                }
            }
        ))

        fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=70, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(25,25,50,0.5)',
            font={'color': 'white', 'family': 'Arial, sans-serif'}
        )

        return fig

    # Definieren der Gauges
    temp_gauge = create_gauge(
        city_data['temperature_2m'], "Temperatur", "°C", [-20, 40],
        [{'range': [-20, 0], 'color': "#1E90FF"}, {'range': [0, 15], 'color': "#00CED1"}, {'range': [15, 25], 'color': "#FFD700"}, {'range': [25, 40], 'color': "#FF4500"}],
        "#FF6B6B"
    )
    humidity_gauge = create_gauge(
        city_data['relative_humidity_2m'], "Luftfeuchtigkeit", "%", [0, 100],
        [{'range': [0, 30], 'color': "#FFD700"}, {'range': [30, 60], 'color': "#90EE90"}, {'range': [60, 100], 'color': "#00BFFF"}],
        "#00CED1"
    )
    pressure_gauge = create_gauge(
        city_data['pressure_msl'], "Luftdruck", "hPa", [990, 1040],
        [{'range': [990, 1010], 'color': "#FF6347"}, {'range': [1010, 1025], 'color': "#FFD700"}, {'range': [1025, 1040], 'color': "#90EE90"}],
        "#FFB6C1"
    )
    cloud_cover_gauge = create_gauge(
        city_data['cloud_cover'], "Bewölkung", "%", [0, 100],
        [{'range': [0, 33], 'color': "#87CEEB"}, {'range': [33, 66], 'color': "#B0C4DE"}, {'range': [66, 100], 'color': "#808080"}],
        "#4169E1"
    )


    # --- Windrose ---
    wind_direction = city_data['wind_direction_10m']
    wind_speed = city_data['wind_speed_10m']
    wind_gusts = city_data['wind_gusts_10m']

    wind_rose_fig = go.Figure()

    # Add wind speed bar
    wind_rose_fig.add_trace(go.Barpolar(
        r=[wind_speed],
        theta=[wind_direction],
        width=[12],
        name='Wind Speed',
        marker_color=["#2E91E5"],
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.8
    ))

    # Add wind gusts bar
    wind_rose_fig.add_trace(go.Barpolar(
        r=[wind_gusts],
        theta=[wind_direction],
        width=[12],
        name='Wind Gusts',
        marker_color=["#FF6B6B"],
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.6
    ))

    wind_rose_fig.update_layout(
        title={'text': f"Wind: {wind_speed:.1f} km/h | Gusts: {wind_gusts:.1f} km/h", 'x': 0.5, 'font': {'color': 'white'}},
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(
                tickfont_size=12,
                rotation=90,  # 0 Grad nach oben (Norden)
                direction="clockwise",
                showline=True,
                showticklabels=True,
                ticks='outside',
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW']
            ),
            radialaxis=dict(
                visible=True,
                range=[0, 20]  # Fixed maximum at 20 km/h
            )
        )
    )

    # Zusammenstellen des Outputs
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=temp_gauge, config={'displayModeBar': False})
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div([
                dcc.Graph(figure=humidity_gauge, config={'displayModeBar': False})
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div([
                dcc.Graph(figure=pressure_gauge, config={'displayModeBar': False})
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div([
                dcc.Graph(figure=cloud_cover_gauge, config={'displayModeBar': False})
            ], style={'width': '23%', 'display': 'inline-block'}),
        ], style={'width': '100%', 'marginBottom': '20px'}),
        html.Div([
            dcc.Graph(figure=wind_rose_fig)
        ], style={'width': '100%'})
    ])

if __name__ == '__main__':
    # Prüft, ob Daten geladen wurden
    if df.empty:
        print("Konnte keine Daten aus der Datenbank laden. Stellen Sie sicher, dass die MySQL-Datenbank 'OpenMeteo' existiert und die View 'verbose_weather_records' Daten enthält.")
    else:
        print("Starte Dash-Server...")
        print(f"Daten für {len(df)} Orte geladen.")
        print("Öffnen Sie http://127.0.0.1:8050 in Ihrem Browser.")
        app.run(debug=True)