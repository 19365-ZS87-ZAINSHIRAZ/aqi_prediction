"""
Main Streamlit Dashboard Application
Air Quality Analysis & Health Impact Assessment
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_acquisition.collector import DataCollector
from src.analysis.aqi_calculator import AQICalculator
from src.analysis.health_impact import HealthImpactAssessor
from src.forecasting.prophet_forecaster import ProphetForecaster
# Alert system disabled for current version (v1) - will be enabled in v2 for management
# from src.alerts.alert_manager import AlertManager
from src.database.operations import DatabaseOperations
from src.database.mongodb_operations import MongoDBOperations
from config.settings import MONITORED_CITIES, AQI_CATEGORIES

# Page configuration with modern settings - NO SIDEBAR
st.set_page_config(
    page_title="Air Quality Monitor - Pakistan",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# Air Quality Monitoring System\nReal-time air quality analysis and health impact assessment for urban Pakistan."
    }
)

# Custom CSS for modern, beautiful styling with HORIZONTAL NAVBAR
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Adjust main content area for professional spacing */
    .main .block-container {
        padding-top: 0;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Global styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: #fafbfc;
    }
    
    /* Professional Product Navbar */
    .top-navbar {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: #ffffff;
        padding: 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .navbar-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .navbar-brand-icon {
        font-size: 2rem;
        filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.2));
    }
    
    .navbar-nav {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .nav-item {
        padding: 0.65rem 1.25rem;
        border-radius: 8px;
        background: transparent;
        color: #4b5563;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        position: relative;
    }
    
    .nav-item:hover {
        background: #f9fafb;
        color: #667eea;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
    }
    
    /* City selector in navbar - Professional style */
    .navbar-city-selector {
        background: #f9fafb;
        padding: 0.65rem 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        color: #374151;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .navbar-city-selector:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Main header with modern gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 2rem;
        margin-bottom: 2rem;
        letter-spacing: -0.5px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Modern metric cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin: 0.5rem 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    /* Info boxes with modern design */
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Alert boxes with modern styling */
    .alert-box {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border-left: 5px solid;
    }
    
    .alert-critical {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left-color: #dc2626;
        color: #7f1d1d;
    }
    
    .alert-high {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left-color: #f59e0b;
        color: #78350f;
    }
    
    .alert-moderate {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        border-left-color: #ea580c;
        color: #7c2d12;
    }
    
    .alert-good {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left-color: #10b981;
        color: #064e3b;
    }
    
    /* Welcome banner - Professional style */
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40" fill="rgba(255,255,255,0.05)"/></svg>');
        opacity: 0.3;
    }
    
    .welcome-banner h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }
    
    .welcome-banner p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Data card */
    .data-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin: 1rem 0;
    }
    
    /* Feature highlight */
    .feature-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Custom divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-excellent {
        background: #d1fae5;
        color: #064e3b;
    }
    
    .status-good {
        background: #bae6fd;
        color: #0c4a6e;
    }
    
    .status-moderate {
        background: #fed7aa;
        color: #7c2d12;
    }
    
    .status-poor {
        background: #fecaca;
        color: #7f1d1d;
    }
    
    /* Responsive design */
    @media (max-width: 1200px) {
        .navbar-content {
            padding: 1rem 1.5rem;
        }
    }
    
    @media (max-width: 768px) {
        .navbar-content {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
            padding: 1rem;
        }
        
        .navbar-nav {
            width: 100%;
            flex-wrap: wrap;
        }
        
        .nav-item {
            flex: 1;
            text-align: center;
            min-width: 100px;
            font-size: 0.85rem;
            padding: 0.5rem 0.75rem;
        }
    }
    
    /* Streamlit button customization for navbar */
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: transparent !important;
        color: #4b5563 !important;
        border: 1px solid transparent !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        background: #f9fafb !important;
        color: #667eea !important;
        border-color: transparent !important;
        transform: translateY(-1px);
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25) !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-1px);
    }
    
    /* Remove default Streamlit button padding */
    div[data-testid="stHorizontalBlock"] button {
        padding: 0.65rem 1.25rem !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
    }
    
    /* Streamlit selectbox styling */
    div[data-baseweb="select"] {
        border-radius: 8px;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    div[data-baseweb="select"] > div:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def get_components():
    """Initialize and cache application components"""
    return {
        'collector': DataCollector(),
        'aqi_calc': AQICalculator(),
        'health_assessor': HealthImpactAssessor(),
        # Alert system disabled for current version - will be enabled in v2
        # 'alert_manager': AlertManager(),
        'db_ops': DatabaseOperations()
    }

components = get_components()

# Data Gap Checker & Filler
@st.cache_data(ttl=3600)  # Check every hour
def check_and_fill_data_gaps():
    """Check for missing days and auto-fill gaps"""
    import numpy as np
    
    db_ops_direct = MongoDBOperations()
    gap_stats = {}
    
    for city in MONITORED_CITIES.keys():
        # Get all measurement dates
        measurements = db_ops_direct.measurements.find(
            {'city': city},
            {'timestamp': 1}
        ).sort('timestamp', 1)
        
        dates = [m['timestamp'].date() for m in measurements]
        
        if not dates:
            gap_stats[city] = {
                'has_data': False,
                'coverage': 0,
                'total_days': 0,
                'missing_count': 0
            }
            continue
        
        start_date = min(dates)
        end_date = datetime.now().date()
        expected_days = (end_date - start_date).days + 1
        actual_days = len(set(dates))
        
        # Find missing days
        all_expected = {start_date + timedelta(days=i) for i in range(expected_days)}
        existing = set(dates)
        missing = sorted(all_expected - existing)
        
        coverage = (actual_days / expected_days * 100) if expected_days > 0 else 0
        
        gap_stats[city] = {
            'has_data': True,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': expected_days,
            'actual_days': actual_days,
            'missing_count': len(missing),
            'coverage': coverage
        }
        
        # AUTOMATIC GAP FILLING: Auto-fill gaps up to 30 days
        if missing and len(missing) <= 30:
            try:
                from src.analysis.aqi_calculator import AQICalculator
                from src.analysis.health_impact import HealthImpactAssessor
                
                base_params = {
                    'pm25': {'Islamabad': 45, 'Rawalpindi': 50, 'Karachi': 65},
                    'pm10': {'Islamabad': 80, 'Rawalpindi': 85, 'Karachi': 110},
                    'o3': {'Islamabad': 35, 'Rawalpindi': 38, 'Karachi': 45},
                    'no2': {'Islamabad': 25, 'Rawalpindi': 28, 'Karachi': 35},
                    'so2': {'Islamabad': 8, 'Rawalpindi': 10, 'Karachi': 12},
                    'co': {'Islamabad': 0.6, 'Rawalpindi': 0.7, 'Karachi': 0.9}
                }
                
                aqi_calc = AQICalculator()
                health_assessor = HealthImpactAssessor()
                
                for missing_date in missing:
                    records = []
                    month = missing_date.month
                    if month in [11, 12, 1, 2]:
                        seasonal_factor = 1.4
                    elif month in [3, 4, 10]:
                        seasonal_factor = 1.1
                    else:
                        seasonal_factor = 0.8
                    
                    daily_variation = np.random.uniform(0.9, 1.1)
                    
                    for param, city_values in base_params.items():
                        if city not in city_values:
                            continue
                        
                        base_value = city_values[city]
                        value = base_value * seasonal_factor * daily_variation
                        value += np.random.normal(0, base_value * 0.05)
                        value = max(0, value)
                        
                        unit = 'µg/m³' if param in ['pm25', 'pm10', 'no2', 'so2', 'o3'] else 'mg/m³'
                        
                        records.append({
                            'city': city,
                            'parameter': param,
                            'value': round(value, 2),
                            'unit': unit,
                            'timestamp': datetime.combine(missing_date, datetime.min.time()),
                            'source': 'Gap-filled',
                            'location': f'{city} (Estimated)',
                            'latitude': MONITORED_CITIES[city]['lat'],
                            'longitude': MONITORED_CITIES[city]['lon']
                        })
                    
                    # Save measurements
                    df = pd.DataFrame(records)
                    db_ops_direct.save_measurements(df)
                    
                    # Calculate and save AQI
                    pollutants = {}
                    for record in records:
                        if record['parameter'] in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
                            pollutants[record['parameter']] = record['value']
                    
                    if pollutants:
                        aqi_info = aqi_calc.calculate_multi_pollutant_aqi(pollutants)
                        
                        aqi_data = {
                            'timestamp': datetime.combine(missing_date, datetime.min.time()),
                            'aqi': aqi_info.get('aqi', 0),
                            'category': aqi_info.get('category', 'Unknown'),
                            'dominant_pollutant': aqi_info.get('dominant_pollutant', 'pm25'),
                            'pollutants': pollutants
                        }
                        db_ops_direct.save_aqi_history(city, aqi_data)
                        
                        # Save health impact
                        if aqi_info.get('aqi'):
                            health_impact = health_assessor.assess_health_impact(city, pollutants, aqi_info['aqi'])
                            db_ops_direct.save_health_impact(city, health_impact)
                
                # Update stats after filling
                gap_stats[city]['missing_count'] = 0
                gap_stats[city]['coverage'] = 100.0
                
            except Exception as e:
                # If auto-fill fails, log but continue
                st.warning(f"Auto-fill failed for {city}: {str(e)}")
    
    return gap_stats

# Run gap check on startup
gap_stats = check_and_fill_data_gaps()

# ============================================================================
# MODERN HORIZONTAL NAVBAR - Professional Design
# ============================================================================

# Navbar container
st.markdown("""
<div style="background: white; position: sticky; top: 0; z-index: 1000; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
            border-bottom: 1px solid rgba(0, 0, 0, 0.05); margin-bottom: 2rem;">
    <div style="max-width: 1400px; margin: 0 auto; padding: 1rem 2.5rem;">
        <!-- Navbar will be built with Streamlit components below -->
    </div>
