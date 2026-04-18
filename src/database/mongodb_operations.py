"""
MongoDB Database Operations Module
Replaces PostgreSQL for MongoDB-only implementation
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pymongo import MongoClient, ASCENDING, DESCENDING
from loguru import logger
from config.settings import MONGODB_URI, MONGODB_DB


class MongoDBOperations:
    """MongoDB operations for air quality data"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[MONGODB_DB]
            
            # Collections
            self.measurements = self.db['air_quality_measurements']
            self.aqi_history = self.db['aqi_history']
            self.health_impacts = self.db['health_impacts']
            self.forecasts = self.db['forecasts']
            self.stations = self.db['monitoring_stations']
            
            # Create indexes for better query performance
            self._create_indexes()
            
            logger.success("MongoDB connection established")
            
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for collections"""
        try:
            # Air Quality Measurements indexes
            self.measurements.create_index([('city', ASCENDING), ('timestamp', DESCENDING)])
            self.measurements.create_index([('city', ASCENDING), ('parameter', ASCENDING)])
            self.measurements.create_index([('timestamp', DESCENDING)])
            
            # AQI History indexes
            self.aqi_history.create_index([('city', ASCENDING), ('timestamp', DESCENDING)])
            
            # Health Impacts indexes
            self.health_impacts.create_index([('city', ASCENDING), ('date', DESCENDING)])
            
            # Forecasts indexes
            self.forecasts.create_index([('city', ASCENDING), ('forecast_date', ASCENDING)])
            
            # Stations indexes
            self.stations.create_index([('station_id', ASCENDING)], unique=True)
            self.stations.create_index([('city', ASCENDING)])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def __del__(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
    
    # === Air Quality Measurements ===
    
    def save_measurements(self, df: pd.DataFrame) -> int:
        """
        Save air quality measurements to database
        
        Args:
            df: DataFrame with measurements
            
        Returns:
            Number of records saved
        """
        try:
            if df.empty:
                return 0
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Ensure datetime objects are properly formatted
            for record in records:
                if 'timestamp' in record and isinstance(record['timestamp'], str):
                    record['timestamp'] = pd.to_datetime(record['timestamp'])
                if 'collected_at' not in record:
                    record['collected_at'] = datetime.now()
            
            # Insert into MongoDB
            result = self.measurements.insert_many(records)
            
            logger.success(f"Saved {len(result.inserted_ids)} measurements to MongoDB")
            return len(result.inserted_ids)
            
        except Exception as e:
            logger.error(f"Error saving measurements: {e}")
            return 0
    
    def get_latest_measurements(self, city: str, hours: int = 24) -> pd.DataFrame:
        """
        Get latest measurements for a city
        
        Args:
            city: City name
            hours: Number of hours to look back
            
        Returns:
            DataFrame with measurements
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = {
                'city': city,
                'timestamp': {'$gte': cutoff_time}
            }
            
            cursor = self.measurements.find(query).sort('timestamp', DESCENDING)
            
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Retrieved {len(df)} measurements for {city}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving measurements: {e}")
            return pd.DataFrame()
    
    def get_measurements(self, city: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Get measurements for a city within a date range
        
        Args:
            city: City name
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with measurements
        """
        try:
            query = {
                'city': city,
                'timestamp': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            cursor = self.measurements.find(query).sort('timestamp', 1)
            
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            logger.info(f"Retrieved {len(df)} measurements for {city} from {start_date.date()} to {end_date.date()}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving measurements: {e}")
            return pd.DataFrame()
    
    def get_current_aqi(self, city: str) -> Optional[Dict]:
        """
        Get TODAY's AQI for a city (not historical data)
        
        Args:
            city: City name
            
        Returns:
            AQI data dictionary for today or None
        """
        try:
            # Get today's date range (start of day to end of day)
            from datetime import datetime, timedelta
            
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # Find most recent AQI from TODAY only
            result = self.aqi_history.find_one(
                {
                    'city': city,
                    'timestamp': {
                        '$gte': today_start,
                        '$lt': today_end
                    }
                },
                sort=[('timestamp', DESCENDING)]
            )
            
            if result:
                result.pop('_id', None)
                return result
            
            # No data for today - return None to trigger fresh fetch
            return None
            
        except Exception as e:
            logger.error(f"Error getting current AQI: {e}")
            return None
    
    # === AQI History ===
    
    def save_aqi_history(self, city: str, aqi_data: Dict) -> bool:
        """
        Save AQI history record
        
        Args:
            city: City name
            aqi_data: Dictionary with AQI data
            
        Returns:
            Success status
        """
        try:
            # Ensure city is in the data
            aqi_data['city'] = city
            
            if 'timestamp' not in aqi_data:
                aqi_data['timestamp'] = datetime.now()
            
            self.aqi_history.insert_one(aqi_data)
            logger.success(f"Saved AQI history for {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving AQI history: {e}")
            return False
    
    def get_aqi_trends(self, city: str, days: int = 30) -> pd.DataFrame:
        """
        Get AQI trends for a city
        
        Args:
            city: City name
            days: Number of days to look back
            
        Returns:
            DataFrame with AQI history
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = {
                'city': city,
                'timestamp': {'$gte': cutoff_date}
            }
            
            cursor = self.aqi_history.find(query).sort('timestamp', ASCENDING)
            
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting AQI trends: {e}")
            return pd.DataFrame()
    
    # === Health Impact ===
    
    def save_health_impact(self, city: str, impact_data: Dict) -> bool:
        """
        Save health impact assessment
        
        Args:
            city: City name
            impact_data: Dictionary with health impact data
            
        Returns:
            Success status
        """
        try:
            #Ensure city is in the data
            impact_data['city'] = city
            
            if 'created_at' not in impact_data:
                impact_data['created_at'] = datetime.now()
            
            self.health_impacts.insert_one(impact_data)
            logger.success(f"Saved health impact for {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving health impact: {e}")
            return False
    
    def get_latest_health_impact(self, city: str) -> Optional[Dict]:
        """
        Get latest health impact assessment
        
        Args:
            city: City name
            
        Returns:
            Health impact data or None
        """
        try:
            result = self.health_impacts.find_one(
                {'city': city},
                sort=[('date', DESCENDING)]
            )
            
            if result:
                result.pop('_id', None)
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting health impact: {e}")
            return None
    
    # === Forecasts ===
    
    def save_forecast(self, forecast_data: Dict) -> bool:
        """
        Save forecast data
        
        Args:
            forecast_data: Dictionary with forecast data
            
        Returns:
            Success status
        """
        try:
            if 'created_at' not in forecast_data:
                forecast_data['created_at'] = datetime.now()
            
            self.forecasts.insert_one(forecast_data)
            return True
            
        except Exception as e:
            logger.error(f"Error saving forecast: {e}")
            return False
    
    def save_forecasts_bulk(self, forecasts: List[Dict]) -> int:
        """
        Save multiple forecasts
        
        Args:
            forecasts: List of forecast dictionaries
            
        Returns:
            Number of forecasts saved
        """
        try:
            if not forecasts:
                return 0
            
            # Add created_at to all forecasts
            for forecast in forecasts:
                if 'created_at' not in forecast:
                    forecast['created_at'] = datetime.now()
            
            result = self.forecasts.insert_many(forecasts)
            logger.success(f"Saved {len(result.inserted_ids)} forecasts")
            return len(result.inserted_ids)
            
        except Exception as e:
            logger.error(f"Error saving forecasts: {e}")
            return 0
    
    def get_forecasts(self, city: str, parameter: str, days: int = 7) -> pd.DataFrame:
        """
        Get forecasts for a city and parameter
        
        Args:
            city: City name
            parameter: Pollutant parameter
            days: Number of days ahead
            
        Returns:
            DataFrame with forecasts
        """
        try:
            end_date = datetime.now() + timedelta(days=days)
            
            query = {
                'city': city,
                'parameter': parameter,
                'forecast_date': {
                    '$gte': datetime.now(),
                    '$lte': end_date
                }
            }
            
            cursor = self.forecasts.find(query).sort('forecast_date', ASCENDING)
            
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting forecasts: {e}")
            return pd.DataFrame()
    
    # === Monitoring Stations ===
    
    def save_station(self, station_data: Dict) -> bool:
        """
        Save or update monitoring station
        
        Args:
            station_data: Dictionary with station data
            
        Returns:
            Success status
        """
        try:
            station_data['last_updated'] = datetime.now()
            
            # Upsert based on station_id
            self.stations.update_one(
                {'station_id': station_data['station_id']},
                {'$set': station_data},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving station: {e}")
            return False
    
    def get_active_stations(self, city: Optional[str] = None) -> pd.DataFrame:
        """
        Get active monitoring stations
        
        Args:
            city: Optional city filter
            
        Returns:
            DataFrame with station data
        """
        try:
            query = {'is_active': True}
            if city:
                query['city'] = city
            
            cursor = self.stations.find(query)
            
            df = pd.DataFrame(list(cursor))
            
            if not df.empty and '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting stations: {e}")
            return pd.DataFrame()
    
    # === Utility Methods ===
    
    def get_statistics(self, city: str, parameter: str, days: int = 30) -> Dict:
        """
        Get statistical summary for a parameter
        
        Args:
            city: City name
            parameter: Pollutant parameter
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    '$match': {
                        'city': city,
                        'parameter': parameter,
                        'timestamp': {'$gte': cutoff_date}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'avg': {'$avg': '$value'},
                        'min': {'$min': '$value'},
                        'max': {'$max': '$value'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            result = list(self.measurements.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id', None)
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def clear_old_data(self, days: int = 90) -> int:
        """
        Remove data older than specified days
        
        Args:
            days: Keep data newer than this many days
            
        Returns:
            Number of documents deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old measurements
            result = self.measurements.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} old measurement records")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing old data: {e}")
            return 0


# Alias for backward compatibility
DatabaseOperations = MongoDBOperations
