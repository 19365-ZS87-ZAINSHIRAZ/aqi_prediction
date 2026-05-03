"""Check for multiple hourly entries per day"""
from src.database.mongodb_operations import MongoDBOperations
from datetime import datetime
import pandas as pd
from collections import defaultdict

db = MongoDBOperations()

print("=" * 60)
print("CHECKING FOR HOURLY DATA")
print("=" * 60)

for city in ['Islamabad', 'Rawalpindi', 'Karachi']:
    print(f"\n{city}:")
    
    # Get all measurements for the last 10 days
    measurements = list(db.measurements.find({'city': city}).sort('timestamp', -1).limit(500))
    
    if not measurements:
        print("  No data")
        continue
    
    # Group by date and parameter
    daily_counts = defaultdict(lambda: defaultdict(int))
    
    for m in measurements:
        date = m['timestamp'].date()
        param = m.get('parameter', 'unknown')
        daily_counts[date][param] += 1
    
    # Check if any day has multiple entries for same parameter
    max_entries = 0
    max_date = None
    max_param = None
    
    for date, params in sorted(daily_counts.items(), reverse=True)[:10]:
        for param, count in params.items():
            if count > max_entries:
                max_entries = count
                max_date = date
                max_param = param
        
        print(f"  {date}: ", end="")
        param_counts = [f"{p}={c}" for p, c in sorted(params.items())]
        print(", ".join(param_counts[:5]))  # Show first 5 params
    
    if max_entries > 1:
        print(f"\n  ⚠️  WARNING: Found {max_entries} entries for {max_param} on {max_date}")
        print(f"  → Daily averaging NEEDED for predictions")
    else:
        print(f"\n  ✓ Only one entry per parameter per day - no averaging needed")

print("\n" + "=" * 60)
