from utils.userutils import get_user
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import re # Added import for validate_username
from utils.logutils import log_error, log_info
from flask import jsonify
from .responseutils import api_response
from .sessionutils import is_session_valid # Added import

# Moved from apiendpoints/auth.py
def validate_username(username):
    """Validate username against security requirements"""
    if not username or not isinstance(username, str):
        return False, "Username must be a non-empty string"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_password(password):
    """Validate password against security requirements"""
    if not password or not isinstance(password, str):
        return False, "Password must be a non-empty string"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    if not any(char.isalpha() for char in password):
        return False, "Password must contain at least one letter"
    
    return True, None

def auth_middleware():
    """
    Middleware to verify JWT and user authentication status
    
    Returns:
        tuple: (user_object, error_response)
            - If authenticated: (user_object, None)
            - If not authenticated: (None, error_response)
    """
    try:
        verify_jwt_in_request()
        username = get_jwt_identity()
        
        if not is_session_valid(username):
            return None, api_response(False, 'Unauthorized', status_code=401)
            
        user = get_user(username)
        if not user:
            return None, api_response(False, 'Unauthorized', status_code=401)
            
        return user, None
    except Exception as e:
        log_error(f"Authentication error: {str(e)}")
        return None, api_response(False, 'Unauthorized', status_code=401)

def admin_required(f):
    """
    Decorator to require admin privileges
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function that checks for admin privileges
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        username = get_jwt_identity()
        user = get_user(username)
        
        if not user or not user.get('is_admin', False):
            return api_response(False, 'Unauthorized', status_code=401)
            
        return f(*args, **kwargs)
    return decorated

# Session validation functions removed from here
