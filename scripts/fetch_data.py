"""
Data Fetching Script
Fetches latest air quality data from all sources and saves to database
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_acquisition.collector import DataCollector
from src.analysis.aqi_calculator import AQICalculator
from src.analysis.health_impact import HealthImpactAssessor
from src.database.operations import DatabaseOperations
from config.settings import MONITORED_CITIES
from loguru import logger

def main():
    """Fetch and save latest air quality data"""
    logger.info("=" * 60)
    logger.info("Air Quality Data Fetcher")
    logger.info("=" * 60)
    
    # Initialize components
    collector = DataCollector()
    aqi_calc = AQICalculator()
    health_assessor = HealthImpactAssessor()
    db_ops = DatabaseOperations()
    
    # Fetch data for all cities
    logger.info(f"Fetching data for {len(MONITORED_CITIES)} cities...")
    all_data = collector.collect_current_data(use_cache=False)
    
    if not all_data:
        logger.error("No data fetched from any source!")
        return
    
    # Process and save data for each city
    for city, df in all_data.items():
        logger.info(f"\nProcessing {city}...")
        
        if df.empty:
            logger.warning(f"  No data available for {city}")
            continue
        
        # Save measurements to database
        saved_count = db_ops.save_measurements(df)
        logger.info(f"  ✓ Saved {saved_count} measurements")
        
        # Calculate and save AQI
        aqi_info = aqi_calc.get_city_current_aqi(df)
        
        aqi_data = {
            'aqi': aqi_info.get('aqi'),
            'category': aqi_info.get('category'),
            'dominant_pollutant': aqi_info.get('dominant_pollutant'),
            'pm25': aqi_info.get('pm25'),
            'pm10': aqi_info.get('pm10'),
            'no2': aqi_info.get('no2'),
            'so2': aqi_info.get('so2'),
            'co': aqi_info.get('co'),
            'o3': aqi_info.get('o3'),
            'timestamp': datetime.now()
        }
        
        db_ops.save_aqi_history(city, aqi_data)
        logger.info(f"  ✓ AQI: {aqi_info.get('aqi')} ({aqi_info.get('category')})")
        
        # Calculate and save health impact
        pollutants = {k: v for k, v in aqi_info.items() if k in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] and v is not None}
        
        if pollutants and aqi_info.get('aqi'):
            health_impact = health_assessor.assess_health_impact(
                city,
                pollutants,
                aqi_info['aqi']
            )
            
            db_ops.save_health_impact(city, health_impact)
            logger.info(f"  ✓ Health Risk: {health_impact.get('risk_category')}")
    
    logger.info("\n" + "=" * 60)
    logger.success("Data fetch completed successfully!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
