import pytest
from unittest.mock import MagicMock
from handlers.transactions import (
    handle_add_transaction,
    handle_get_transactions,
    handle_get_transaction_by_id,
    handle_get_my_transactions,
    handle_update_transaction,
    handle_delete_transaction
)
import database
from utils import create_jwt_token
from models.transaction import Transaction


@pytest.fixture
def auth_setup():
    """Setup a user and return jwt token."""
    database.users[1] = {"id": 1, "name": "Sender",
                         "role": "USER", "balance": 1000.0}
    database.users[2] = {"id": 2, "name": "Receiver",
                         "role": "USER", "balance": 0.0}
    token = create_jwt_token(1, "USER")
    return token


def test_add_transaction_success(mock_handler_factory, auth_setup, monkeypatch):
    body = {
        "receiverId": 2,
        "amount": 100.0,
        "type": "transfer"
    }
    handler = mock_handler_factory(
        body=body,
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    monkeypatch.setattr(Transaction, "create",
                        MagicMock(return_value=(1, None)))

    handle_add_transaction(handler)

    assert handler.status_code == 201
    response = handler.get_response_body()
    assert response["message"] == "Transaction successful"
    assert response["id"] == 1


def test_get_transactions_success(mock_handler_factory, auth_setup, monkeypatch):
    database.transactions = [{"id": 1, "sender_id": 1, "amount": 100.0}]
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    monkeypatch.setattr(Transaction, "get_all", MagicMock(
        return_value=database.transactions))

    handle_get_transactions(handler)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert len(response) == 1
    assert response[0]["id"] == 1


def test_get_my_transactions_success(mock_handler_factory, auth_setup, monkeypatch):
    database.transactions = [{"id": 1, "sender_id": 1, "amount": 100.0}]
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    monkeypatch.setattr(Transaction, "get_by_user", MagicMock(
        return_value=database.transactions))

    handle_get_my_transactions(handler)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert len(response) == 1


def test_get_transaction_by_id_success(mock_handler_factory, auth_setup, monkeypatch):
    transaction = {"id": 1, "sender_id": 1, "amount": 100.0}
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    monkeypatch.setattr(Transaction, "get_by_id",
                        MagicMock(return_value=transaction))

    handle_get_transaction_by_id(handler, 1)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert response["id"] == 1


def test_get_transaction_by_id_not_found(mock_handler_factory, auth_setup, monkeypatch):
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    monkeypatch.setattr(Transaction, "get_by_id", MagicMock(return_value=None))

    handle_get_transaction_by_id(handler, 999)

    assert handler.status_code == 404
    response = handler.get_response_body()
    assert response["message"] == "Transaction not found"


def test_get_transaction_by_id_indexed_success(mock_handler_factory, auth_setup, monkeypatch):
    transaction = {"id": 1, "sender_id": 1, "amount": 100.0}
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    from handlers.transactions import handle_get_transaction_by_id_indexed
    monkeypatch.setattr(Transaction, "get_by_id_indexed",
                        MagicMock(return_value=transaction))

    handle_get_transaction_by_id_indexed(handler, 1)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert response["id"] == 1


def test_update_transaction_success(mock_handler_factory, auth_setup, monkeypatch):
    body = {"type": "payment"}
    handler = mock_handler_factory(
        body=body,
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    updated_transaction = {"id": 1, "type": "payment"}
    monkeypatch.setattr(Transaction, "update", MagicMock(
        return_value=(updated_transaction, None)))

    handle_update_transaction(handler, 1)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert response["transaction"]["type"] == "payment"


def test_delete_transaction_success(mock_handler_factory, auth_setup, monkeypatch):
    handler = mock_handler_factory(
        user_id=1,
        user_role="USER",
        user_name="Sender",
        token=auth_setup
    )

    deleted_transaction = {"id": 1}
    monkeypatch.setattr(Transaction, "delete", MagicMock(
        return_value=(True, deleted_transaction)))

    handle_delete_transaction(handler, 1)

    assert handler.status_code == 200
    response = handler.get_response_body()
    assert response["message"] == "Transaction deleted"
