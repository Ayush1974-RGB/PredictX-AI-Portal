"""
middleware/auth_middleware.py
JWT token verification decorator for protected routes.
Usage:
    from middleware.auth_middleware import token_required

    @app.route('/api/protected')
    @token_required
    def protected(current_user):
        return jsonify({'user': current_user})
"""
from functools import wraps
from flask import request, jsonify
import jwt, os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            secret  = os.getenv('SECRET_KEY', 'predictx-dev-secret-2024')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            current_user = payload['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
