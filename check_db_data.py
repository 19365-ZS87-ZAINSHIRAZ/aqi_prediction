"""Quick script to check database data"""
from src.database.mongodb_operations import MongoDBOperations
from datetime import datetime, timedelta
import pandas as pd

db = MongoDBOperations()

print("=" * 60)
print("DATABASE ANALYSIS FOR ISLAMABAD")
print("=" * 60)

# Total measurements
total = db.measurements.count_documents({'city': 'Islamabad'})
print(f"\nTotal measurements in DB: {total}")

# Get all measurements
measurements = list(db.measurements.find({'city': 'Islamabad'}).sort('timestamp', -1).limit(100))

if measurements:
    print("\n--- Last 20 measurements ---")
    for m in measurements[:20]:
        print(f"{m['timestamp']} - Parameter: {m.get('parameter', 'N/A'):10s} - Value: {m.get('value', 'N/A')}")
    
    # Unique dates
    all_measurements = list(db.measurements.find({'city': 'Islamabad'}, {'timestamp': 1, 'parameter': 1}))
    dates = [m['timestamp'].date() for m in all_measurements]
    unique_dates = sorted(set(dates))
    
    print(f"\n--- Date Coverage ---")
    print(f"Unique dates: {len(unique_dates)}")
    if unique_dates:
        print(f"Date range: {unique_dates[0]} to {unique_dates[-1]}")
        print(f"\nFirst 10 dates: {unique_dates[:10]}")
        print(f"Last 10 dates: {unique_dates[-10:]}")
    
    # Parameters
    params = [m.get('parameter', 'N/A') for m in all_measurements]
    unique_params = set(params)
    print(f"\n--- Parameters ---")
    print(f"Unique parameters: {unique_params}")
    
    # Check for air quality parameters
    aq_params = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']
    print(f"\n--- Air Quality Parameters Available ---")
    for param in aq_params:
        count = sum(1 for p in params if p == param)
        print(f"  {param}: {count} measurements")

else:
    print("\nNo measurements found!")

# Check AQI history
print("\n" + "=" * 60)
print("AQI HISTORY")
print("=" * 60)

aqi_count = db.aqi_history.count_documents({'city': 'Islamabad'})
print(f"\nTotal AQI records: {aqi_count}")

if aqi_count > 0:
    aqi_records = list(db.aqi_history.find({'city': 'Islamabad'}).sort('timestamp', -1).limit(10))
    print("\n--- Last 10 AQI records ---")
    for record in aqi_records:
        print(f"{record.get('timestamp')} - AQI: {record.get('aqi', 'N/A')} - Category: {record.get('category', 'N/A')}")

# Check today's data
print("\n" + "=" * 60)
print("TODAY'S DATA")
print("=" * 60)

today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today_end = today_start + timedelta(days=1)

today_measurements = list(db.measurements.find({
    'city': 'Islamabad',
    'timestamp': {'$gte': today_start, '$lt': today_end}
}))

print(f"\nMeasurements today: {len(today_measurements)}")
if today_measurements:
    for m in today_measurements[:10]:
        print(f"{m['timestamp']} - {m.get('parameter', 'N/A')}: {m.get('value', 'N/A')}")

today_aqi = db.get_current_aqi('Islamabad')
print(f"\nToday's AQI: {today_aqi}")

print("\n" + "=" * 60)
