import pandas as pd
import requests
import os
from datetime import datetime, timedelta

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def load_data_from_api(*args, **kwargs):
    # Set a 3-day window to stay within NASA's 7-day API limit
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Retrieve API key securely from environment variables
    api_key = os.getenv('NASA_API_KEY')
    
    if not api_key:
        raise ValueError("❌ NASA_API_KEY not found. Ensure the .env file is correctly loaded.")

    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_str}&end_date={end_str}&api_key={api_key}"
    
    print(f"📡 Fetching data from NASA: {start_str} to {end_str}...")
    response = requests.get(url)
    
    # Error handling for rate limits and invalid keys
    if response.status_code in [403, 429]:
        raise Exception(f"❌ API Limit reached or Invalid Key! Status: {response.status_code}")
        
    response.raise_for_status()
    data = response.json()
    
    neo_data = data.get('near_earth_objects', {})
    
    # Safety check: Stop execution if no data is returned
    if not neo_data:
         raise ValueError(f"❌ API request successful, but no asteroids found for this period. Response: {data}")
         
    # Data parsing and flattening
    asteroids_list = []
    for date_key, aster_list in neo_data.items():
        for asteroid in aster_list:
            asteroids_list.append({
                'id': asteroid.get('id'),
                'name': asteroid.get('name'),
                'date': date_key,
                'estimated_diameter_min_km': asteroid.get('estimated_diameter', {}).get('kilometers', {}).get('estimated_diameter_min'),
                'estimated_diameter_max_km': asteroid.get('estimated_diameter', {}).get('kilometers', {}).get('estimated_diameter_max'),
                'is_potentially_hazardous': asteroid.get('is_potentially_hazardous_asteroid'),
                'close_approach_date': asteroid.get('close_approach_data', [{}])[0].get('close_approach_date'),
                'relative_velocity_kmh': float(asteroid.get('close_approach_data', [{}])[0].get('relative_velocity', {}).get('kilometers_per_hour', 0) or 0),
                'miss_distance_km': float(asteroid.get('close_approach_data', [{}])[0].get('miss_distance', {}).get('kilometers', 0) or 0)
            })
    
    df = pd.DataFrame(asteroids_list)
    print(f"✅ Extraction successful! {len(df)} asteroids found.")
    
    return df