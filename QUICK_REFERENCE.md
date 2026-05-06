# Quick Reference Guide
## Air Quality Index (AQI) Prediction System - FYP

---

## 1-Minute Overview

**What**: Real-time AQI monitoring and 7-day forecasting system for Pakistani cities  
**Where**: Islamabad, Rawalpindi, Karachi  
**How**: API integration → Data processing → AQI calculation → ML forecasting → Web dashboard  
**Why**: Public health awareness and air quality prediction

---

## System at a Glance

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Source** | WAQI API | Real-time pollutant data |
| **Database** | MongoDB | Store measurements & AQI history |
| **Processing** | Python/Pandas | Data validation & cleaning |
| **Calculation** | US EPA Standard | AQI computation |
| **Forecasting** | Prophet + ARIMA | 7-day predictions |
| **Interface** | Streamlit | Interactive web dashboard |

---

## Key Modules

### 1. **Data Acquisition** (`src/data_acquisition/`)
- Fetches data from WAQI API every hour
- Handles API failures with retry logic
- Caches responses (1-hour TTL)
- **Key Files**: `collector.py`, `waqi_api.py`

### 2. **Data Processing** (`src/analysis/`)
- Validates data ranges
- Removes outliers (3σ rule)
- Calculates AQI using linear interpolation
- Assesses health impacts
- **Key Files**: `aqi_calculator.py`, `health_impact.py`

### 3. **Forecasting** (`src/forecasting/`)
- Trains Prophet models on 180 days of data
- Generates 7-day forecasts
- Calculates 95% confidence intervals
- **Key Files**: `prophet_forecaster.py`, `arima_forecaster.py`

### 4. **Database** (`src/database/`)
- Stores 5 collections in MongoDB
- Indexed for fast queries
- Handles time-series data efficiently
- **Key Files**: `mongodb_operations.py`

### 5. **Dashboard** (`app.py`)
- 5 interactive pages
- Real-time visualizations
- Auto gap-filling feature
- **Framework**: Streamlit

---

## Data Flow (Simplified)

```
API → Parse → Validate → Clean → Calculate AQI → Assess Health → Save to DB → Display
```

**Detailed:**
1. **Fetch** data from WAQI (hourly)
2. **Parse** JSON to DataFrame
3. **Validate** ranges and types
4. **Clean** outliers and missing values
5. **Calculate** AQI for each pollutant
6. **Assess** health risks (respiratory, cardiovascular)
7. **Save** to MongoDB (measurements, AQI, health impacts)
8. **Display** on Streamlit dashboard

---

## AQI Calculation (Simplified)

**Formula:**
```
AQI = [(IHi - ILo) / (BPHi - BPLo)] × (Cp - BPLo) + ILo
```

**Categories:**
- 0-50: Good (Green)
- 51-100: Moderate (Yellow)
- 101-150: Unhealthy for Sensitive (Orange)
- 151-200: Unhealthy (Red)
- 201-300: Very Unhealthy (Purple)
- 301-500: Hazardous (Maroon)

**Overall AQI** = Maximum of all pollutant AQIs

---

## Forecasting (Simplified)

**Prophet Model:**
- **Input**: 180 days of historical data
- **Components**: Trend + Daily seasonality + Weekly seasonality
- **Output**: 7-day forecast with confidence intervals
- **Training Time**: ~30 seconds per pollutant

**Process:**
1. Load 6 months of historical data
2. Preprocess (daily averages, remove outliers)
3. Train Prophet model for each pollutant
4. Generate 7-day predictions
5. Calculate overall AQI forecast
6. Visualize with historical comparison

---

## Database Schema (Quick View)

**Collections:**
1. **measurements** - Raw pollutant values
2. **aqi_history** - Calculated AQI values
3. **health_impacts** - Risk assessments
4. **forecasts** - Prediction results
5. **stations** - Monitoring station metadata

**Indexes:**
- `city + timestamp` (fast city-specific queries)
- `timestamp` (temporal queries)
- `city + parameter` (pollutant-specific queries)

---

## Health Impact Assessment

**Respiratory Risk = 0.40×PM2.5 + 0.30×PM10 + 0.20×NO₂ + 0.10×SO₂**  
**Cardiovascular Risk = 0.50×PM2.5 + 0.25×PM10 + 0.15×NO₂ + 0.10×CO**

**Affected Population:**
- General: Based on AQI level (70% at AQI > 150)
- Children: 30% of population
- Elderly: 6% of population
- Respiratory patients: 5% of population

---

## Scripts Overview

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/fetch_data.py` | Fetch latest AQI data | Hourly (automated) |
| `scripts/init_database.py` | Initialize MongoDB | Once (setup) |
| `scripts/run_forecasting.py` | Generate forecasts | Every 6 hours |
| `scripts/check_and_fill_gaps.py` | Fill missing data | Daily |
| `scripts/clear_database.py` | Reset database | Maintenance |
| `scripts/check_data.py` | Validate data quality | As needed |

---

## Dashboard Pages

### 1. **🏠 Dashboard**
- Current AQI gauge
- Pollutant bar chart
- Health recommendations
- Latest measurements table

### 2. **📊 City Comparison**
- Interactive map
- Comparison table
- Side-by-side bar charts

### 3. **📈 Forecasting**
- 7-day AQI predictions
- Historical vs forecast chart
- Pollutant-wise forecasts
- Confidence intervals

### 4. **🏥 Health Impact**
- Risk score metrics
- Affected population stats
- Health advisory

### 5. **📜 Historical Trends**
- Time period selector (7-90 days)
- Pollutant trend charts
- Statistics (avg, max, min)

---

## How to Run

### Setup (One-time)
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key in .env
WAQI_API_KEY=your_api_key_here

# Initialize database
python scripts/init_database.py
```

