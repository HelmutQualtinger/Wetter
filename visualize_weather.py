import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import numpy as np
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
print(f"Date range: {df['recorded_date'].min()} to {df['recorded_date'].max()}")

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Create figure with subplots
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('Austrian Towns Weather Analysis', fontsize=20, fontweight='bold')

# Group by date if multiple records exist
df_latest = df.drop_duplicates(subset=['town'], keep='first')

# 1. Temperature Distribution
ax1 = axes[0, 0]
sorted_data = df_latest.sort_values('temperature_2m', ascending=True).tail(20)
ax1.barh(sorted_data['town'], sorted_data['temperature_2m'], color='steelblue')
ax1.set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
ax1.set_title('Top 20 Warmest Towns', fontsize=12, fontweight='bold')
ax1.axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.7)

# 2. Humidity Distribution
ax2 = axes[0, 1]
ax2.scatter(df_latest['temperature_2m'], df_latest['relative_humidity_2m'],
           s=100, alpha=0.6, c=df_latest['temperature_2m'], cmap='coolwarm')
ax2.set_xlabel('Temperature (°C)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Humidity (%)', fontsize=11, fontweight='bold')
ax2.set_title('Temperature vs Humidity', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Wind Speed Distribution
ax3 = axes[0, 2]
sorted_wind = df_latest.sort_values('wind_speed_10m', ascending=False).head(15)
colors_wind = plt.cm.YlOrRd(sorted_wind['wind_speed_10m'] / sorted_wind['wind_speed_10m'].max())
ax3.barh(sorted_wind['town'], sorted_wind['wind_speed_10m'], color=colors_wind)
ax3.set_xlabel('Wind Speed (km/h)', fontsize=11, fontweight='bold')
ax3.set_title('Top 15 Windiest Towns', fontsize=12, fontweight='bold')

# 4. Cloud Cover Distribution
ax4 = axes[1, 0]
cloud_categories = pd.cut(df_latest['cloud_cover'], bins=[0, 25, 50, 75, 100],
                          labels=['Clear', 'Partly Cloudy', 'Mostly Cloudy', 'Overcast'])
cloud_counts = cloud_categories.value_counts()
colors_cloud = ['#FFD700', '#87CEEB', '#B0C4DE', '#696969']
ax4.pie(cloud_counts.values, labels=cloud_counts.index, autopct='%1.1f%%',
       colors=colors_cloud, startangle=90)
ax4.set_title('Cloud Cover Distribution', fontsize=12, fontweight='bold')

# 5. Apparent Temperature vs Actual Temperature
ax5 = axes[1, 1]
ax5.scatter(df_latest['temperature_2m'], df_latest['apparent_temperature'],
           s=100, alpha=0.6, color='coral')
# Add diagonal line for reference
min_temp = min(df_latest['temperature_2m'].min(), df_latest['apparent_temperature'].min())
max_temp = max(df_latest['temperature_2m'].max(), df_latest['apparent_temperature'].max())
ax5.plot([min_temp, max_temp], [min_temp, max_temp], 'k--', alpha=0.5, label='Same')
ax5.set_xlabel('Actual Temperature (°C)', fontsize=11, fontweight='bold')
ax5.set_ylabel('Apparent Temperature (°C)', fontsize=11, fontweight='bold')
ax5.set_title('Actual vs Apparent Temperature', fontsize=12, fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3)

# 6. Federal State Statistics
ax6 = axes[1, 2]
state_data = df_latest.groupby('federal_state')['temperature_2m'].mean().sort_values(ascending=True)
colors_state = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(state_data)))
ax6.barh(state_data.index, state_data.values, color=colors_state)
ax6.set_xlabel('Average Temperature (°C)', fontsize=11, fontweight='bold')
ax6.set_title('Average Temperature by Federal State', fontsize=12, fontweight='bold')

plt.tight_layout()

# Save figure
output_file = 'weather_visualization.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualization saved to {output_file}")

# Print statistics
print("\n" + "="*80)
print("WEATHER STATISTICS")
print("="*80)
print(f"\nTemperature Statistics:")
print(f"  Highest: {df_latest['temperature_2m'].max()}°C ({df_latest.loc[df_latest['temperature_2m'].idxmax(), 'town']})")
print(f"  Lowest: {df_latest['temperature_2m'].min()}°C ({df_latest.loc[df_latest['temperature_2m'].idxmin(), 'town']})")
print(f"  Average: {df_latest['temperature_2m'].mean():.2f}°C")
print(f"  Std Dev: {df_latest['temperature_2m'].std():.2f}°C")

print(f"\nHumidity Statistics:")
print(f"  Highest: {df_latest['relative_humidity_2m'].max()}% ({df_latest.loc[df_latest['relative_humidity_2m'].idxmax(), 'town']})")
print(f"  Lowest: {df_latest['relative_humidity_2m'].min()}% ({df_latest.loc[df_latest['relative_humidity_2m'].idxmin(), 'town']})")
print(f"  Average: {df_latest['relative_humidity_2m'].mean():.1f}%")

print(f"\nWind Speed Statistics:")
print(f"  Highest: {df_latest['wind_speed_10m'].max()} km/h ({df_latest.loc[df_latest['wind_speed_10m'].idxmax(), 'town']})")
print(f"  Lowest: {df_latest['wind_speed_10m'].min()} km/h ({df_latest.loc[df_latest['wind_speed_10m'].idxmin(), 'town']})")
print(f"  Average: {df_latest['wind_speed_10m'].mean():.2f} km/h")

print(f"\nCloud Cover Statistics:")
print(f"  Clearest: {df_latest['cloud_cover'].min()}% ({df_latest.loc[df_latest['cloud_cover'].idxmin(), 'town']})")
print(f"  Most Cloudy: {df_latest['cloud_cover'].max()}% ({df_latest.loc[df_latest['cloud_cover'].idxmax(), 'town']})")
print(f"  Average: {df_latest['cloud_cover'].mean():.1f}%")

print(f"\nPressure Statistics:")
print(f"  Highest: {df_latest['pressure_msl'].max()} hPa ({df_latest.loc[df_latest['pressure_msl'].idxmax(), 'town']})")
print(f"  Lowest: {df_latest['pressure_msl'].min()} hPa ({df_latest.loc[df_latest['pressure_msl'].idxmin(), 'town']})")
print(f"  Average: {df_latest['pressure_msl'].mean():.2f} hPa")

plt.show()
