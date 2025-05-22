from flask import current_app, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from utils.userutils import load_users, get_user
from utils.logutils import log_info, log_error

# Centralized invalid sessions tracking
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

def get_current_user():
    """
    Get the current authenticated user from JWT token
    
    Returns:
        dict: User object if authenticated, None otherwise
    """
    try:
        verify_jwt_in_request()
        username = get_jwt_identity()
        
        if not is_session_valid(username):
            return None
            
        return get_user(username)
    except Exception as e:
        log_error(f"Error getting current user: {str(e)}")
        return None

def invalidate_session(user_id):
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

def validate_session(user_id):
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

def get_session_id(username):
    """
    Get Socket.IO session ID for a username
    
    Args:
        username: Username to get session ID for
        
    Returns:
        str: Session ID if found, None otherwise
    """
    if hasattr(current_app, 'user_sessions') and username in current_app.user_sessions:
        return current_app.user_sessions[username]
    return None

def emit_to_user(username, event, data):
    """
    Emit a Socket.IO event to a specific user
    
    Args:
        username: Target username
        event: Event name
        data: Event data
        
    Returns:
        bool: True if event was emitted, False otherwise
    """
    session_id = get_session_id(username)
    if session_id and hasattr(current_app, 'socketio'):
        try:
            current_app.socketio.emit(event, data, room=username)
            return True
        except Exception as e:
            log_error(f"Error emitting event to user: {str(e)}")
    return False
