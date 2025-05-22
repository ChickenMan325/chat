from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import check_password_hash
from utils.userutils import load_users
from utils.sessionutils import invalidate_session
from utils.logutils import log_error

def authenticate_user(username, password):
    users = load_users()
    user = next((u for u in users if u['username'] == username), None)
    
    if not user:
        return None, "Invalid username or password"
    
    if user.get('is_suspended', False):
        return None, "Account suspended"
    
    if not check_password_hash(user['password'], password):
        return None, "Invalid username or password"
    
    return user, None

def login_user(username, response):
    """
    Set JWT access token cookies on response object
    
    Args:
        username: User identity for JWT token
        response: Response object or tuple from api_response
        
    Returns:
        Response object with JWT cookies set
    """
    access_token = create_access_token(identity=username)
    
    # Fix for critical registration error - handle tuple response
    if isinstance(response, tuple):
        response = response[0]  # Extract the response object from the tuple
    
    try:
        set_access_cookies(response, access_token)
    except Exception as e:
        log_error(f"Error setting access cookies: {str(e)}")
        
    return response

def logout_user(response):
    """
    Unset JWT cookies on response object
    
    Args:
        response: Response object or tuple from api_response
        
    Returns:
        Response object with JWT cookies unset
    """
    # Fix for logout error - handle tuple response
    if isinstance(response, tuple):
        response = response[0]  # Extract the response object from the tuple
    
    try:
        unset_jwt_cookies(response)
    except Exception as e:
        log_error(f"Error unsetting JWT cookies: {str(e)}")
    
    return response
