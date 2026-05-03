"""
Verify current AQI calculation for Islamabad
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.mongodb_operations import MongoDBOperations
from src.analysis.aqi_calculator import AQICalculator
from src.data_acquisition.collector import DataCollector
from datetime import datetime

def verify_aqi():
    print("=" * 70)
    print("CURRENT AQI VERIFICATION FOR ISLAMABAD")
    print("=" * 70)
    
    # Method 1: Get from database (today's record)
    print("\n📊 Method 1: From Database (Today's Record)")
    print("-" * 70)
    db = MongoDBOperations()
    current_aqi = db.get_current_aqi('Islamabad')
    
    if current_aqi:
        print(f"AQI: {current_aqi.get('aqi', 'N/A')}")
        print(f"Category: {current_aqi.get('category', 'N/A')}")
        print(f"Dominant Pollutant: {current_aqi.get('dominant_pollutant', 'N/A')}")
        print(f"Timestamp: {current_aqi.get('timestamp', 'N/A')}")
        print(f"\nPollutant Values:")
        for pollutant in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            val = current_aqi.get(pollutant)
            if val:
                print(f"  {pollutant.upper()}: {val}")
    else:
        print("No AQI record for today found in database")
    
    # Method 2: Fetch fresh from API
    print("\n\n🌐 Method 2: Fresh Data from WAQI API")
    print("-" * 70)
    collector = DataCollector()
    fresh_data = collector.collect_current_data(use_cache=False)
    
    if 'Islamabad' in fresh_data:
        df = fresh_data['Islamabad']
        print(f"Total measurements received: {len(df)}")
        print(f"\nParameters available: {df['parameter'].unique().tolist()}")
        
        # Calculate AQI
        calc = AQICalculator()
        aqi_info = calc.get_city_current_aqi(df)
        
        print(f"\n✅ CALCULATED AQI:")
        print(f"  Overall AQI: {aqi_info.get('aqi', 'N/A')}")
        print(f"  Category: {aqi_info.get('category', 'N/A')}")
        print(f"  Dominant Pollutant: {aqi_info.get('dominant_pollutant', 'N/A')}")
        
        print(f"\n📈 Individual Pollutant Concentrations & AQIs:")
        for pollutant in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            if pollutant in aqi_info:
                concentration = aqi_info[pollutant]
                individual_aqi = calc.calculate_aqi(pollutant, concentration)
                print(f"  {pollutant.upper():6s}: {concentration:7.2f} → AQI {individual_aqi}")
    else:
        print("Failed to fetch fresh data from API")
    
    # Method 3: Manual calculation example
    print("\n\n🧮 Method 3: Manual Calculation Example")
    print("-" * 70)
    print("EPA Breakpoints for PM2.5 (Moderate range):")
    print("  Concentration: 12.1 - 35.4 µg/m³")
    print("  AQI Range: 51 - 100")
    print("\nFormula:")
    print("  AQI = ((100-51)/(35.4-12.1)) × (C-12.1) + 51")
    print("\nExamples:")
    for pm25 in [15, 21, 25, 30, 35]:
        aqi = calc.calculate_aqi('pm25', pm25)
        category = calc.get_aqi_category(aqi)
        print(f"  PM2.5 = {pm25} µg/m³  →  AQI = {aqi}  ({category['name']})")
    
    print("\n" + "=" * 70)
    print("✅ All calculations use official EPA standard breakpoints!")
    print("=" * 70)

if __name__ == "__main__":
    verify_aqi()
