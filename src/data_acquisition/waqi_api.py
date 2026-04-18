"""
WAQI (World Air Quality Index) API Integration Module
Fetches real-time air quality data from WAQI platform
"""
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import time
from loguru import logger
from config.settings import WAQI_API_KEY, WAQI_BASE_URL, API_TIMEOUT, MONITORED_CITIES


class WAQIAPI:
    """WAQI API Client for fetching air quality data"""
    
    def __init__(self):
        self.base_url = WAQI_BASE_URL
        self.api_key = WAQI_API_KEY
        self.token = WAQI_API_KEY
    
    def get_city_feed(self, city: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Get current air quality feed for a city with retry logic and geo fallback
        
        Args:
            city: City name (Lahore, Karachi, or Islamabad)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary with AQI data or None if failed
        """
        # Try city name first with retries
        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}/feed/{city}/"
                params = {'token': self.token}
                
                logger.info(f"Fetching WAQI data for {city} (attempt {attempt + 1}/{max_retries})")
                response = requests.get(url, params=params, timeout=API_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok':
                    logger.success(f"Successfully fetched WAQI data for {city}")
                    return data.get('data')
                else:
                    logger.warning(f"WAQI API returned status: {data.get('status')} for {city}")
                    
            except requests.exceptions.Timeout as e:
                logger.warning(f"WAQI API timeout for {city} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"WAQI API request failed for {city}: {e}")
                break
            except Exception as e:
                logger.error(f"Error processing WAQI data for {city}: {e}")
                break
        
        # Fallback to geo coordinates if city name fails
        logger.info(f"Trying geo-coordinate fallback for {city}")
        city_info = MONITORED_CITIES.get(city)
        if city_info:
            try:
                geo_data = self.get_geo_feed(city_info['lat'], city_info['lon'])
                if geo_data:
                    logger.success(f"Successfully fetched WAQI data for {city} using coordinates")
                    return geo_data
            except Exception as e:
                logger.error(f"Geo fallback also failed for {city}: {e}")
        
        return None
    
    def get_geo_feed(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get air quality data by geographic coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with AQI data or None if failed
        """
        try:
            url = f"{self.base_url}/feed/geo:{lat};{lon}/"
            params = {'token': self.token}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                return None
            
            return data.get('data')
            
        except Exception as e:
            logger.error(f"Error fetching geo feed for ({lat}, {lon}): {e}")
            return None
    
    def parse_city_data(self, city: str, data: Dict) -> pd.DataFrame:
        """
        Parse WAQI city feed data into structured DataFrame
        
        Args:
            city: City name
            data: Raw API response data
            
        Returns:
            DataFrame with parsed measurements
        """
        try:
            records = []
            
            # Overall AQI
            aqi = data.get('aqi', None)
            timestamp = data.get('time', {}).get('s', datetime.now().isoformat())
            
            # Individual pollutants
            iaqi = data.get('iaqi', {})
            
            for param, value_dict in iaqi.items():
                if isinstance(value_dict, dict) and 'v' in value_dict:
                    records.append({
                        'city': city,
                        'parameter': param,
                        'value': value_dict['v'],
                        'aqi': aqi,
                        'timestamp': timestamp,
                        'station': data.get('city', {}).get('name'),
                        'latitude': data.get('city', {}).get('geo', [None, None])[0],
                        'longitude': data.get('city', {}).get('geo', [None, None])[1]
                    })
            
            # Add dominant pollutant
            dominant = data.get('dominentpol', 'unknown')
            
            df = pd.DataFrame(records)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['dominant_pollutant'] = dominant
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing WAQI data for {city}: {e}")
            return pd.DataFrame()
    
    def get_all_cities_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get current air quality data for all monitored cities
        
        Returns:
            Dictionary mapping city names to DataFrames
        """
        results = {}
        
        for city in MONITORED_CITIES.keys():
            data = self.get_city_feed(city)
            if data:
                df = self.parse_city_data(city, data)
                if not df.empty:
                    results[city] = df
            time.sleep(1)  # Rate limiting
        
        return results
    
    def get_station_details(self, city: str) -> Optional[Dict]:
        """
        Get detailed information about monitoring station
        
        Args:
            city: City name
            
        Returns:
            Dictionary with station details
        """
        try:
            data = self.get_city_feed(city)
            if not data:
                return None
            
            station_info = {
                'name': data.get('city', {}).get('name'),
                'url': data.get('city', {}).get('url'),
                'location': data.get('city', {}).get('geo'),
                'attributions': data.get('attributions', []),
                'forecast': data.get('forecast', {}),
                'time': data.get('time', {})
            }
            
            return station_info
            
        except Exception as e:
            logger.error(f"Error getting station details for {city}: {e}")
            return None
    
    def search_stations(self, keyword: str) -> Optional[List[Dict]]:
        """
        Search for monitoring stations by keyword
        
        Args:
            keyword: Search keyword (city name, etc.)
            
        Returns:
            List of matching stations
        """
        try:
            url = f"{self.base_url}/search/"
            params = {
                'token': self.token,
                'keyword': keyword
            }
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                return None
            
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Error searching stations for '{keyword}': {e}")
            return None
