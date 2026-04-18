"""
Database Initialization Script for MongoDB
Sets up MongoDB collections and indexes
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_operations import MongoDBOperations
from loguru import logger
from config.settings import MONGODB_URI, MONGODB_DB

def main():
    """Initialize MongoDB database"""
    logger.info("Initializing MongoDB database...")
    logger.info(f"Database: {MONGODB_DB}")
    
    try:
        # Initialize MongoDB operations (this will create indexes)
        db_ops = MongoDBOperations()
        
        logger.success("✓ MongoDB initialized successfully!")
        logger.info("Collections and indexes created:")
        logger.info("  - air_quality_measurements")
        logger.info("  - aqi_history")
        logger.info("  - health_impacts")
        logger.info("  - forecasts")
        logger.info("  - monitoring_stations")
        logger.info("")
        logger.info("MongoDB is ready to use!")
        logger.info(f"Connection: {MONGODB_URI}")
        logger.info(f"Database: {MONGODB_DB}")
        
    except Exception as e:
        logger.error(f"✗ Error initializing MongoDB: {e}")
        logger.info("Make sure:")
        logger.info("  1. MongoDB is running")
        logger.info("  2. MONGODB_URI in .env is correct")
        logger.info("  3. You have connection permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()
