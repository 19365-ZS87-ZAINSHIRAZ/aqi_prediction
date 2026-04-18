"""
Database Models and Schema Definitions
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import POSTGRES_CONFIG

Base = declarative_base()


class AirQualityMeasurement(Base):
    """Air quality measurement data"""
    __tablename__ = 'air_quality_measurements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50), nullable=False, index=True)
    location = Column(String(200))
    parameter = Column(String(20), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    aqi = Column(Integer)
    timestamp = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    source = Column(String(50))
    collected_at = Column(DateTime, default=datetime.now)
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_city_param_time', 'city', 'parameter', 'timestamp'),
    )


class AQIHistory(Base):
    """Historical AQI records"""
    __tablename__ = 'aqi_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50), nullable=False, index=True)
    aqi = Column(Integer, nullable=False)
    aqi_category = Column(String(50))
    dominant_pollutant = Column(String(20))
    pm25 = Column(Float)
    pm10 = Column(Float)
    no2 = Column(Float)
    so2 = Column(Float)
    co = Column(Float)
    o3 = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)
    health_risk_score = Column(Float)
    
    __table_args__ = (
        Index('idx_city_time', 'city', 'timestamp'),
    )


class HealthImpact(Base):
    """Health impact assessments"""
    __tablename__ = 'health_impacts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    respiratory_risk = Column(Float)
    cardiovascular_risk = Column(Float)
    overall_risk = Column(Float)
    risk_category = Column(String(50))
    affected_population_estimate = Column(Integer)
    health_advisory = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Forecast(Base):
    """Air quality forecasts"""
    __tablename__ = 'forecasts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50), nullable=False, index=True)
    forecast_date = Column(DateTime, nullable=False, index=True)
    parameter = Column(String(20), nullable=False)
    predicted_value = Column(Float, nullable=False)
    predicted_aqi = Column(Integer)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_used = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_city_forecast_param', 'city', 'forecast_date', 'parameter'),
    )


class Alert(Base):
    """Alert history"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # AQI, PM2.5, PM10, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    aqi_value = Column(Integer)
    pollutant_value = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    sent_email = Column(Integer, default=0)  # Boolean as int
    sent_sms = Column(Integer, default=0)
    acknowledged = Column(Integer, default=0)


class MonitoringStation(Base):
    """Monitoring station information"""
    __tablename__ = 'monitoring_stations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    parameters_measured = Column(String(200))
    source = Column(String(50))
    first_seen = Column(DateTime, default=datetime.now)
    last_updated = Column(DateTime, default=datetime.now)
    is_active = Column(Integer, default=1)


def get_db_engine():
    """Create and return database engine"""
    connection_string = (
        f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
        f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
    )
    engine = create_engine(connection_string, echo=False)
    return engine


def init_database():
    """Initialize database tables"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully")


def get_session():
    """Get database session"""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()
