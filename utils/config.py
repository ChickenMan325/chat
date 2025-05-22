import os
import json
import datetime
from utils.logutils import log_info, log_error

class Config:
    """
    Application configuration settings
    
    Centralizes all configuration parameters and provides
    initialization methods for the Flask application
    """
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES_DAYS = 365
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    PROFILE_PICTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'pfps')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    
    @classmethod
    def init_app(cls, app):
        """
        Initialize Flask application with configuration settings
        
        Args:
            app: Flask application instance
        """
        try:
            # JWT configuration
            app.config['JWT_SECRET_KEY'] = cls.JWT_SECRET_KEY
            app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=cls.JWT_ACCESS_TOKEN_EXPIRES_DAYS)
            app.config['JSON_SORT_KEYS'] = False
            app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
            app.config['JWT_COOKIE_SECURE'] = True
            app.config['JWT_COOKIE_CSRF_PROTECT'] = True
            app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
            app.config['JWT_COOKIE_PATH'] = '/'
            app.config['JWT_COOKIE_DOMAIN'] = None
            app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
            
            # Flask configuration
            app.config['SECRET_KEY'] = cls.SECRET_KEY
            
            # Ensure directories exist
            os.makedirs(cls.DATA_DIR, exist_ok=True)
            os.makedirs(cls.PROFILE_PICTURES_DIR, exist_ok=True)
            
            # Initialize users file if it doesn't exist
            if not os.path.exists(cls.USERS_FILE):
                with open(cls.USERS_FILE, 'w') as f:
                    json.dump([], f)
                    
            log_info("Application configuration initialized successfully")
        except Exception as e:
            log_error(f"Error initializing application configuration: {str(e)}")
            raise