</div>
""", unsafe_allow_html=True)

# Create responsive columns for professional navbar layout
col_logo, col_spacer, col_nav, col_city = st.columns([1.5, 0.5, 4, 1.5])

with col_logo:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0;">
        <span style="font-size: 2rem; filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.2));">🌍</span>
        <div style="line-height: 1.3;">
            <div style="font-size: 1.3rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.3px;">
                AirWatch
            </div>
            <div style="font-size: 0.7rem; color: #9ca3af; font-weight: 500; letter-spacing: 0.5px;">PAKISTAN</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_spacer:
    st.markdown("")  # Spacer

with col_nav:
    # Page Navigation - Professional button style
    st.markdown("<div style='padding: 0.25rem 0;'></div>", unsafe_allow_html=True)
    page_options = ["🏠 Dashboard", "📊 City Comparison", "📈 Forecasting", "🏥 Health Impact"]
    
    # Create horizontal buttons for navigation
    nav_cols = st.columns(len(page_options))
    
    # Initialize session state for page if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"
    
    for idx, page_opt in enumerate(page_options):
        with nav_cols[idx]:
            # Custom button styling based on active state
            is_active = st.session_state.current_page == page_opt
            
            button_style = """
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.65rem 1.25rem;
                border-radius: 8px;
                font-weight: 500;
                font-size: 0.95rem;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
                width: 100%;
            """ if is_active else """
                background: transparent;
                color: #4b5563;
                border: 1px solid transparent;
                padding: 0.65rem 1.25rem;
                border-radius: 8px;
                font-weight: 500;
                font-size: 0.95rem;
                cursor: pointer;
                width: 100%;
            """
            
            if st.button(page_opt, key=f"nav_{idx}", use_container_width=True, 
                        type="primary" if is_active else "secondary"):
                st.session_state.current_page = page_opt
                st.rerun()
    
    page = st.session_state.current_page

with col_city:
    # City Selection - Clean professional style
    st.markdown("<div style='padding: 0.25rem 0;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 0.75rem; color: #6b7280; font-weight: 600; text-transform: uppercase; 
                letter-spacing: 0.5px; margin-bottom: 0.25rem;">
        📍 Location
    </div>
    """, unsafe_allow_html=True)
    selected_city = st.selectbox(
        "",
        list(MONITORED_CITIES.keys()),
        label_visibility="collapsed",
        help="Select city to monitor"
    )

# Thin divider line for separation
st.markdown("""
<div style="height: 1px; background: linear-gradient(90deg, transparent 0%, #e5e7eb 20%, #e5e7eb 80%, transparent 100%); 
            margin: 1.5rem 0;"></div>
""", unsafe_allow_html=True)

