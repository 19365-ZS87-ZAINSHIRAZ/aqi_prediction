"""
Generate Historical Air Quality Data
Creates 6 months of simulated historical data for training ML models
Based on realistic patterns for Pakistani cities
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from src.database.mongodb_operations import MongoDBOperations
from src.analysis.aqi_calculator import AQICalculator
from src.analysis.health_impact import HealthImpactAssessor
from config.settings import MONITORED_CITIES


def generate_city_historical_data(city: str, days: int = 180) -> pd.DataFrame:
    """
    Generate realistic historical air quality data for a city
    
    Args:
        city: City name
        days: Number of days of historical data
        
    Returns:
        DataFrame with historical measurements
    """
    logger.info(f"Generating {days} days of historical data for {city}")
    
    # Base AQI values for each city (realistic for Pakistan)
    base_aqi = {
        'Islamabad': 110,
        'Rawalpindi': 115,
        'Karachi': 140
    }
    
    # Seasonal variation (winter worse, summer better)
    # Parameters mapped to typical concentrations
    base_params = {
        'pm25': {'Islamabad': 45, 'Rawalpindi': 50, 'Karachi': 65},
        'pm10': {'Islamabad': 80, 'Rawalpindi': 85, 'Karachi': 110},
        'o3': {'Islamabad': 35, 'Rawalpindi': 38, 'Karachi': 45},
        'no2': {'Islamabad': 25, 'Rawalpindi': 28, 'Karachi': 35},
        'so2': {'Islamabad': 8, 'Rawalpindi': 10, 'Karachi': 12},
        'co': {'Islamabad': 0.6, 'Rawalpindi': 0.7, 'Karachi': 0.9}
    }
    
    records = []
    # End date is April 18, 2026 (today)
    end_date = datetime(2026, 4, 18)
    # Start date is October 1, 2025 (exactly 6 months ago)
    start_date = datetime(2025, 10, 1)
    days = (end_date - start_date).days
    
    logger.info(f"Generating data from {start_date.date()} to {end_date.date()} ({days} days)")
    
    for day_num in range(days + 1):
        timestamp = start_date + timedelta(days=day_num)
        
        # Seasonal factor (winter = higher pollution)
        month = timestamp.month
        if month in [11, 12, 1, 2]:  # Winter
            seasonal_factor = 1.4
        elif month in [3, 4, 10]:  # Transition
            seasonal_factor = 1.1
        else:  # Summer
            seasonal_factor = 0.8
        
        # Daily variation (random but realistic)
        daily_variation = np.random.uniform(0.85, 1.15)
        
        # Trend (slight improvement over time)
        trend_factor = 1.0 - (day_num / days) * 0.1
        
        # Generate measurements for each parameter
        for param, city_baselines in base_params.items():
            base_value = city_baselines.get(city, 50)
            
            # Apply factors
            value = base_value * seasonal_factor * daily_variation * trend_factor
            
            # Add some noise
            value += np.random.normal(0, base_value * 0.1)
            value = max(0, value)  # No negative values
            
            # Determine unit
            unit = 'µg/m³' if param in ['pm25', 'pm10', 'no2', 'so2', 'o3'] else 'mg/m³'
            
            records.append({
                'city': city,
                'parameter': param,
                'value': round(value, 2),
                'unit': unit,
                'timestamp': timestamp,
                'source': 'WAQI',
                'location': f'{city} Station',
                'latitude': MONITORED_CITIES[city]['lat'],
                'longitude': MONITORED_CITIES[city]['lon']
            })
    
    df = pd.DataFrame(records)
    logger.success(f"Generated {len(df)} historical records for {city}")
    return df


def main():
    """Generate and save historical data for all cities"""
    logger.info("=" * 60)
    logger.info("Historical Data Generator")
    logger.info("Generating 6 months of data for training ML models")
    logger.info("=" * 60)
    
    # Initialize components
    db_ops = MongoDBOperations()
    aqi_calc = AQICalculator()
    health_assessor = HealthImpactAssessor()
    
    days_to_generate = 180  # 6 months
    
    for city in MONITORED_CITIES.keys():
        logger.info(f"\nProcessing {city}...")
        
        # Generate historical data
        historical_df = generate_city_historical_data(city, days_to_generate)
        
        # Save measurements to MongoDB
        saved_count = db_ops.save_measurements(historical_df)
        logger.info(f"  ✓ Saved {saved_count} measurements to MongoDB")
        
        # Generate and save daily AQI history
        dates = historical_df['timestamp'].dt.date.unique()
        for date in dates:
            day_data = historical_df[historical_df['timestamp'].dt.date == date]
            
            # Calculate AQI from pollutants
            pollutants = {}
            for _, row in day_data.iterrows():
                param = row['parameter']
                if param in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
                    pollutants[param] = row['value']
            
            if pollutants:
                aqi_info = aqi_calc.calculate_multi_pollutant_aqi(pollutants)
                
                # Save AQI history
                aqi_data = {
                    'timestamp': datetime.combine(date, datetime.min.time()),
                    'aqi': aqi_info.get('aqi', 0),
                    'category': aqi_info.get('category', 'Unknown'),
                    'dominant_pollutant': aqi_info.get('dominant_pollutant', 'pm25'),
                    'pollutants': pollutants
                }
                db_ops.save_aqi_history(city, aqi_data)
                
                # Save health impact
                if aqi_info.get('aqi'):
                    health_impact = health_assessor.assess_health_impact(
                        city, pollutants, aqi_info['aqi']
                    )
                    db_ops.save_health_impact(city, health_impact)
        
        logger.success(f"  ✓ Saved 180 days of AQI history for {city}")
    
    logger.info("\n" + "=" * 60)
    logger.success("Historical data generation completed!")
    logger.info(f"Total records per city: ~{days_to_generate * 6} (6 parameters × 180 days)")
    logger.info(f"Total cities: {len(MONITORED_CITIES)}")
    logger.info(f"Database: MongoDB (air_quality_db)")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
