"""
Clear All MongoDB Data
Removes all collections and starts fresh
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.database.mongodb_operations import MongoDBOperations


def main():
    """Clear all MongoDB collections"""
    logger.info("=" * 60)
    logger.info("MongoDB Database Cleaner")
    logger.info("=" * 60)
    
    db_ops = MongoDBOperations()
    
    # Get all collection names
    collections = db_ops.db.list_collection_names()
    
    if not collections:
        logger.info("Database is already empty")
        return
    
    logger.warning(f"Found {len(collections)} collections: {', '.join(collections)}")
    logger.warning("Clearing all data...")
    
    # Drop each collection
    for collection_name in collections:
        count_before = db_ops.db[collection_name].count_documents({})
        db_ops.db[collection_name].drop()
        logger.info(f"  ✓ Dropped '{collection_name}' ({count_before} documents)")
    
    logger.success("\n" + "=" * 60)
    logger.success("All data cleared successfully!")
    logger.success("Database is now empty and ready for new data")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
