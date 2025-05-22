from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies
import time
from utils.pfputils import save_profile_picture, delete_profile_picture
from utils.userutils import load_users, save_users, get_user, update_user
from utils.authutils import auth_middleware, api_response
from utils.decorators import api_error_handler
from utils.logutils import log_info, log_error
from utils.sessionutils import emit_to_user
from utils.authutils import validate_username # Changed import

user_bp = Blueprint('user', __name__)

def get_user_profile_data(user, include_admin=False):
    """Centralized function to get user profile data"""
    profile_data = {
        'id': user['id'],
        'username': user['username'],
        'created_at': user['created_at'],
        'profile_picture': user.get('profile_picture')
    }
    
    if include_admin:
        profile_data['is_admin'] = user.get('is_admin', False)
        
    return profile_data

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
@api_error_handler
def get_profile():
    user, error_response = auth_middleware()
    if error_response:
        return error_response
    
    return api_response(True, data={
        'user': get_user_profile_data(user)
    })

@user_bp.route('/me', methods=['GET'])
@jwt_required()
@api_error_handler
def get_me():
    user, error_response = auth_middleware()
    if error_response:
        return error_response
    
    return api_response(True, data={
        'user': get_user_profile_data(user, include_admin=True)
    })

@user_bp.route('/update-username', methods=['POST'])
@jwt_required()
@api_error_handler
def update_username():
    user, error_response = auth_middleware()
    if error_response:
        return error_response
    
    data = request.get_json()
    
    if not data or not data.get('new_username'):
        return api_response(False, 'New username required', status_code=400)
    
    new_username = data.get('new_username')
    
    # Use centralized validation function
    valid, error = validate_username(new_username)
    if not valid:
        return api_response(False, error, status_code=400)
    
    current_username = user['username']
    
    # Only check for duplicates if username is actually changing
    if new_username != current_username:
        users = load_users()
        if any(u['username'] == new_username for u in users):
            return api_response(False, 'Username already exists', status_code=400)
        
        old_username = current_username
        
        # Update username in users database
        updates = {
            'username': new_username,
            'username_changed_at': int(time.time())
        }
        update_user(user['id'], updates)
        
        # Update session mapping
        if hasattr(current_app, 'user_sessions'):
            if old_username in current_app.user_sessions:
                session_id = current_app.user_sessions[old_username]
                del current_app.user_sessions[old_username]
                current_app.user_sessions[new_username] = session_id
                log_info(f"Session ID {session_id} remapped from {old_username} to {new_username}")
        
        # Create new access token with updated identity
        access_token = create_access_token(identity=new_username)
        
        resp = api_response(True, 'Username updated successfully', data={'new_username': new_username})
        set_access_cookies(resp[0], access_token)
        
        return resp
    else:
        return api_response(False, 'New username must be different from current username', status_code=400)

@user_bp.route('/update-profile-picture', methods=['POST'])
@jwt_required()
@api_error_handler
def update_profile_picture():
    user, error_response = auth_middleware()
    if error_response:
        return error_response
    
    if 'profile_picture' not in request.files:
        return api_response(False, 'No profile picture provided', status_code=400)
    
    profile_picture = request.files['profile_picture']
    
    if not profile_picture.filename:
        return api_response(False, 'No profile picture selected', status_code=400)
    
    # Delete old profile picture if exists
    if 'profile_picture' in user:
        delete_profile_picture(user['profile_picture'])
    
    profile_picture_path = save_profile_picture(profile_picture)
    
    if not profile_picture_path:
        return api_response(False, 'Failed to save profile picture', status_code=500)
    
    # Update user record with new profile picture path
    updates = {
        'profile_picture': profile_picture_path
    }
    update_user(user['id'], updates)
    
    return api_response(True, 'Profile picture updated successfully', data={'profile_picture': profile_picture_path})
