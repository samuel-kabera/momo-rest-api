from models.user import User
from utils import json_response, read_json_body, hash_password, check_password, create_jwt_token, jwt_required


def handle_register(handler):
    data = read_json_body(handler)
    if User.get_by_email(data.get('email')):
        return json_response(handler, 403, {"message": "User already exists"})

    user_id = User.create(
        name=data.get('name'),
        email=data.get('email'),
        hashed_password=hash_password(data.get('password')),
        role=data.get('role', 'USER'),
        balance=data.get('balance', 0.0)
    )

    if user_id:
        user = User.get_by_id(user_id)
        return json_response(handler, 201, user.to_dict())
    return json_response(handler, 500, {"message": "Error creating user"})


def handle_login(handler):
    data = read_json_body(handler)
    user = User.get_by_email(data.get('email'))

    if user and check_password(data.get('password'), user.password):
        token = create_jwt_token(user.id, user.role)
        return json_response(handler, 200, {"access_token": token})

    return json_response(handler, 401, {"message": "Invalid email or password"})


@jwt_required
def handle_logout(handler):
    from database import blocked_tokens
    token = handler.headers.get('Authorization', '').replace('Bearer ', '')
    if token:
        blocked_tokens.add(token)
    return json_response(handler, 200, {"message": "Logged out successfully"})
