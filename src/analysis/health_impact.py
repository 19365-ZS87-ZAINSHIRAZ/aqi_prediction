"""
Health Impact Assessment Module
Analyzes health risks based on air quality data
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from loguru import logger
from config.settings import HEALTH_RISK_FACTORS, MONITORED_CITIES


class HealthImpactAssessor:
    """Assess health impacts from air quality data"""
    
    # Population estimates for cities (approximate)
    CITY_POPULATIONS = {
        'Lahore': 11_000_000,
        'Karachi': 16_000_000,
        'Islamabad': 1_200_000
    }
    
    # Sensitive population percentages
    SENSITIVE_GROUPS = {
        'children': 0.30,  # 30% children under 15
        'elderly': 0.06,   # 6% elderly over 65
        'respiratory': 0.05,  # 5% with respiratory conditions
        'cardiovascular': 0.08  # 8% with cardiovascular conditions
    }
    
    def __init__(self):
        self.risk_factors = HEALTH_RISK_FACTORS
    
    def calculate_respiratory_risk(self, pollutants: Dict[str, float]) -> float:
        """
        Calculate respiratory health risk score (0-100)
        
        Args:
            pollutants: Dictionary of pollutant concentrations
            
        Returns:
            Risk score from 0 (low) to 100 (severe)
        """
        weights = self.risk_factors['respiratory']
        risk_score = 0
        
        # PM2.5 contribution
        pm25 = pollutants.get('pm25', 0)
        if pm25 > 0:
            # Normalize to 0-100 scale (250 µg/m³ = max)
            pm25_risk = min((pm25 / 250.0) * 100, 100)
            risk_score += pm25_risk * weights['pm25_weight']
        
        # PM10 contribution
        pm10 = pollutants.get('pm10', 0)
        if pm10 > 0:
            pm10_risk = min((pm10 / 500.0) * 100, 100)
            risk_score += pm10_risk * weights['pm10_weight']
        
        # NO2 contribution
        no2 = pollutants.get('no2', 0)
        if no2 > 0:
            no2_risk = min((no2 / 400.0) * 100, 100)
            risk_score += no2_risk * weights['no2_weight']
        
        # SO2 contribution
        so2 = pollutants.get('so2', 0)
        if so2 > 0:
            so2_risk = min((so2 / 300.0) * 100, 100)
            risk_score += so2_risk * weights['so2_weight']
        
        return min(risk_score, 100)
    
    def calculate_cardiovascular_risk(self, pollutants: Dict[str, float]) -> float:
        """
        Calculate cardiovascular health risk score (0-100)
        
        Args:
            pollutants: Dictionary of pollutant concentrations
            
        Returns:
            Risk score from 0 (low) to 100 (severe)
        """
        weights = self.risk_factors['cardiovascular']
        risk_score = 0
        
        # PM2.5 contribution
        pm25 = pollutants.get('pm25', 0)
        if pm25 > 0:
            pm25_risk = min((pm25 / 250.0) * 100, 100)
            risk_score += pm25_risk * weights['pm25_weight']
        
        # PM10 contribution
        pm10 = pollutants.get('pm10', 0)
        if pm10 > 0:
            pm10_risk = min((pm10 / 500.0) * 100, 100)
            risk_score += pm10_risk * weights['pm10_weight']
        
        # NO2 contribution
        no2 = pollutants.get('no2', 0)
        if no2 > 0:
            no2_risk = min((no2 / 400.0) * 100, 100)
            risk_score += no2_risk * weights['no2_weight']
        
        # CO contribution
        co = pollutants.get('co', 0)
        if co > 0:
            co_risk = min((co / 30.0) * 100, 100)
            risk_score += co_risk * weights['co_weight']
        
        return min(risk_score, 100)
    
    def assess_health_impact(self, city: str, pollutants: Dict[str, float], 
                            aqi: int) -> Dict:
        """
        Comprehensive health impact assessment
        
        Args:
            city: City name
            pollutants: Dictionary of pollutant concentrations
            aqi: Current AQI value
            
        Returns:
            Dictionary with health impact assessment
        """
        # Calculate risk scores
        respiratory_risk = self.calculate_respiratory_risk(pollutants)
        cardiovascular_risk = self.calculate_cardiovascular_risk(pollutants)
        overall_risk = (respiratory_risk + cardiovascular_risk) / 2
        
        # Determine risk category
        risk_category = self._get_risk_category(overall_risk)
        
        # Estimate affected population
        population = self.CITY_POPULATIONS.get(city, 1_000_000)
        affected_estimates = self._estimate_affected_population(
            population, overall_risk, aqi
        )
        
        # Generate health advisory
        advisory = self._generate_health_advisory(
            city, aqi, respiratory_risk, cardiovascular_risk
        )
        
        return {
            'city': city,
            'date': datetime.now(),
            'respiratory_risk': round(respiratory_risk, 2),
            'cardiovascular_risk': round(cardiovascular_risk, 2),
            'overall_risk': round(overall_risk, 2),
            'risk_category': risk_category,
            'affected_population': affected_estimates,
            'advisory': advisory,
            'aqi': aqi,
            'pollutants': pollutants
        }
    
    def _get_risk_category(self, risk_score: float) -> str:
        """Categorize risk score"""
        if risk_score < 20:
            return 'Low'
        elif risk_score < 40:
            return 'Moderate'
        elif risk_score < 60:
            return 'High'
        elif risk_score < 80:
            return 'Very High'
        else:
            return 'Severe'
    
    def _estimate_affected_population(self, total_population: int, 
                                     risk_score: float, aqi: int) -> Dict:
        """
        Estimate number of people affected
        
        Args:
            total_population: Total city population
            risk_score: Overall risk score
            aqi: Current AQI
            
        Returns:
            Dictionary with affected population estimates
        """
        # Base affected percentage based on AQI
        if aqi < 50:
            base_affected = 0.01
        elif aqi < 100:
            base_affected = 0.05
        elif aqi < 150:
            base_affected = 0.15
        elif aqi < 200:
            base_affected = 0.30
        elif aqi < 300:
            base_affected = 0.50
        else:
            base_affected = 0.75
        
        # Adjust by risk score
        risk_multiplier = 1 + (risk_score / 100)
        adjusted_affected = min(base_affected * risk_multiplier, 0.95)
        
        # Calculate estimates for different groups
        general_affected = int(total_population * adjusted_affected)
        children_affected = int(total_population * self.SENSITIVE_GROUPS['children'] * adjusted_affected * 1.5)
        elderly_affected = int(total_population * self.SENSITIVE_GROUPS['elderly'] * adjusted_affected * 1.5)
        respiratory_affected = int(total_population * self.SENSITIVE_GROUPS['respiratory'] * adjusted_affected * 2.0)
        cardiovascular_affected = int(total_population * self.SENSITIVE_GROUPS['cardiovascular'] * adjusted_affected * 2.0)
        
        return {
            'total_population': total_population,
            'general_affected': general_affected,
            'children_at_risk': children_affected,
            'elderly_at_risk': elderly_affected,
            'respiratory_patients_at_risk': respiratory_affected,
            'cardiovascular_patients_at_risk': cardiovascular_affected,
            'percentage_affected': round(adjusted_affected * 100, 2)
        }
    
    def _generate_health_advisory(self, city: str, aqi: int, 
                                 respiratory_risk: float, 
                                 cardiovascular_risk: float) -> str:
        """Generate health advisory message"""
        advisory_parts = []
        
        # Overall status
        if aqi < 50:
            advisory_parts.append(f"Air quality in {city} is currently good. No health concerns expected.")
        elif aqi < 100:
            advisory_parts.append(f"Air quality in {city} is moderate. Generally acceptable for most people.")
        elif aqi < 150:
            advisory_parts.append(f"Air quality in {city} is unhealthy for sensitive groups.")
        elif aqi < 200:
            advisory_parts.append(f"Air quality in {city} is unhealthy. Everyone may experience health effects.")
        elif aqi < 300:
            advisory_parts.append(f"Air quality in {city} is very unhealthy. Health alert conditions.")
        else:
            advisory_parts.append(f"HAZARDOUS air quality in {city}. Health warning of emergency conditions.")
        
        # Respiratory advisory
        if respiratory_risk > 60:
            advisory_parts.append(
                "HIGH RESPIRATORY HEALTH RISK: People with asthma, COPD, or other respiratory conditions should stay indoors and avoid physical exertion. Keep quick-relief medications readily available."
            )
        elif respiratory_risk > 40:
            advisory_parts.append(
                "Elevated respiratory health risk. People with respiratory conditions should limit outdoor activities."
            )
        
        # Cardiovascular advisory
        if cardiovascular_risk > 60:
            advisory_parts.append(
                "HIGH CARDIOVASCULAR HEALTH RISK: People with heart disease should avoid all outdoor activities and stay indoors in air-conditioned environments."
            )
        elif cardiovascular_risk > 40:
            advisory_parts.append(
                "Elevated cardiovascular health risk. People with heart conditions should limit outdoor exertion."
            )
        
        # General recommendations
        if aqi >= 150:
            advisory_parts.append(
                "RECOMMENDATIONS: (1) Stay indoors with windows closed, (2) Use air purifiers if available, (3) Wear N95 masks if going outside is necessary, (4) Schools should cancel outdoor activities, (5) Seek medical attention if experiencing difficulty breathing or chest discomfort."
            )
        
        return " ".join(advisory_parts)
    
    def track_health_trends(self, historical_data: pd.DataFrame) -> Dict:
        """
        Analyze health risk trends over time
        
        Args:
            historical_data: DataFrame with historical AQI and pollutant data
            
        Returns:
            Dictionary with trend analysis
        """
        if historical_data.empty:
            return {}
        
        # Calculate daily health risks
        daily_risks = []
        
        for date in historical_data['timestamp'].dt.date.unique():
            day_data = historical_data[historical_data['timestamp'].dt.date == date]
            
            # Get average pollutants for the day
            pollutants = {}
            for param in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
                param_data = day_data[day_data['parameter'] == param]
                if not param_data.empty:
                    pollutants[param] = param_data['value'].mean()
            
            if pollutants:
                resp_risk = self.calculate_respiratory_risk(pollutants)
                cardio_risk = self.calculate_cardiovascular_risk(pollutants)
                
                daily_risks.append({
                    'date': date,
                    'respiratory_risk': resp_risk,
                    'cardiovascular_risk': cardio_risk,
                    'overall_risk': (resp_risk + cardio_risk) / 2
                })
        
        if not daily_risks:
            return {}
        
        risks_df = pd.DataFrame(daily_risks)
        
        return {
            'avg_respiratory_risk': round(risks_df['respiratory_risk'].mean(), 2),
            'avg_cardiovascular_risk': round(risks_df['cardiovascular_risk'].mean(), 2),
            'max_respiratory_risk': round(risks_df['respiratory_risk'].max(), 2),
            'max_cardiovascular_risk': round(risks_df['cardiovascular_risk'].max(), 2),
            'days_high_risk': len(risks_df[risks_df['overall_risk'] > 60]),
            'trend': 'improving' if risks_df['overall_risk'].iloc[-7:].mean() < risks_df['overall_risk'].mean() else 'worsening'
        }
