from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
import time
import re
from utils.pfputils import save_profile_picture
from utils.authutils import invalidate_user_session, admin_required, api_response
from utils.userutils import load_users, save_users, get_user, update_user
from utils.auth_manager import authenticate_user, login_user, logout_user
from utils.ratelimit import login_limiter
from utils.logutils import log_info, log_error
from utils.decorators import api_error_handler, require_fields

auth_bp = Blueprint('auth', __name__)

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

@auth_bp.route('/login', methods=['POST'])
@api_error_handler
@require_fields('username', 'password')
def login():
    data = request.get_json()
    
    ip = request.remote_addr
    if login_limiter.is_rate_limited(ip):
        return api_response(False, 'Too many login attempts. Please try again later.', status_code=429)
    
    user, error = authenticate_user(data.get('username'), data.get('password'))
    
    if error:
        return api_response(False, error, status_code=401)
    
    resp = api_response(True, 'Login successful')
    return login_user(user['username'], resp)

@auth_bp.route('/register', methods=['POST'])
@api_error_handler
def register():
    if request.content_type and 'multipart/form-data' in request.content_type:
        username = request.form.get('username')
        password = request.form.get('password')
        profile_picture = request.files.get('profile_picture')
    else:
        data = request.get_json()
        if not data:
            return api_response(False, 'Invalid request format', status_code=400)
        username = data.get('username')
        password = data.get('password')
        profile_picture = None
    
    if not username or not password:
        return api_response(False, 'Username and password required', status_code=400)
    
    # Use centralized validation functions
    valid, error = validate_username(username)
    if not valid:
        return api_response(False, error, status_code=400)
    
    valid, error = validate_password(password)
    if not valid:
        return api_response(False, error, status_code=400)
    
    users = load_users()
    
    if get_user(username, 'username', users):
        return api_response(False, 'Username already exists', status_code=400)
    
    profile_picture_path = None
    if profile_picture:
        profile_picture_path = save_profile_picture(profile_picture)
        if profile_picture_path:
            log_info(f"Profile picture saved: {profile_picture_path}")
    
    new_user = {
        'id': len(users) + 1,
        'username': username,
        'password': generate_password_hash(password),
        'is_admin': False,
        'is_suspended': False,
        'created_at': int(time.time())
    }
    
    if profile_picture_path:
        new_user['profile_picture'] = profile_picture_path
    
    users.append(new_user)
    save_users(users)
    
    resp = api_response(True, 'Registration successful')
    return login_user(username, resp)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = api_response(True, 'Logout successful')
    return logout_user(resp)

@auth_bp.route('/force-logout', methods=['POST'])
@jwt_required()
@admin_required
@api_error_handler
@require_fields('user_id')
def force_logout():
    data = request.get_json()
    target_user_id = int(data.get('user_id'))
    target_user = get_user(target_user_id, 'id')
    
    if not target_user:
        return api_response(False, 'User not found', status_code=404)
    
    invalidate_user_session(target_user_id)
    return api_response(True, 'User forced to logout')
