from utils.userutils import get_user
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from utils.logutils import log_error
from flask import jsonify

def api_response(success, message=None, data=None, status_code=200):
    """
    Standardized API response format
    
    Args:
        success: Boolean indicating success/failure
        message: Optional message string
        data: Optional data dictionary
        status_code: HTTP status code
        
    Returns:
        tuple: (Flask response object, status_code)
    """
    response = {'success': success}
    if message:
        response['message'] = message
    if data:
        response.update(data)
    return jsonify(response), status_code

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

# Session validation functions
invalid_sessions = set()
exempt_sessions = {}

def is_session_valid(username):
    """
    Check if a user session is valid
    
    Args:
        username: Username to check
        
    Returns:
        Boolean indicating if session is valid
    """
    from flask import request
    
    user = get_user(username)
    
    if not user:
        return False
    
    current_sid = None
    if hasattr(request, 'sid'):
        current_sid = request.sid
    
    user_id_str = str(user['id'])
    if user_id_str in invalid_sessions:
        if user_id_str in exempt_sessions and exempt_sessions[user_id_str] == current_sid:
            return True
        return False
    
    if user.get('is_suspended', False):
        return False
    
    return True

def invalidate_user_session(user_id):
    """
    Invalidate a user session by ID
    
    Args:
        user_id: User ID to invalidate
    """
    user_id_str = str(user_id)
    invalid_sessions.add(user_id_str)
    if user_id_str in exempt_sessions:
        del exempt_sessions[user_id_str]
    log_info(f"Session invalidated for user ID: {user_id}")

def validate_user_session(user_id):
    """
    Validate a previously invalidated session
    
    Args:
        user_id: User ID to validate
    """
    user_id_str = str(user_id)
    if user_id_str in invalid_sessions:
        invalid_sessions.remove(user_id_str)
    if user_id_str in exempt_sessions:
        del exempt_sessions[user_id_str]
    log_info(f"Session validated for user ID: {user_id}")
