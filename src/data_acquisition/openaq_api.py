"""
OpenAQ API Integration Module v3
Fetches air quality data from OpenAQ platform using v3 API
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from loguru import logger
from config.settings import OPENAQ_API_KEY, OPENAQ_BASE_URL, API_TIMEOUT, MONITORED_CITIES


class OpenAQAPI:
    """OpenAQ API v3 Client for fetching air quality data"""
    
    def __init__(self):
        self.base_url = OPENAQ_BASE_URL
        self.api_key = OPENAQ_API_KEY
        self.session = requests.Session()
        
        # v3 API uses API key in header
        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'Accept': 'application/json'
            })
        else:
            logger.warning("OpenAQ API key not set - may have limited access")
    
    def get_latest_measurements(self, city: str, max_retries: int = 2) -> Optional[pd.DataFrame]:
        """
        Get latest air quality measurements for a city using v3 API
        Based on official docs: https://docs.openaq.org/
        
        Process:
        1. Find locations near city coordinates
        2. Get latest data from each location
        
        Args:
            city: City name
            max_retries: Maximum retry attempts
            
        Returns:
            DataFrame with latest measurements or None if failed
        """
        try:
            city_info = MONITORED_CITIES.get(city)
            if not city_info:
                logger.error(f"City {city} not found in monitored cities")
                return None
            
            lat = city_info['lat']
            lon = city_info['lon']
            
            logger.info(f"Fetching OpenAQ v3 data for {city} (coords: {lat},{lon})")
            
            # Step 1: Find locations near the city using geospatial search
            # coordinates format: latitude,longitude (Y,X)
            # radius: in meters, max 25000 (25km)
            locations_url = f"{self.base_url}/locations"
            params = {
                'coordinates': f"{lat},{lon}",  # lat,lon format per docs
                'radius': 25000,  # 25km radius (max allowed)
                'limit': 20,  # Get up to 20 nearest stations
                'country': city_info['country']
            }
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(locations_url, params=params, timeout=API_TIMEOUT)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'results' not in data or not data['results']:
                        logger.debug(f"No OpenAQ locations found near {city}")
                        return None
                    
                    locations = data['results']
                    logger.success(f"Found {len(locations)} OpenAQ locations near {city}")
                    
                    # Step 2: Get latest measurements from each location
                    all_records = []
                    for location in locations[:5]:  # Limit to 5 closest stations
                        location_id = location.get('id')
                        location_name = location.get('name', city)
                        coords = location.get('coordinates', {})
                        
                        # Get latest data for this location
                        latest_url = f"{self.base_url}/locations/{location_id}/latest"
                        latest_response = self.session.get(latest_url, timeout=API_TIMEOUT)
                        
                        if latest_response.status_code == 200:
                            latest_data = latest_response.json()
                            
                            for result in latest_data.get('results', []):
                                # Extract sensor data
                                sensors_id = result.get('sensorsId')
                                value = result.get('value')
                                datetime_info = result.get('datetime', {})
                                
                                # Need to map sensor ID to parameter name
                                # Look in location sensors list
                                parameter_name = None
                                for sensor in location.get('sensors', []):
                                    if sensor.get('id') == sensors_id:
                                        param_info = sensor.get('parameter', {})
                                        parameter_name = param_info.get('name')
                                        break
                                
                                if parameter_name and value is not None:
                                    all_records.append({
                                        'city': city,
                                        'location': location_name,
                                        'location_id': location_id,
                                        'parameter': parameter_name,
                                        'value': value,
                                        'unit': 'µg/m³',  # OpenAQ uses standard units
                                        'lastUpdated': datetime_info.get('utc'),
                                        'latitude': coords.get('latitude'),
                                        'longitude': coords.get('longitude')
                                    })
                        
                        time.sleep(0.5)  # Rate limiting between location requests
                    
                    if not all_records:
                        logger.debug(f"No measurements extracted from OpenAQ for {city}")
                        return None
                    
                    df = pd.DataFrame(all_records)
                    df['lastUpdated'] = pd.to_datetime(df['lastUpdated'], errors='coerce')
                    # Don't add 'timestamp' here - it will be renamed from 'lastUpdated' in collector
                    
                    logger.success(f"OpenAQ v3: Fetched {len(df)} measurements for {city}")
                    return df
                    
                except requests.exceptions.Timeout:
                    logger.debug(f"OpenAQ timeout for {city} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return None
                        
                except requests.exceptions.RequestException as e:
                    if '429' in str(e):
                        logger.warning(f"OpenAQ rate limit reached for {city}, will use WAQI instead")
                    else:
                        logger.debug(f"OpenAQ v3 request failed for {city}: {e}")
                    return None
            
        except Exception as e:
            logger.debug(f"OpenAQ v3 error for {city}: {e}")
            return None
    
    def _get_location_measurements(self, location_id: int) -> Optional[List[Dict]]:
        """
        Get measurements for a specific location using v3 API
        
        Args:
            location_id: Location ID from OpenAQ
            
        Returns:
            List of measurement dictionaries
        """
        try:
            url = f"{self.base_url}/locations/{location_id}/latest"
            
            response = self.session.get(url, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data:
                return data['results']
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not fetch measurements for location {location_id}: {e}")
            return None
    def get_historical_measurements(self, city: str, date_from: datetime, 
                                   date_to: datetime) -> Optional[pd.DataFrame]:
        """
        Get historical air quality measurements for a city using v3 API
        (DISABLED: OpenAQ v3 historical endpoint not available yet)
        
        Args:
            city: City name
            date_from: Start date
            date_to: End date
            
        Returns:
            DataFrame with historical measurements or None if failed
        """
        # OpenAQ v3 historical endpoint not available yet (returns 404)
        logger.debug(f"OpenAQ v3 historical data not available for {city}")
        return None
    
    def get_all_cities_latest(self) -> Dict[str, pd.DataFrame]:
        """
        Get latest measurements for all monitored cities
        
        Returns:
            Dictionary mapping city names to DataFrames
        """
        results = {}
        for city in MONITORED_CITIES.keys():
            data = self.get_latest_measurements(city)
            if data is not None:
                results[city] = data
            time.sleep(1)  # Rate limiting
        
        return results
    
    def get_locations(self, city: str) -> Optional[pd.DataFrame]:
        """
        Get all monitoring locations for a city
        
        Args:
            city: City name
            
        Returns:
            DataFrame with location information
        """
        try:
            url = f"{self.base_url}/locations"
            params = {
                'city': city,
                'limit': 100
            }
            
            response = self.session.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' not in data:
                return None
            
            locations = []
            for loc in data['results']:
                locations.append({
                    'location': loc.get('name'),
                    'city': loc.get('city'),
                    'country': loc.get('country'),
                    'latitude': loc.get('coordinates', {}).get('latitude'),
                    'longitude': loc.get('coordinates', {}).get('longitude'),
                    'firstUpdated': loc.get('firstUpdated'),
                    'lastUpdated': loc.get('lastUpdated'),
                    'parameters': ','.join(loc.get('parameters', []))
                })
            
            df = pd.DataFrame(locations)
            logger.info(f"Found {len(df)} monitoring locations in {city}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching locations for {city}: {e}")
            return None
