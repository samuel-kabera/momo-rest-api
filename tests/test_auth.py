import pytest
from unittest.mock import MagicMock
from handlers.auth import handle_register, handle_login, handle_logout
import database
from utils import hash_password, create_jwt_token


def test_register_success(mock_handler_factory):
    body = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "USER",
        "balance": 100.0
    }
    handler = mock_handler_factory(body=body)

    handle_register(handler)

    assert handler.status_code == 201
    response = handler.get_response_body()
    assert response["email"] == "test@example.com"
    assert "id" in response


def test_register_duplicate_email(mock_handler_factory):
    # Register first user
    database.users[1] = {
        "id": 1,
        "name": "Existing User",
        "email": "test@example.com",
        "password": "hashed_password",
        "role": "USER",
        "balance": 0.0
    }

    body = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123"
    }
    handler = mock_handler_factory(body=body)

    handle_register(handler)

    assert handler.status_code == 403
    response = handler.get_response_body()
    assert response["message"] == "User already exists"


def test_login_success(mock_handler_factory, monkeypatch):
    # Create a user for login
    user = MagicMock(
        id=1,
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        role="USER",
        balance=100.0,
        to_dict=lambda: {"id": 1, "email": "test@example.com"}
    )
    database.users[1] = user

    from models.user import User
    monkeypatch.setattr(
        User, "get_by_email", lambda email: user if email == "test@example.com" else None)

    body = {
        "email": "test@example.com",
        "password": "password123"
    }
    handler = mock_handler_factory(body=body)

    handle_login(handler)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert "access_token" in response


def test_login_invalid_password(mock_handler_factory, monkeypatch):
    from models.user import User
    user = MagicMock(
        id=1,
        password=hash_password("correct_password")
    )
    monkeypatch.setattr(User, "get_by_email", lambda email: user)

    body = {
        "email": "test@example.com",
        "password": "wrong_password"
    }
    handler = mock_handler_factory(body=body)

    handle_login(handler)

    assert handler.status_code == 401
    response = handler.get_response_body()
    assert response["message"] == "Invalid email or password"


def test_logout_success(mock_handler_factory):
    token = create_jwt_token(1, "USER")
    database.users[1] = {"name": "Test User"}

    handler = mock_handler_factory(
        headers={"Authorization": f"Bearer {token}"})

    handle_logout(handler)

    assert handler.status_code == 200
    assert token in database.blocked_tokens
    response = handler.get_response_body()
    assert response["message"] == "Logged out successfully"
