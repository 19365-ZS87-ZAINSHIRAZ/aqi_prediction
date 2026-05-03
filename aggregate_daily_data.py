"""
Aggregate Daily Data Script
Ensures all data is properly aggregated by day for forecasting
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.mongodb_operations import MongoDBOperations
from datetime import datetime
import pandas as pd
from loguru import logger
from collections import defaultdict

def aggregate_daily_data():
    """Aggregate any hourly/multiple entries per day into single daily averages"""
    db = MongoDBOperations()
    
    logger.info("=" * 60)
    logger.info("AGGREGATING DAILY DATA")
    logger.info("=" * 60)
    
    for city in ['Islamabad', 'Rawalpindi', 'Karachi']:
        logger.info(f"\nProcessing {city}...")
        
        # Get all measurements
        all_measurements = list(db.measurements.find({'city': city}))
        
        if not all_measurements:
            logger.warning(f"  No data for {city}")
            continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_measurements)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        # Group by date and parameter, check for duplicates
        duplicates = df.groupby(['date', 'parameter']).size()
        duplicate_dates = duplicates[duplicates > 1]
        
        if len(duplicate_dates) == 0:
            logger.success(f"  ✓ No duplicates found - data is clean")
            continue
        
        logger.info(f"  Found {len(duplicate_dates)} date-parameter combinations with multiple entries")
        logger.info(f"  Aggregating to daily averages...")
        
        # Calculate daily averages
        daily_avg = df.groupby(['city', 'date', 'parameter']).agg({
            'value': 'mean',
            'latitude': 'first',
            'longitude': 'first',
            'unit': 'first',
            'location': 'first',
            'source': 'first'
        }).reset_index()
        
        # Convert date back to datetime (midnight)
        daily_avg['timestamp'] = pd.to_datetime(daily_avg['date'])
        daily_avg = daily_avg.drop('date', axis=1)
        
        # Delete old measurements for this city
        delete_result = db.measurements.delete_many({'city': city})
        logger.info(f"  Deleted {delete_result.deleted_count} old measurements")
        
        # Insert aggregated data
        records = daily_avg.to_dict('records')
        if records:
            db.measurements.insert_many(records)
            logger.success(f"  ✓ Inserted {len(records)} aggregated daily records")
    
    logger.info("\n" + "=" * 60)
    logger.success("Daily aggregation completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    aggregate_daily_data()
