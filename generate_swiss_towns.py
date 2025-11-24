import requests
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd

def get_population(text):
    # Remove references and commas/dots
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = text.replace(',', '').replace('.', '')
    try:
        return int(text.strip())
    except ValueError:
        return 0

def fetch_top_towns():
    url = "https://en.wikipedia.org/wiki/Cities_in_Switzerland"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    towns = []

    for table in soup.find_all('table', class_='wikitable'):
        headers = [th.text.strip() for th in table.find_all('th')]
        if not headers:
            # Try first row as header if no th
            headers = [td.text.strip() for td in table.find_all('tr')[0].find_all('td')]

        has_population_header = False
        for h in headers:
            if 'Population' in h:
                has_population_header = True
                break

        if ('Name' in headers or 'Town' in headers) and has_population_header:
            try:
                name_idx = -1
                pop_idx = -1
                canton_idx = -1

                # Find Name or Town index
                for i, h in enumerate(headers):
                    if 'Name' in h or 'Town' in h:
                        name_idx = i
                        break

                # Find Population index (more flexibly)
                for i, h in enumerate(headers):
                    if 'Population' in h:
                        pop_idx = i
                        break

                # Find Canton index
                for i, h in enumerate(headers):
                    if 'Canton' in h:
                        canton_idx = i
                        break

                if name_idx == -1 or pop_idx == -1:
                    continue

                # Iterate rows
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) > max(name_idx, pop_idx):
                        name = re.sub(r'\[[^\]]*\]|\([^)]*\)', '', cols[name_idx].text).strip()
                        pop_str = cols[pop_idx].text.strip()
                        population = get_population(pop_str)

                        canton = "Unknown"
                        # Try to find canton from table column if it exists
                        if canton_idx != -1 and len(cols) > canton_idx:
                            canton = cols[canton_idx].text.strip()
                        else:
                            # Fallback to finding canton from nearby header
                            prev = table.find_previous(['h2', 'h3'])
                            if prev:
                                canton_cand = prev.text.strip()
                                if canton_cand:
                                    canton = canton_cand

                        if population > 0 and canton != "Unknown":
                            towns.append({
                                'town': name,
                                'canton': canton,
                                'inhabitants': population
                            })
            except Exception as e:
                continue

    # Dedup by name + canton (just in case)
    unique_towns = {}
    for t in towns:
        key = (t['town'], t['canton'])
        if key not in unique_towns or unique_towns[key]['inhabitants'] < t['inhabitants']:
            unique_towns[key] = t

    sorted_towns = sorted(unique_towns.values(), key=lambda x: x['inhabitants'], reverse=True)
    return sorted_towns[:200]

def get_coordinates(town, canton):
    base_url = "https://nominatim.openstreetmap.org/search"
    query = f"{town}, {canton}, Switzerland"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'SwissTownsFetcher/1.0'
    }
    try:
        r = requests.get(base_url, params=params, headers=headers)
        if r.status_code == 200 and r.json():
            data = r.json()[0]
            return float(data['lon']), float(data['lat'])
        else:
            params['q'] = f"{town}, Switzerland"
            r = requests.get(base_url, params=params, headers=headers)
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                return float(data['lon']), float(data['lat'])
    except Exception as e:
        print(f"Error geocoding {town}: {e}")
    return None, None

def main():
    print("Fetching Swiss towns...")
    top_100 = fetch_top_towns()
    print(f"Found {len(top_100)} towns. Fetching coordinates...")

    final_data = []
    for i, town in enumerate(top_100):
        print(f"Processing {i+1}/{len(top_100)}: {town['town']}")
        lon, lat = get_coordinates(town['town'], town['canton'])

        if lon is None:
            query = f"{town['town']}, {town['canton']}, Switzerland"
            try:
                r = requests.get("https://nominatim.openstreetmap.org/search",
                               params={'q': query, 'format': 'json', 'limit': 1},
                               headers={'User-Agent': 'SwissTownsFetcher/1.0'})
                if r.status_code == 200 and r.json():
                    d = r.json()[0]
                    lon, lat = float(d['lon']), float(d['lat'])
            except:
                pass

        entry = {
            "town": town['town'],
            "canton": town['canton'],
            "longitude": lon,
            "latitude": lat,
            "inhabitants": town['inhabitants']
        }
        final_data.append(entry)
        time.sleep(0.1)

    df = pd.DataFrame(final_data)
    print("\n--- Extracted Swiss Towns DataFrame ---")
    print(df.to_string())
    print("--- End DataFrame ---")

    # Keeping the JSON output for backward compatibility/other uses
    print("\n--- Raw JSON Output ---")
    print(json.dumps(final_data, indent=4))
    print("--- End Raw JSON Output ---")

    # Save the DataFrame to a CSV file
    csv_filename = "swiss_towns.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8")
    print(f"\n--- Saved DataFrame to {csv_filename} ---")

if __name__ == "__main__":
    main()
