from functools import wraps
from utils.logutils import log_error
from flask import jsonify

def api_error_handler(f):
    """
    Decorator for standardized API error handling
    
    Wraps API endpoint functions to catch exceptions and return
    standardized error responses
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function with error handling
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log_error(f"Error in {f.__name__}: {str(e)}")
            from utils.authutils import api_response
            return api_response(False, 'An error occurred while processing your request', status_code=500)
    return decorated

def require_fields(*fields):
    """
    Decorator to require specific fields in request JSON
    
    Args:
        *fields: Field names to require
        
    Returns:
        Decorated function that validates required fields
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask import request
            from utils.authutils import api_response
            
            data = request.get_json()
            
            if not data:
                return api_response(False, 'Request must include JSON data', status_code=400)
                
            missing_fields = [field for field in fields if field not in data]
            if missing_fields:
                return api_response(False, f'Missing required fields: {", ".join(missing_fields)}', status_code=400)
                
            return f(*args, **kwargs)
        return decorated
    return decorator
