"""
ARIMA-based Air Quality Forecasting
Alternative forecasting approach using ARIMA models
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from loguru import logger
import pickle

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    logger.warning("Statsmodels not installed. Install with: pip install statsmodels")
    STATSMODELS_AVAILABLE = False

from config.settings import FORECAST_DAYS, MODELS_DIR
from ..analysis.aqi_calculator import AQICalculator


class ARIMAForecaster:
    """Forecast air quality using ARIMA models"""
    
    def __init__(self):
        if not STATSMODELS_AVAILABLE:
            raise ImportError("Statsmodels package is required for ARIMA forecasting")
        self.aqi_calc = AQICalculator()
        self.models = {}
    
    def prepare_data(self, df: pd.DataFrame, parameter: str) -> pd.Series:
        """
        Prepare time series data for ARIMA
        
        Args:
            df: DataFrame with measurements
            parameter: Pollutant parameter
            
        Returns:
            Time series data
        """
        # Filter for parameter
        param_data = df[df['parameter'] == parameter].copy()
        
        if param_data.empty:
            return pd.Series()
        
        # Aggregate by day
        param_data['date'] = pd.to_datetime(param_data['timestamp']).dt.date
        daily_avg = param_data.groupby('date')['value'].mean()
        daily_avg.index = pd.to_datetime(daily_avg.index)
        
        # Remove outliers
        mean = daily_avg.mean()
        std = daily_avg.std()
        daily_avg = daily_avg[(daily_avg >= mean - 3*std) & (daily_avg <= mean + 3*std)]
        
        # Ensure regular frequency (fill missing dates with interpolation)
        daily_avg = daily_avg.asfreq('D')
        daily_avg = daily_avg.interpolate(method='linear', limit=3)
        daily_avg = daily_avg.dropna()
        
        return daily_avg
    
    def check_stationarity(self, series: pd.Series) -> Dict:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            series: Time series data
            
        Returns:
            Dictionary with test results
        """
        try:
            result = adfuller(series, autolag='AIC')
            
            return {
                'adf_statistic': result[0],
                'p_value': result[1],
                'is_stationary': result[1] < 0.05,
                'critical_values': result[4]
            }
        except Exception as e:
            logger.error(f"Error checking stationarity: {e}")
            return {'is_stationary': False}
    
    def find_optimal_order(self, series: pd.Series) -> Tuple[int, int, int]:
        """
        Find optimal ARIMA order (p, d, q) using grid search
        
        Args:
            series: Time series data
            
        Returns:
            Tuple of (p, d, q)
        """
        # Check stationarity to determine d
        stationarity = self.check_stationarity(series)
        d = 0 if stationarity['is_stationary'] else 1
        
        # Grid search for p and q
        best_aic = np.inf
        best_order = (1, d, 1)
        
        p_range = range(0, 4)
        q_range = range(0, 4)
        
        for p in p_range:
            for q in q_range:
                try:
                    model = ARIMA(series, order=(p, d, q))
                    fitted = model.fit()
                    
                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                        
                except:
                    continue
        
        logger.info(f"Optimal ARIMA order: {best_order} (AIC: {best_aic:.2f})")
        return best_order
    
    def train_model(self, df: pd.DataFrame, parameter: str, 
                   order: Optional[Tuple[int, int, int]] = None) -> Optional[ARIMA]:
        """
        Train ARIMA model for a pollutant
        
        Args:
            df: Historical data
            parameter: Pollutant parameter
            order: ARIMA order (p, d, q). If None, will be auto-determined
            
        Returns:
            Fitted ARIMA model or None
        """
        try:
            # Prepare data
            series = self.prepare_data(df, parameter)
            
            if len(series) < 14:
                logger.warning(f"Insufficient data for {parameter}")
                return None
            
            # Determine order if not provided
            if order is None:
                order = self.find_optimal_order(series)
            
            logger.info(f"Training ARIMA{order} for {parameter}")
            
            # Train model
            model = ARIMA(series, order=order)
            fitted_model = model.fit()
            
            logger.success(f"Successfully trained ARIMA model for {parameter}")
            self.models[parameter] = fitted_model
            
            return fitted_model
            
        except Exception as e:
            logger.error(f"Error training ARIMA model for {parameter}: {e}")
            return None
    
    def forecast(self, model, days_ahead: int = FORECAST_DAYS) -> pd.DataFrame:
        """
        Generate forecast using trained ARIMA model
        
        Args:
            model: Fitted ARIMA model
            days_ahead: Number of days to forecast
            
        Returns:
            DataFrame with forecast
        """
        try:
            # Generate forecast
            forecast_result = model.forecast(steps=days_ahead)
            
            # Get confidence intervals
            forecast_df = model.get_forecast(steps=days_ahead)
            conf_int = forecast_df.conf_int()
            
            # Create result DataFrame
            last_date = model.data.dates[-1]
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
            
            result = pd.DataFrame({
                'date': future_dates,
                'predicted_value': forecast_result.values,
                'lower_bound': conf_int.iloc[:, 0].values,
                'upper_bound': conf_int.iloc[:, 1].values
            })
            
            # Ensure non-negative values
            result['predicted_value'] = result['predicted_value'].clip(lower=0)
            result['lower_bound'] = result['lower_bound'].clip(lower=0)
            result['upper_bound'] = result['upper_bound'].clip(lower=0)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return pd.DataFrame()
    
    def forecast_pollutant(self, historical_data: pd.DataFrame,
                          parameter: str,
                          days_ahead: int = FORECAST_DAYS) -> pd.DataFrame:
        """
        Train and forecast for a specific pollutant
        
        Args:
            historical_data: Historical measurements
            parameter: Pollutant parameter
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
            
            # Calculate AQI
            forecast['predicted_aqi'] = forecast['predicted_value'].apply(
                lambda x: self.aqi_calc.calculate_aqi(parameter, x)
            )
        
        return forecast
    
    def save_model(self, city: str, parameter: str):
        """Save trained model"""
        if parameter not in self.models:
            return
        
        try:
            model_path = MODELS_DIR / f"{city}_{parameter}_arima.pkl"
            self.models[parameter].save(model_path)
            logger.info(f"Saved ARIMA model for {city}/{parameter}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, city: str, parameter: str):
        """Load saved model"""
        try:
            model_path = MODELS_DIR / f"{city}_{parameter}_arima.pkl"
            
            if not model_path.exists():
                return None
            
            from statsmodels.tsa.arima.model import ARIMAResults
            model = ARIMAResults.load(model_path)
            
            self.models[parameter] = model
            logger.info(f"Loaded ARIMA model for {city}/{parameter}")
            
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