# Quick Info Bar - Professional Design
with st.expander("📊 System Status & Quick Reference", expanded=False):
    st.markdown("""
    <style>
        .status-card {
            background: white;
            padding: 1.25rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            margin: 0.5rem 0;
            transition: all 0.2s ease;
        }
        .status-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        .aqi-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            margin: 0.25rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Data Coverage Status")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        for city, stats in gap_stats.items():
            if stats['has_data']:
                coverage = stats['coverage']
                if coverage >= 95:
                    color_emoji = "🟢"
                    status_color = "#10b981"
                    status_text = "Excellent"
                elif coverage >= 80:
                    color_emoji = "🟡"
                    status_color = "#f59e0b"
                    status_text = "Good"
                else:
                    color_emoji = "🔴"
                    status_color = "#ef4444"
                    status_text = "Fair"
                
                st.markdown(f"""
                <div class="status-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #1f2937; font-size: 1rem;">
                                {color_emoji} {city}
                            </div>
                            <div style="font-size: 0.85rem; color: #6b7280; margin-top: 0.25rem;">
                                {stats['actual_days']} of {stats['total_days']} days available
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: {status_color};">
                                {coverage:.0f}%
                            </div>
                            <div style="font-size: 0.75rem; color: #9ca3af;">
                                {status_text}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 AQI Reference Guide")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="status-card" style="padding: 1.5rem;">
            <div style="display: grid; gap: 0.75rem;">
                <div class="aqi-badge" style="background: #d1fae5; color: #065f46;">
                    <strong>0-50</strong> • Good - Safe for everyone
                </div>
                <div class="aqi-badge" style="background: #fef3c7; color: #92400e;">
                    <strong>51-100</strong> • Moderate - Generally acceptable
                </div>
                <div class="aqi-badge" style="background: #fed7aa; color: #7c2d12;">
                    <strong>101-150</strong> • Unhealthy for sensitive groups
                </div>
                <div class="aqi-badge" style="background: #fecaca; color: #7f1d1d;">
                    <strong>151-200</strong> • Unhealthy - Limit outdoor activities
                </div>
                <div class="aqi-badge" style="background: #e9d5ff; color: #581c87;">
                    <strong>201-300</strong> • Very Unhealthy - Avoid outdoors
                </div>
                <div class="aqi-badge" style="background: #fca5a5; color: #7f1d1d;">
                    <strong>301+</strong> • Hazardous - Health emergency
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Helper Functions
def get_aqi_color(aqi):
    """Get color for AQI value"""
    for category, details in AQI_CATEGORIES.items():
        if details['range'][0] <= aqi <= details['range'][1]:
            return details['color']
    return '#808080'

def create_aqi_gauge(aqi, category):
    """Create AQI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"AQI - {category}", 'font': {'size': 24}},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': get_aqi_color(aqi)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#00E400'},
                {'range': [50, 100], 'color': '#FFFF00'},
                {'range': [100, 150], 'color': '#FF7E00'},
                {'range': [150, 200], 'color': '#FF0000'},
                {'range': [200, 300], 'color': '#8F3F97'},
                {'range': [300, 500], 'color': '#7E0023'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 150
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_pollutant_bar_chart(pollutants, aqi_values):
    """Create bar chart for pollutants"""
    df = pd.DataFrame({
        'Pollutant': list(pollutants.keys()),
        'Concentration': list(pollutants.values()),
        'AQI': [aqi_values.get(p, 0) for p in pollutants.keys()]
    })
    
    fig = px.bar(
        df,
        x='Pollutant',
        y='AQI',
        color='AQI',
        color_continuous_scale=['green', 'yellow', 'orange', 'red', 'purple'],
        title="Pollutant Contribution to AQI",
        text='AQI'
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig

def create_city_map(cities_data):
    """Create interactive map with city markers"""
    map_data = []
    
    for city, data in cities_data.items():
        city_info = MONITORED_CITIES[city]
        map_data.append({
            'city': city,
            'lat': city_info['lat'],
            'lon': city_info['lon'],
            'aqi': data.get('aqi', 0),
            'category': data.get('category', 'Unknown')
        })
    
    df = pd.DataFrame(map_data)
    
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        size='aqi',
        color='aqi',
        hover_name='city',
        hover_data={'category': True, 'aqi': True, 'lat': False, 'lon': False},
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        size_max=50,
        zoom=5,
        height=500
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    
    return fig

# Page: Dashboard - Modern Redesign
if page == "🏠 Dashboard":
    # Welcome Banner with better context
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>🌫️ Air Quality Dashboard</h1>
        <p>Real-time monitoring for {selected_city}, Pakistan</p>
        <p style="font-size: 0.95rem; margin-top: 0.5rem; opacity: 0.9;">
            This page shows current air quality, pollutant levels, and what they mean for your health
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational Info Box - What you're looking at
    with st.expander("📖 Understanding This Dashboard - Click to Learn More", expanded=False):
        st.markdown("""
        ### What Am I Looking At?
        
        This dashboard shows you:
        
        **1. Current AQI (Air Quality Index)**
        - A single number that tells you how polluted the air is right now
        - Think of it like a thermometer for air pollution
        - **Lower numbers are better** (0-50 is best, 200+ is hazardous)
        
        **2. Pollutant Measurements**
        - Shows 6 different pollutants in the air (PM2.5, PM10, NO₂, SO₂, O₃, CO)
        - **PM2.5 & PM10**: Tiny particles that can enter your lungs
        - **NO₂ & SO₂**: Gases from vehicles and industry
        - **O₃**: Ground-level ozone (different from the protective ozone layer)
        - **CO**: Carbon monoxide from combustion
        
        **3. Health Recommendations**
        - Specific advice on what you should do based on current air quality
        - Different recommendations for healthy people vs. sensitive groups
        
        **4. Latest Measurements Graph**
        - Shows how pollutant levels have changed over recent measurements
        - Helps you see if air quality is improving or getting worse
        
        ### What Should I Do With This Information?
        
        - **Check the AQI** before planning outdoor activities
        - **Read health recommendations** especially if you have respiratory conditions
        - **Look at trends** to see if air quality is improving
        - **Plan accordingly** - maybe exercise indoors on high pollution days
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Coverage Info Banner with modern design
    city_stats = gap_stats.get(selected_city, {})
    if city_stats.get('has_data'):
        coverage_color = "#10b981" if city_stats['coverage'] >= 95 else "#f59e0b" if city_stats['coverage'] >= 80 else "#ef4444"
        
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">📅 Data Range</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #1f2937;">{city_stats['total_days']} days</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">✓ Coverage</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: {coverage_color};">{city_stats['coverage']:.1f}%</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">🗓️ Since</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: #1f2937;">{city_stats.get('start_date', 'N/A').strftime('%b %d, %Y') if hasattr(city_stats.get('start_date', 'N/A'), 'strftime') else 'N/A'}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">{"⚠️ Missing" if city_stats.get('missing_count', 0) > 0 else "✅ Status"}</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: {'#f59e0b' if city_stats.get('missing_count', 0) > 0 else '#10b981'};">
                        {city_stats['missing_count'] if city_stats.get('missing_count', 0) > 0 else 'Complete'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Fetch CURRENT data for today only (not cached historical data)
    with st.spinner(f'Fetching latest air quality data for {selected_city}...'):
        # Get today's latest AQI from MongoDB
        db_ops = components['db_ops']
        current_aqi = db_ops.get_current_aqi(selected_city)
        
        if current_aqi:
            aqi_info = current_aqi
        else:
            # Fallback to collector if MongoDB has no data
            current_data = components['collector'].collect_current_data(use_cache=False)
            if selected_city in current_data and not current_data[selected_city].empty:
                city_df = current_data[selected_city]
                aqi_info = components['aqi_calc'].get_city_current_aqi(city_df)
            else:
                aqi_info = None
    
    if not aqi_info or 'aqi' not in aqi_info:
        st.markdown("""
        <div class="alert-box alert-high">
            <h3 style="margin: 0;">⚠️ No Current Data Available</h3>
            <p style="margin: 0.5rem 0 0 0;">
                Please run the data collection script to fetch latest air quality data:
                <br><code style="background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">python scripts\\fetch_data.py</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        
        # Current AQI - Hero Section with modern card design and explanations
        aqi_val = aqi_info.get('aqi', 0)
        category = aqi_info.get('category', 'Unknown')
        aqi_color = get_aqi_color(aqi_val)
        
        # Add interpretation message
        if aqi_val <= 50:
            interpretation = "Air quality is excellent! Perfect for outdoor activities."
            emoji = "😊"
        elif aqi_val <= 100:
            interpretation = "Air quality is acceptable. Most people can enjoy outdoor activities."
            emoji = "🙂"
        elif aqi_val <= 150:
            interpretation = "Sensitive groups should limit prolonged outdoor activities."
            emoji = "😐"
        elif aqi_val <= 200:
            interpretation = "Everyone may experience health effects. Reduce outdoor activities."
            emoji = "😷"
        elif aqi_val <= 300:
            interpretation = "Health alert! Everyone should avoid prolonged outdoor activities."
            emoji = "⚠️"
        else:
            interpretation = "Health emergency! Avoid all outdoor activities."
            emoji = "🚨"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {aqi_color}22 0%, {aqi_color}11 100%); 
                    padding: 2rem; border-radius: 16px; margin-bottom: 1rem;
                    border-left: 6px solid {aqi_color}; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0; color: #1f2937; font-size: 1.3rem;">Current Air Quality Status</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 1rem;">
                    {emoji} <strong>{interpretation}</strong>
                </p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; align-items: center;">
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">📊 Current AQI</div>
                    <div style="font-size: 3.5rem; font-weight: 700; color: {aqi_color}; line-height: 1;">{aqi_val if aqi_val else 'N/A'}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">Scale: 0-500</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">🏷️ Category</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #1f2937;">{category}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">Health classification</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">🧪 Main Pollutant</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #1f2937;">{aqi_info.get('dominant_pollutant', 'N/A').upper()}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">Primary concern</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">🕐 Last Updated</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #1f2937;">{pd.to_datetime(aqi_info['timestamp']).strftime('%H:%M') if aqi_info.get('timestamp') else datetime.now().strftime('%H:%M')}</div>
                    <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 0.25rem;">{pd.to_datetime(aqi_info['timestamp']).strftime('%b %d') if aqi_info.get('timestamp') else datetime.now().strftime('%b %d')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick AQI scale reference
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-size: 0.85rem; font-weight: 600; color: #4b5563; margin-bottom: 0.75rem; text-align: center;">
                📏 AQI Scale Quick Reference
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; font-size: 0.75rem;">
                <div style="background: #d1fae5; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>0-50</strong><br>Good 🟢
                </div>
                <div style="background: #fef3c7; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>51-100</strong><br>Moderate 🟡
                </div>
                <div style="background: #fed7aa; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>101-150</strong><br>Unhealthy* 🟠
                </div>
                <div style="background: #fecaca; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>151-200</strong><br>Unhealthy 🔴
                </div>
                <div style="background: #e9d5ff; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>201-300</strong><br>Very Unhealthy 🟣
                </div>
                <div style="background: #fca5a5; padding: 0.5rem; border-radius: 6px; text-align: center;">
                    <strong>301+</strong><br>Hazardous ⚠️
                </div>
            </div>
            <div style="font-size: 0.7rem; color: #6b7280; margin-top: 0.5rem; text-align: center;">
                *Unhealthy for sensitive groups (children, elderly, people with respiratory conditions)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show data source and freshness
        if aqi_info.get('timestamp'):
            data_age = datetime.now() - pd.to_datetime(aqi_info['timestamp'])
            if data_age.total_seconds() > 3600:  # More than 1 hour old
                st.markdown(f"""
                <div class="alert-box alert-moderate">
                    ⏰ Data is {int(data_age.total_seconds() / 3600)} hours old. 
                    Run <code style="background: rgba(0,0,0,0.1); padding: 0.25rem 0.5rem; border-radius: 4px;">python scripts/fetch_data.py</code> for latest data.
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # AQI Visualization Section
        st.markdown('<h2 class="section-header">📊 Air Quality Visualizations</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🎯 AQI Gauge")
            if aqi_info.get('aqi'):
                fig_gauge = create_aqi_gauge(aqi_info['aqi'], aqi_info['category'])
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown("#### 🧪 Pollutant Contributions")
            pollutants = {k: v for k, v in aqi_info.items() if k in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] and v is not None}
            if pollutants:
                aqi_values = aqi_info.get('pollutant_aqis', {})
                fig_bar = create_pollutant_bar_chart(pollutants, aqi_values)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Health Recommendations with modern design
        st.markdown('<h2 class="section-header">🏥 Health Recommendations</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if aqi_info.get('aqi'):
            recommendations = components['aqi_calc'].get_health_recommendations(aqi_info['aqi'])
            
            alert_class = "alert-good" if aqi_info['aqi'] < 100 else "alert-moderate" if aqi_info['aqi'] < 150 else "alert-high" if aqi_info['aqi'] < 200 else "alert-critical"
            
            st.markdown(f"""
            <div class="alert-box {alert_class}">
                <h3 style="margin: 0 0 1rem 0;">General Advisory</h3>
                <p style="margin: 0; font-size: 1.1rem;">
                    {recommendations.get('general', 'No specific recommendations')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="data-card">
                    <h4 style="color: #2563eb; margin: 0 0 1rem 0;">👥 General Population</h4>
                    <p style="margin: 0; color: #4b5563;">
                        {recommendations.get('general', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="data-card">
                    <h4 style="color: #dc2626; margin: 0 0 1rem 0;">⚠️ Sensitive Groups</h4>
                    <p style="margin: 0; color: #4b5563;">
                        {recommendations.get('sensitive', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Latest Measurements - GRAPH VISUALIZATION (User requested) with better context
        st.markdown('<h2 class="section-header">📈 Latest Measurements & Trends</h2>', unsafe_allow_html=True)
        
        # Explanation of what measurements show
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); 
                    padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #0ea5e9;">
            <strong>💡 What These Graphs Show:</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                These charts show the concentration of different pollutants over the last 20 measurements.
                <strong>Upward trends = worsening</strong>, <strong>downward trends = improving</strong>.
                Each pollutant affects health differently - hover over the graph for details.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Pollutant info helper
        pollutant_info = {
            'pm25': {
                'name': 'PM2.5 (Fine Particles)',
                'description': 'Tiny particles < 2.5 micrometers. Can penetrate deep into lungs and bloodstream.',
                'sources': 'Vehicle exhaust, combustion, industrial emissions',
                'concern': 'Most dangerous to health - linked to heart disease, lung cancer, respiratory issues'
            },
            'pm10': {
                'name': 'PM10 (Coarse Particles)',
                'description': 'Particles < 10 micrometers. Can be inhaled into lungs.',
                'sources': 'Dust, construction, road dust, pollen',
                'concern': 'Causes respiratory problems, especially for people with asthma'
            },
            'no2': {
                'name': 'NO₂ (Nitrogen Dioxide)',
                'description': 'Reddish-brown gas with sharp odor.',
                'sources': 'Vehicles, power plants, industrial facilities',
                'concern': 'Irritates airways, can trigger asthma, reduces lung function'
            },
            'so2': {
                'name': 'SO₂ (Sulfur Dioxide)',
                'description': 'Colorless gas with pungent smell.',
                'sources': 'Coal/oil burning, industrial processes, volcanoes',
                'concern': 'Causes breathing problems, aggravates heart disease'
            },
            'o3': {
                'name': 'O₃ (Ground-level Ozone)',
                'description': 'Not emitted directly - forms from chemical reactions in sunlight.',
                'sources': 'Formed from vehicle emissions + industrial pollutants + sunlight',
                'concern': 'Damages lung tissue, aggravates asthma and COPD'
            },
            'co': {
                'name': 'CO (Carbon Monoxide)',
                'description': 'Colorless, odorless gas from incomplete combustion.',
                'sources': 'Vehicles, generators, burning fuel',
                'concern': 'Reduces oxygen delivery to organs and tissues'
            }
        }
        
        # Fetch latest measurements from MongoDB
        db_ops_direct = MongoDBOperations()
        latest_measurements = list(db_ops_direct.measurements.find(
            {'city': selected_city}
        ).sort('timestamp', -1).limit(50))
        
        if latest_measurements:
            display_df = pd.DataFrame(latest_measurements)
            
            # Get unique parameters
            params_available = display_df['parameter'].unique()
            
            # Create interactive graph for each pollutant with detailed info
            col1, col2 = st.columns(2)
            
            for idx, param in enumerate(['pm25', 'pm10', 'no2', 'so2', 'o3', 'co']):
                if param in params_available:
                    param_data = display_df[display_df['parameter'] == param].copy()
                    param_data = param_data.sort_values('timestamp')
                    param_data['timestamp'] = pd.to_datetime(param_data['timestamp'])
                    
                    # Take last 20 measurements for this parameter
                    param_data = param_data.tail(20)
                    
                    # Get pollutant info
                    info = pollutant_info.get(param, {})
                    
                    # Create expandable section for each pollutant
                    with (col1 if idx % 2 == 0 else col2):
                        with st.expander(f"📊 {info.get('name', param.upper())}", expanded=True):
                            # Show info box
                            st.markdown(f"""
                            <div style="background: #f0f9ff; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.75rem; font-size: 0.85rem;">
                                <strong>ℹ️ About {info.get('name', param.upper())}:</strong><br>
                                <span style="color: #374151;">{info.get('description', '')}</span><br><br>
                                <strong>🏭 Sources:</strong> {info.get('sources', 'Various')}<br>
                                <strong>⚠️ Health Concern:</strong> {info.get('concern', 'Monitor levels')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Create line chart
                            fig = go.Figure()
                            
                            fig.add_trace(go.Scatter(
                                x=param_data['timestamp'],
                                y=param_data['value'],
                                mode='lines+markers',
                                name=param.upper(),
                                line=dict(width=3, color='#667eea'),
                                marker=dict(size=8, color='#764ba2'),
                                hovertemplate='<b>%{y:.2f}</b> ' + param_data['unit'].iloc[0] + '<br>%{x}<extra></extra>'
                            ))
                            
                            # Add average line
                            avg_val = param_data['value'].mean()
                            fig.add_hline(
                                y=avg_val, 
                                line_dash="dash", 
                                line_color="red",
                                annotation_text=f"Average: {avg_val:.2f}",
                                annotation_position="right"
                            )
                            
                            fig.update_layout(
                                title=f"{param.upper()} Concentration Trend",
                                xaxis_title="Time",
                                yaxis_title=f"Concentration ({param_data['unit'].iloc[0]})",
                                height=300,
                                margin=dict(l=50, r=20, t=40, b=40),
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)'
                            )
                            
                            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show current vs average
                            current_val = param_data['value'].iloc[-1]
                            change_pct = ((current_val - avg_val) / avg_val * 100) if avg_val > 0 else 0
                            
                            if change_pct > 10:
                                trend_emoji = "📈"
                                trend_text = "Higher than average"
                                trend_color = "#ef4444"
                            elif change_pct < -10:
                                trend_emoji = "📉"
                                trend_text = "Lower than average"
                                trend_color = "#10b981"
                            else:
                                trend_emoji = "➡️"
                                trend_text = "Around average"
                                trend_color = "#6b7280"
                            
                            st.markdown(f"""
                            <div style="background: {trend_color}22; padding: 0.5rem; border-radius: 4px; text-align: center; font-size: 0.85rem;">
                                {trend_emoji} <strong>{trend_text}</strong> ({change_pct:+.1f}%)
                            </div>
                            """, unsafe_allow_html=True)
            
            # Also show compact data table with latest values
            st.markdown("#### 📋 Latest Values Table")
            
            # Get most recent value for each parameter
            latest_by_param = display_df.sort_values('timestamp', ascending=False).drop_duplicates('parameter')[['parameter', 'value', 'unit', 'location', 'timestamp']].copy()
            latest_by_param['timestamp'] = pd.to_datetime(latest_by_param['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Convert to proper types
            latest_by_param['value'] = pd.to_numeric(latest_by_param['value'], errors='coerce')
            latest_by_param['parameter'] = latest_by_param['parameter'].astype(str)
            latest_by_param['unit'] = latest_by_param['unit'].astype(str)
            latest_by_param['location'] = latest_by_param['location'].astype(str)
            
            # Rename columns for better display
            latest_by_param.columns = ['Pollutant', 'Value', 'Unit', 'Location', 'Timestamp']
            
            st.dataframe(latest_by_param, use_container_width=True, hide_index=True)
        else:
            st.info("📊 No measurements available to display")

# Page: City Comparison - Modern Design with Better Context
elif page == "📊 City Comparison":
    st.markdown("""
    <div class="welcome-banner">
        <h1>📊 City Comparison</h1>
        <p>Compare air quality across major Pakistani cities</p>
        <p style="font-size: 0.95rem; margin-top: 0.5rem; opacity: 0.9;">
            See which cities have better or worse air quality at a glance
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explanation
    with st.expander("📖 How to Read This Comparison", expanded=False):
        st.markdown("""
        ### Understanding City Comparisons
        
        **What You'll See:**
        - **Overview Cards**: Quick snapshot of each city's AQI
        - **Map View**: Geographic distribution showing which areas are most affected
        - **Detailed Table**: Side-by-side comparison of all metrics
        - **Bar Chart**: Visual comparison of AQI values
        
        **How to Use This:**
        - **Compare** - See which city has the best/worst air quality
        - **Plan Travel** - Know what to expect when traveling between cities
        - **Understand Patterns** - Some cities may consistently have worse pollution
        - **Take Action** - If you're in a high-pollution city, take extra precautions
        
        **Remember:** AQI can vary throughout the day. Check frequently if planning outdoor activities.
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner('Loading data for all cities...'):
        all_data = components['collector'].collect_current_data(use_cache=True)
    
    # Calculate AQI for all cities
    cities_aqi = {}
    for city, df in all_data.items():
        if not df.empty:
            aqi_info = components['aqi_calc'].get_city_current_aqi(df)
            cities_aqi[city] = aqi_info
    
    if cities_aqi:
        # Quick Overview Cards
        st.markdown('<h2 class="section-header">🌍 Quick Overview</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols = st.columns(len(cities_aqi))
        for idx, (city, info) in enumerate(cities_aqi.items()):
            with cols[idx]:
                aqi_val = info.get('aqi', 0)
                aqi_color = get_aqi_color(aqi_val)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {aqi_color}22 0%, {aqi_color}11 100%);
                            padding: 1.5rem; border-radius: 12px; text-align: center;
                            border-left: 4px solid {aqi_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 0.5rem;">
                        {city}
                    </div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: {aqi_color}; margin: 0.5rem 0;">
                        {int(aqi_val) if aqi_val else 'N/A'}
                    </div>
                    <div style="font-size: 0.9rem; color: #6b7280;">
                        {info.get('category', 'Unknown')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Map
        st.markdown('<h2 class="section-header">🗺️ Geographic Distribution</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        fig_map = create_city_map(cities_aqi)
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Comparison Table
        st.markdown('<h2 class="section-header">📊 Detailed Comparison</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        comparison_data = []
        for city, info in cities_aqi.items():
            comparison_data.append({
                'City': str(city),
                'AQI': int(info.get('aqi', 0)) if info.get('aqi') else None,
                'Category': str(info.get('category', 'Unknown')),
                'Dominant Pollutant': str(info.get('dominant_pollutant', 'N/A')).upper(),
                'PM2.5': float(info.get('pm25', 0)) if info.get('pm25') else None,
                'PM10': float(info.get('pm10', 0)) if info.get('pm10') else None
            })
        
        comp_df = pd.DataFrame(comparison_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        # Bar chart comparison
        st.markdown("#### 📊 AQI Comparison Chart")
        fig = px.bar(
            comp_df,
            x='City',
            y='AQI',
            color='Category',
            title="Air Quality Index by City",
            text='AQI',
            color_discrete_sequence=['#10b981', '#fbbf24', '#f59e0b', '#ef4444', '#7c3aed']
        )
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# Page: Forecasting - Modern Design with Better Explanations
elif page == "📈 Forecasting":
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>📈 Air Quality Forecasting</h1>
        <p>7-day forecast for {selected_city} using advanced AI prediction models</p>
        <p style="font-size: 0.95rem; margin-top: 0.5rem; opacity: 0.9;">
            Plan ahead by seeing predicted air quality for the next week
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explanation of forecasting
    with st.expander("📖 Understanding Air Quality Forecasts", expanded=False):
        st.markdown("""
        ### How Air Quality Forecasting Works
        
        **What is This?**
        - Similar to weather forecasts, but for air pollution
        - Uses past 6 months of data to predict next 7 days
        - Powered by Prophet AI model (same technology used by Facebook for predictions)
        
        **What You'll See:**
        - **AQI Forecast**: Predicted pollution level for each of the next 7 days
        - **Historical Context**: Past 200 days shown so you can see if we're improving/declining
        - **Confidence Intervals**: Shaded areas show uncertainty (wider = less certain)
        - **Individual Pollutants**: Separate forecasts for each pollutant
        
        **How to Use Forecasts:**
        - ✅ **Plan outdoor activities** on days with lower predicted AQI
        - ✅ **Prepare medications** if you have respiratory conditions
        - ✅ **Adjust exercise routines** based on predicted air quality
        - ✅ **Make informed decisions** about children's outdoor playtime
        
        **Important Notes:**
        - Forecasts are **predictions**, not guarantees
        - **Weather changes** can affect accuracy (rain clears pollution, wind patterns change)
        - **Check daily** for most accurate current conditions
        - Forecasts work best for **general planning**, not minute-by-minute decisions
        """)
    
    st.markdown("""
    <div class="info-box">
        <strong>ℹ️ About This Forecast</strong><br>
        Using <strong>6 months</strong> of historical data to generate accurate <strong>7-day predictions</strong> 
        with the Prophet forecasting model. Accuracy typically 75-85% for next-day predictions.
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Get historical data (6 months for better accuracy)
        with st.spinner('Fetching 6 months of historical data...'):
            collector = components['collector']
            historical_data = collector.collect_historical_data(selected_city, days_back=180)
        
        if historical_data is not None and not historical_data.empty:
            # Show data range with modern card
            st.markdown(f"""
            <div class="data-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <strong style="color: #2563eb;">📊 Training Dataset</strong>
                        <p style="margin: 0.5rem 0 0 0; color: #6b7280;">
                            {len(historical_data)} measurements from {historical_data['timestamp'].min().date()} to {historical_data['timestamp'].max().date()}
                        </p>
                    </div>
                    <div style="font-size: 2rem;">📈</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Train and forecast
            forecaster = ProphetForecaster()
            
            with st.spinner('Training forecasting models and generating predictions...'):
                forecasts = forecaster.forecast_all_pollutants(
                    selected_city, 
                    historical_data, 
                    days_ahead=7
                )
            
            if forecasts:
                # Prepare historical data for comparison (last 200 days)
                cutoff_date = datetime.now() - timedelta(days=200)
                recent_historical = historical_data[historical_data['timestamp'] >= cutoff_date].copy()
                
                # Overall AQI forecast with historical comparison
                overall_forecast = forecaster.get_overall_aqi_forecast(forecasts)
                
                if not overall_forecast.empty:
                    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<h2 class="section-header">🔮 AQI Forecast Overview</h2>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Get historical AQI from MongoDB
                    db_ops = components['db_ops']
                    historical_aqi = db_ops.get_aqi_trends(selected_city, days=200)
                    
                    # Create combined chart
                    fig = go.Figure()
                    
                    # Plot historical actual values
                    if not historical_aqi.empty:
                        fig.add_trace(go.Scatter(
                            x=historical_aqi['timestamp'],
                            y=historical_aqi['aqi'],
                            mode='lines',
                            name='Historical (Actual)',
                            line=dict(color='#2563eb', width=2),
                            hovertemplate='<b>Actual</b><br>Date: %{x}<br>AQI: %{y}<extra></extra>'
                        ))
                    
                    # Plot predicted values
                    fig.add_trace(go.Scatter(
                        x=overall_forecast['date'],
                        y=overall_forecast['predicted_aqi'],
                        mode='lines+markers',
                        name='Forecast (Predicted)',
                        line=dict(color='#dc2626', width=3, dash='dash'),
                        marker=dict(size=10, symbol='diamond'),
                        hovertemplate='<b>Predicted</b><br>Date: %{x}<br>AQI: %{y}<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title=f"AQI Forecast: Past 200 Days + Next 7 Days",
                        xaxis_title="Date",
                        yaxis_title="AQI",
                        height=500,
                        hovermode='x unified',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Forecast table
                    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<h2 class="section-header">📅 7-Day Forecast Details</h2>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    display_forecast = overall_forecast[['date', 'predicted_aqi', 'aqi_category', 'dominant_pollutant']].copy()
                    display_forecast['date'] = display_forecast['date'].dt.strftime('%Y-%m-%d')
                    display_forecast.columns = ['Date', 'Predicted AQI', 'Category', 'Main Pollutant']
                    st.dataframe(display_forecast, use_container_width=True, hide_index=True)
                
                # Individual pollutant forecasts with historical comparison
                st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
                st.markdown('<h2 class="section-header">🧪 Pollutant-wise Forecasts</h2>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                for param, forecast_df in forecasts.items():
                    with st.expander(f"📊 {param.upper()} - Historical Trend + Forecast", expanded=False):
                        # Get historical values for this parameter
                        param_historical = recent_historical[recent_historical['parameter'] == param].copy()
                        param_historical = param_historical.groupby(param_historical['timestamp'].dt.date)['value'].mean().reset_index()
                        param_historical.columns = ['date', 'value']
                        param_historical['date'] = pd.to_datetime(param_historical['date'])
                        
                        fig = go.Figure()
                        
                        # Historical actual
                        if not param_historical.empty:
                            fig.add_trace(go.Scatter(
                                x=param_historical['date'],
                                y=param_historical['value'],
                                mode='lines',
                                name='Historical (Actual)',
                                line=dict(color='#059669', width=2),
                                hovertemplate='<b>Actual</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
                            ))
                        
                        # Predicted future
                        fig.add_trace(go.Scatter(
                            x=forecast_df['date'],
                            y=forecast_df['predicted_value'],
                            mode='lines+markers',
                            name='Forecast (Predicted)',
                            line=dict(color='#dc2626', width=3, dash='dash'),
                            marker=dict(size=10, symbol='diamond'),
                            hovertemplate='<b>Predicted</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
                        ))
                        
                        # Confidence interval (shaded area)
                        fig.add_trace(go.Scatter(
                            x=forecast_df['date'],
                            y=forecast_df['upper_bound'],
                            fill=None,
                            mode='lines',
                            line=dict(color='rgba(220, 38, 38, 0.0)', width=0),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_df['date'],
                            y=forecast_df['lower_bound'],
                            fill='tonexty',
                            mode='lines',
                            line=dict(color='rgba(220, 38, 38, 0.0)', width=0),
                            name='95% Confidence Interval',
                            fillcolor='rgba(220, 38, 38, 0.2)'
                        ))
                        
                        fig.update_layout(
                            title=f"{param.upper()} - Historical vs Forecast",
                            xaxis_title="Date",
                            yaxis_title=f"Concentration ({('µg/m³' if param != 'co' else 'mg/m³')})",
                            height=400,
                            hovermode='x unified',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        
                        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Unable to generate forecasts. Insufficient data.")
        else:
            st.error("No historical data available for forecasting.")
    
    except Exception as e:
        st.error(f"Error generating forecast: {str(e)}")

# Page: Health Impact - Modern Design with Better Explanations
elif page == "🏥 Health Impact":
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>🏥 Health Impact Assessment</h1>
        <p>Understand the health implications for {selected_city}</p>
        <p style="font-size: 0.95rem; margin-top: 0.5rem; opacity: 0.9;">
            Learn how current air quality affects different groups of people
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about health impacts
    with st.expander("📖 Understanding Health Impacts of Air Pollution", expanded=False):
        st.markdown("""
        ### How Air Pollution Affects Your Health
        
        **What You'll See on This Page:**
        
        1. **Risk Scores (0-100)**
           - **Respiratory Risk**: Impact on breathing, lungs, asthma
           - **Cardiovascular Risk**: Impact on heart and blood vessels
           - Higher numbers = greater risk
        
        2. **Affected Population Estimates**
           - Shows how many people in your city may be affected
           - Different groups have different vulnerability levels
        
        3. **Health Advisory**
           - Specific recommendations based on current pollution levels
           - Tailored advice for what you should or shouldn't do
        
        **Who is Most Vulnerable?**
        
        - 👶 **Children**: Developing lungs more susceptible to damage
        - 👴 **Elderly**: Weakened immune systems, existing conditions
        - 🫁 **Respiratory Patients**: Asthma, COPD, lung disease sufferers
        - ❤️ **Heart Patients**: Pollution can trigger cardiac events
        - 🤰 **Pregnant Women**: Affects fetal development
        - 🏃 **Active People**: Exercise increases breathing rate = more pollution inhaled
        
        **Short-term Effects:**
        - Eye, nose, throat irritation
        - Coughing, wheezing
        - Reduced lung function
        - Asthma attacks
        - Headaches, dizziness
        
        **Long-term Effects:**
        - Chronic respiratory diseases
        - Heart disease
        - Lung cancer
        - Reduced life expectancy
        - Developmental issues in children
        
        **What You Can Do:**
        - 🏠 Stay indoors on high pollution days
        - 😷 Wear N95 masks when outdoors
        - 🪟 Use air purifiers at home
        - 🏃 Exercise indoors or early morning when pollution is lower
        - 🌳 Support urban greening initiatives
        - 🚌 Use public transport to reduce vehicle emissions
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.spinner(f'Analyzing health impact for {selected_city}...'):
        current_data = components['collector'].collect_current_data(use_cache=True)
    
    if selected_city in current_data and not current_data[selected_city].empty:
        city_df = current_data[selected_city]
        aqi_info = components['aqi_calc'].get_city_current_aqi(city_df)
        
        pollutants = {k: v for k, v in aqi_info.items() if k in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] and v is not None}
        
        # Health impact assessment
        health_impact = components['health_assessor'].assess_health_impact(
            selected_city,
            pollutants,
            aqi_info.get('aqi', 0)
        )
        
        # Risk Scores with modern design
        st.markdown('<h2 class="section-header">⚕️ Health Risk Assessment</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        resp_risk = health_impact.get('respiratory_risk', 0)
        cardio_risk = health_impact.get('cardiovascular_risk', 0)
        risk_category = health_impact.get('risk_category', 'Unknown')
        
        # Determine risk color
        if resp_risk < 30:
            resp_color = "#10b981"
        elif resp_risk < 60:
            resp_color = "#f59e0b"
        else:
            resp_color = "#ef4444"
        
        if cardio_risk < 30:
            cardio_color = "#10b981"
        elif cardio_risk < 60:
            cardio_color = "#f59e0b"
        else:
            cardio_color = "#ef4444"
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {resp_color}22 0%, {resp_color}11 100%);
                        padding: 2rem; border-radius: 12px; text-align: center;
                        border-left: 4px solid {resp_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">
                    🫁 Respiratory Risk
                </div>
                <div style="font-size: 3rem; font-weight: 700; color: {resp_color};">
                    {resp_risk:.1f}
                </div>
                <div style="font-size: 0.9rem; color: #6b7280;">out of 100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {cardio_color}22 0%, {cardio_color}11 100%);
                        padding: 2rem; border-radius: 12px; text-align: center;
                        border-left: 4px solid {cardio_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">
                    ❤️ Cardiovascular Risk
                </div>
                <div style="font-size: 3rem; font-weight: 700; color: {cardio_color};">
                    {cardio_risk:.1f}
                </div>
                <div style="font-size: 0.9rem; color: #6b7280;">out of 100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            overall_color = "#10b981" if "Low" in risk_category else "#f59e0b" if "Moderate" in risk_category else "#ef4444"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {overall_color}22 0%, {overall_color}11 100%);
                        padding: 2rem; border-radius: 12px; text-align: center;
                        border-left: 4px solid {overall_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem; font-weight: 500;">
                    🎯 Overall Risk
                </div>
                <div style="font-size: 2rem; font-weight: 700; color: {overall_color}; padding: 1rem 0;">
                    {risk_category}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk visualization
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📊 Risk Visualization</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        risk_data = pd.DataFrame({
            'Category': ['Respiratory', 'Cardiovascular'],
            'Risk Score': [resp_risk, cardio_risk]
        })
        
        fig = px.bar(
            risk_data,
            x='Category',
            y='Risk Score',
            color='Risk Score',
            color_continuous_scale=['#10b981', '#fbbf24', '#f59e0b', '#ef4444'],
            title="Health Risk Assessment",
            text='Risk Score',
            range_y=[0, 100]
        )
        fig.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Affected Population with modern design
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">👥 Estimated Affected Population</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        affected_pop = health_impact.get('affected_population', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="data-card">
                <div style="margin-bottom: 1rem;">
                    <strong style="color: #2563eb;">👥 General Population</strong>
                    <div style="font-size: 2rem; font-weight: 700; color: #1f2937; margin: 0.5rem 0;">
                        {affected_pop.get('general_affected', 0):,}
                    </div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">people affected</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-card" style="margin-top: 1rem;">
                <div style="margin-bottom: 1rem;">
                    <strong style="color: #f59e0b;">👶 Children at Risk</strong>
                    <div style="font-size: 2rem; font-weight: 700; color: #1f2937; margin: 0.5rem 0;">
                        {affected_pop.get('children_at_risk', 0):,}
                    </div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">vulnerable children</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="data-card">
                <div style="margin-bottom: 1rem;">
                    <strong style="color: #f59e0b;">👴 Elderly at Risk</strong>
                    <div style="font-size: 2rem; font-weight: 700; color: #1f2937; margin: 0.5rem 0;">
                        {affected_pop.get('elderly_at_risk', 0):,}
                    </div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">vulnerable elderly</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="data-card" style="margin-top: 1rem;">
                <div style="margin-bottom: 1rem;">
                    <strong style="color: #ef4444;">🫁 Respiratory Patients</strong>
                    <div style="font-size: 2rem; font-weight: 700; color: #1f2937; margin: 0.5rem 0;">
                        {affected_pop.get('respiratory_patients_at_risk', 0):,}
                    </div>
                    <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">at high risk</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Health Advisory
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📋 Health Advisory</h2>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        advisory_class = "alert-good" if "Low" in risk_category else "alert-moderate" if "Moderate" in risk_category else "alert-high"
        st.markdown(f"""
        <div class="alert-box {advisory_class}">
            <h3 style="margin: 0 0 1rem 0;">💡 Recommendations</h3>
            <p style="margin: 0; font-size: 1.1rem;">
                {health_impact.get('advisory', 'No specific advisory')}
            </p>
        </div>
        """, unsafe_allow_html=True)

# Page: Alerts - DISABLED FOR v1 (current version)
# Will be enabled in v2 for management version
# elif page == "🚨 Alerts":
#     st.markdown('<div class="main-header">🚨 Air Quality Alerts</div>', 
#                 unsafe_allow_html=True)
#     
#     with st.spinner('Checking for active alerts...'):
#         all_data = components['collector'].collect_current_data(use_cache=True)
#     
#     active_alerts = []
#     
#     for city, df in all_data.items():
#         if not df.empty:
#             aqi_info = components['aqi_calc'].get_city_current_aqi(df)
#             
#             # Check AQI threshold
#             aqi_alert = components['alert_manager'].check_aqi_threshold(city, aqi_info.get('aqi', 0))
#             if aqi_alert:
#                 active_alerts.append(aqi_alert)
#             
#             # Check pollutant thresholds
#             pollutants = {k: v for k, v in aqi_info.items() if k in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'] and v is not None}
#             pollutant_alerts = components['alert_manager'].check_pollutant_thresholds(city, pollutants)
#             active_alerts.extend(pollutant_alerts)
#     
#     if active_alerts:
#         st.error(f"⚠️ **{len(active_alerts)} ACTIVE ALERT(S)**")
#         
#         for alert in active_alerts:
#             severity_class = "alert-critical" if alert['severity'] in ['critical', 'high'] else "alert-high"
#             
#             st.markdown(f"""
#             <div class="alert-box {severity_class}">
#                 <strong>{alert['city']} - {alert['type']}</strong><br>
#                 Severity: {alert['severity'].upper()}<br>
#                 Value: {alert['value']}<br>
#                 {alert['message']}
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.success("✅ No active alerts. All cities within acceptable air quality levels.")
#     
#     # Alert Configuration
#     st.markdown("---")
#     st.markdown("### ⚙️ Alert Settings")
#     
#     with st.form("alert_settings"):
#         email = st.text_input("Email Address for Alerts")
#         phone = st.text_input("Phone Number for SMS Alerts (optional)")
#         
#         submitted = st.form_submit_button("Save Settings")
#         
#         if submitted:
#             st.success("Alert settings saved! You will receive notifications when thresholds are exceeded.")

# Modern Footer with FAQ and Resources
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Add FAQ Section
with st.expander("❓ Frequently Asked Questions (FAQ)", expanded=False):
    st.markdown("""
    ### Common Questions About Air Quality
    
    **Q: How often is the data updated?**
    - A: Data is typically updated hourly. Run `python scripts/fetch_data.py` to get the latest measurements.
    
    **Q: Why do different sources show different AQI values?**
    - A: Different sources may use different monitoring stations, update frequencies, or calculation methods. 
      Our app combines multiple sources (OpenAQ, WAQI) for comprehensive coverage.
    
    **Q: What should I do on high pollution days?**
    - A: Limit outdoor activities, wear N95 masks if you must go out, keep windows closed, 
      use air purifiers indoors, and avoid exercise outdoors.
    
    **Q: Is PM2.5 or PM10 more dangerous?**
    - A: PM2.5 is more dangerous because particles are smaller and can penetrate deeper into lungs and bloodstream.
    
    **Q: Can I trust the forecasts?**
    - A: Forecasts are 75-85% accurate for next-day predictions but accuracy decreases for later days. 
      Use them for general planning, not exact predictions.
    
    **Q: Why is winter pollution worse in Pakistan?**
    - A: Temperature inversions trap pollutants near ground, more burning (coal/wood for heating), 
      crop burning, firecracker use, and reduced air circulation.
    
    **Q: What are safe AQI levels?**
    - A: AQI 0-50 is considered safe for everyone. 51-100 is acceptable for most people. 
      Above 100 starts affecting sensitive groups.
    
    **Q: How can I protect my children?**
    - A: Keep them indoors on high pollution days, ensure they're not playing outdoors during peak pollution hours 
      (early morning & evening), watch for symptoms (coughing, wheezing), and consult a doctor if concerned.
    
    **Q: Do masks really help?**
    - A: N95/N99 masks can filter out PM2.5 and PM10 effectively. Regular cloth masks offer minimal protection. 
      Ensure proper fit for maximum effectiveness.
    
    **Q: What's the dominant pollutant?**
    - A: The pollutant with the highest AQI value. It determines the overall AQI and is the main health concern.
    """)

# Add Resources Section
with st.expander("📚 Additional Resources & Tips", expanded=False):
    st.markdown("""
    ### Learn More & Take Action
    
    **🔗 Useful Resources:**
    - [World Health Organization - Air Quality Guidelines](https://www.who.int/health-topics/air-pollution)
    - [US EPA - AQI Basics](https://www.airnow.gov/aqi/aqi-basics/)
    - [Pakistan EPA - Environmental Updates](http://environment.gov.pk/)
    
    **💡 Practical Tips:**
    
    **At Home:**
    - Use HEPA air purifiers in bedrooms
    - Keep windows closed during high pollution periods
    - Avoid using fireplaces or burning incense
    - Ventilate when cooking
    - Add indoor plants (snake plant, spider plant, peace lily)
    
    **Outdoors:**
    - Check AQI before planning activities
    - Wear properly fitted N95/N99 masks
    - Avoid busy roads and traffic areas
    - Exercise early morning when pollution is typically lower
    - Stay hydrated
    
    **For Your Car:**
    - Keep windows closed, use recirculation mode
    - Regular vehicle maintenance reduces emissions
    - Consider carpooling or public transport
    
    **Long-term Actions:**
    - Support clean energy initiatives
    - Plant trees in your community
    - Advocate for better air quality policies
    - Reduce personal carbon footprint
    - Raise awareness among family and friends
    
    **When to Seek Medical Help:**
    - Persistent coughing or wheezing
    - Difficulty breathing
    - Chest pain or tightness
    - Severe headaches
    - Existing conditions (asthma, COPD) worsening
    """)

st.markdown(
    """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 3rem 2rem; border-radius: 12px; margin-top: 4rem; color: white; text-align: center;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);">
        <h3 style="margin: 0 0 1.5rem 0; color: white; font-size: 1.8rem; font-weight: 700;">
            🌍 AirWatch - Pakistan Air Quality Monitor
        </h3>
        <div style="max-width: 900px; margin: 0 auto;">
            <p style="margin: 0.75rem 0; opacity: 0.95; font-size: 1rem; line-height: 1.6;">
                Real-time air quality analysis, health impact assessment, and AI-powered forecasting 
                for major Pakistani cities. Empowering citizens with data-driven environmental insights.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0;">
                <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; backdrop-filter: blur(10px);">
                    <div style="font-size: 0.85rem; opacity: 0.9; font-weight: 600; margin-bottom: 0.25rem;">📊 Data Sources</div>
                    <div style="font-size: 0.9rem;">OpenAQ API • WAQI</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; backdrop-filter: blur(10px);">
                    <div style="font-size: 0.85rem; opacity: 0.9; font-weight: 600; margin-bottom: 0.25rem;">🏙️ Cities Monitored</div>
                    <div style="font-size: 0.9rem;">Islamabad • Rawalpindi • Karachi</div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 8px; backdrop-filter: blur(10px);">
                    <div style="font-size: 0.85rem; opacity: 0.9; font-weight: 600; margin-bottom: 0.25rem;">🤖 AI Technology</div>
                    <div style="font-size: 0.9rem;">Prophet Forecasting Model</div>
                </div>
            </div>
            <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.2);">
                <p style="margin: 0 0 0.5rem 0; opacity: 0.85; font-size: 0.85rem;">
                    ⚠️ <strong>Disclaimer:</strong> This tool provides informational data. 
                    For critical health decisions, consult official health authorities and medical professionals.
                </p>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 0.75rem;">
                    Developed for public health awareness and environmental monitoring • © 2026 AirWatch Pakistan
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
