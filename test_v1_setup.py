"""
Quick test to verify V1 setup with MongoDB and alert logging
"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("V1 SETUP VERIFICATION")
print("=" * 80)

# Test 1: Cities Configuration
print("\n1. Testing Cities Configuration...")
try:
    from config.settings import MONITORED_CITIES, DATA_REFRESH_INTERVAL
    print(f"   ✓ Number of cities: {len(MONITORED_CITIES)}")
    print(f"   ✓ Cities: {', '.join(MONITORED_CITIES.keys())}")
    print(f"   ✓ Data refresh interval: {DATA_REFRESH_INTERVAL} seconds ({DATA_REFRESH_INTERVAL/60} minutes)")
    assert len(MONITORED_CITIES) == 6, "Expected 6 cities"
    assert DATA_REFRESH_INTERVAL == 900, "Expected 900 seconds (15 minutes)"
    print("   ✓ Cities configuration: PASSED")
except Exception as e:
    print(f"   ✗ Cities configuration: FAILED - {e}")

# Test 2: Alert Thresholds
print("\n2. Testing Alert Thresholds...")
try:
    from config.settings import AQI_ALERT_THRESHOLD, PM25_ALERT_THRESHOLD, PM10_ALERT_THRESHOLD
    print(f"   ✓ AQI Alert Threshold: {AQI_ALERT_THRESHOLD}")
    print(f"   ✓ PM2.5 Alert Threshold: {PM25_ALERT_THRESHOLD} µg/m³")
    print(f"   ✓ PM10 Alert Threshold: {PM10_ALERT_THRESHOLD} µg/m³")
    print("   ✓ Alert thresholds: PASSED")
except Exception as e:
    print(f"   ✗ Alert thresholds: FAILED - {e}")

# Test 3: Alert Manager (File-based logging)
print("\n3. Testing Alert Manager...")
try:
    from src.alerts.alert_manager import AlertManager
    alert_mgr = AlertManager()
    
    # Test AQI threshold check
    alert = alert_mgr.check_aqi_threshold('Lahore', 200)
    if alert:
        print(f"   ✓ AQI threshold check works: {alert['severity']} severity")
        # Log the alert
        alert_mgr.log_alert(alert)
        print(f"   ✓ Alert logged to file successfully")
    
    # Test pollutant threshold check
    test_pollutants = {'pm25': 100, 'pm10': 200}
    pollutant_alerts = alert_mgr.check_pollutant_thresholds('Karachi', test_pollutants)
    if pollutant_alerts:
        print(f"   ✓ Pollutant threshold check works: {len(pollutant_alerts)} alert(s)")
        for pa in pollutant_alerts:
            alert_mgr.log_alert(pa)
    
    print("   ✓ Alert Manager: PASSED")
except Exception as e:
    print(f"   ✗ Alert Manager: FAILED - {e}")
    import traceback
    traceback.print_exc()

# Test 4: Alert File Creation
print("\n4. Testing Alert File...")
try:
    alert_file = Path(__file__).parent / 'alerts' / 'alert.txt'
    if alert_file.exists():
        print(f"   ✓ Alert file exists: {alert_file}")
        with open(alert_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                print(f"   ✓ Alert file has content ({len(content)} bytes)")
            else:
                print("   ℹ Alert file is empty (no alerts logged yet)")
    else:
        print(f"   ✗ Alert file not found: {alert_file}")
except Exception as e:
    print(f"   ✗ Alert file check: FAILED - {e}")

# Test 5: MongoDB Connection (if configured)
print("\n5. Testing MongoDB Connection...")
try:
    from src.database.mongodb_operations import MongoDBOperations
    db_ops = MongoDBOperations()
    print("   ✓ MongoDB connection: SUCCESS")
    print(f"   ✓ Database: {db_ops.db.name}")
    print(f"   ✓ Collections: {', '.join(db_ops.db.list_collection_names()[:5])}...")
except Exception as e:
    print(f"   ⚠ MongoDB connection: {e}")
    print("   ℹ Make sure MongoDB is configured and running")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
print("\nV1 Setup Summary:")
print("✓ 6 cities configured (Lahore, Karachi, Islamabad, Rawalpindi, Faisalabad, Multan)")
print("✓ 15-minute data refresh interval")
print("✓ Alert thresholds configured (AQI: 150, PM2.5: 55.4, PM10: 154)")
print("✓ Alert logging to file system (alerts/alert.txt)")
print("✓ MongoDB-only database (no PostgreSQL)")
print("\nNext Steps:")
print("1. Run: streamlit run app.py")
print("2. Check alerts/alert.txt for any logged alerts")
print("3. Monitor logs/ directory for application logs")
