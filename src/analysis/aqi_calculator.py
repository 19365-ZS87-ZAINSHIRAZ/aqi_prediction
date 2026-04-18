"""
AQI Calculator Module
Calculates Air Quality Index based on pollutant concentrations
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from loguru import logger
from config.settings import AQI_BREAKPOINTS, AQI_CATEGORIES


class AQICalculator:
    """Calculate Air Quality Index from pollutant concentrations"""
    
    def __init__(self):
        self.breakpoints = AQI_BREAKPOINTS
        self.categories = AQI_CATEGORIES
    
    def calculate_aqi(self, pollutant: str, concentration: float) -> Optional[int]:
        """
        Calculate AQI for a specific pollutant
        
        Args:
            pollutant: Pollutant name (pm25, pm10, no2, so2, co, o3)
            concentration: Pollutant concentration
            
        Returns:
            AQI value or None if unable to calculate
        """
        if pollutant not in self.breakpoints:
            logger.warning(f"Unknown pollutant: {pollutant}")
            return None
        
        if pd.isna(concentration) or concentration < 0:
            return None
        
        # Get breakpoints for this pollutant
        breakpoints = self.breakpoints[pollutant]
        
        # Find the appropriate breakpoint range
        for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
            if bp_low <= concentration <= bp_high:
                # Calculate AQI using linear interpolation
                aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                return int(round(aqi))
        
        # If concentration exceeds all breakpoints, use highest category
        if concentration > breakpoints[-1][1]:
            return 500
        
        return None
    
    def calculate_multi_pollutant_aqi(self, pollutants: Dict[str, float]) -> Dict:
        """
        Calculate overall AQI from multiple pollutants
        Takes the maximum AQI among all pollutants (dominant pollutant approach)
        
        Args:
            pollutants: Dictionary of pollutant names to concentrations
            
        Returns:
            Dictionary with overall AQI, category, and dominant pollutant
        """
        aqi_values = {}
        
        for pollutant, concentration in pollutants.items():
            if concentration is not None and not pd.isna(concentration):
                aqi = self.calculate_aqi(pollutant, concentration)
                if aqi is not None:
                    aqi_values[pollutant] = aqi
        
        if not aqi_values:
            return {
                'aqi': None,
                'category': 'Unknown',
                'dominant_pollutant': None,
                'color': '#CCCCCC',
                'health_message': 'Data unavailable'
            }
        
        # Overall AQI is the maximum
        overall_aqi = max(aqi_values.values())
        dominant_pollutant = max(aqi_values, key=aqi_values.get)
        
        # Get category
        category_info = self.get_aqi_category(overall_aqi)
        
        return {
            'aqi': overall_aqi,
            'category': category_info['name'],
            'dominant_pollutant': dominant_pollutant,
            'color': category_info['color'],
            'health_message': category_info['health_message'],
            'pollutant_aqis': aqi_values
        }
    
    def get_aqi_category(self, aqi: int) -> Dict:
        """
        Get AQI category information
        
        Args:
            aqi: AQI value
            
        Returns:
            Dictionary with category name, color, and health message
        """
        for category_name, details in self.categories.items():
            aqi_range = details['range']
            if aqi_range[0] <= aqi <= aqi_range[1]:
                return {
                    'name': category_name,
                    'color': details['color'],
                    'health_message': details['health_message'],
                    'range': aqi_range
                }
        
        # If AQI exceeds all categories
        return {
            'name': 'Beyond Index',
            'color': '#7E0023',
            'health_message': 'Extremely hazardous conditions',
            'range': (501, 999)
        }
    
    def process_dataframe_aqi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate AQI for all measurements in a DataFrame
        
        Args:
            df: DataFrame with pollutant measurements
            
        Returns:
            DataFrame with AQI column added
        """
        df_copy = df.copy()
        
        # Calculate individual AQIs
        df_copy['calculated_aqi'] = df_copy.apply(
            lambda row: self.calculate_aqi(row['parameter'], row['value']),
            axis=1
        )
        
        return df_copy
    
    def get_city_current_aqi(self, measurements_df: pd.DataFrame) -> Dict:
        """
        Calculate current overall AQI for a city from measurements DataFrame
        
        Args:
            measurements_df: DataFrame with latest measurements
            
        Returns:
            Dictionary with AQI information
        """
        if measurements_df.empty:
            return {
                'aqi': None,
                'category': 'Unknown',
                'dominant_pollutant': None
            }
        
        # Get latest value for each pollutant
        latest_pollutants = {}
        
        for param in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            param_data = measurements_df[measurements_df['parameter'] == param]
            if not param_data.empty:
                # Take the mean of latest values
                latest_pollutants[param] = param_data['value'].mean()
        
        # Calculate overall AQI
        aqi_result = self.calculate_multi_pollutant_aqi(latest_pollutants)
        
        # Add individual pollutant values
        aqi_result.update(latest_pollutants)
        
        return aqi_result
    
    def get_health_recommendations(self, aqi: int) -> Dict:
        """
        Get health recommendations based on AQI
        
        Args:
            aqi: AQI value
            
        Returns:
            Dictionary with recommendations for different groups
        """
        category = self.get_aqi_category(aqi)
        
        recommendations = {
            'Good': {
                'general': 'Air quality is satisfactory. Enjoy outdoor activities!',
                'sensitive': 'Ideal conditions for outdoor activities.',
                'cautionary': None
            },
            'Moderate': {
                'general': 'Air quality is acceptable for most people.',
                'sensitive': 'Unusually sensitive people should consider limiting prolonged outdoor exertion.',
                'cautionary': 'Consider reducing intense outdoor activities if you experience symptoms.'
            },
            'Unhealthy for Sensitive Groups': {
                'general': 'General public is unlikely to be affected.',
                'sensitive': 'Active children and adults, and people with respiratory disease should limit prolonged outdoor exertion.',
                'cautionary': 'People with asthma should keep quick-relief medicine handy.'
            },
            'Unhealthy': {
                'general': 'Everyone may begin to experience health effects. Limit prolonged outdoor exertion.',
                'sensitive': 'Active children and adults, and people with respiratory disease should avoid prolonged outdoor exertion.',
                'cautionary': 'Keep windows closed. Use air purifiers if available. Wear N95 masks outdoors.'
            },
            'Very Unhealthy': {
                'general': 'Health alert: everyone may experience more serious health effects. Avoid outdoor activities.',
                'sensitive': 'Active children and adults, and people with respiratory disease should avoid all outdoor exertion.',
                'cautionary': 'Everyone should stay indoors. Use air purifiers. Seek medical help if experiencing symptoms.'
            },
            'Hazardous': {
                'general': 'Health warning of emergency conditions. Everyone should avoid all outdoor activity.',
                'sensitive': 'Everyone should remain indoors and keep activity levels low.',
                'cautionary': 'Emergency conditions. Stay indoors. Schools and offices should close. Seek immediate medical attention for symptoms.'
            }
        }
        
        category_name = category['name']
        if category_name in recommendations:
            return {
                'category': category_name,
                'aqi': aqi,
                'color': category['color'],
                **recommendations[category_name]
            }
        else:
            return {
                'category': 'Beyond Index',
                'aqi': aqi,
                'color': '#7E0023',
                'general': 'Extremely hazardous - Emergency protocols required',
                'sensitive': 'Remain indoors with air filtration',
                'cautionary': 'Immediate evacuation may be necessary'
            }
