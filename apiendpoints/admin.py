from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from utils.userutils import load_users, save_users, get_user, update_user
from utils.authutils import admin_required, api_response
from utils.sessionutils import validate_session, emit_to_user
from utils.decorators import api_error_handler, require_fields
import time
from utils.logutils import log_info, log_error

admin_bp = Blueprint('admin', __name__)

def update_user_suspension_status(username=None, user_id=None, suspend=True):
    """
    Centralized function to handle user suspension/unsuspension
    
    Args:
        username: Target username (optional if user_id provided)
        user_id: Target user ID (optional if username provided)
        suspend: True to suspend, False to unsuspend
    
    Returns:
        tuple: (success, response_or_error)
    """
    users = load_users()
    target_user = None
    
    # Find user by either username or ID
    if username:
        target_user = get_user(username, 'username', users)
    elif user_id:
        target_user = get_user(user_id, 'id', users)
    
    if not target_user:
        return False, api_response(False, 'User not found', status_code=404)
    
    # Update user suspension status
    updates = {
        'is_suspended': suspend
    }
    
    if suspend:
        updates['suspended_at'] = int(time.time())
    
    user_id = target_user['id']
    update_user(user_id, updates)
    
    # Handle session validation
    validate_session(user_id)
    
    # Notify user via Socket.IO if connected
    target_username = target_user['username']
    if hasattr(current_app, 'socketio'):
        reason = 'suspended' if suspend else 'unsuspended'
        message = 'Your account has been suspended by an administrator' if suspend else 'Your account has been unsuspended. Please log in again.'
        
        emit_data = {
            'reason': reason,
            'message': message,
            'timestamp': int(time.time()),
            'user_id': user_id
        }
        emit_to_user(target_username, 'force_logout', emit_data)
    
    action = 'suspended' if suspend else 'unsuspended'
    return True, api_response(True, f"User {target_username} has been {action}")

@admin_bp.route('/suspend', methods=['POST'])
@jwt_required()
@admin_required
@api_error_handler
@require_fields('username')
def suspend_user():
    data = request.get_json()
    success, response = update_user_suspension_status(username=data.get('username'), suspend=True)
    return response

@admin_bp.route('/unsuspend', methods=['POST'])
@jwt_required()
@admin_required
@api_error_handler
@require_fields('username')
def unsuspend_user():
    data = request.get_json()
    success, response = update_user_suspension_status(username=data.get('username'), suspend=False)
    return response

@admin_bp.route('/ban', methods=['POST'])
@jwt_required()
@admin_required
@api_error_handler
@require_fields('user_id')
def ban_user():
    data = request.get_json()
    success, response = update_user_suspension_status(user_id=int(data.get('user_id')), suspend=True)
    return response

@admin_bp.route('/unban', methods=['POST'])
@jwt_required()
@admin_required
@api_error_handler
@require_fields('user_id')
def unban_user():
    data = request.get_json()
    success, response = update_user_suspension_status(user_id=int(data.get('user_id')), suspend=False)
    return response
