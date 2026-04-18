"""
Logging Configuration
Sets up logging for the application
"""
import sys
from loguru import logger
from pathlib import Path
from config.settings import LOGS_DIR, LOG_LEVEL

# Remove default handler
logger.remove()

# Console handler with colors
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# File handler for all logs
logger.add(
    LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # Rotate at midnight
    retention="30 days",  # Keep logs for 30 days
    compression="zip",  # Compress old logs
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# File handler for errors only
logger.add(
    LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",
    compression="zip",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
)

logger.info("Logging system initialized")
