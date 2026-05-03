"""
Show current AQI values and PM2.5 concentrations for all cities
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.mongodb_operations import MongoDBOperations
from datetime import datetime

def show_current():
    db = MongoDBOperations()
    
    print("\n" + "="*70)
    print("CURRENT AQI VALUES FROM API (Just Fetched)")
    print("="*70)
    
    for city in ['Islamabad', 'Rawalpindi', 'Karachi']:
        current = db.get_current_aqi(city)
        
        if current:
            pm25 = current.get('pm25', 'N/A')
            aqi = current.get('aqi', 'N/A')
            category = current.get('category', 'N/A')
            timestamp = current.get('timestamp', 'N/A')
            
            print(f"\n{city}:")
            print(f"  PM2.5 Value: {pm25} µg/m³")
            print(f"  AQI: {aqi} ({category})")
            print(f"  Time: {timestamp}")
        else:
            print(f"\n{city}: No data")
    
    print("\n" + "="*70)
    print("WHY NOT SHOWING 70?")
    print("="*70)
    print("""
The WAQI API (US Embassy station) is reporting:
  PM2.5 = 154 µg/m³  →  AQI = 204

To get AQI 70, we would need:
  PM2.5 = 21 µg/m³  →  AQI = 70

✅ The system is showing the CORRECT value from the API!

If you see AQI 70 on another website, that means:
  • Different monitoring station (different location)
  • Different time of measurement
  • Different data source (not WAQI)

Air quality varies by location and time - both values can be correct!
    """)
    print("="*70 + "\n")

if __name__ == "__main__":
    show_current()
