import requests
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd

def get_population(text):
    # Remove references and commas/dots
    text = re.sub(r'[[^]]*]', '', text)
    text = text.replace(',', '').replace('.', '')
    try:
        return int(text.strip())
    except ValueError:
        return 0

def fetch_top_towns():
    url = "https://en.wikipedia.org/wiki/List_of_cities_in_Germany_by_population"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    towns = []

    # There might be multiple tables, we need to find the one with city data
    # Look for a table that has 'City', 'State', and 'Population' headers
    for table in soup.find_all('table', class_='wikitable'):
        headers = [th.text.strip() for th in table.find_all('th')]
        print(f"Table Headers: {headers}")
        
        has_required_headers = False
        city_idx, state_idx, pop_idx = -1, -1, -1

        for i, h in enumerate(headers):
            if h.strip() == 'City':
                city_idx = i
            elif 'State' in h:
                state_idx = i
            elif 'estimate' in h.lower(): # More flexible matching for Population
                pop_idx = i
        
        if city_idx != -1 and state_idx != -1 and pop_idx != -1:
            has_required_headers = True
            print(f"Required headers found in this table. Indices: City={city_idx}, State={state_idx}, Pop={pop_idx}")

        if has_required_headers:
            try:
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all(['td', 'th'])
                    print(f"Row has {len(cols)} columns. Max required index: {max(city_idx, state_idx, pop_idx)}")
                    if len(cols) > max(city_idx, state_idx, pop_idx):
                        city = cols[city_idx].text.strip()
                        state = re.sub(r'\[[^\]]*\]', '', cols[state_idx].text).strip()
                        pop_str = cols[pop_idx].text.strip()
                        population = get_population(pop_str)

                        if population > 0 and city and state:
                            towns.append({
                                'town': city,
                                'federal_state': state,
                                'inhabitants': population
                            })
            except Exception as e:
                print(f"Error parsing table row: {e}")
                continue

    # Dedup by name + federal_state
    unique_towns = {}
    for t in towns:
        key = (t['town'], t['federal_state'])
        if key not in unique_towns or unique_towns[key]['inhabitants'] < t['inhabitants']:
            unique_towns[key] = t

    sorted_towns = sorted(unique_towns.values(), key=lambda x: x['inhabitants'], reverse=True)
    return sorted_towns[:200] # Limit to top 200 towns

def get_coordinates(town, federal_state):
    base_url = "https://nominatim.openstreetmap.org/search"
    query = f"{town}, {federal_state}, Germany"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'GermanTownsFetcher/1.0' # Changed User-Agent
    }
    try:
        r = requests.get(base_url, params=params, headers=headers)
        if r.status_code == 200 and r.json():
            data = r.json()[0]
            return float(data['lon']), float(data['lat'])
        else:
            # Fallback to just town, Germany if federal_state lookup fails
            params['q'] = f"{town}, Germany"
            r = requests.get(base_url, params=params, headers=headers)
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                return float(data['lon']), float(data['lat'])
    except Exception as e:
        print(f"Error geocoding {town}: {e}")
    return None, None

def main():
    print("Fetching German towns...")
    top_towns = fetch_top_towns()
    print(f"Found {len(top_towns)} towns. Fetching coordinates...")

    final_data = []
    for i, town in enumerate(top_towns):
        print(f"Processing {i+1}/{len(top_towns)}: {town['town']}")
        lon, lat = get_coordinates(town['town'], town['federal_state'])

        entry = {
            "town": town['town'],
            "federal_state": town['federal_state'],
            "longitude": lon,
            "latitude": lat,
            "inhabitants": town['inhabitants']
        }
        final_data.append(entry)
        time.sleep(0.1) # Be respectful to the API

    df = pd.DataFrame(final_data)
    print("\n--- Extracted German Towns DataFrame ---")
    print(df.to_string())
    print("--- End DataFrame ---")

    # Save the DataFrame to a CSV file
    csv_filename = "german_towns.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"\n--- Saved DataFrame to {csv_filename} ---")

if __name__ == "__main__":
    main()
