"""
Configuration Management for Air Quality Analysis System
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Settings
APP_ENV = os.getenv('APP_ENV', 'development')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DATA_REFRESH_INTERVAL = int(os.getenv('DATA_REFRESH_INTERVAL', 3600))

# API Configuration - Using WAQI only (more reliable for Pakistan)
USE_OPENAQ = False  # Disabled: unreliable for Pakistan
USE_WAQI = True

OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY', '')  # Not used
WAQI_API_KEY = os.getenv('WAQI_API_KEY', '')

OPENAQ_BASE_URL = "https://api.openaq.org/v3"
WAQI_BASE_URL = "https://api.waqi.info"

# Database Configuration - v1 uses MongoDB only
DB_TYPE = os.getenv('DB_TYPE', 'mongodb')  # Default to MongoDB for v1

# PostgreSQL (disabled in v1, will be enabled in v2)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'air_quality_db'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

# MongoDB - Primary database for v1
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'air_quality_db')

# Cities Configuration - Focused on 3 major cities
MONITORED_CITIES = {
    'Islamabad': {'lat': 33.6844, 'lon': 73.0479, 'country': 'PK'},
    'Rawalpindi': {'lat': 33.5651, 'lon': 73.0169, 'country': 'PK'},
    'Karachi': {'lat': 24.8607, 'lon': 67.0011, 'country': 'PK'}
}

# Pollutants Configuration
POLLUTANTS = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']

POLLUTANT_NAMES = {
    'pm25': 'PM2.5',
    'pm10': 'PM10',
    'no2': 'NO₂',
    'so2': 'SO₂',
    'co': 'CO',
    'o3': 'O₃'
}

# AQI Thresholds (US EPA Standard)
AQI_BREAKPOINTS = {
    'pm25': [
        (0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ],
    'pm10': [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500)
    ],
    'no2': [
        (0, 53, 0, 50),
        (54, 100, 51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 2049, 301, 500)
    ],
    'so2': [
        (0, 35, 0, 50),
        (36, 75, 51, 100),
        (76, 185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 1004, 301, 500)
    ],
    'co': [
        (0, 4.4, 0, 50),
        (4.5, 9.4, 51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 50.4, 301, 500)
    ],
    'o3': [
        (0, 54, 0, 50),
        (55, 70, 51, 100),
        (71, 85, 101, 150),
        (86, 105, 151, 200),
        (106, 200, 201, 300),
        (201, 604, 301, 500)
    ]
}

# AQI Categories
AQI_CATEGORIES = {
    'Good': {'range': (0, 50), 'color': '#00E400', 'health_message': 'Air quality is satisfactory'},
    'Moderate': {'range': (51, 100), 'color': '#FFFF00', 'health_message': 'Acceptable for most people'},
    'Unhealthy for Sensitive Groups': {'range': (101, 150), 'color': '#FF7E00', 
                                       'health_message': 'Sensitive groups may experience health effects'},
    'Unhealthy': {'range': (151, 200), 'color': '#FF0000', 
                  'health_message': 'Everyone may begin to experience health effects'},
    'Very Unhealthy': {'range': (201, 300), 'color': '#8F3F97', 
                       'health_message': 'Health alert: everyone may experience serious effects'},
    'Hazardous': {'range': (301, 500), 'color': '#7E0023', 
                  'health_message': 'Health warning of emergency conditions'}
}

# Alert Configuration
AQI_ALERT_THRESHOLD = int(os.getenv('AQI_ALERT_THRESHOLD', 150))
PM25_ALERT_THRESHOLD = float(os.getenv('PM25_ALERT_THRESHOLD', 55.4))
PM10_ALERT_THRESHOLD = float(os.getenv('PM10_ALERT_THRESHOLD', 154))

# Notification Configuration (for V2 - currently disabled)
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
# TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
# ALERT_EMAIL_FROM = os.getenv('ALERT_EMAIL_FROM', 'alerts@airquality.pk')

# Data Directories
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
CACHE_DIR = DATA_DIR / 'cache'

# Model Directory
MODELS_DIR = BASE_DIR / 'models' / 'saved'

# Logs Directory
LOGS_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Forecasting Configuration
FORECAST_DAYS = 8  # Predict next 8 days
FORECAST_MODELS = ['prophet', 'arima', 'lstm']

# Health Impact Factors
HEALTH_RISK_FACTORS = {
    'respiratory': {
        'pm25_weight': 0.4,
        'pm10_weight': 0.3,
        'no2_weight': 0.2,
        'so2_weight': 0.1
    },
    'cardiovascular': {
        'pm25_weight': 0.35,
        'pm10_weight': 0.25,
        'no2_weight': 0.25,
        'co_weight': 0.15
    }
}

# Visualization Settings
CHART_THEME = 'plotly_white'
COLOR_PALETTE = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Cache Settings
CACHE_EXPIRY = 1800  # 30 minutes

# API Rate Limiting
API_RATE_LIMIT = 100  # requests per hour
API_TIMEOUT = 60  # seconds (increased for slower APIs)

# Testing
TEST_MODE = APP_ENV == 'testing'
