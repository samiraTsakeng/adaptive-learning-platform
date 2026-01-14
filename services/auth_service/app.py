from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
from datetime import datetime, timedelta

# reuse existing registration/login logic
from backend.auth import register_user, login_user
from backend.database import get_user_info_by_username

SECRET_KEY = os.environ.get('ALP_SECRET', 'change_this_secret')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = 24

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/auth/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    requested_role = data.get('role', 'student')
    admin_token = data.get('admin_token')

    if not username or not password:
        return jsonify({'success': False, 'message': 'username and password required'}), 400

    role = 'student'
    if requested_role == 'teacher':
        if not admin_token or admin_token != os.environ.get('ADMIN_TOKEN', 'admin_secret'):
            return jsonify({'success': False, 'message': 'Admin token required for teacher registration'}), 403
        role = 'teacher'

    success, msg = register_user(username, password, role)
    if success:
        return jsonify({'success': True, 'message': msg, 'role': role}), 201
    return jsonify({'success': False, 'message': msg}), 400


@app.route('/auth/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'username and password required'}), 400
    success, result = login_user(username, password)
    if not success:
        return jsonify({'success': False, 'message': result}), 401
    user_id, role = get_user_info_by_username(username)
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return jsonify({'success': True, 'token': token, 'user_id': user_id, 'role': role})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
