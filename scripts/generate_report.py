"""
Report Generation Script
Generates daily air quality reports
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_acquisition.collector import DataCollector
from src.analysis.aqi_calculator import AQICalculator
from src.analysis.health_impact import HealthImpactAssessor
from src.alerts.alert_manager import AlertManager
from config.settings import MONITORED_CITIES, BASE_DIR
from loguru import logger

def generate_report():
    """Generate comprehensive daily report"""
    logger.info("Generating Air Quality Report...")
    
    # Initialize components
    collector = DataCollector()
    aqi_calc = AQICalculator()
    health_assessor = HealthImpactAssessor()
    alert_manager = AlertManager()
    
    # Fetch current data
    all_data = collector.collect_current_data(use_cache=False)
    
    # Prepare report data
    report_data = []
    
    for city, df in all_data.items():
        if df.empty:
            continue
        
        # Calculate AQI
        aqi_info = aqi_calc.get_city_current_aqi(df)
        
        # Get pollutants
        pollutants = {k: v for k, v in aqi_info.items() if k in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] and v is not None}
        
        # Health impact
        if pollutants and aqi_info.get('aqi'):
            health_impact = health_assessor.assess_health_impact(city, pollutants, aqi_info['aqi'])
            
            report_data.append({
                'City': city,
                'AQI': aqi_info.get('aqi'),
                'Category': aqi_info.get('category'),
                'Dominant Pollutant': aqi_info.get('dominant_pollutant', 'N/A').upper(),
                'PM2.5 (µg/m³)': round(pollutants.get('pm25', 0), 2) if pollutants.get('pm25') else 'N/A',
                'PM10 (µg/m³)': round(pollutants.get('pm10', 0), 2) if pollutants.get('pm10') else 'N/A',
                'Health Risk': health_impact.get('risk_category'),
                'Respiratory Risk': f"{health_impact.get('respiratory_risk', 0):.1f}/100",
                'Cardiovascular Risk': f"{health_impact.get('cardiovascular_risk', 0):.1f}/100",
                'Affected Population': health_impact.get('affected_population', {}).get('general_affected', 0)
            })
    
    # Create report DataFrame
    report_df = pd.DataFrame(report_data)
    
    # Save report
    report_dir = BASE_DIR / 'reports'
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = report_dir / f'air_quality_report_{timestamp}.csv'
    
    report_df.to_csv(report_path, index=False)
    
    logger.success(f"Report saved to: {report_path}")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print(f"AIR QUALITY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(report_df.to_string(index=False))
    print("=" * 80)
    
    return report_df

if __name__ == "__main__":
    generate_report()
