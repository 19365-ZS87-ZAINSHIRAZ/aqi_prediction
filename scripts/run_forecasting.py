"""
Forecasting Script
Generates air quality forecasts for all cities
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_acquisition.collector import DataCollector
from src.forecasting.prophet_forecaster import ProphetForecaster
from src.database.operations import DatabaseOperations
from config.settings import MONITORED_CITIES, FORECAST_DAYS
from loguru import logger

def main():
    """Generate forecasts for all cities"""
    logger.info("=" * 60)
    logger.info("Air Quality Forecasting")
    logger.info("=" * 60)
    
    collector = DataCollector()
    forecaster = ProphetForecaster()
    db_ops = DatabaseOperations()
    
    for city in MONITORED_CITIES.keys():
        logger.info(f"\n Processing {city}...")
        
        # Get historical data
        logger.info(f"  Fetching historical data...")
        historical_data = collector.collect_historical_data(city, days_back=60)
        
        if historical_data is None or historical_data.empty:
            logger.warning(f"  No historical data available for {city}")
            continue
        
        logger.info(f"  Found {len(historical_data)} historical records")
        
        # Generate forecasts
        logger.info(f"  Generating {FORECAST_DAYS}-day forecasts...")
        forecasts = forecaster.forecast_all_pollutants(city, historical_data, FORECAST_DAYS)
        
        if not forecasts:
            logger.warning(f"  Unable to generate forecasts for {city}")
            continue
        
        # Save forecasts to database
        total_saved = 0
        for param, forecast_df in forecasts.items():
            saved = db_ops.save_forecast(city, forecast_df, 'prophet')
            total_saved += saved
            logger.info(f"  ✓ {param.upper()}: {len(forecast_df)} days forecasted")
        
        logger.success(f"  Total forecast records saved: {total_saved}")
    
    logger.info("\n" + "=" * 60)
    logger.success("Forecasting completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
