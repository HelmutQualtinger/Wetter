import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env

# MySQL connection settings
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DATABASE = "OpenMeteo"

# Connect to database
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")

print("Fetching weather data from OpenMeteo database...")

# Read weather data
query = "SELECT * FROM weather_records ORDER BY recorded_at DESC LIMIT 100"
df = pd.read_sql(query, engine)

print(f"Retrieved {len(df)} records")

# Get latest records for each town
df_latest = df.drop_duplicates(subset=['town'], keep='first').sort_values('temperature_2m', ascending=False)

# Create subplots
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        'Temperature Distribution Across Towns',
        'Temperature vs Humidity',
        'Wind Speed by Town',
        'Cloud Cover Distribution',
        'Apparent Temperature Difference',
        'Pressure Levels by Federal State'
    ),
    specs=[
        [{'type': 'bar'}, {'type': 'scatter'}],
        [{'type': 'bar'}, {'type': 'pie'}],
        [{'type': 'scatter'}, {'type': 'box'}]
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.15
)

# 1. Temperature Distribution
temp_sorted = df_latest.sort_values('temperature_2m')
fig.add_trace(
    go.Bar(
        x=temp_sorted['temperature_2m'],
        y=temp_sorted['town'],
        orientation='h',
        marker=dict(
            color=temp_sorted['temperature_2m'],
            colorscale='RdBu_r',
            showscale=True,
            colorbar=dict(x=0.46, len=0.25, y=0.85)
        ),
        name='Temperature',
        hovertemplate='<b>%{y}</b><br>Temperature: %{x:.1f}°C<extra></extra>'
    ),
    row=1, col=1
)

# 2. Temperature vs Humidity Scatter
fig.add_trace(
    go.Scatter(
        x=df_latest['temperature_2m'],
        y=df_latest['relative_humidity_2m'],
        mode='markers+text',
        marker=dict(
            size=10,
            color=df_latest['temperature_2m'],
            colorscale='Viridis',
            showscale=False,
            line=dict(width=1, color='white')
        ),
        text=df_latest['town'],
        textposition='top center',
        textfont=dict(size=8),
        hovertemplate='<b>%{text}</b><br>Temperature: %{x:.1f}°C<br>Humidity: %{y:.0f}%<extra></extra>',
        name='Towns'
    ),
    row=1, col=2
)

