"""
Quick script to check MongoDB data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_operations import MongoDBOperations
from loguru import logger

def main():
    """Check what data we have in MongoDB"""
    logger.info("Checking MongoDB data...")
    
    db_ops = MongoDBOperations()
    
    # Check measurements
    measurements_count = db_ops.measurements.count_documents({})
    logger.info(f"Total measurements: {measurements_count}")
    
    # Check by city
    for city in ['Islamabad', 'Rawalpindi', 'Karachi']:
        city_count = db_ops.measurements.count_documents({'city': city})
        aqi_count = db_ops.aqi_history.count_documents({'city': city})
        logger.info(f"{city}: {city_count} measurements, {aqi_count} AQI records")
    
    # Check date range
    oldest = db_ops.measurements.find_one(sort=[('timestamp', 1)])
    newest = db_ops.measurements.find_one(sort=[('timestamp', -1)])
    
    if oldest and newest:
        logger.info(f"Date range: {oldest['timestamp']} to {newest['timestamp']}")
    
    logger.success("✓ Data check complete!")

if __name__ == "__main__":
    main()
