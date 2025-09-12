"""
MongoDB Database Connection

This file handles connecting to MongoDB database.
I'm using pymongo to interact with MongoDB from Django.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    This class manages the MongoDB connection using singleton pattern.
    This way I only create one connection for the entire app.
    """
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        """
        Makes sure we only have one instance of database connection.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initializes MongoDB connection when first created.
        """
        if self._client is None:
            self._connect()
    
    def _connect(self):
        """
        Establish connection to MongoDB using settings from Django configuration.
        """
        try:
            # Create MongoDB client using URI from settings
            self._client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Test the connection by pinging the server
            self._client.admin.command('ping')
            
            # Get the database instance
            self._database = self._client[settings.MONGO_DB_NAME]
            
            logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
            print(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
            
        except ConnectionFailure as e:
            logger.warning(f"❌ Failed to connect to MongoDB: {e}")
            print(f"❌ MongoDB not available: {e}")
            print("⚠️  Using fallback mode for demo")
            self._client = None
            self._database = None
        except Exception as e:
            logger.error(f"❌ Error connecting to MongoDB: {e}")
            print(f"❌ MongoDB connection error: {e}")
            print("⚠️  Using fallback mode for demo")
            self._client = None
            self._database = None
     
    @property
    def database(self):
        """
        Get the MongoDB database instance.
        Returns the database object for performing operations.
        """
        if self._database is None:
            self._connect()
        return self._database
    
    @property
    def client(self):
        """
        Get the MongoDB client instance.
        """
        if self._client is None:
            self._connect()
        return self._client
    
    def close_connection(self):
        """
        Close the MongoDB connection.
        Useful for cleanup when the application shuts down.
        """
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# Create a global instance of the database connection
db_connection = DatabaseConnection()

# Get the database instance that will be used throughout the app
database = None
employees_collection = None

# Initialize connection on import, but don't fail if MongoDB is not available
try:
    database = db_connection.database
    if database is not None:
        employees_collection = database.employees
    else:
        logger.warning("MongoDB not available - employees_collection is None")
except Exception as e:
    logger.warning(f"Could not initialize MongoDB collections: {e}")
    database = None
    employees_collection = None

def setup_database_indexes():
    """
    Set up database indexes for better query performance.
    Indexes make searching and sorting much faster.
    """
    try:
        # Create unique index on employee_id to prevent duplicates
        employees_collection.create_index("employee_id", unique=True)
        
        # Create indexes on commonly searched fields
        employees_collection.create_index("department")  # For department filtering
        employees_collection.create_index("skills")      # For skill searching
        employees_collection.create_index("email", unique=True)  # Unique email addresses
        employees_collection.create_index("joining_date")  # For date-based queries
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating database indexes: {e}")

def get_database_stats():
    """
    Get basic statistics about the database.
    Useful for monitoring and debugging.
    """
    try:
        stats = {
            'total_employees': employees_collection.count_documents({}),
            'database_name': database.name,
            'collection_names': database.list_collection_names()
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return None
