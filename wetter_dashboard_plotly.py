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
        import math
        import numpy as np

        min_val, max_val = value_range

        # Calculate angle for needle (0-360 degrees, where 0 is at top)
        percentage = (value - min_val) / (max_val - min_val)
        angle = percentage * 360

        # Create circular gauge using pie chart
        num_zones = len(colors)
        zone_values = [100 / num_zones] * num_zones
        zone_colors = [c['color'] for c in colors]

        fig = go.Figure(go.Pie(
            values=zone_values,
            marker=dict(
                colors=zone_colors,
                line=dict(color='#1a1a2e', width=2)
            ),
            hole=0.65,
            hoverinfo='skip',
            showlegend=False,
            sort=False,
            direction='clockwise',
            rotation=0,
            textinfo='none'
        ))

        # Add numeric scale labels around the ring
        num_labels = 11  # Number of scale labels
        for i in range(num_labels):
            angle = (i / (num_labels - 1)) * 360
            angle_rad = math.radians(angle)

            # Position labels around the ring at radius 0.78
            radius = 0.78
            x = 0.5 + radius * math.sin(angle_rad)
            y = 0.5 + radius * math.cos(angle_rad)

            label_value = min_val + (i / (num_labels - 1)) * (max_val - min_val)

            fig.add_annotation(
                text=f"{label_value:.0f}",
                x=x, y=y,
                showarrow=False,
                font=dict(size=10, color='#FFFFFF', family='Arial'),
                xref='paper', yref='paper'
            )

        # Add needle using a line from center to edge
        needle_length = 0.55
        angle_rad = math.radians(angle)
        needle_x = [0.5, 0.5 + needle_length * math.sin(angle_rad)]
        needle_y = [0.5, 0.5 + needle_length * math.cos(angle_rad)]

        fig.add_shape(
            type='line',
            x0=needle_x[0], y0=needle_y[0],
            x1=needle_x[1], y1=needle_y[1],
            line=dict(color='#FFFFFF', width=5),
            xref='paper', yref='paper',
            layer='above'
        )

        # Add circle at center
        fig.add_shape(
            type='circle',
            x0=0.45, y0=0.45, x1=0.55, y1=0.55,
            fillcolor='#FFFFFF',
            line=dict(color='#000000', width=2),
            xref='paper', yref='paper',
            layer='above'
        )

        # Add value display
        fig.add_annotation(
            text=f"{value:.1f}",
            x=0.5, y=0.35,
            showarrow=False,
            font=dict(size=40, color='#FFFFFF', family='Arial Black'),
            xref='paper', yref='paper'
        )

        # Add unit
        fig.add_annotation(
            text=unit,
            x=0.5, y=0.27,
            showarrow=False,
            font=dict(size=14, color='#CCCCCC', family='Arial'),
            xref='paper', yref='paper'
        )

        # Add title
        fig.add_annotation(
            text=title,
            x=0.5, y=0.95,
            showarrow=False,
            font=dict(size=14, color='#FFFFFF', family='Arial'),
            xref='paper', yref='paper'
        )

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
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

    wind_rose_fig = go.Figure(go.Barpolar(
        r=[wind_speed],
        theta=[wind_direction],
        width=[15], # Breite des Keils
        marker_color=["#2E91E5"],
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.8
    ))

    wind_rose_fig.update_layout(
        title={'text': f"Wind (Geschw: {wind_speed:.1f} km/h)", 'x': 0.5, 'font': {'color': 'white'}},
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
                range=[0, max(50, wind_speed * 1.2)] # Dynamischer Bereich
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