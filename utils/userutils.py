import json, os, time
from utils.logutils import log_error

_users_cache = None
_last_load_time = 0
_cache_ttl = 5  # seconds

def load_users():
    """
    Load users from JSON file with caching
    
    Returns:
        List of user dictionaries
    """
    global _users_cache, _last_load_time
    current_time = time.time()
    
    if _users_cache and current_time - _last_load_time < _cache_ttl:
        return _users_cache
    
    users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
    try:
        with open(users_file, 'r') as f:
            _users_cache = json.load(f)
            _last_load_time = current_time
            return _users_cache
    except Exception as e:
        log_error(f"Error loading users: {str(e)}")
        _users_cache = []
        _last_load_time = current_time
        return _users_cache

def save_users(users):
    """
    Save users to JSON file and update cache
    
    Args:
        users: List of user dictionaries
    
    Returns:
        Boolean indicating success or failure
    """
    global _users_cache, _last_load_time
    _users_cache = users
    _last_load_time = time.time()
    
    users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f)
        return True
    except Exception as e:
        log_error(f"Error saving users: {str(e)}")
        return False

def get_user(identifier, identifier_type='username', users=None):
    """
    Get user by identifier (username or id)
    
    Args:
        identifier: Username string or user ID
        identifier_type: 'username' or 'id'
        users: Optional pre-loaded users list
        
    Returns:
        User dict or None if not found
    """
    if users is None:
        users = load_users()
    
    if identifier_type == 'username':
        return next((user for user in users if user['username'] == identifier), None)
    elif identifier_type == 'id':
        return next((user for user in users if user['id'] == identifier), None)
    return None

def update_user(user_id, updates, users=None):
    """
    Update user with specified changes
    
    Args:
        user_id: ID of user to update
        updates: Dictionary of fields to update
        users: Optional pre-loaded users list
        
    Returns:
        Updated user dict or None if not found
    """
    if users is None:
        users = load_users()
    
    for i, user in enumerate(users):
        if user['id'] == user_id:
            users[i].update(updates)
            save_users(users)
            return users[i]
    
    return None
