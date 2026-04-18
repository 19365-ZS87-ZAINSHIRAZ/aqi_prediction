"""
Database Operations Module
Now using MongoDB exclusively
"""
# Import MongoDB operations as the primary database interface
from .mongodb_operations import MongoDBOperations as DatabaseOperations

# For backward compatibility, export as DatabaseOperations
__all__ = ['DatabaseOperations']
