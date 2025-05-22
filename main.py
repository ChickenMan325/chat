from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from utils.userutils import load_users, get_user
from utils.authutils import is_session_valid
from utils.responseutils import api_response
from utils.config import Config
from utils.logutils import log_error, log_info
from utils.sessionutils import get_current_user

app = Flask(__name__)
Config.init_app(app)

jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, 
                   ping_timeout=60, ping_interval=60000)

user_sessions = {}

@socketio.on('connect')
def handle_connect():
    log_info(f"Client connected with SID: {request.sid}")

@socketio.on('register_user')
def handle_register_user(data):
    username = data.get('username')
    if username:
        user_sessions[username] = request.sid
        join_room(username)
        log_info(f"User {username} registered with session {request.sid}")
        emit('registration_confirmed', {'username': username, 'status': 'registered'}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    log_info(f"Client disconnected: {request.sid}")
    for username, sid in list(user_sessions.items()):
        if sid == request.sid:
            del user_sessions[username]
            log_info(f"User {username} disconnected")
            break

@app.route('/api/test/emit', methods=['POST'])
def test_emit():
    data = request.get_json()
    username = data.get('username')
    event = data.get('event', 'test_event')
    payload = data.get('payload', {'message': 'Test message'})
    
    if not username:
        return api_response(False, 'Username required', status_code=400)
    
    if username in user_sessions:
        sid = user_sessions[username]
        log_info(f"Emitting {event} to {username} with SID {sid}")
        socketio.emit(event, payload, room=username)
        return api_response(True, f'Event {event} emitted to {username}')
    else:
        return api_response(False, f'User {username} not found in active sessions', status_code=404)

from apiendpoints.auth import auth_bp
from apiendpoints.user import user_bp
from apiendpoints.admin import admin_bp
from apiendpoints.password import password_bp

app.user_sessions = user_sessions
app.socketio = socketio

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(password_bp, url_prefix='/api/password')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    message = request.args.get('message')
    return render_template('login.html', message=message)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user and is_session_valid(current_user):
            return render_template('dashboard.html', username=current_user)
    except Exception as e:
        log_error(f"Dashboard access error: {str(e)}")
    
    return redirect(url_for('login'))

@app.route('/profile_settings')
def profile_settings():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if current_user and is_session_valid(current_user):
            return render_template('profile_settings.html', current_user={'username': current_user})
    except Exception as e:
        log_error(f"Profile settings access error: {str(e)}")
    
    return redirect(url_for('login'))

# Removed conflicting get_current_user API endpoint. 
# The endpoint /api/user/me is handled by user_bp in apiendpoints/user.py
# The utility function get_current_user is imported from utils.sessionutils

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    from utils.auth_manager import logout_user
    resp = api_response(True, 'Logout successful')
    return logout_user(resp), 200

@app.errorhandler(Exception)
def handle_exception(e):
    log_error(f"Unhandled exception: {str(e)}")
    return api_response(False, 'An unexpected error occurred', status_code=500)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
