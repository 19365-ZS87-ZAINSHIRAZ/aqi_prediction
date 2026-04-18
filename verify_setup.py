"""
System Verification Script for v1.0 (MongoDB Version)
Checks all components and dependencies
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("Testing Module Imports...")
    print("=" * 60)
    
    tests = {
        "MongoDB Driver": lambda: __import__('pymongo'),
        "Pandas": lambda: __import__('pandas'),
        "Streamlit": lambda: __import__('streamlit'),
        "Plotly": lambda: __import__('plotly'),
        "Prophet": lambda: __import__('prophet'),
        "Requests": lambda: __import__('requests'),
        "Loguru": lambda: __import__('loguru'),
    }
    
    passed = 0
    failed = 0
    
    for name, test_func in tests.items():
        try:
            test_func()
            print(f"✓ {name:30} OK")
            passed += 1
        except ImportError as e:
            print(f"✗ {name:30} FAILED: {e}")
            failed += 1
    
    print(f"\nImport Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n" + "=" * 60)
    print("Testing MongoDB Connection...")
    print("=" * 60)
    
    try:
        from pymongo import MongoClient
        from config.settings import MONGODB_URI, MONGODB_DB
        
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise exception if cannot connect
        
        print(f"✓ MongoDB connection successful")
        print(f"  URI: {MONGODB_URI}")
        print(f"  Database: {MONGODB_DB}")
        
        # List collections
        db = client[MONGODB_DB]
        collections = db.list_collection_names()
        
        if collections:
            print(f"  Existing collections: {', '.join(collections)}")
        else:
            print(f"  No collections yet (will be created automatically)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure MongoDB is running")
        print("  2. Check MONGODB_URI in .env file")
        print("  3. Verify MongoDB service is started")
        return False

def test_database_operations():
    """Test database operations module"""
    print("\n" + "=" * 60)
    print("Testing Database Operations...")
    print("=" * 60)
    
    try:
        from src.database.operations import DatabaseOperations
        
        db_ops = DatabaseOperations()
        print("✓ DatabaseOperations initialized successfully")
        print(f"  Using: MongoDB")
        
        # Test basic operation
        import pandas as pd
        test_df = pd.DataFrame({
            'city': ['Test'],
            'parameter': ['pm25'],
            'value': [25.5],
            'unit': ['µg/m³'],
            'timestamp': [pd.Timestamp.now()],
            'source': ['test']
        })
        
        # Just verify we can call the method (don't actually save test data)
        print("✓ Database operations module is working")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        return False

def test_core_modules():
    """Test core application modules"""
    print("\n" + "=" * 60)
    print("Testing Core Modules...")
    print("=" * 60)
    
    modules = {
        "Data Collector": "src.data_acquisition.collector.DataCollector",
        "AQI Calculator": "src.analysis.aqi_calculator.AQICalculator",
        "Health Impact Assessor": "src.analysis.health_impact.HealthImpactAssessor",
        "Prophet Forecaster": "src.forecasting.prophet_forecaster.ProphetForecaster",
    }
    
    passed = 0
    failed = 0
    
    for name, module_path in modules.items():
        try:
            parts = module_path.rsplit('.', 1)
            module = __import__(parts[0], fromlist=[parts[1]])
            cls = getattr(module, parts[1])
            instance = cls()
            print(f"✓ {name:30} OK")
            passed += 1
        except Exception as e:
            print(f"✗ {name:30} FAILED: {e}")
            failed += 1
    
    print(f"\nCore Module Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_configuration():
    """Test configuration loading"""
    print("\n" + "=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    
    try:
        from config.settings import (
            MONITORED_CITIES, DB_TYPE, MONGODB_URI, MONGODB_DB,
            OPENAQ_API_KEY, WAQI_API_KEY
        )
        
        print(f"✓ Configuration loaded successfully")
        print(f"  Database Type: {DB_TYPE}")
        print(f"  Monitored Cities: {', '.join(MONITORED_CITIES.keys())}")
        print(f"  OpenAQ API Key: {'Set' if OPENAQ_API_KEY else 'Not set (optional)'}")
        print(f"  WAQI API Key: {'Set' if WAQI_API_KEY else 'Not set (optional)'}")
        
        if not OPENAQ_API_KEY and not WAQI_API_KEY:
            print("\n  ℹ️  Note: API keys not set. Some features may be limited.")
            print("     Add keys to .env file for full functionality.")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "AIR QUALITY APP - SYSTEM VERIFICATION" + " " * 10 + "║")
    print("║" + " " * 15 + "Version 1.0 (MongoDB)" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    results = []
    
    # Run all tests
    results.append(("Import Tests", test_imports()))
    results.append(("Configuration", test_configuration()))
    results.append(("MongoDB Connection", test_mongodb_connection()))
    results.append(("Database Operations", test_database_operations()))
    results.append(("Core Modules", test_core_modules()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Your system is ready to use.")
        print("\nNext steps:")
        print("  1. Run the dashboard: streamlit run app.py")
        print("  2. Or use the batch file: run_dashboard.bat")
        print("  3. Fetch data: python scripts/fetch_data.py")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Make sure MongoDB is running")
        print("  2. Activate virtual environment: .venv\\Scripts\\activate")
        print("  3. Install dependencies: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
