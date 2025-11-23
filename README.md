# Austrian Towns Weather Dashboard

This project fetches current weather data for the 100 most populous towns in Austria using the Open-Meteo API, stores it in a MySQL database, and generates interactive web dashboards and static visualizations.

## Features

*   **Fetch Weather Data**: Retrieves current weather conditions (temperature, humidity, wind, etc.) for specified Austrian towns.
*   **Data Storage**: Persists historical and current weather data in a MySQL database.
*   **Web Dashboard**: Generates an interactive `weather_dashboard.html` using Plotly for detailed visualizations.
*   **Summary Webpage**: Creates `index.html` with quick statistics and rankings, linking to the full dashboard.
*   **Static Visualizations**: Generates `weather_visualization.png` using Matplotlib and Seaborn for a quick overview.
*   **Town Data Management**: Includes scripts to generate and manage the list of Austrian towns.
*   **Credential Management**: Securely handles database credentials using environment variables.

## Setup

### Prerequisites

*   Python 3.8+
*   MySQL Server
*   `uv` (or `pip`) for package management

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/Wetter.git
    cd Wetter
    ```

2.  **Install Python dependencies**:
    This project uses `uv` for dependency management. If you don't have `uv`, install it:
    ```bash
    pip install uv
    ```
    Then, install the project dependencies:
    ```bash
    uv pip install -e .
    ```
    *(Note: If `uv pip install -e .` fails due to package discovery issues, you can install dependencies directly: `uv pip install pandas sqlalchemy python-dotenv`)*

3.  **MySQL Database Setup**:
    *   Ensure your MySQL server is running.
    *   Create the necessary databases. The scripts expect `geodata` and `OpenMeteo` databases to exist. You can create them manually or run `python create_openmeteo_db.py` which will create the `OpenMeteo` database.

4.  **Configure Credentials**:
    Create a `.env` file in the project root based on `.env.example` and fill in your MySQL credentials:
    ```
    MYSQL_USER="your_mysql_username"
    MYSQL_PASSWORD="your_mysql_password"
    MYSQL_HOST="your_mysql_host"
    MYSQL_PORT=3306
    ```
    Replace `your_mysql_username`, `your_mysql_password`, and `your_mysql_host` with your actual MySQL credentials. The `MYSQL_PORT` is typically `3306`.

## Usage

### 1. Generate Town Data (Optional, if you want to regenerate `austria_towns.csv`)

```bash
python generate_towns.py
```

### 2. Create the OpenMeteo Database

```bash
python create_openmeteo_db.py
```
*(This script creates the `OpenMeteo` database if it doesn't exist and lists available databases.)*

### 3. Fetch and Store Current Weather Data

```bash
python fetch_weather.py
```
*(This script fetches current weather and saves it to the `OpenMeteo.weather_records` table and `austria_towns_current_weather.csv`.)*

### 4. Save Weather to a Separate DB Table (e.g., `geodata.austria_towns_current_weather`)

```bash
python save_weather_to_db.py
```

### 5. Generate Web Dashboards and Visualizations

```bash
python generate_weather_webpage.py
```
*(This generates `index.html` and `weather_dashboard.html`.)*

```bash
python visualize_weather.py
```
*(This generates `weather_visualization.png`.)*

### 6. Delete Database Tables (Use with Caution)

```bash
python delete_weather_table.py
```
*(Deletes `geodata.austria_towns_current_weather` table.)*

```bash
python delete_openmeteo_table.py
```
*(Deletes `OpenMeteo.OpenMeteon` table. Note: There seems to be a discrepancy in table name `OpenMeteon` vs `weather_records` in `fetch_weather.py` and `generate_weather_webpage.py`. Please verify the correct table name.)*

## File Structure

*   `.env`: Contains sensitive environment variables (not tracked by Git).
*   `.env.example`: Template for the `.env` file.
*   `.gitignore`: Specifies intentionally untracked files to ignore.
*   `pyproject.toml`: Project metadata and Python dependencies.
*   `austria_top100_towns_2025.csv`: CSV file with top Austrian towns.
*   `austria_towns.csv`: Another CSV file for Austrian towns (likely generated).
*   `austria_towns_current_weather.csv`: CSV output of fetched weather data.
*   `austrian_towns.py`: Script to generate or manage Austrian town data.
*   `create_openmeteo_db.py`: Script to create the `OpenMeteo` database.
*   `delete_openmeteo_table.py`: Script to delete a table from the `OpenMeteo` database.
*   `delete_weather_table.py`: Script to delete a table from the `geodata` database.
*   `fetch_weather.py`: Main script to fetch weather data from Open-Meteo.
*   `generate_towns.py`: Likely generates town data (similar to `austrian_towns.py`).
*   `generate_weather_webpage.py`: Generates the HTML web dashboard (`index.html`, `weather_dashboard.html`).
*   `index.html`: Main summary webpage.
*   `main.py`: (Purpose not explicitly clear from file name, might be an orchestrator or another main entry point).
*   `save_weather_to_db.py`: Saves weather data to a database table.
*   `store_weather_timeseries.py`: Stores historical weather timeseries data.
*   `visualize_weather.py`: Generates static weather visualizations (`weather_visualization.png`).
*   `weather_dashboard.html`: Interactive Plotly dashboard.
*   `weather_visualization.png`: Static image of weather visualizations.

## Contributing

(Add details on how others can contribute to your project)

## License

(Add license information)
