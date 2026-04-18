"""
Alert System Module
Monitors air quality and logs alerts when thresholds are exceeded
V1: File-based logging (Email/SMS will be added in V2)
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
from config.settings import (
    AQI_ALERT_THRESHOLD, PM25_ALERT_THRESHOLD, PM10_ALERT_THRESHOLD
)


class AlertManager:
    """Manage air quality alerts - V1: File-based logging"""
    
    # Alert severity levels
    SEVERITY_LEVELS = {
        'low': {'threshold': 101, 'color': '#FFA500'},
        'medium': {'threshold': 151, 'color': '#FF4500'},
        'high': {'threshold': 201, 'color': '#8B0000'},
        'critical': {'threshold': 301, 'color': '#800080'}
    }
    
    def __init__(self):
        # V1: Use file-based alerts only
        self.alert_file = Path(__file__).parent.parent.parent / 'alerts' / 'alert.txt'
        self.alert_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize alert file if it doesn't exist
        if not self.alert_file.exists():
            self.alert_file.touch()
            logger.info(f"Created alert log file: {self.alert_file}")
        
        logger.info("Alert Manager initialized - V1 (File-based logging)")
    
    def check_aqi_threshold(self, city: str, aqi: int) -> Optional[Dict]:
        """
        Check if AQI exceeds alert threshold
        
        Args:
            city: City name
            aqi: Current AQI value
            
        Returns:
            Alert data if threshold exceeded, None otherwise
        """
        if aqi >= AQI_ALERT_THRESHOLD:
            severity = self._determine_severity(aqi)
            
            return {
                'city': city,
                'type': 'AQI',
                'severity': severity,
                'value': aqi,
                'threshold': AQI_ALERT_THRESHOLD,
                'message': self._generate_aqi_alert_message(city, aqi, severity),
                'timestamp': datetime.now()
            }
        
        return None
    
    def check_pollutant_thresholds(self, city: str, pollutants: Dict[str, float]) -> List[Dict]:
        """
        Check if any pollutant exceeds thresholds
        
        Args:
            city: City name
            pollutants: Dictionary of pollutant concentrations
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Check PM2.5
        pm25 = pollutants.get('pm25', 0)
        if pm25 >= PM25_ALERT_THRESHOLD:
            alerts.append({
                'city': city,
                'type': 'PM2.5',
                'severity': 'high' if pm25 >= PM25_ALERT_THRESHOLD * 2 else 'medium',
                'value': pm25,
                'threshold': PM25_ALERT_THRESHOLD,
                'message': f"PM2.5 levels in {city} are {pm25:.1f} µg/m³, exceeding safe threshold of {PM25_ALERT_THRESHOLD} µg/m³. Limit outdoor activities.",
                'timestamp': datetime.now()
            })
        
        # Check PM10
        pm10 = pollutants.get('pm10', 0)
        if pm10 >= PM10_ALERT_THRESHOLD:
            alerts.append({
                'city': city,
                'type': 'PM10',
                'severity': 'high' if pm10 >= PM10_ALERT_THRESHOLD * 2 else 'medium',
                'value': pm10,
                'threshold': PM10_ALERT_THRESHOLD,
                'message': f"PM10 levels in {city} are {pm10:.1f} µg/m³, exceeding safe threshold of {PM10_ALERT_THRESHOLD} µg/m³.",
                'timestamp': datetime.now()
            })
        
        return alerts
    
    def log_alert(self, alert: Dict) -> bool:
        """
        Log alert to file (V1 implementation)
        
        Args:
            alert: Alert data
            
        Returns:
            True if logged successfully
        """
        try:
            timestamp = alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            severity_marker = {
                'low': '⚠️ ',
                'medium': '🔶',
                'high': '🔴',
                'critical': '🚨'
            }.get(alert['severity'], '⚠️')
            
            # Format alert message
            alert_line = (
                f"\n{'='*80}\n"
                f"{severity_marker} ALERT - {timestamp}\n"
                f"{'='*80}\n"
                f"City: {alert['city']}\n"
                f"Type: {alert['type']}\n"
                f"Severity: {alert['severity'].upper()}\n"
                f"Current Value: {alert['value']}\n"
                f"Threshold: {alert['threshold']}\n"
                f"Message: {alert['message']}\n"
                f"{'='*80}\n"
            )
            
            # Append to alert file
            with open(self.alert_file, 'a', encoding='utf-8') as f:
                f.write(alert_line)
            
            logger.warning(f"ALERT LOGGED: {alert['city']} - {alert['type']} = {alert['value']} (Threshold: {alert['threshold']})")
            return True
            
        except Exception as e:
            logger.error(f"Error logging alert to file: {e}")
            return False
    
    def generate_daily_report(self, city: str, aqi_data: Dict, 
                            health_impact: Dict) -> Dict:
        """
        Generate daily air quality report
        
        Args:
            city: City name
            aqi_data: AQI information
            health_impact: Health impact assessment
            
        Returns:
            Report dictionary
        """
        report = {
            'city': city,
            'date': datetime.now().date(),
            'aqi': aqi_data.get('aqi'),
            'category': aqi_data.get('category'),
            'dominant_pollutant': aqi_data.get('dominant_pollutant'),
            'health_risk': health_impact.get('risk_category'),
            'respiratory_risk': health_impact.get('respiratory_risk'),
            'cardiovascular_risk': health_impact.get('cardiovascular_risk'),
            'affected_population': health_impact.get('affected_population', {}).get('general_affected'),
            'recommendations': health_impact.get('advisory')
        }
        
        return report
    
    def send_email_alert(self, recipient: str, alert: Dict) -> bool:
        """
        V1: Log alert to file (Email functionality in V2)
        
        Args:
            recipient: Email address (unused in V1)
            alert: Alert data
            
        Returns:
            True if logged successfully
        """
        logger.info(f"V1: Logging alert to file instead of email for {recipient}")
        return self.log_alert(alert)
    
    def send_sms_alert(self, phone_number: str, alert: Dict) -> bool:
        """
        V1: Log alert to file (SMS functionality in V2)
        
        Args:
            phone_number: Recipient phone number (unused in V1)
            alert: Alert data
            
        Returns:
            True if logged successfully
        """
        logger.info(f"V1: Logging alert to file instead of SMS for {phone_number}")
        return self.log_alert(alert)
    
    def _determine_severity(self, aqi: int) -> str:
        """Determine alert severity based on AQI"""
        if aqi >= 301:
            return 'critical'
        elif aqi >= 201:
            return 'high'
        elif aqi >= 151:
            return 'medium'
        else:
            return 'low'
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color code for severity level"""
        return self.SEVERITY_LEVELS.get(severity, {}).get('color', '#808080')
    
    def _generate_aqi_alert_message(self, city: str, aqi: int, severity: str) -> str:
        """Generate alert message for AQI threshold breach"""
        messages = {
            'low': f"Air quality in {city} has reached unhealthy levels (AQI: {aqi}). Sensitive groups should limit outdoor exposure.",
            'medium': f"Air quality in {city} is unhealthy (AQI: {aqi}). Everyone should reduce prolonged outdoor exertion.",
            'high': f"Air quality in {city} is very unhealthy (AQI: {aqi}). Everyone should avoid outdoor activities.",
            'critical': f"HAZARDOUS air quality in {city} (AQI: {aqi}). Emergency conditions - remain indoors!"
        }
        
        return messages.get(severity, f"Air quality alert for {city}: AQI {aqi}")
    
    def create_alert_summary(self, alerts: List[Dict]) -> str:
        """
        Create summary of multiple alerts
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Summary text
        """
        if not alerts:
            return "No alerts at this time. Air quality is within acceptable levels."
        
        summary_parts = [
            f"⚠️ {len(alerts)} ACTIVE AIR QUALITY ALERT(S)",
            ""
        ]
        
        for i, alert in enumerate(alerts, 1):
            summary_parts.append(
                f"{i}. {alert['city']} - {alert['type']}: {alert['value']} "
                f"({alert['severity'].upper()})"
            )
        
        return "\n".join(summary_parts)
