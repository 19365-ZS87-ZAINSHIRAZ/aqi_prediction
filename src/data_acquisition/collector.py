"""
Unified Data Collector
Combines data from multiple sources (OpenAQ, WAQI)
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from loguru import logger
import json
from pathlib import Path

from .openaq_api import OpenAQAPI
from .waqi_api import WAQIAPI
from config.settings import MONITORED_CITIES, RAW_DATA_DIR, CACHE_DIR, CACHE_EXPIRY, USE_OPENAQ, USE_WAQI


class DataCollector:
    """Unified data collector from multiple air quality sources"""
    
    def __init__(self):
        self.openaq = OpenAQAPI()
        self.waqi = WAQIAPI()
        self.cache_dir = CACHE_DIR
    
    def collect_current_data(self, use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Collect current air quality data from all sources for all cities
        V1.1: Using both OpenAQ v3 and WAQI for redundancy
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary mapping city names to combined DataFrames
        """
        combined_data = {}
        
        for city in MONITORED_CITIES.keys():
            logger.info(f"Collecting data for {city}")
            
            # Check cache first
            if use_cache:
                cached_data = self._load_from_cache(city)
                if cached_data is not None:
                    logger.info(f"Using cached data for {city}")
                    combined_data[city] = cached_data
                    continue
            
            # Collect from OpenAQ v3 (if enabled)
            openaq_data = None
            if USE_OPENAQ:
                openaq_data = self.openaq.get_latest_measurements(city)
            
            # Collect from WAQI (primary source)
            waqi_raw = None
            waqi_data = None
            if USE_WAQI:
                waqi_raw = self.waqi.get_city_feed(city)
                if waqi_raw:
                    waqi_data = self.waqi.parse_city_data(city, waqi_raw)
            
            # Combine data sources
            city_data = self._combine_sources(city, openaq_data, waqi_data)
            
            if city_data is not None and not city_data.empty:
                combined_data[city] = city_data
                # Cache the data
                self._save_to_cache(city, city_data)
            else:
                logger.warning(f"No data collected for {city}")
        
        return combined_data
    
    def collect_historical_data(self, city: str, days_back: int = 30) -> Optional[pd.DataFrame]:
        """
        Collect historical air quality data from MongoDB
        
        Args:
            city: City name
            days_back: Number of days to look back
            
        Returns:
            DataFrame with historical data from database
        """
        from src.database.mongodb_operations import MongoDBOperations
        
        date_to = datetime.now()
        date_from = date_to - timedelta(days=days_back)
        
        logger.info(f"Fetching {days_back} days of historical data from MongoDB for {city}")
        
        try:
            # Get data from MongoDB
            db_ops = MongoDBOperations()
            historical_data = db_ops.get_measurements(
                city=city,
                start_date=date_from,
                end_date=date_to
            )
            
            if historical_data is not None and not historical_data.empty:
                logger.success(f"Retrieved {len(historical_data)} historical records for {city}")
                return historical_data
            else:
                logger.warning(f"No historical data found in MongoDB for {city}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching historical data for {city}: {e}")
            return None
    
    def _combine_sources(self, city: str, openaq_df: Optional[pd.DataFrame], 
                         waqi_df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """
        Combine data from multiple sources into unified format
        
        Args:
            city: City name
            openaq_df: OpenAQ data
            waqi_df: WAQI data
            
        Returns:
            Combined DataFrame
        """
        dfs_to_combine = []
        
        # Standardize OpenAQ data
        if openaq_df is not None and not openaq_df.empty:
            openaq_std = openaq_df.copy()
            openaq_std['source'] = 'OpenAQ'
            openaq_std = openaq_std.rename(columns={'lastUpdated': 'timestamp'})
            # Remove duplicate columns if any
            openaq_std = openaq_std.loc[:, ~openaq_std.columns.duplicated()]
            openaq_std = openaq_std.reset_index(drop=True)
            dfs_to_combine.append(openaq_std)
        
        # Standardize WAQI data
        if waqi_df is not None and not waqi_df.empty:
            waqi_std = waqi_df.copy()
            waqi_std['source'] = 'WAQI'
            waqi_std['location'] = waqi_std.get('station', city)
            waqi_std['unit'] = 'AQI'
            # Remove duplicate columns if any
            waqi_std = waqi_std.loc[:, ~waqi_std.columns.duplicated()]
            waqi_std = waqi_std.reset_index(drop=True)
            dfs_to_combine.append(waqi_std)
        
        if not dfs_to_combine:
            return None
        
        # Combine all sources
        try:
            combined = pd.concat(dfs_to_combine, ignore_index=True, sort=False)
            combined['city'] = city
            combined['collected_at'] = datetime.now()
            logger.success(f"Combined {len(combined)} records for {city} from {len(dfs_to_combine)} sources")
            return combined
        except Exception as e:
            logger.error(f"Error concatenating DataFrames for {city}: {e}")
            return None
    
    def _save_to_cache(self, city: str, data: pd.DataFrame):
        """Save data to cache"""
        try:
            cache_file = self.cache_dir / f"{city}_cache.csv"
            data.to_csv(cache_file, index=False)
            
            # Save metadata
            metadata = {
                'city': city,
                'cached_at': datetime.now().isoformat(),
                'records': len(data),
                'expires_at': (datetime.now() + timedelta(seconds=CACHE_EXPIRY)).isoformat()
            }
            
            meta_file = self.cache_dir / f"{city}_meta.json"
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"Cached data for {city}")
            
        except Exception as e:
            logger.error(f"Error caching data for {city}: {e}")
    
    def _load_from_cache(self, city: str) -> Optional[pd.DataFrame]:
        """Load data from cache if valid"""
        try:
            cache_file = self.cache_dir / f"{city}_cache.csv"
            meta_file = self.cache_dir / f"{city}_meta.json"
            
            if not cache_file.exists() or not meta_file.exists():
                return None
            
            # Check if cache is expired
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                logger.debug(f"Cache expired for {city}")
                return None
            
            # Load cached data
            data = pd.read_csv(cache_file)
            data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce', format='mixed')
            data['collected_at'] = pd.to_datetime(data['collected_at'], errors='coerce', format='mixed')
            
            return data
            
        except Exception as e:
            logger.debug(f"Cache not usable for {city}: {e}")
            return None
    
    def get_all_monitoring_locations(self) -> pd.DataFrame:
        """
        Get all monitoring station locations for all cities
        
        Returns:
            DataFrame with all locations
        """
        all_locations = []
        
        for city in MONITORED_CITIES.keys():
            locations = self.openaq.get_locations(city)
            if locations is not None:
                all_locations.append(locations)
        
        if all_locations:
            return pd.concat(all_locations, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def save_current_snapshot(self):
        """Save current data snapshot to raw data directory"""
        data = self.collect_current_data(use_cache=False)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for city, df in data.items():
            filename = f"{city}_snapshot_{timestamp}.csv"
            filepath = RAW_DATA_DIR / filename
            df.to_csv(filepath, index=False)
            logger.info(f"Saved snapshot for {city} to {filepath}")
        
        return data
