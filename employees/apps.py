from django.apps import AppConfig

class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    
    def ready(self):
        # Set up database indexes when the app starts
        try:
            from .database import setup_database_indexes
            setup_database_indexes()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not set up database indexes: {e}")