# 3. Wind Speed
wind_sorted = df_latest.sort_values('wind_speed_10m', ascending=True).tail(15)
fig.add_trace(
    go.Bar(
        x=wind_sorted['wind_speed_10m'],
        y=wind_sorted['town'],
        orientation='h',
        marker=dict(
            color=wind_sorted['wind_speed_10m'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(x=0.46, len=0.25, y=0.5)
        ),
        name='Wind Speed',
        hovertemplate='<b>%{y}</b><br>Wind Speed: %{x:.1f} km/h<extra></extra>'
    ),
    row=2, col=1
)

# 4. Cloud Cover Pie
cloud_categories = pd.cut(df_latest['cloud_cover'],
                          bins=[-1, 25, 50, 75, 100],
                          labels=['Clear (0-25%)', 'Partly Cloudy (25-50%)', 'Mostly Cloudy (50-75%)', 'Overcast (75-100%)'])
cloud_counts = cloud_categories.value_counts()
fig.add_trace(
    go.Pie(
        labels=cloud_counts.index,
        values=cloud_counts.values,
        marker=dict(colors=['#FFD700', '#87CEEB', '#B0C4DE', '#696969']),
        name='Cloud Cover',
        hovertemplate='<b>%{label}</b><br>Towns: %{value}<br>Percentage: %{percent}<extra></extra>'
    ),
    row=2, col=2
)

# 5. Apparent Temperature Difference
df_latest['temp_diff'] = abs(df_latest['apparent_temperature'] - df_latest['temperature_2m'])
fig.add_trace(
    go.Scatter(
        x=df_latest['temperature_2m'],
        y=df_latest['apparent_temperature'],
        mode='markers',
        marker=dict(
            size=8,
            color=df_latest['temp_diff'],
            colorscale='Hot',
            showscale=True,
            colorbar=dict(x=0.46, len=0.25, y=0.15, title='Temp Diff (°C)')
        ),
        text=df_latest['town'],
        hovertemplate='<b>%{text}</b><br>Actual: %{x:.1f}°C<br>Apparent: %{y:.1f}°C<extra></extra>',
        name='Temperature'
    ),
    row=3, col=1
)

# Add diagonal reference line
min_temp = min(df_latest['temperature_2m'].min(), df_latest['apparent_temperature'].min()) - 2
max_temp = max(df_latest['temperature_2m'].max(), df_latest['apparent_temperature'].max()) + 2
fig.add_trace(
    go.Scatter(
        x=[min_temp, max_temp],
        y=[min_temp, max_temp],
        mode='lines',
        line=dict(dash='dash', color='gray'),
        name='Equal Line',
        hoverinfo='skip'
    ),
    row=3, col=1
)

# 6. Pressure by Federal State (Box plot)
fig.add_trace(
    go.Box(
        y=df_latest['pressure_msl'],
        x=df_latest['federal_state'],
        name='Pressure',
        boxmean='sd',
        hovertemplate='<b>%{x}</b><br>Pressure: %{y:.1f} hPa<extra></extra>'
    ),
    row=3, col=2
)

# Update layout
fig.update_layout(
    title_text='<b>Austrian Towns Weather Dashboard</b>',
    title_font_size=24,
    title_x=0.5,
    height=1400,
    showlegend=False,
    hovermode='closest',
    template='plotly_white'
)

# Update x-axes
fig.update_xaxes(title_text='Temperature (°C)', row=1, col=1)
fig.update_xaxes(title_text='Temperature (°C)', row=1, col=2)
fig.update_xaxes(title_text='Wind Speed (km/h)', row=2, col=1)
fig.update_xaxes(title_text='Actual Temperature (°C)', row=3, col=1)
fig.update_xaxes(title_text='Federal State', row=3, col=2)

# Update y-axes
fig.update_yaxes(title_text='Town', row=1, col=1)
fig.update_yaxes(title_text='Humidity (%)', row=1, col=2)
fig.update_yaxes(title_text='Town', row=2, col=1)
fig.update_yaxes(title_text='Apparent Temperature (°C)', row=3, col=1)
fig.update_yaxes(title_text='Pressure (hPa)', row=3, col=2)

# Save to HTML
html_file = 'weather_dashboard.html'
fig.write_html(html_file)
print(f"✓ Dashboard saved to {html_file}")

# Create a summary statistics page
summary_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Austrian Towns Weather Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .nav {{
            background: #f8f9fa;
            padding: 15px 40px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 20px;
        }}
        .nav a {{
            text-decoration: none;
            color: #667eea;
            font-weight: 600;
            transition: color 0.3s;
        }}
        .nav a:hover {{
            color: #764ba2;
        }}
        .content {{
            padding: 40px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .stat-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-card .detail {{
            font-size: 0.85em;
            margin-top: 10px;
            opacity: 0.8;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th {{
            background: #f0f0f0;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #667eea;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 25px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
            margin: 10px 0;
        }}
        .button:hover {{
            background: #764ba2;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Austrian Towns Weather Report</h1>
            <p>Real-time weather data from Open Meteo API</p>
        </div>

        <div class="nav">
            <a href="#dashboard">Dashboard</a>
            <a href="#statistics">Statistics</a>
            <a href="#rankings">Rankings</a>
        </div>

        <div class="content">
            <section class="section">
                <h2>Quick Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="label">Highest Temperature</div>
                        <div class="value">{df_latest['temperature_2m'].max():.1f}°C</div>
                        <div class="detail">{df_latest.loc[df_latest['temperature_2m'].idxmax(), 'town']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Lowest Temperature</div>
                        <div class="value">{df_latest['temperature_2m'].min():.1f}°C</div>
                        <div class="detail">{df_latest.loc[df_latest['temperature_2m'].idxmin(), 'town']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Average Humidity</div>
                        <div class="value">{df_latest['relative_humidity_2m'].mean():.1f}%</div>
                        <div class="detail">Across all towns</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Highest Wind Speed</div>
                        <div class="value">{df_latest['wind_speed_10m'].max():.1f} km/h</div>
                        <div class="detail">{df_latest.loc[df_latest['wind_speed_10m'].idxmax(), 'town']}</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Average Pressure</div>
                        <div class="value">{df_latest['pressure_msl'].mean():.1f} hPa</div>
                        <div class="detail">Sea level pressure</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Data Points</div>
                        <div class="value">{len(df_latest)}</div>
                        <div class="detail">Towns monitored</div>
                    </div>
                </div>
            </section>

            <section class="section" id="dashboard">
                <h2>Interactive Dashboard</h2>
                <a href="{html_file}" class="button" target="_blank">Open Full Dashboard →</a>
                <p style="margin-top: 15px; color: #666;">Click the button above to view the interactive weather visualization dashboard.</p>
            </section>

            <section class="section" id="rankings">
                <h2>Temperature Rankings</h2>
                <h3 style="color: #667eea; margin: 20px 0 10px 0;">Warmest Towns</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Town</th>
                            <th>Temperature</th>
                            <th>Humidity</th>
                            <th>Federal State</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add top 10 warmest towns
for idx, (i, row) in enumerate(df_latest.nlargest(10, 'temperature_2m').iterrows(), 1):
    summary_html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><b>{row['town']}</b></td>
                            <td>{row['temperature_2m']:.1f}°C</td>
                            <td>{row['relative_humidity_2m']:.0f}%</td>
                            <td>{row['federal_state']}</td>
                        </tr>
"""

summary_html += """
                    </tbody>
                </table>

                <h3 style="color: #667eea; margin: 20px 0 10px 0;">Coldest Towns</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Town</th>
                            <th>Temperature</th>
                            <th>Humidity</th>
                            <th>Federal State</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Add top 10 coldest towns
for idx, (i, row) in enumerate(df_latest.nsmallest(10, 'temperature_2m').iterrows(), 1):
    summary_html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><b>{row['town']}</b></td>
                            <td>{row['temperature_2m']:.1f}°C</td>
                            <td>{row['relative_humidity_2m']:.0f}%</td>
                            <td>{row['federal_state']}</td>
                        </tr>
"""

summary_html += f"""
                    </tbody>
                </table>
            </section>

            <section class="section" id="statistics">
                <h2>Detailed Statistics</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Min</th>
                            <th>Max</th>
                            <th>Average</th>
                            <th>Std Dev</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>Temperature (°C)</b></td>
                            <td>{df_latest['temperature_2m'].min():.2f}</td>
                            <td>{df_latest['temperature_2m'].max():.2f}</td>
                            <td>{df_latest['temperature_2m'].mean():.2f}</td>
                            <td>{df_latest['temperature_2m'].std():.2f}</td>
                        </tr>
                        <tr>
                            <td><b>Humidity (%)</b></td>
                            <td>{df_latest['relative_humidity_2m'].min():.0f}</td>
                            <td>{df_latest['relative_humidity_2m'].max():.0f}</td>
                            <td>{df_latest['relative_humidity_2m'].mean():.1f}</td>
                            <td>{df_latest['relative_humidity_2m'].std():.1f}</td>
                        </tr>
                        <tr>
                            <td><b>Wind Speed (km/h)</b></td>
                            <td>{df_latest['wind_speed_10m'].min():.2f}</td>
                            <td>{df_latest['wind_speed_10m'].max():.2f}</td>
                            <td>{df_latest['wind_speed_10m'].mean():.2f}</td>
                            <td>{df_latest['wind_speed_10m'].std():.2f}</td>
                        </tr>
                        <tr>
                            <td><b>Cloud Cover (%)</b></td>
                            <td>{df_latest['cloud_cover'].min():.0f}</td>
                            <td>{df_latest['cloud_cover'].max():.0f}</td>
                            <td>{df_latest['cloud_cover'].mean():.1f}</td>
                            <td>{df_latest['cloud_cover'].std():.1f}</td>
                        </tr>
                        <tr>
                            <td><b>Pressure (hPa)</b></td>
                            <td>{df_latest['pressure_msl'].min():.2f}</td>
                            <td>{df_latest['pressure_msl'].max():.2f}</td>
                            <td>{df_latest['pressure_msl'].mean():.2f}</td>
                            <td>{df_latest['pressure_msl'].std():.2f}</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>

        <div class="footer">
            <p>Austrian Towns Weather Dashboard | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Data provided by Open-Meteo (https://open-meteo.com)</p>
        </div>
    </div>
</body>
</html>
"""

# Save summary page
index_file = 'index.html'
with open(index_file, 'w') as f:
    f.write(summary_html)

print(f"✓ Summary page saved to {index_file}")
print(f"\nWebpage files created:")
print(f"  1. {index_file} - Main summary and statistics page")
print(f"  2. {html_file} - Interactive dashboard")
