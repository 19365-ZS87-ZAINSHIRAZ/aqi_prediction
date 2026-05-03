# Quick Start Guide - AQI Prediction System

## Running the Dashboard

**Just one command - everything is automatic:**

```powershell
streamlit run app.py
```

The system will automatically:
- ✅ Fill missing days (up to 30 days gap)
- ✅ Fetch current data
- ✅ Generate 8-day forecasts
- ✅ Calculate health impacts

## About Current AQI Values

### Why might AQI values seem different from other sources?

The system uses **WAQI (World Air Quality Index) API**, which:
1. Gets data from specific monitoring stations
2. May show different values than city averages
3. Updates at different times than other sources

**Example:** If Islamabad shows AQI 204 but another source shows 29:
- **204** = Data from US Embassy station (specific location, official EPA standard)
- **29** = Might be from a different station or different calculation method

Both can be correct - they're just from different monitoring stations!

### Data Freshness

- If data is > 1 hour old, you'll see a warning
- To force refresh: `python scripts/fetch_data.py`
- The dashboard caches data for 1 hour to avoid API rate limits

## Manual Commands (Optional)

**Fetch Fresh Data:**
```powershell
python scripts/fetch_data.py
```

**Fill Missing Days (if needed):**
```powershell
python fill_missing_days.py
```

**Aggregate Hourly Data to Daily:**
```powershell
python aggregate_daily_data.py
```

**Generate Report:**
```powershell
python scripts/generate_report.py
```

## Forecast Period

- **Days forecasted:** Next 8 days
- **Historical data used:** All available (from October 2025 onwards)
- **Update frequency:** Models retrain each time you open the Forecasting page

## Troubleshooting

### Issue: "No current data available"
**Solution:** Run `python scripts/fetch_data.py`

### Issue: AQI seems wrong
**Check:**
1. When was data last updated? (shown in dashboard)
2. Which station is it from? (shown in Latest Measurements)
3. Different stations = different readings (this is normal!)

### Issue: Forecast shows "NaT"
**Solution:** Restart the Streamlit app - forecasting code was recently fixed

### Issue: Missing days in database
**Solution:** The app now fills them automatically! Just refresh the dashboard.

## Data Sources

- **Primary:** WAQI API (World Air Quality Index)  
- **Stations:** US Embassy stations for major cities
- **Update:** Real-time when available, otherwise most recent reading

## Database Structure

- **MongoDB** - All data storage
- **Collections:**
  - `air_quality_measurements` - Raw pollutant data
  - `aqi_history` - Calculated AQI values
  - `health_impacts` - Health assessments
  - `forecasts` - Prediction results

## Need Help?

1. Check the logs in the terminal
2. Look for error messages in the dashboard
3. Verify API connection: Data should update automatically every hour

---

**Last Updated:** May 3, 2026
**Version:** 1.0 (MongoDB only)
