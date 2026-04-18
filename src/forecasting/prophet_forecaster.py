"""
Air Quality Forecasting Module using Prophet
Time series forecasting for pollutant levels
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger
import pickle
from pathlib import Path

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    logger.warning("Prophet not installed. Install with: pip install prophet")
    PROPHET_AVAILABLE = False

from config.settings import FORECAST_DAYS, MODELS_DIR
from ..analysis.aqi_calculator import AQICalculator


class ProphetForecaster:
    """Forecast air quality using Facebook Prophet"""
    
    def __init__(self):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet package is required for forecasting")
        self.aqi_calc = AQICalculator()
        self.models = {}
    
    def prepare_data(self, df: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """
        Prepare data for Prophet (requires 'ds' and 'y' columns)
        
        Args:
            df: DataFrame with timestamp and value columns
            parameter: Pollutant parameter name
            
        Returns:
            DataFrame formatted for Prophet
        """
        # Filter for specific parameter
        param_data = df[df['parameter'] == parameter].copy()
        
        if param_data.empty:
            return pd.DataFrame()
        
        # Aggregate by day (take mean of all measurements)
        param_data['date'] = pd.to_datetime(param_data['timestamp']).dt.date
        daily_avg = param_data.groupby('date')['value'].mean().reset_index()
        
        # Rename columns for Prophet
        daily_avg.columns = ['ds', 'y']
        daily_avg['ds'] = pd.to_datetime(daily_avg['ds'])
        
        # Remove outliers (values beyond 3 standard deviations)
        mean = daily_avg['y'].mean()
        std = daily_avg['y'].std()
        daily_avg = daily_avg[
            (daily_avg['y'] >= mean - 3*std) & 
            (daily_avg['y'] <= mean + 3*std)
        ]
        
        return daily_avg
    
    def train_model(self, df: pd.DataFrame, parameter: str) -> Optional[Prophet]:
        """
        Train Prophet model for a specific pollutant
        
        Args:
            df: Historical data DataFrame
            parameter: Pollutant parameter name
            
        Returns:
            Trained Prophet model or None if training failed
        """
        try:
            # Prepare data
            prophet_data = self.prepare_data(df, parameter)
            
            if len(prophet_data) < 14:  # Need at least 2 weeks of data
                logger.warning(f"Insufficient data for {parameter} (need at least 14 days)")
                return None
            
            logger.info(f"Training Prophet model for {parameter} with {len(prophet_data)} days of data")
            
            # Initialize and train model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,  # Not enough data for yearly patterns
                changepoint_prior_scale=0.05,  # Flexibility of trend
                seasonality_prior_scale=10.0,  # Flexibility of seasonality
                interval_width=0.95  # 95% confidence interval
            )
            
            model.fit(prophet_data)
            
            logger.success(f"Successfully trained model for {parameter}")
            self.models[parameter] = model
            
            return model
            
        except Exception as e:
            logger.error(f"Error training model for {parameter}: {e}")
            return None
    
    def forecast(self, model: Prophet, days_ahead: int = FORECAST_DAYS) -> pd.DataFrame:
        """
        Generate forecast using trained model (FUTURE dates only)
        
        Args:
            model: Trained Prophet model
            days_ahead: Number of days to forecast into the future
            
        Returns:
            DataFrame with forecast for FUTURE dates only
        """
        try:
            # Create future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract relevant columns
            forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            forecast.columns = ['date', 'predicted_value', 'lower_bound', 'upper_bound']
            
            # IMPORTANT: Only keep FUTURE predictions (dates after today)
            today = pd.Timestamp(datetime.now().date())
            forecast = forecast[forecast['date'] > today].copy()
            
            logger.info(f"Forecast range: {forecast['date'].min()} to {forecast['date'].max()}")
            
            # Ensure non-negative values
            forecast['predicted_value'] = forecast['predicted_value'].clip(lower=0)
            forecast['lower_bound'] = forecast['lower_bound'].clip(lower=0)
            forecast['upper_bound'] = forecast['upper_bound'].clip(lower=0)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return pd.DataFrame()
    
    def forecast_pollutant(self, historical_data: pd.DataFrame, 
                          parameter: str, 
                          days_ahead: int = FORECAST_DAYS) -> pd.DataFrame:
        """
        Train and forecast for a specific pollutant
        
        Args:
            historical_data: Historical measurements DataFrame
            parameter: Pollutant parameter name
            days_ahead: Number of days to forecast
            
        Returns:
            DataFrame with forecast
        """
        # Train model
        model = self.train_model(historical_data, parameter)
        
        if model is None:
            return pd.DataFrame()
        
        # Generate forecast
        forecast = self.forecast(model, days_ahead)
        
        if not forecast.empty:
            forecast['parameter'] = parameter
            
            # Calculate AQI for forecasted values
            forecast['predicted_aqi'] = forecast['predicted_value'].apply(
                lambda x: self.aqi_calc.calculate_aqi(parameter, x)
            )
        
        return forecast
    
    def forecast_all_pollutants(self, city: str, historical_data: pd.DataFrame,
                               days_ahead: int = FORECAST_DAYS) -> Dict[str, pd.DataFrame]:
        """
        Forecast all available pollutants for a city
        
        Args:
            city: City name
            historical_data: Historical measurements DataFrame
            days_ahead: Number of days to forecast
            
        Returns:
            Dictionary mapping pollutant names to forecast DataFrames
        """
        forecasts = {}
        
        available_params = historical_data['parameter'].unique()
        
        for param in available_params:
            logger.info(f"Forecasting {param} for {city}")
            forecast = self.forecast_pollutant(historical_data, param, days_ahead)
            
            if not forecast.empty:
                forecasts[param] = forecast
                
                # Save model
                self.save_model(city, param)
        
        return forecasts
    
    def get_overall_aqi_forecast(self, all_forecasts: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generate overall AQI forecast from individual pollutant forecasts
        
        Args:
            all_forecasts: Dictionary of pollutant forecasts
            
        Returns:
            DataFrame with daily AQI forecast
        """
        if not all_forecasts:
            return pd.DataFrame()
        
        # Get all unique FUTURE forecast dates only
        all_dates = set()
        today = datetime.now().date()
        for forecast_df in all_forecasts.values():
            future_dates = forecast_df[forecast_df['date'].dt.date > today]['date'].dt.date
            all_dates.update(future_dates)
        
        logger.info(f"Generating AQI forecast for {len(all_dates)} future days")
        daily_aqi = []
        
        for date in sorted(all_dates):
            date_pollutants = {}
            date_aqis = []
            
            for param, forecast_df in all_forecasts.items():
                day_forecast = forecast_df[forecast_df['date'].dt.date == date]
                if not day_forecast.empty:
                    value = day_forecast.iloc[0]['predicted_value']
                    aqi = day_forecast.iloc[0]['predicted_aqi']
                    
                    if aqi is not None:
                        date_pollutants[param] = value
                        date_aqis.append(aqi)
            
            if date_aqis:
                overall_aqi = max(date_aqis)
                dominant = max(date_pollutants, key=lambda k: self.aqi_calc.calculate_aqi(k, date_pollutants[k]))
                category = self.aqi_calc.get_aqi_category(overall_aqi)
                
                daily_aqi.append({
                    'date': pd.Timestamp(date),
                    'predicted_aqi': overall_aqi,
                    'aqi_category': category['name'],
                    'dominant_pollutant': dominant,
                    'color': category['color']
                })
        
        return pd.DataFrame(daily_aqi)
    
    def save_model(self, city: str, parameter: str):
        """Save trained model to disk"""
        if parameter not in self.models:
            return
        
        try:
            model_path = MODELS_DIR / f"{city}_{parameter}_prophet.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(self.models[parameter], f)
            
            logger.info(f"Saved model for {city}/{parameter}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, city: str, parameter: str) -> Optional[Prophet]:
        """Load saved model from disk"""
        try:
            model_path = MODELS_DIR / f"{city}_{parameter}_prophet.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return None
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            self.models[parameter] = model
            logger.info(f"Loaded model for {city}/{parameter}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def evaluate_model(self, model: Prophet, test_data: pd.DataFrame) -> Dict:
        """
        Evaluate model performance
        
        Args:
            model: Trained Prophet model
            test_data: Test dataset
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            forecast = model.predict(test_data)
            
            # Calculate metrics
            actual = test_data['y'].values
            predicted = forecast['yhat'].values
            
            mae = np.mean(np.abs(actual - predicted))
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            mape = np.mean(np.abs((actual - predicted) / actual)) * 100
            
            return {
                'mae': round(mae, 2),
                'rmse': round(rmse, 2),
                'mape': round(mape, 2)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {}
