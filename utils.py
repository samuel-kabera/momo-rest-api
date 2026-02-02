import json
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_jwt_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def jwt_required(handler_func):
    def wrapper(handler, *args, **kwargs):
        from database import users, blocked_tokens

        token = handler.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return json_response(handler, 401, {"message": "Authentication token is missing"})

        if token in blocked_tokens:
            return json_response(handler, 401, {"message": "Token has been blacklisted"})

        payload = decode_jwt_token(token)
        if not payload:
            return json_response(handler, 401, {"message": "Invalid or expired token"})

        handler.user_id = payload['user_id']
        handler.user_role = payload['role']

        # Get user's name for transaction display
        user_data = users.get(payload['user_id'])
        handler.user_name = user_data['name'] if user_data else 'Me'

        return handler_func(handler, *args, **kwargs)
    return wrapper


def json_response(handler, status_code, data):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))


def read_json_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    body = handler.rfile.read(content_length)
    return json.loads(body)
