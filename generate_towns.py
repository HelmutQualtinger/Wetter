import requests
from bs4 import BeautifulSoup
import time
import json
import re

def get_population(text):
    # Remove references like [1] and commas/dots
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace(',', '').replace('.', '')
    try:
        return int(text.strip())
    except ValueError:
        return 0

def fetch_top_towns():
    url = "https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Austria"
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    print(f"Content length: {len(response.content)}")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    towns = []
    
    # The page has multiple tables, usually under headings for each state.
    # But there's also a section "List of cities and towns in Austria" which might be just the list.
    # Looking at the web_fetch output earlier:
    # "Lists of cities, towns and municipalities divided by state"
    # Each state has a table.
    
    # Let's iterate over all tables and try to extract Name, Designation, Population
    
    # Map for normalizing state names if needed, but wikipedia usually has them right.
    
    # We need to be careful not to duplicate or pick up wrong tables.
    # The tables for states usually have headers: Name, Designation, Population...
    
    for table in soup.find_all('table', class_='wikitable'):
        headers = [th.text.strip() for th in table.find_all('th')]
        if not headers:
             # Try first row as header if no th
            headers = [td.text.strip() for td in table.find_all('tr')[0].find_all('td')]

        # Check if this table looks like a city list
        if 'Name' in headers and 'Population' in headers: # Or variants
             # Find index
            try:
                name_idx = -1
                pop_idx = -1
                for i, h in enumerate(headers):
                    if 'Name' in h: name_idx = i
                    if 'Population' in h: pop_idx = i
                
                if name_idx == -1 or pop_idx == -1:
                    continue

                # Iterate rows
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) > max(name_idx, pop_idx):
                        name = cols[name_idx].text.strip()
                        pop_str = cols[pop_idx].text.strip()
                        population = get_population(pop_str)
                        
                        # Some tables might be "Main cities" vs "All municipalities"
                        # We want to collect all and sort.
                        
                        # We need federal state.
                        # The Wikipedia page structure for state tables: 
                        # usually under a heading like "Burgenland", "Carinthia", etc.
                        # We can try to infer state from the preceding heading.
                        
                        state = "Unknown"
                        # Find the preceding header
                        prev = table.find_previous(['h2', 'h3'])
                        if prev:
                            state_cand = prev.text.strip().replace('[edit]', '')
                            if state_cand in ['Burgenland', 'Carinthia', 'Lower Austria', 'Salzburg', 'Styria', 'Tyrol', 'Upper Austria', 'Vienna', 'Vorarlberg']:
                                state = state_cand
                        
                        if state == "Unknown" and name == "Vienna":
                            state = "Vienna"

                        if population > 0:
                            towns.append({
                                'town': name,
                                'federal_state': state,
                                'inhabitants': population
                            })
            except Exception as e:
                print(f"Error parsing table: {e}")
                continue

    # Dedup by name + state (just in case)
    unique_towns = {}
    for t in towns:
        key = (t['town'], t['federal_state'])
        # If duplicate, keep higher population (maybe one was year X and another year Y)
        if key not in unique_towns or unique_towns[key]['inhabitants'] < t['inhabitants']:
            unique_towns[key] = t
            
    sorted_towns = sorted(unique_towns.values(), key=lambda x: x['inhabitants'], reverse=True)
    return sorted_towns[:100]

def get_coordinates(town, state):
    base_url = "https://nominatim.openstreetmap.org/search"
    query = f"{town}, {state}, Austria"
    params = {
        'q': query,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'AustriaTownsFetcher/1.0'
    }
    try:
        r = requests.get(base_url, params=params, headers=headers)
        if r.status_code == 200 and r.json():
            data = r.json()[0]
            return float(data['lon']), float(data['lat'])
        else:
            # Try just town name if specific query fails
            params['q'] = f"{town}, Austria"
            r = requests.get(base_url, params=params, headers=headers)
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                return float(data['lon']), float(data['lat'])
    except Exception as e:
        print(f"Error geocoding {town}: {e}")
    return None, None

def main():
    print("Fetching towns...")
    top_100 = fetch_top_towns()
    print(f"Found {len(top_100)} towns. Fetching coordinates...")
    
    final_data = []
    for i, town in enumerate(top_100):
        print(f"Processing {i+1}/100: {town['town']}")
        lon, lat = get_coordinates(town['town'], town['federal_state'])
        
        # Keep trying to fix state names if they are English vs German for better results
        # Wikipedia has English names e.g. "Carinthia" but Nominatim works better with "Kärnten" sometimes?
        # Actually Nominatim is quite good with English names for Austria.
        # But let's map English to German state names for the output if desired, or keep as is.
        # The user's existing file has "Steiermark", "Oberösterreich" (German).
        # Wikipedia output gave English "Styria", "Upper Austria".
        # I should convert them to German to match the user's existing style.
        
        state_map = {
            'Burgenland': 'Burgenland',
            'Carinthia': 'Kärnten',
            'Lower Austria': 'Niederösterreich',
            'Salzburg': 'Salzburg',
            'Styria': 'Steiermark',
            'Tyrol': 'Tirol',
            'Upper Austria': 'Oberösterreich',
            'Vienna': 'Wien',
            'Vorarlberg': 'Vorarlberg'
        }
        
        german_state = state_map.get(town['federal_state'], town['federal_state'])
        
        if lon is None:
            # Fallback for geocoding with German state name if first try failed
            query = f"{town['town']}, {german_state}, Austria"
            # ... simple retry logic inside the loop for brevity
            try:
                r = requests.get("https://nominatim.openstreetmap.org/search", 
                               params={'q': query, 'format': 'json', 'limit': 1},
                               headers={'User-Agent': 'AustriaTownsFetcher/1.0'})
                if r.status_code == 200 and r.json():
                    d = r.json()[0]
                    lon, lat = float(d['lon']), float(d['lat'])
            except:
                pass
        
        entry = {
            "town": town['town'],
            "federal_state": german_state,
            "longitude": lon,
            "latitude": lat,
            "inhabitants": town['inhabitants']
        }
        final_data.append(entry)
        time.sleep(1.1) # Respect Nominatim 1 request/sec policy
        
    # Print as JSON so I can read it back easily
    print("JSON_START")
    print(json.dumps(final_data, indent=4))
    print("JSON_END")

if __name__ == "__main__":
    main()
