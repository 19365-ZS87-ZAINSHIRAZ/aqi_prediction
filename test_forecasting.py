"""Quick test for forecasting"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.forecasting.prophet_forecaster import ProphetForecaster
from src.database.mongodb_operations import MongoDBOperations
from datetime import datetime, timedelta
from loguru import logger

def test_forecasting():
    """Test forecasting functionality"""
    logger.info("=" * 60)
    logger.info("TESTING FORECASTING")
    logger.info("=" * 60)
    
    db = MongoDBOperations()
    forecaster = ProphetForecaster()
    
    # Test for Islamabad
    city = 'Islamabad'
    logger.info(f"\nTesting forecasting for {city}...")
    
    # Get historical data (last 60 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    historical_data = db.get_measurements(city, start_date, end_date)
    
    if historical_data.empty:
        logger.error("No historical data found!")
        return
    
    logger.info(f"Retrieved {len(historical_data)} historical records")
    
    # Test forecasting for PM2.5
    parameter = 'pm25'
    logger.info(f"\nForecasting {parameter}...")
    
    try:
        forecast = forecaster.forecast_pollutant(
            historical_data=historical_data,
            parameter=parameter,
            days_ahead=7
        )
        
        if forecast is not None and not forecast.empty:
            logger.success(f"✓ Forecast generated successfully!")
            logger.info(f"  Forecast dates: {forecast['date'].min()} to {forecast['date'].max()}")
            logger.info(f"  Number of forecast days: {len(forecast)}")
            logger.info(f"\n  Forecast values:")
            for _, row in forecast.head(7).iterrows():
                logger.info(f"    {row['date'].date()}: {row['predicted_value']:.2f} µg/m³")
        else:
            logger.error("Forecast generation failed!")
            
    except Exception as e:
        logger.error(f"Error during forecasting: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "=" * 60)
    logger.info("FORECASTING TEST COMPLETE")
    logger.info("=" * 60)

if __name__ == "__main__":
    test_forecasting()
