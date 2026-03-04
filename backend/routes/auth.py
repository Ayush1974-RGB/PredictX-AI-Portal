"""
routes/auth.py — Authentication: Signup, Login, JWT Verify
"""
from flask import Blueprint, request, jsonify
import jwt, bcrypt, datetime, os, json

auth_bp = Blueprint('auth', __name__)

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

# ── helpers ────────────────────────────────────────────────────
def load_users():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def make_token(email):
    secret = os.getenv('SECRET_KEY', 'predictx-dev-secret-2024')
    payload = {
        'email': email,
        'exp':   datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat':   datetime.datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm='HS256')

# ── routes ─────────────────────────────────────────────────────
@auth_bp.route('/signup', methods=['POST'])
def signup():
    d        = request.get_json()
    username = d.get('username', '').strip()
    email    = d.get('email', '').strip().lower()
    password = d.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    users = load_users()
    if email in users:
        return jsonify({'error': 'Email already registered'}), 409

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[email] = {
        'username':   username,
        'email':      email,
        'password_hash': pw_hash,
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    save_users(users)

    return jsonify({
        'message': 'Account created',
        'token':   make_token(email),
        'user':    {'username': username, 'email': email}
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    d        = request.get_json()
    email    = d.get('email', '').strip().lower()
    password = d.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    users = load_users()
    user  = users.get(email)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'token':   make_token(email),
        'user':    {'username': user['username'], 'email': email}
    }), 200


@auth_bp.route('/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'No token'}), 401
    try:
        secret  = os.getenv('SECRET_KEY', 'predictx-dev-secret-2024')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        users   = load_users()
        user    = users.get(payload['email'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': {'username': user['username'], 'email': payload['email']}}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401
