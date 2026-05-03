"""
Script to fill missing days in the database
Fills gaps with interpolated/estimated data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.mongodb_operations import MongoDBOperations
from src.analysis.aqi_calculator import AQICalculator
from src.analysis.health_impact import HealthImpactAssessor
from config.settings import MONITORED_CITIES
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

def fill_missing_days():
    """Fill missing days with estimated data"""
    db = MongoDBOperations()
    aqi_calc = AQICalculator()
    health_assessor = HealthImpactAssessor()
    
    logger.info("=" * 60)
    logger.info("FILLING MISSING DAYS")
    logger.info("=" * 60)
    
    for city in MONITORED_CITIES.keys():
        logger.info(f"\nProcessing {city}...")
        
        # Get all measurement dates
        all_measurements = list(db.measurements.find(
            {'city': city},
            {'timestamp': 1}
        ).sort('timestamp', 1))
        
        if not all_measurements:
            logger.warning(f"  No data found for {city}")
            continue
        
        dates = [m['timestamp'].date() for m in all_measurements]
        start_date = min(dates)
        end_date = datetime.now().date() - timedelta(days=1)  # Up to yesterday
        
        # Find missing days
        expected_days = (end_date - start_date).days + 1
        all_expected = {start_date + timedelta(days=i) for i in range(expected_days)}
        existing = set(dates)
        missing = sorted(all_expected - existing)
        
        logger.info(f"  Date range: {start_date} to {end_date}")
        logger.info(f"  Total days: {expected_days}")
        logger.info(f"  Existing: {len(existing)}")
        logger.info(f"  Missing: {len(missing)}")
        
        if not missing:
            logger.success(f"  ✓ No missing days for {city}")
            continue
        
        logger.info(f"  Filling {len(missing)} missing days...")
        
        # Base parameters by city (monthly averages)
        base_params = {
            'pm25': {'Islamabad': 45, 'Rawalpindi': 50, 'Karachi': 65},
            'pm10': {'Islamabad': 80, 'Rawalpindi': 85, 'Karachi': 110},
            'o3': {'Islamabad': 35, 'Rawalpindi': 38, 'Karachi': 45},
            'no2': {'Islamabad': 25, 'Rawalpindi': 28, 'Karachi': 35},
            'so2': {'Islamabad': 8, 'Rawalpindi': 10, 'Karachi': 12},
            'co': {'Islamabad': 0.6, 'Rawalpindi': 0.7, 'Karachi': 0.9}
        }
        
        filled_count = 0
        for missing_date in missing:
            try:
                records = []
                
                # Seasonal adjustment
                month = missing_date.month
                if month in [11, 12, 1, 2]:  # Winter - worse air quality
                    seasonal_factor = 1.5
                elif month in [3, 4, 10]:  # Spring/Fall
                    seasonal_factor = 1.2
                else:  # Summer - better air quality
                    seasonal_factor = 0.8
                
                # Daily variation
                daily_variation = np.random.uniform(0.85, 1.15)
                
                for param, city_values in base_params.items():
                    if city not in city_values:
                        continue
                    
                    base_value = city_values[city]
                    value = base_value * seasonal_factor * daily_variation
                    value += np.random.normal(0, base_value * 0.05)
                    value = max(0, value)
                    
                    unit = 'µg/m³' if param in ['pm25', 'pm10', 'no2', 'so2', 'o3'] else 'mg/m³'
                    
                    records.append({
                        'city': city,
                        'parameter': param,
                        'value': round(value, 2),
                        'unit': unit,
                        'timestamp': datetime.combine(missing_date, datetime.min.time()),
                        'source': 'Gap-filled',
                        'location': f'{city} (Estimated)',
                        'latitude': MONITORED_CITIES[city]['lat'],
                        'longitude': MONITORED_CITIES[city]['lon']
                    })
                
                # Save measurements
                df = pd.DataFrame(records)
                db.save_measurements(df)
                
                # Calculate and save AQI
                pollutants = {}
                for record in records:
                    if record['parameter'] in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
                        pollutants[record['parameter']] = record['value']
                
                if pollutants:
                    aqi_info = aqi_calc.calculate_multi_pollutant_aqi(pollutants)
                    
                    aqi_data = {
                        'timestamp': datetime.combine(missing_date, datetime.min.time()),
                        'aqi': aqi_info.get('aqi', 0),
                        'category': aqi_info.get('category', 'Unknown'),
                        'dominant_pollutant': aqi_info.get('dominant_pollutant', 'pm25'),
                        'pollutants': pollutants
                    }
                    db.save_aqi_history(city, aqi_data)
                    
                    # Save health impact
                    if aqi_info.get('aqi'):
                        health_impact = health_assessor.assess_health_impact(city, pollutants, aqi_info['aqi'])
                        db.save_health_impact(city, health_impact)
                
                filled_count += 1
                
            except Exception as e:
                logger.error(f"    Error filling {missing_date}: {e}")
                continue
        
        logger.success(f"  ✓ Filled {filled_count} missing days for {city}")
    
    logger.info("\n" + "=" * 60)
    logger.success("Missing days filled successfully!")
    logger.info("=" * 60)

if __name__ == "__main__":
    fill_missing_days()
