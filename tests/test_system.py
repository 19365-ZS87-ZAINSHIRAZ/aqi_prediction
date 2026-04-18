"""
System Verification Script
Tests all components of the air quality system
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from config import settings

def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    try:
        assert settings.BASE_DIR.exists(), "Base directory not found"
        assert len(settings.MONITORED_CITIES) == 3, "Expected 3 monitored cities"
        assert settings.DATA_DIR.exists(), "Data directory not found"
        
        logger.success("✓ Configuration test passed")
        return True
    except AssertionError as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

def test_database_connection():
    """Test database connectivity"""
    logger.info("Testing database connection...")
    
    try:
        from src.database.models import get_db_engine
        
        engine = get_db_engine()
        connection = engine.connect()
        connection.close()
        
        logger.success("✓ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"✗ Database connection test failed: {e}")
        logger.info("Make sure PostgreSQL is running and credentials are correct")
        return False

def test_api_access():
    """Test API accessibility"""
    logger.info("Testing API access...")
    
    try:
        import requests
        
        # Test OpenAQ
        response = requests.get(f"{settings.OPENAQ_BASE_URL}/latest", params={'limit': 1}, timeout=10)
        assert response.status_code == 200, "OpenAQ API not accessible"
        
        # Test WAQI
        if settings.WAQI_API_KEY:
            response = requests.get(
                f"{settings.WAQI_BASE_URL}/feed/lahore/",
                params={'token': settings.WAQI_API_KEY},
                timeout=10
            )
            assert response.status_code == 200, "WAQI API not accessible"
        else:
            logger.warning("WAQI API key not configured")
        
        logger.success("✓ API access test passed")
        return True
    except Exception as e:
        logger.error(f"✗ API access test failed: {e}")
        return False

def test_data_acquisition():
    """Test data collection"""
    logger.info("Testing data acquisition...")
    
    try:
        from src.data_acquisition.collector import DataCollector
        
        collector = DataCollector()
        data = collector.collect_current_data(use_cache=False)
        
        assert len(data) > 0, "No data collected"
        
        logger.success(f"✓ Data acquisition test passed ({len(data)} cities)")
        return True
    except Exception as e:
        logger.error(f"✗ Data acquisition test failed: {e}")
        return False

def test_aqi_calculation():
    """Test AQI calculator"""
    logger.info("Testing AQI calculation...")
    
    try:
        from src.analysis.aqi_calculator import AQICalculator
        
        calc = AQICalculator()
        
        # Test individual AQI calculation
        pm25_aqi = calc.calculate_aqi('pm25', 35.5)
        assert pm25_aqi == 101, f"Expected AQI 101, got {pm25_aqi}"
        
        # Test multi-pollutant AQI
        result = calc.calculate_multi_pollutant_aqi({
            'pm25': 55.5,
            'pm10': 155,
            'no2': 100
        })
        assert result['aqi'] is not None, "Multi-pollutant AQI calculation failed"
        
        logger.success("✓ AQI calculation test passed")
        return True
    except Exception as e:
        logger.error(f"✗ AQI calculation test failed: {e}")
        return False

def test_health_assessment():
    """Test health impact assessor"""
    logger.info("Testing health impact assessment...")
    
    try:
        from src.analysis.health_impact import HealthImpactAssessor
        
        assessor = HealthImpactAssessor()
        
        result = assessor.assess_health_impact(
            'Lahore',
            {'pm25': 55, 'pm10': 150, 'no2': 100},
            150
        )
        
        assert 'respiratory_risk' in result, "Respiratory risk not calculated"
        assert 'cardiovascular_risk' in result, "Cardiovascular risk not calculated"
        
        logger.success("✓ Health assessment test passed")
        return True
    except Exception as e:
        logger.error(f"✗ Health assessment test failed: {e}")
        return False

def test_forecasting():
    """Test forecasting capabilities"""
    logger.info("Testing forecasting...")
    
    try:
        from src.forecasting.prophet_forecaster import ProphetForecaster
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Create dummy data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        dummy_data = pd.DataFrame({
            'parameter': ['pm25'] * 30,
            'value': [50 + i % 20 for i in range(30)],
            'timestamp': dates
        })
        
        forecaster = ProphetForecaster()
        model = forecaster.train_model(dummy_data, 'pm25')
        
        assert model is not None, "Model training failed"
        
        logger.success("✓ Forecasting test passed")
        return True
    except ImportError:
        logger.warning("⚠ Prophet not installed - skipping forecasting test")
        return True
    except Exception as e:
        logger.error(f"✗ Forecasting test failed: {e}")
        return False

def test_alert_system():
    """Test alert manager"""
    logger.info("Testing alert system...")
    
    try:
        from src.alerts.alert_manager import AlertManager
        
        alert_mgr = AlertManager()
        
        alert = alert_mgr.check_aqi_threshold('Lahore', 200)
        assert alert is not None, "Alert not triggered for high AQI"
        assert alert['severity'] in ['low', 'medium', 'high', 'critical'], "Invalid severity"
        
        logger.success("✓ Alert system test passed")
        return True
    except Exception as e:
        logger.error(f"✗ Alert system test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("Air Quality System Verification")
    logger.info("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("API Access", test_api_access),
        ("Data Acquisition", test_data_acquisition),
        ("AQI Calculation", test_aqi_calculation),
        ("Health Assessment", test_health_assessment),
        ("Forecasting", test_forecasting),
        ("Alert System", test_alert_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'─' * 60}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'─' * 60}")
        
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status: <10} {test_name}")
    
    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.success("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        logger.error(f"\n⚠ {total - passed} test(s) failed. Please fix issues before using the system.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
