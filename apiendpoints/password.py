from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from utils.userutils import load_users, save_users
from utils.authutils import auth_middleware
from utils.responseutils import api_response
from utils.logutils import log_error, log_info
import time
from apiendpoints.auth import validate_password

password_bp = Blueprint('password', __name__)

@password_bp.route('/change', methods=['POST'])
@jwt_required()
def change_password():
    try:
        user, error_response = auth_middleware()
        if error_response:
            return error_response
        
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return api_response(False, 'Current password and new password required', status_code=400)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Use centralized password validation
        valid, error = validate_password(new_password)
        if not valid:
            return api_response(False, error, status_code=400)

        if not check_password_hash(user['password'], current_password):
            return api_response(False, 'Current password is incorrect', status_code=401)

        users = load_users()
        current_username = user['username']
        
        for i, u in enumerate(users):
            if u['username'] == current_username:
                users[i]['password'] = generate_password_hash(new_password)
                users[i]['password_changed_at'] = int(time.time())
                save_users(users)
                break

        from utils.sessionutils import invalidate_session
        invalidate_session(user['id'])

        # Notify user via Socket.IO if connected
        if hasattr(current_app, 'user_sessions'):
            if current_username in current_app.user_sessions:
                try:
                    current_app.socketio.emit('force_logout', {
                        'reason': 'password_changed',
                        'message': 'Your password has been changed. Please log in again with your new password.',
                        'timestamp': int(time.time()),
                        'user_id': user['id']
                    }, room=current_username)
                except Exception as e:
                    log_error(f"Error sending force logout after password change: {str(e)}")
        
        log_info(f"Password changed successfully for user {current_username}")
        return api_response(True, 'Password changed successfully. All sessions have been invalidated for security.')
    except Exception as e:
        log_error(f"Password change error: {str(e)}")
        return api_response(False, 'An error occurred while changing password', status_code=500)