### Fetch Data
```bash
# Manual fetch
python scripts/fetch_data.py
```

### Run Dashboard
```bash
# Start Streamlit
streamlit run app.py

# Access at: http://localhost:8501
```

### Generate Forecasts
```bash
# Create 7-day predictions
python scripts/run_forecasting.py
```

---

## Key Features

✅ **Real-time Monitoring**: Hourly data updates  
✅ **Multi-city Support**: 3 major Pakistani cities  
✅ **6 Pollutants**: PM2.5, PM10, NO₂, SO₂, CO, O₃  
✅ **AQI Calculation**: US EPA standard  
✅ **Forecasting**: 7-day predictions with confidence intervals  
✅ **Health Impact**: Risk assessment for vulnerable populations  
✅ **Auto Gap-Filling**: Automatic missing data handling  
✅ **Interactive Dashboard**: 5 visualization pages  
✅ **Caching**: 1-hour cache for API responses  
✅ **Logging**: Comprehensive error tracking  

---

## Technical Highlights

### Data Preprocessing
- **Outlier Removal**: 3-sigma rule
- **Missing Values**: Linear interpolation (limit=3)
- **Normalization**: UTC timestamp standardization
- **Validation**: Range checks for each pollutant

### Forecasting Accuracy
- **Training Data**: 180 days (6 months)
- **Model**: Facebook Prophet (primary)
- **Seasonality**: Daily + Weekly
- **Confidence**: 95% intervals
- **Evaluation**: MAE, RMSE, MAPE

### Performance Optimization
- **Caching**: Streamlit `@st.cache_data` (1-hour TTL)
- **Database Indexing**: Compound indexes on city+timestamp
- **Batch Operations**: Bulk inserts for measurements
- **Lazy Loading**: On-demand forecast generation

---

## Project Structure (Simplified)

```
AQI Prediction/
├── app.py                      # Dashboard
├── config/settings.py          # Configuration
├── src/
│   ├── data_acquisition/       # API integration
│   ├── analysis/               # AQI & health
│   ├── forecasting/            # Prophet & ARIMA
│   ├── database/               # MongoDB ops
│   └── alerts/                 # Alert system
├── scripts/                    # Automation scripts
├── data/cache/                 # API cache
└── requirements.txt            # Dependencies
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| API timeout | Enable retry mechanism (max 3 attempts) |
| Missing data | Auto gap-filling (up to 30 days) |
| Database connection | Check MongoDB URI in .env |
| Forecast errors | Ensure 180+ days of historical data |
| Dashboard not loading | Clear Streamlit cache (`Ctrl+Shift+R`) |

---

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud (Free)
1. Push to GitHub
2. Connect repository on streamlit.io
3. Set environment variables
4. Deploy

### Docker
```bash
docker build -t aqi-prediction .
docker run -p 8501:8501 aqi-prediction
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Data Fetch Time | ~2-5 seconds/city |
| AQI Calculation Time | <1 second |
| Forecast Training Time | ~30 seconds/pollutant |
| Dashboard Load Time | ~3-5 seconds |
| Database Query Time | <100ms (with indexes) |
| API Cache Hit Rate | ~80% (hourly updates) |

---

## Future Enhancements

- 📧 Email/SMS alerts
- 📱 Mobile app
- 🌍 More cities
- 🧠 LSTM neural networks
- 📊 Advanced analytics
- 🔐 User authentication
- 📡 API endpoints

---

## Dependencies (Key Packages)

```
streamlit==1.28.0          # Dashboard
pandas==2.0.3              # Data processing
plotly==5.17.0             # Visualization
pymongo==4.5.0             # MongoDB
prophet==1.1.5             # Forecasting
statsmodels==0.14.0        # ARIMA
requests==2.31.0           # API calls
loguru==0.7.2              # Logging
```

---

## Quick Commands Cheat Sheet

```bash
# Setup
pip install -r requirements.txt
python scripts/init_database.py

# Data operations
python scripts/fetch_data.py              # Fetch latest data
python scripts/check_data.py              # Validate data
python scripts/check_and_fill_gaps.py     # Fill missing data
python scripts/clear_database.py          # Clear database

# Forecasting
python scripts/run_forecasting.py         # Generate forecasts

# Dashboard
streamlit run app.py                      # Start dashboard
streamlit run app.py --server.port=8080   # Custom port

# Database
mongodump --db air_quality_db             # Backup
mongorestore --db air_quality_db          # Restore
```

---

## Contact & Support

**Project Type**: Final Year Project (FYP)  
**Domain**: Air Quality Monitoring & Prediction  
**Technologies**: Python, MongoDB, Streamlit, Prophet  
**Cities Monitored**: Islamabad, Rawalpindi, Karachi  
**Data Source**: WAQI (World Air Quality Index)

---

## Key Takeaways

1. **Real-time + Predictive**: Combines current monitoring with 7-day forecasting
2. **Health-focused**: Not just AQI numbers, but actual health impact assessment
3. **Automated**: Hourly data fetching, auto gap-filling, scheduled forecasts
4. **User-friendly**: Interactive dashboard accessible to general public
5. **Scalable**: Modular architecture allows easy addition of cities/features
6. **Reliable**: Caching, retry logic, and error handling ensure robustness

---

**Document Version**: 1.0  
**Last Updated**: May 6, 2026  
**Purpose**: Quick reference for presentations and reports
