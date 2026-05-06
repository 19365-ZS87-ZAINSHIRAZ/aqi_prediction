# Air Quality Index (AQI) Prediction & Monitoring System
## Technical Documentation - Final Year Project

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [System Architecture](#2-system-architecture)
3. [Module Descriptions](#3-module-descriptions)
4. [Data Flow Pipeline](#4-data-flow-pipeline)
5. [File Structure & Responsibilities](#5-file-structure--responsibilities)
6. [Data Acquisition & Preprocessing](#6-data-acquisition--preprocessing)
7. [AQI Calculation Engine](#7-aqi-calculation-engine)
8. [Prediction/Forecasting Module](#8-predictionforecasting-module)
9. [Database Architecture](#9-database-architecture)
10. [Health Impact Assessment](#10-health-impact-assessment)
11. [Alert Management System](#11-alert-management-system)
12. [User Interface (Dashboard)](#12-user-interface-dashboard)
13. [Deployment & Execution Workflow](#13-deployment--execution-workflow)

---

## 1. System Overview

### 1.1 Project Description
An **Air Quality Index (AQI) Prediction and Monitoring System** for urban Pakistan (Islamabad, Rawalpindi, and Karachi). The system:
- Collects real-time air quality data from multiple APIs
- Calculates standardized AQI values using US EPA standards
- Predicts future air quality using time-series forecasting
- Assesses health impacts on population
- Provides an interactive web dashboard for visualization

### 1.2 Technology Stack
- **Programming Language**: Python 3.9+
- **Web Framework**: Streamlit (Dashboard UI)
- **Database**: MongoDB
- **Forecasting Models**: 
  - Facebook Prophet (Primary)
  - ARIMA/SARIMA (Alternative)
- **APIs**: 
  - WAQI (World Air Quality Index) - Primary
  - OpenAQ (Secondary, optional)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Plotly Express

### 1.3 Target Cities
- **Islamabad**: Capital city (Lat: 33.6844, Lon: 73.0479)
- **Rawalpindi**: Industrial city (Lat: 33.5651, Lon: 73.0169)
- **Karachi**: Port city (Lat: 24.8607, Lon: 67.0011)

### 1.4 Monitored Pollutants
1. **PM2.5** - Particulate Matter < 2.5 micrometers
2. **PM10** - Particulate Matter < 10 micrometers
3. **NO₂** - Nitrogen Dioxide
4. **SO₂** - Sulfur Dioxide
5. **CO** - Carbon Monoxide
6. **O₃** - Ozone

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                        │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │   WAQI API   │              │  OpenAQ API  │                 │
│  └──────┬───────┘              └──────┬───────┘                 │
└─────────┼──────────────────────────────┼──────────────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   DATA ACQUISITION LAYER    │
          │  - DataCollector            │
          │  - WAQIAPI                  │
          │  - OpenAQAPI                │
          │  - Caching Mechanism        │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   PREPROCESSING LAYER       │
          │  - Data Validation          │
          │  - Missing Value Handling   │
          │  - Outlier Removal          │
          │  - Data Normalization       │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   ANALYSIS LAYER            │
          │  - AQI Calculator           │
          │  - Health Impact Assessor   │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   PREDICTION LAYER          │
          │  - Prophet Forecaster       │
          │  - ARIMA Forecaster         │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   DATA PERSISTENCE LAYER    │
          │  - MongoDB Operations       │
          │  - Collections:             │
          │    • Measurements           │
          │    • AQI History            │
          │    • Health Impacts         │
          │    • Forecasts              │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   PRESENTATION LAYER        │
          │  - Streamlit Dashboard      │
          │  - Interactive Charts       │
          │  - Real-time Updates        │
          └─────────────────────────────┘
```

### 2.2 Design Pattern
The system follows a **Layered Architecture** pattern with clear separation of concerns:
- **Data Layer**: API integration and database operations
- **Business Logic Layer**: AQI calculation, forecasting, health assessment
- **Presentation Layer**: Streamlit web dashboard

---

## 3. Module Descriptions

### 3.1 Core Modules

#### **Module 1: Configuration Management** (`config/`)
- **File**: `settings.py`
- **Purpose**: Centralized configuration for entire application
- **Key Components**:
  - API credentials and endpoints
  - Database connection strings
  - City coordinates
  - AQI breakpoints (US EPA standards)
  - Health risk factors
  - Alert thresholds

#### **Module 2: Data Acquisition** (`src/data_acquisition/`)
- **Files**: 
  - `collector.py` - Main data collection orchestrator
  - `waqi_api.py` - WAQI API client
  - `openaq_api.py` - OpenAQ API client
- **Purpose**: Fetch real-time air quality data from external sources
- **Key Features**:
  - Multi-source data collection
  - Retry mechanism with exponential backoff
  - Geographic coordinate fallback
  - Data caching (1-hour TTL)
  - Error handling and logging

#### **Module 3: Data Analysis** (`src/analysis/`)
- **Files**:
  - `aqi_calculator.py` - AQI computation
  - `health_impact.py` - Health risk assessment
- **Purpose**: Calculate AQI and assess health impacts
- **Key Features**:
  - Multi-pollutant AQI calculation
  - Dominant pollutant identification
  - Risk categorization
  - Population impact estimation

#### **Module 4: Forecasting** (`src/forecasting/`)
- **Files**:
  - `prophet_forecaster.py` - Facebook Prophet implementation
  - `arima_forecaster.py` - ARIMA model implementation
- **Purpose**: Time-series prediction of air quality
- **Key Features**:
  - 7-day ahead forecasting
  - Confidence intervals
  - Seasonal decomposition
  - Model persistence

#### **Module 5: Database Operations** (`src/database/`)
- **Files**:
  - `mongodb_operations.py` - MongoDB CRUD operations
  - `operations.py` - High-level database interface
  - `models.py` - Data models/schemas
- **Purpose**: Data persistence and retrieval
- **Key Features**:
  - Connection pooling
  - Indexed queries
  - Batch operations
  - Data aggregation

#### **Module 6: Alert System** (`src/alerts/`)
- **File**: `alert_manager.py`
- **Purpose**: Monitor thresholds and generate alerts
- **Key Features**:
  - AQI threshold monitoring
  - Pollutant-specific alerts
  - Severity categorization
  - File-based logging (V1)

#### **Module 7: User Interface** (`app.py`)
- **Purpose**: Interactive web dashboard
- **Pages**:
  1. Dashboard - Real-time AQI display
  2. City Comparison - Multi-city analysis
  3. Forecasting - 7-day predictions
  4. Health Impact - Risk assessment
  5. Historical Trends - Time-series visualization

---

## 4. Data Flow Pipeline

### 4.1 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: DATA COLLECTION (Every 1 hour)                          │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. User triggers: `python scripts/fetch_data.py`
    2. DataCollector initialized
    3. For each city (Islamabad, Rawalpindi, Karachi):
       a. Check cache (1-hour validity)
       b. If expired/missing:
          - Call WAQI API with city name
          - On failure: Use geo-coordinates fallback
          - On success: Parse JSON response
       c. Extract pollutant measurements
       d. Save to cache (CSV + metadata JSON)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: DATA PREPROCESSING                                      │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. Validate data types and ranges
    2. Handle missing values:
       - Use interpolation for gaps < 3 hours
       - Use historical averages for larger gaps
    3. Remove outliers (beyond 3 standard deviations)
    4. Normalize timestamps to UTC
    5. Convert units (if necessary)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: AQI CALCULATION                                         │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. For each pollutant:
       a. Find appropriate AQI breakpoint
       b. Apply linear interpolation formula:
          AQI = [(IHi-ILo)/(BPHi-BPLo)] × (Cp-BPLo) + ILo
          Where:
          - IHi, ILo = AQI range values
          - BPHi, BPLo = Breakpoint concentration range
          - Cp = Pollutant concentration
    2. Determine overall AQI (maximum of all pollutants)
    3. Identify dominant pollutant
    4. Assign health category (Good/Moderate/Unhealthy/etc.)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: HEALTH IMPACT ASSESSMENT                                │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. Calculate respiratory risk score (0-100):
       - PM2.5 weight: 40%
       - PM10 weight: 30%
       - NO2 weight: 20%
       - SO2 weight: 10%
    2. Calculate cardiovascular risk score (0-100):
       - PM2.5 weight: 50%
       - PM10 weight: 25%
       - NO2 weight: 15%
       - CO weight: 10%
    3. Estimate affected population:
       - General population: Based on AQI level
       - Sensitive groups: Children (30%), Elderly (6%), etc.

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: DATABASE STORAGE                                        │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. Save to MongoDB collections:
       a. air_quality_measurements (raw measurements)
       b. aqi_history (calculated AQI values)
       c. health_impacts (health assessment results)
    2. Create indexes on timestamp and city fields
    3. Return confirmation

┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: GAP FILLING (Automatic in Dashboard)                    │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. On dashboard load:
       a. Check for missing dates in last 180 days
       b. If gaps ≤ 30 days:
          - Generate synthetic data using:
            • Seasonal factors (winter: 1.4x, summer: 0.8x)
            • Random daily variation (±10%)
            • City-specific base values
          - Mark as "Gap-filled" in source
       c. Save to database

┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: FORECASTING (On-demand)                                 │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. User navigates to Forecasting page
    2. Fetch 180 days of historical data from MongoDB
    3. For each pollutant (PM2.5, PM10, NO2, SO2, CO, O3):
       a. Prepare data:
          - Aggregate to daily averages
          - Remove outliers (3σ rule)
          - Fill missing dates with interpolation
       b. Train Prophet model:
          - Daily seasonality: ON
          - Weekly seasonality: ON
          - Yearly seasonality: OFF
          - Changepoint prior scale: 0.05
       c. Generate 7-day forecast
       d. Calculate confidence intervals (95%)
    4. Combine forecasts:
       - Calculate predicted AQI for each day
       - Determine category and dominant pollutant
    5. Display results with historical comparison

┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: VISUALIZATION (Real-time Dashboard)                     │
└─────────────────────────────────────────────────────────────────┘
    ↓
    1. Streamlit app loads
    2. Fetch current AQI from database
    3. Render interactive visualizations:
       - AQI gauge chart
       - Pollutant bar charts
       - City comparison map
       - Historical trend lines
       - Forecast charts
    4. Update every hour (via cache TTL)
```

### 4.2 Data Transformation Steps

**Raw API Response → Processed Measurement**

```python
# Raw WAQI Response
{
  "aqi": 156,
  "iaqi": {
    "pm25": {"v": 65.3},
    "pm10": {"v": 120.5}
  },
  "time": {"iso": "2026-05-06T10:00:00Z"}
}

# ↓ TRANSFORMATION ↓

# Processed DataFrame
{
  "city": "Islamabad",
  "parameter": "pm25",
  "value": 65.3,
  "unit": "µg/m³",
  "timestamp": "2026-05-06 10:00:00",
  "source": "WAQI",
  "location": "Islamabad (F-9 Park)",
  "latitude": 33.6844,
  "longitude": 73.0479
}

# ↓ AQI CALCULATION ↓

# AQI Result
{
  "aqi": 156,
  "category": "Unhealthy",
  "dominant_pollutant": "pm25",
  "color": "#FF0000",
  "health_message": "Everyone may begin to experience health effects",
  "pollutant_aqis": {
    "pm25": 156,
    "pm10": 98
  }
}

# ↓ HEALTH ASSESSMENT ↓

# Health Impact
{
  "respiratory_risk": 72.5,
  "cardiovascular_risk": 65.3,
  "overall_risk": "High",
  "affected_population": {
    "general_affected": 840000,
    "children_at_risk": 252000,
    "elderly_at_risk": 42000,
    "respiratory_patients_at_risk": 35000
  }
}
```

---

## 5. File Structure & Responsibilities

### 5.1 Directory Organization

```
AQI Prediction/
│
├── app.py                          # Main Streamlit dashboard application
│
├── config/
│   ├── __init__.py
│   └── settings.py                 # All configuration constants
│
├── src/                            # Source code modules
│   ├── __init__.py
│   │
│   ├── data_acquisition/           # Data collection layer
│   │   ├── __init__.py
│   │   ├── collector.py           # Main data collector orchestrator
│   │   ├── waqi_api.py            # WAQI API client
│   │   └── openaq_api.py          # OpenAQ API client
│   │
│   ├── analysis/                   # Data analysis layer
│   │   ├── __init__.py
│   │   ├── aqi_calculator.py      # AQI computation engine
│   │   └── health_impact.py       # Health risk assessment
│   │
│   ├── forecasting/                # Prediction layer
│   │   ├── __init__.py
│   │   ├── prophet_forecaster.py  # Facebook Prophet models
│   │   └── arima_forecaster.py    # ARIMA/SARIMA models
│   │
│   ├── database/                   # Data persistence layer
│   │   ├── __init__.py
│   │   ├── mongodb_operations.py  # MongoDB CRUD operations
│   │   ├── operations.py          # High-level DB interface
│   │   └── models.py              # Data models/schemas
│   │
│   ├── alerts/                     # Alert management
│   │   ├── __init__.py
│   │   └── alert_manager.py       # Alert threshold monitoring
│   │
│   └── utils/                      # Utility functions
│       └── __init__.py
│
├── scripts/                        # Executable scripts
│   ├── __init__.py
│   ├── fetch_data.py              # Data collection script
│   ├── init_database.py           # Database initialization
│   ├── run_forecasting.py         # Batch forecasting
│   ├── check_and_fill_gaps.py     # Gap detection and filling
│   ├── generate_historical_data.py # Historical data generation
│   ├── clear_database.py          # Database cleanup
│   ├── check_data.py              # Data validation
│   └── generate_report.py         # Report generation
│
├── data/                           # Data storage
│   ├── cache/                      # API response cache
│   │   ├── Islamabad_cache.csv
│   │   ├── Islamabad_meta.json
│   │   ├── Karachi_cache.csv
│   │   ├── Karachi_meta.json
│   │   ├── Rawalpindi_cache.csv
│   │   └── Rawalpindi_meta.json
│   ├── raw/                        # Raw API responses
│   └── processed/                  # Processed datasets
│
├── models/                         # Saved ML models
│   └── saved/                      # Trained model files
│
├── logs/                           # Application logs
│
├── alerts/                         # Alert files
│
├── reports/                        # Generated reports
│
├── docs/                           # Documentation
│
├── tests/                          # Unit tests
│   └── test_system.py
│
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API keys)
└── README.md                       # Project documentation
```

### 5.2 Key File Responsibilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| **app.py** | Main dashboard application | - Streamlit UI rendering<br>- Page navigation<br>- Data visualization<br>- Gap checking & auto-filling |
| **config/settings.py** | Configuration management | - API endpoints<br>- City coordinates<br>- AQI breakpoints<br>- Alert thresholds |
| **src/data_acquisition/collector.py** | Data orchestration | - `collect_current_data()`: Fetch latest data<br>- `collect_historical_data()`: Fetch from DB<br>- `_combine_sources()`: Merge API responses |
| **src/data_acquisition/waqi_api.py** | WAQI API integration | - `get_city_feed()`: Fetch by city name<br>- `get_geo_feed()`: Fetch by coordinates<br>- `parse_city_data()`: Parse response |
| **src/analysis/aqi_calculator.py** | AQI computation | - `calculate_aqi()`: Single pollutant AQI<br>- `calculate_multi_pollutant_aqi()`: Overall AQI<br>- `get_aqi_category()`: Categorization |
| **src/analysis/health_impact.py** | Health assessment | - `calculate_respiratory_risk()`: Respiratory score<br>- `calculate_cardiovascular_risk()`: Cardio score<br>- `assess_health_impact()`: Full assessment |
| **src/forecasting/prophet_forecaster.py** | Time-series prediction | - `train_model()`: Train Prophet model<br>- `forecast_pollutant()`: Generate predictions<br>- `forecast_all_pollutants()`: Batch forecasting |
| **src/forecasting/arima_forecaster.py** | ARIMA modeling | - `find_optimal_order()`: ARIMA parameter tuning<br>- `train_model()`: Fit ARIMA model<br>- `forecast()`: Generate predictions |
| **src/database/mongodb_operations.py** | Database operations | - `save_measurements()`: Insert measurements<br>- `get_measurements()`: Query data<br>- `save_aqi_history()`: Store AQI<br>- `get_aqi_trends()`: Retrieve trends |
| **scripts/fetch_data.py** | Data collection script | - Fetch data for all cities<br>- Calculate AQI<br>- Save to database |
| **scripts/init_database.py** | Database setup | - Create collections<br>- Create indexes |
| **scripts/run_forecasting.py** | Batch forecasting | - Generate forecasts for all cities<br>- Save predictions to DB |

---

## 6. Data Acquisition & Preprocessing

### 6.1 Data Sources

#### **Primary Source: WAQI (World Air Quality Index)**
- **Endpoint**: `https://api.waqi.info/feed/{city}/`
- **Authentication**: Token-based (`?token=YOUR_API_KEY`)
- **Coverage**: Global, real-time data
- **Update Frequency**: Hourly
- **Reliability**: High (99.5% uptime)

**Sample Request:**
```python
url = f"https://api.waqi.info/feed/Islamabad/"
params = {'token': 'YOUR_API_KEY'}
response = requests.get(url, params=params)
```

**Sample Response:**
```json
{
  "status": "ok",
  "data": {
    "aqi": 156,
    "idx": 2345,
    "city": {
      "name": "Islamabad, Pakistan"
    },
    "time": {
      "iso": "2026-05-06T10:00:00Z"
    },
    "iaqi": {
      "pm25": {"v": 65.3},
      "pm10": {"v": 120.5},
      "no2": {"v": 28.3},
      "so2": {"v": 12.1},
      "co": {"v": 0.7},
      "o3": {"v": 35.2}
    }
  }
}
```

#### **Secondary Source: OpenAQ (Optional)**
- **Endpoint**: `https://api.openaq.org/v3/locations`
- **Authentication**: API key in headers
- **Coverage**: Limited for Pakistan
- **Status**: Disabled in V1 due to unreliable data

### 6.2 Caching Mechanism

**Cache Files:**
- `data/cache/{city}_cache.csv` - Measurement data
- `data/cache/{city}_meta.json` - Metadata (timestamp, source)

**Cache Logic:**
```python
def _load_from_cache(self, city: str) -> Optional[pd.DataFrame]:
    meta_file = self.cache_dir / f"{city}_meta.json"
    cache_file = self.cache_dir / f"{city}_cache.csv"
    
    if not cache_file.exists():
        return None
    
    # Check cache age
    with open(meta_file, 'r') as f:
        meta = json.load(f)
    
    cache_age = datetime.now() - datetime.fromisoformat(meta['timestamp'])
    
    if cache_age.total_seconds() < CACHE_EXPIRY:  # 1 hour
        return pd.read_csv(cache_file)
    
    return None
```

### 6.3 Preprocessing Steps

#### **Step 1: Data Validation**
```python
# Check value ranges
valid_ranges = {
    'pm25': (0, 500),
    'pm10': (0, 1000),
    'no2': (0, 500),
    'so2': (0, 500),
    'co': (0, 50),
    'o3': (0, 400)
}

df = df[df['value'].between(valid_ranges[param][0], 
                             valid_ranges[param][1])]
```

#### **Step 2: Missing Value Handling**
```python
# Interpolate small gaps
df['value'] = df['value'].interpolate(method='linear', limit=3)

# Use historical averages for larger gaps
historical_avg = df.groupby('parameter')['value'].mean()
df['value'] = df['value'].fillna(df['parameter'].map(historical_avg))
```

#### **Step 3: Outlier Removal**
```python
# Remove values beyond 3 standard deviations
mean = df['value'].mean()
std = df['value'].std()
df = df[(df['value'] >= mean - 3*std) & 
        (df['value'] <= mean + 3*std)]
```

#### **Step 4: Timestamp Normalization**
```python
# Convert to UTC
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC')

# Round to nearest hour
df['timestamp'] = df['timestamp'].dt.floor('H')
```

---

## 7. AQI Calculation Engine

### 7.1 AQI Formula (US EPA Standard)

The **Air Quality Index (AQI)** is calculated using linear interpolation:

```
         (IHi - ILo)
AQI = ───────────────── × (Cp - BPLo) + ILo
         (BPHi - BPLo)
```

**Where:**
- **Cp** = Pollutant concentration (measured value)
- **BPLo** = Breakpoint concentration ≤ Cp
- **BPHi** = Breakpoint concentration ≥ Cp
- **ILo** = AQI value corresponding to BPLo
- **IHi** = AQI value corresponding to BPHi

### 7.2 AQI Breakpoints

#### **PM2.5 Breakpoints:**

| Concentration (µg/m³) | AQI Range | Category |
|-----------------------|-----------|----------|
| 0.0 - 12.0 | 0 - 50 | Good |
| 12.1 - 35.4 | 51 - 100 | Moderate |
| 35.5 - 55.4 | 101 - 150 | Unhealthy for Sensitive Groups |
| 55.5 - 150.4 | 151 - 200 | Unhealthy |
| 150.5 - 250.4 | 201 - 300 | Very Unhealthy |
| 250.5 - 500.4 | 301 - 500 | Hazardous |

#### **PM10 Breakpoints:**

| Concentration (µg/m³) | AQI Range | Category |
|-----------------------|-----------|----------|
| 0 - 54 | 0 - 50 | Good |
| 55 - 154 | 51 - 100 | Moderate |
| 155 - 254 | 101 - 150 | Unhealthy for Sensitive Groups |
| 255 - 354 | 151 - 200 | Unhealthy |
| 355 - 424 | 201 - 300 | Very Unhealthy |
| 425 - 604 | 301 - 500 | Hazardous |

*(Similar breakpoints exist for NO₂, SO₂, CO, O₃)*

### 7.3 Multi-Pollutant AQI

The **overall AQI** is determined by taking the **maximum AQI** among all pollutants:

```python
aqi_values = {
    'pm25': 156,
    'pm10': 98,
    'no2': 45,
    'so2': 30,
    'co': 25,
    'o3': 60
}

overall_aqi = max(aqi_values.values())  # 156
dominant_pollutant = 'pm25'
```

### 7.4 AQI Categories

| AQI Range | Category | Color | Health Message |
|-----------|----------|-------|----------------|
| 0-50 | Good | Green (#00E400) | Air quality is satisfactory |
| 51-100 | Moderate | Yellow (#FFFF00) | Acceptable for most people |
| 101-150 | Unhealthy for Sensitive Groups | Orange (#FF7E00) | Sensitive groups should limit outdoor exposure |
| 151-200 | Unhealthy | Red (#FF0000) | Everyone may experience health effects |
| 201-300 | Very Unhealthy | Purple (#8F3F97) | Health alert: everyone may experience serious effects |
| 301-500 | Hazardous | Maroon (#7E0023) | Health warning: emergency conditions |

### 7.5 Implementation Example

```python
def calculate_aqi(self, pollutant: str, concentration: float) -> int:
    breakpoints = self.breakpoints[pollutant]
    
    # Find appropriate breakpoint
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= concentration <= bp_high:
            # Apply formula
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * \
                  (concentration - bp_low) + aqi_low
            return int(round(aqi))
    
    # Concentration exceeds all breakpoints
    return 500
```

---

## 8. Prediction/Forecasting Module

### 8.1 Forecasting Approach

The system uses **two complementary forecasting models**:

#### **Model 1: Facebook Prophet (Primary)**
- **Type**: Additive regression model
- **Components**: Trend + Seasonality + Holidays
- **Strengths**: 
  - Handles missing data well
  - Automatic detection of trend changes
  - Easy to interpret
- **Use Case**: General 7-day forecasting

#### **Model 2: ARIMA (Alternative)**
- **Type**: Autoregressive Integrated Moving Average
- **Components**: AR(p) + I(d) + MA(q)
- **Strengths**:
  - Well-suited for stationary time series
  - Statistical rigor
- **Use Case**: Short-term predictions, model comparison

### 8.2 Prophet Forecasting Pipeline

#### **Step 1: Data Preparation**
```python
def prepare_data(self, df: pd.DataFrame, parameter: str) -> pd.DataFrame:
    # Filter for parameter
    param_data = df[df['parameter'] == parameter]
    
    # Aggregate to daily averages
    param_data['date'] = pd.to_datetime(param_data['timestamp']).dt.date
    daily_avg = param_data.groupby('date')['value'].mean().reset_index()
    
    # Format for Prophet (requires 'ds' and 'y' columns)
    daily_avg.columns = ['ds', 'y']
    daily_avg['ds'] = pd.to_datetime(daily_avg['ds'])
    
    # Remove outliers (3σ rule)
    mean, std = daily_avg['y'].mean(), daily_avg['y'].std()
    daily_avg = daily_avg[
        (daily_avg['y'] >= mean - 3*std) & 
        (daily_avg['y'] <= mean + 3*std)
    ]
    
    return daily_avg
```

#### **Step 2: Model Training**
```python
def train_model(self, df: pd.DataFrame, parameter: str) -> Prophet:
    prophet_data = self.prepare_data(df, parameter)
    
    model = Prophet(
        daily_seasonality=True,      # Capture daily patterns
        weekly_seasonality=True,     # Capture weekly patterns
        yearly_seasonality=False,    # Not enough data for yearly
        changepoint_prior_scale=0.05,  # Trend flexibility
        seasonality_prior_scale=10.0,  # Seasonality flexibility
        interval_width=0.95          # 95% confidence interval
    )
    
    model.fit(prophet_data)
    return model
```

#### **Step 3: Generate Forecast**
```python
def forecast_pollutant(self, city: str, parameter: str, 
                       historical_data: pd.DataFrame, 
                       days_ahead: int = 7) -> pd.DataFrame:
    # Train model
    model = self.train_model(historical_data, parameter)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=days_ahead)
    
    # Generate forecast
    forecast = model.predict(future)
    
    # Extract predictions
    predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
    predictions.columns = ['date', 'predicted_value', 'lower_bound', 'upper_bound']
    
    return predictions
```

#### **Step 4: AQI Forecast**
```python
def get_overall_aqi_forecast(self, forecasts: Dict) -> pd.DataFrame:
    # Combine all pollutant forecasts
    all_forecasts = []
    
    for date in forecast_dates:
        pollutant_values = {
            param: forecast_df[forecast_df['date'] == date]['predicted_value'].values[0]
            for param, forecast_df in forecasts.items()
        }
        
        # Calculate AQI
        aqi_info = self.aqi_calc.calculate_multi_pollutant_aqi(pollutant_values)
        
        all_forecasts.append({
            'date': date,
            'predicted_aqi': aqi_info['aqi'],
            'aqi_category': aqi_info['category'],
            'dominant_pollutant': aqi_info['dominant_pollutant']
        })
    
    return pd.DataFrame(all_forecasts)
```

### 8.3 ARIMA Forecasting

#### **Step 1: Stationarity Check**
```python
def check_stationarity(self, series: pd.Series) -> Dict:
    result = adfuller(series, autolag='AIC')
    
    return {
        'adf_statistic': result[0],
        'p_value': result[1],
        'is_stationary': result[1] < 0.05
    }
```

#### **Step 2: Find Optimal Order**
```python
def find_optimal_order(self, series: pd.Series) -> Tuple[int, int, int]:
    # Check stationarity
    stationarity = self.check_stationarity(series)
    d = 0 if stationarity['is_stationary'] else 1
    
    # Grid search for p and q
    best_aic = np.inf
    best_order = None
    
    for p in range(0, 6):
        for q in range(0, 6):
            try:
                model = ARIMA(series, order=(p, d, q))
                fitted = model.fit()
                
                if fitted.aic < best_aic:
                    best_aic = fitted.aic
                    best_order = (p, d, q)
            except:
                continue
    
    return best_order
```

#### **Step 3: Train & Forecast**
```python
def train_model(self, series: pd.Series) -> ARIMA:
    order = self.find_optimal_order(series)
    model = ARIMA(series, order=order)
    fitted_model = model.fit()
    return fitted_model

def forecast(self, model: ARIMA, steps: int = 7) -> pd.DataFrame:
    forecast = model.forecast(steps=steps)
    conf_int = model.get_forecast(steps=steps).conf_int()
    
    return pd.DataFrame({
        'predicted_value': forecast,
        'lower_bound': conf_int[:, 0],
        'upper_bound': conf_int[:, 1]
    })
```

### 8.4 Model Evaluation

**Metrics Used:**
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
```

---

## 9. Database Architecture

### 9.1 Database Choice: MongoDB

**Why MongoDB?**
- **Schema Flexibility**: Easy to adapt to changing data structures
- **Performance**: Fast writes for time-series data
- **Scalability**: Horizontal scaling support
- **JSON-like Documents**: Natural fit for API responses

### 9.2 Database Schema

#### **Collection 1: air_quality_measurements**
Stores raw pollutant measurements.

```javascript
{
  "_id": ObjectId("..."),
  "city": "Islamabad",
  "parameter": "pm25",
  "value": 65.3,
  "unit": "µg/m³",
  "timestamp": ISODate("2026-05-06T10:00:00Z"),
  "source": "WAQI",
  "location": "Islamabad (F-9 Park)",
  "latitude": 33.6844,
  "longitude": 73.0479
}
```

**Indexes:**
- `{city: 1, timestamp: -1}`
- `{city: 1, parameter: 1}`
- `{timestamp: -1}`

#### **Collection 2: aqi_history**
Stores calculated AQI values.

```javascript
{
  "_id": ObjectId("..."),
  "city": "Islamabad",
  "timestamp": ISODate("2026-05-06T10:00:00Z"),
  "aqi": 156,
  "category": "Unhealthy",
  "dominant_pollutant": "pm25",
  "pollutants": {
    "pm25": 65.3,
    "pm10": 120.5,
    "no2": 28.3,
    "so2": 12.1,
    "co": 0.7,
    "o3": 35.2
  }
}
```

**Indexes:**
- `{city: 1, timestamp: -1}`

#### **Collection 3: health_impacts**
Stores health risk assessments.

```javascript
{
  "_id": ObjectId("..."),
  "city": "Islamabad",
  "date": ISODate("2026-05-06T00:00:00Z"),
  "respiratory_risk": 72.5,
  "cardiovascular_risk": 65.3,
  "overall_risk": "High",
  "risk_category": "High",
  "affected_population": {
    "general_affected": 840000,
    "children_at_risk": 252000,
    "elderly_at_risk": 42000,
    "respiratory_patients_at_risk": 35000,
    "cardiovascular_patients_at_risk": 56000
  },
  "advisory": "Sensitive groups should avoid outdoor activities. General public should limit prolonged outdoor exertion."
}
```

**Indexes:**
- `{city: 1, date: -1}`

#### **Collection 4: forecasts**
Stores prediction results.

```javascript
{
  "_id": ObjectId("..."),
  "city": "Islamabad",
  "parameter": "pm25",
  "forecast_date": ISODate("2026-05-07T00:00:00Z"),
  "predicted_value": 68.2,
  "lower_bound": 55.4,
  "upper_bound": 81.0,
  "confidence": 0.95,
  "model": "Prophet",
  "created_at": ISODate("2026-05-06T10:00:00Z")
}
```

**Indexes:**
- `{city: 1, forecast_date: 1}`
- `{created_at: -1}`

#### **Collection 5: monitoring_stations**
Stores station metadata.

```javascript
{
  "_id": ObjectId("..."),
  "station_id": "PK-ISB-001",
  "city": "Islamabad",
  "name": "F-9 Park Station",
  "latitude": 33.6844,
  "longitude": 73.0479,
  "elevation": 540,
  "status": "active"
}
```

**Indexes:**
- `{station_id: 1}` (unique)
- `{city: 1}`

### 9.3 Database Operations

#### **Insert Measurement**
```python
def save_measurements(self, df: pd.DataFrame) -> int:
    records = df.to_dict('records')
    
    # Ensure datetime objects
    for record in records:
        if isinstance(record.get('timestamp'), str):
            record['timestamp'] = pd.to_datetime(record['timestamp'])
    
    result = self.measurements.insert_many(records)
    return len(result.inserted_ids)
```

#### **Query Historical Data**
```python
def get_measurements(self, city: str, start_date: datetime, 
                     end_date: datetime) -> pd.DataFrame:
    query = {
        'city': city,
        'timestamp': {'$gte': start_date, '$lte': end_date}
    }
    
    cursor = self.measurements.find(query).sort('timestamp', 1)
    data = list(cursor)
    
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame()
```

#### **Get Current AQI**
```python
def get_current_aqi(self, city: str) -> Optional[Dict]:
    query = {'city': city}
    result = self.aqi_history.find_one(
        query, 
        sort=[('timestamp', -1)]
    )
    
    return result
```

#### **Get AQI Trends**
```python
def get_aqi_trends(self, city: str, days: int = 30) -> pd.DataFrame:
    date_from = datetime.now() - timedelta(days=days)
    
    query = {
        'city': city,
        'timestamp': {'$gte': date_from}
    }
    
    cursor = self.aqi_history.find(query).sort('timestamp', 1)
    data = list(cursor)
    
    return pd.DataFrame(data)
```

---

## 10. Health Impact Assessment

### 10.1 Risk Calculation Methodology

#### **Respiratory Risk Score (0-100)**

**Formula:**
```
Respiratory Risk = (PM2.5 Risk × 0.40) + 
                   (PM10 Risk × 0.30) + 
                   (NO₂ Risk × 0.20) + 
                   (SO₂ Risk × 0.10)
```

**Individual Pollutant Risk:**
```python
pm25_risk = min((pm25 / 250.0) * 100, 100)  # Normalized to 0-100
pm10_risk = min((pm10 / 500.0) * 100, 100)
no2_risk = min((no2 / 400.0) * 100, 100)
so2_risk = min((so2 / 300.0) * 100, 100)
```

#### **Cardiovascular Risk Score (0-100)**

**Formula:**
```
Cardiovascular Risk = (PM2.5 Risk × 0.50) + 
                      (PM10 Risk × 0.25) + 
                      (NO₂ Risk × 0.15) + 
                      (CO Risk × 0.10)
```

### 10.2 Population Impact Estimation

#### **City Populations**
- Islamabad: 1,200,000
- Rawalpindi: 2,200,000
- Karachi: 16,000,000

#### **Sensitive Groups**
- Children (<15 years): 30%
- Elderly (>65 years): 6%
- Respiratory patients: 5%
- Cardiovascular patients: 8%

#### **Calculation Example**

For Islamabad with AQI = 156 (Unhealthy):

```python
population = 1_200_000

# Base affected percentage based on AQI
if aqi > 150:
    affected_percentage = 0.70  # 70% affected
else:
    affected_percentage = 0.40  # 40% affected

general_affected = population * affected_percentage
# = 1,200,000 × 0.70 = 840,000

children_at_risk = population * 0.30  # 30% are children
# = 1,200,000 × 0.30 = 360,000

elderly_at_risk = population * 0.06  # 6% are elderly
# = 1,200,000 × 0.06 = 72,000

respiratory_patients_at_risk = population * 0.05
# = 1,200,000 × 0.05 = 60,000
```

### 10.3 Health Advisory Generation

```python
def generate_advisory(self, aqi: int, risk_category: str) -> str:
    if aqi <= 50:
        return "Air quality is good. Enjoy outdoor activities."
    elif aqi <= 100:
        return "Air quality is acceptable. Sensitive individuals should consider limiting prolonged outdoor exertion."
    elif aqi <= 150:
        return "Sensitive groups (children, elderly, respiratory patients) should limit prolonged outdoor exertion."
    elif aqi <= 200:
        return "Everyone should limit prolonged outdoor exertion. Sensitive groups should avoid outdoor activities."
    elif aqi <= 300:
        return "Everyone should avoid prolonged outdoor exertion. Sensitive groups should remain indoors."
    else:
        return "HEALTH ALERT: Everyone should avoid all outdoor activities."
```

---

## 11. Alert Management System

### 11.1 Alert Thresholds

| Alert Type | Threshold | Severity |
|------------|-----------|----------|
| AQI Alert | AQI ≥ 150 | Medium |
| AQI High Alert | AQI ≥ 200 | High |
| AQI Critical | AQI ≥ 300 | Critical |
| PM2.5 Alert | PM2.5 ≥ 55.5 µg/m³ | Medium |
| PM10 Alert | PM10 ≥ 155 µg/m³ | Medium |

### 11.2 Alert Workflow

```
1. Check AQI threshold
   ├─ If AQI ≥ 150 → Generate Alert
   └─ Determine severity (medium/high/critical)

2. Check pollutant thresholds
   ├─ For each pollutant
   │  ├─ Compare to threshold
   │  └─ Generate alert if exceeded
   └─ Aggregate alerts

3. Log alerts
   ├─ Write to alerts/alert.txt
   └─ Timestamp and severity

4. [V2 Feature] Send notifications
   ├─ Email to subscribers
   └─ SMS to registered numbers
```

### 11.3 Alert Message Format

```python
def _generate_aqi_alert_message(self, city: str, aqi: int, severity: str) -> str:
    return f"""
    ⚠️ AIR QUALITY ALERT - {severity.upper()}
    
    City: {city}
    Current AQI: {aqi}
    Category: {self._get_aqi_category(aqi)}
    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Health Advisory:
    {self._get_health_advisory(aqi)}
    
    Recommended Actions:
    - Limit outdoor activities
    - Use air purifiers indoors
    - Wear N95 masks if going outside
    - Keep windows closed
    """
```

---

## 12. User Interface (Dashboard)

### 12.1 Dashboard Pages

#### **Page 1: Home Dashboard**
**Components:**
1. **Metric Cards**
   - Current AQI value
   - AQI category
   - Dominant pollutant
   - Last update time

2. **AQI Gauge Chart**
   - Circular gauge (0-500)
   - Color-coded zones
   - Current value needle

3. **Pollutant Bar Chart**
   - Individual AQI for each pollutant
   - Color gradient (green → red)

4. **Health Recommendations**
   - General public advisory
   - Sensitive groups advisory
   - Color-coded alert boxes

5. **Latest Measurements Table**
   - Last 10 measurements
   - Parameter, value, unit, timestamp

#### **Page 2: City Comparison**
**Components:**
1. **Interactive Map**
   - Marker for each city
   - Bubble size = AQI value
   - Color = AQI category
   - Hover: City details

2. **Comparison Table**
   - All cities in one view
   - Sortable columns
   - Color-coded rows

3. **Bar Chart Comparison**
   - AQI values side-by-side
   - Category color coding

#### **Page 3: Forecasting**
**Components:**
1. **Combined Trend Chart**
   - Historical data (past 200 days) - solid line
   - Forecast (next 7 days) - dashed line
   - Confidence intervals - shaded area

2. **Forecast Table**
   - Date, Predicted AQI, Category, Main Pollutant

3. **Pollutant-wise Forecasts**
   - Individual charts for each pollutant
   - Expandable accordions

#### **Page 4: Health Impact**
**Components:**
1. **Risk Score Metrics**
   - Respiratory risk (0-100)
   - Cardiovascular risk (0-100)
   - Overall risk category

2. **Risk Bar Chart**
   - Visual comparison of risks

3. **Affected Population Stats**
   - General population affected
   - Children at risk
   - Elderly at risk
   - Patients at risk

4. **Health Advisory**
   - Detailed recommendations

#### **Page 5: Historical Trends**
**Components:**
1. **Time Period Selector**
   - Slider: 7-90 days

2. **Pollutant Trend Charts**
   - Line charts for each pollutant
   - Daily averages
   - Expandable sections

3. **Statistics**
   - Average, Maximum, Minimum values

### 12.2 Streamlit App Structure

```python
# Page configuration
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide"
)

# Sidebar navigation
page = st.sidebar.radio("Select Page", [
    "🏠 Dashboard",
    "📊 City Comparison",
    "📈 Forecasting",
    "🏥 Health Impact",
    "📜 Historical Trends"
])

# Initialize components (cached)
@st.cache_resource
def get_components():
    return {
        'collector': DataCollector(),
        'aqi_calc': AQICalculator(),
        'health_assessor': HealthImpactAssessor(),
        'db_ops': DatabaseOperations()
    }

# Auto gap-filling on load
@st.cache_data(ttl=3600)  # Cache for 1 hour
def check_and_fill_data_gaps():
    # Check for missing dates
    # Auto-fill gaps up to 30 days
    # Return gap statistics
    pass

# Page rendering
if page == "🏠 Dashboard":
    # Render dashboard
elif page == "📊 City Comparison":
    # Render comparison
# ... etc.
```

### 12.3 Data Caching Strategy

```python
# Cache components initialization (runs once)
@st.cache_resource
def get_components():
    return {...}

# Cache data fetching (refreshes every hour)
@st.cache_data(ttl=3600)
def fetch_current_data():
    return collector.collect_current_data()

# Cache gap filling (refreshes every hour)
@st.cache_data(ttl=3600)
def check_and_fill_data_gaps():
    return gap_stats
```

---

## 13. Deployment & Execution Workflow

### 13.1 System Setup

#### **Step 1: Environment Setup**
```bash
# Clone repository
git clone <repository-url>
cd "AQI Prediction"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### **Step 2: Configuration**
Create `.env` file:
```env
# API Keys
WAQI_API_KEY=your_waqi_api_key_here
OPENAQ_API_KEY=your_openaq_api_key_here

# Database
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=air_quality_db

# Environment
APP_ENV=production
LOG_LEVEL=INFO
```

#### **Step 3: Database Initialization**
```bash
# Start MongoDB
# (Ensure MongoDB is installed and running)

# Initialize database
python scripts/init_database.py
```

### 13.2 Data Collection Workflow

#### **Manual Data Fetch**
```bash
# Fetch latest data for all cities
python scripts/fetch_data.py
```

**What it does:**
1. Fetches data from WAQI API
2. Validates and preprocesses data
3. Calculates AQI
4. Assesses health impact
5. Saves to MongoDB

#### **Automated Data Fetch (Scheduled)**
```bash
# Windows Task Scheduler
# Create task to run scripts/fetch_data.py every hour
```

### 13.3 Running the Dashboard

```bash
# Start Streamlit app
streamlit run app.py
```

**Access:** http://localhost:8501

### 13.4 Running Forecasts

```bash
# Generate 7-day forecasts for all cities
python scripts/run_forecasting.py
```

### 13.5 Data Management Scripts

#### **Check Data Quality**
```bash
python scripts/check_data.py
```

#### **Fill Missing Data**
```bash
python scripts/check_and_fill_gaps.py
```

#### **Clear Database**
```bash
python scripts/clear_database.py
```

#### **Generate Report**
```bash
python scripts/generate_report.py
```

### 13.6 Production Deployment

#### **Option 1: Streamlit Cloud**
```bash
# Push to GitHub
git push origin main

# Deploy on Streamlit Cloud
# - Connect GitHub repository
# - Set environment variables
# - Deploy
```

#### **Option 2: Heroku**
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create aqi-prediction-pakistan
git push heroku main
```

#### **Option 3: Docker**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t aqi-prediction .
docker run -p 8501:8501 aqi-prediction
```

### 13.7 Monitoring & Maintenance

#### **Log Files**
- Location: `logs/`
- Format: Timestamped entries
- Rotation: Daily

#### **Database Backups**
```bash
# MongoDB backup
mongodump --uri="mongodb://localhost:27017/air_quality_db" --out=backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/air_quality_db" backup/air_quality_db/
```

#### **Performance Monitoring**
- Monitor API response times
- Track database query performance
- Monitor Streamlit app responsiveness

---

## 14. Summary: Complete Data Flow

### 14.1 Hourly Data Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: scripts/fetch_data.py (Hourly Cron Job)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DATA ACQUISITION                                                 │
│ • DataCollector.collect_current_data()                          │
│   - WAQIAPI.get_city_feed(city)                                 │
│   - Parse JSON response                                          │
│   - Extract pollutants: PM2.5, PM10, NO₂, SO₂, CO, O₃          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PREPROCESSING                                                    │
│ • Validate value ranges                                          │
│ • Remove outliers (3σ rule)                                      │
│ • Interpolate missing values (limit=3)                          │
│ • Normalize timestamps to UTC                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ AQI CALCULATION                                                  │
│ • AQICalculator.calculate_multi_pollutant_aqi()                 │
│   - Calculate individual AQI for each pollutant                  │
│   - Select maximum AQI (dominant pollutant approach)            │
│   - Assign category (Good/Moderate/Unhealthy/...)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ HEALTH IMPACT ASSESSMENT                                         │
│ • HealthImpactAssessor.assess_health_impact()                   │
│   - Calculate respiratory risk (0-100)                          │
│   - Calculate cardiovascular risk (0-100)                       │
│   - Estimate affected population                                │
│   - Generate health advisory                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE STORAGE                                                 │
│ • MongoDB.save_measurements(df)                                  │
│ • MongoDB.save_aqi_history(city, aqi_data)                      │
│ • MongoDB.save_health_impact(city, health_data)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DASHBOARD UPDATE                                                 │
│ • Streamlit cache invalidation (1-hour TTL)                     │
│ • Auto-refresh on next page load                                │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 On-Demand Forecasting Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: User navigates to Forecasting page                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ HISTORICAL DATA RETRIEVAL                                        │
│ • MongoDB.get_measurements(city, days_back=180)                 │
│ • Returns 180 days of measurements                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ DATA PREPARATION (Per Pollutant)                                │
│ • Aggregate to daily averages                                    │
│ • Remove outliers (3σ rule)                                      │
│ • Fill missing dates (linear interpolation)                     │
│ • Format for Prophet (ds, y columns)                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ MODEL TRAINING                                                   │
│ • For each pollutant:                                            │
│   - Initialize Prophet model                                     │
│   - Configure seasonality (daily, weekly)                       │
│   - Fit model on historical data                                │
│   - Generate 7-day forecast                                      │
│   - Calculate confidence intervals (95%)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ AQI FORECAST COMPUTATION                                         │
│ • For each forecasted day:                                       │
│   - Combine all pollutant predictions                           │
│   - Calculate predicted AQI                                      │
│   - Determine category and dominant pollutant                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ VISUALIZATION                                                    │
│ • Render combined chart (historical + forecast)                 │
│ • Display forecast table                                         │
│ • Show pollutant-wise predictions                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15. Key Technologies & Libraries

| Category | Technology | Purpose |
|----------|------------|---------|
| **Programming** | Python 3.9+ | Core language |
| **Web Framework** | Streamlit 1.28+ | Dashboard UI |
| **Database** | MongoDB 4.4+ | Data persistence |
| **Data Processing** | Pandas 2.0+ | Data manipulation |
| **Numerical Computing** | NumPy 1.24+ | Numerical operations |
| **Forecasting** | Prophet 1.1+ | Time-series prediction |
| **Forecasting** | Statsmodels 0.14+ | ARIMA models |
| **Visualization** | Plotly 5.17+ | Interactive charts |
| **API Client** | Requests 2.31+ | HTTP requests |
| **Database Driver** | PyMongo 4.5+ | MongoDB client |
| **Logging** | Loguru 0.7+ | Application logging |
| **Environment** | Python-dotenv 1.0+ | Config management |

---

## 16. Future Enhancements (V2)

1. **Email/SMS Alerts**: Implement real notification system
2. **Multi-user Support**: User authentication and personalized dashboards
3. **Mobile App**: React Native mobile application
4. **More Cities**: Expand to all major Pakistani cities
5. **Advanced ML**: LSTM/GRU neural networks for forecasting
6. **Air Quality Index Predictions**: Predict AQI directly instead of pollutant-wise
7. **Historical Data Export**: CSV/Excel export functionality
8. **API Endpoint**: RESTful API for external access
9. **Data Quality Metrics**: Reliability scores for measurements
10. **Satellite Data Integration**: Incorporate satellite-based AQI

---

## 17. Conclusion

This **Air Quality Index (AQI) Prediction & Monitoring System** provides a comprehensive solution for:

✅ **Real-time Monitoring**: Hourly data collection from reliable sources  
✅ **Accurate AQI Calculation**: US EPA standard implementation  
✅ **Predictive Analytics**: 7-day forecasting with confidence intervals  
✅ **Health Impact Assessment**: Population-level risk estimation  
✅ **User-friendly Interface**: Interactive web dashboard  
✅ **Data Persistence**: Robust MongoDB database  
✅ **Automated Gap Filling**: Ensures data continuity  

The modular architecture ensures **scalability**, **maintainability**, and **extensibility** for future enhancements.

---

**Document Version**: 1.0  
**Last Updated**: May 6, 2026  
**Author**: Final Year Project - Air Quality Analysis System  
**Institution**: [Your University Name]
