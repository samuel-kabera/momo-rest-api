import database
import pytest
import json
import io
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockHandler:
    def __init__(self, body=None, headers=None, user_id=None, user_role=None, user_name=None):
        self.rfile = io.BytesIO(json.dumps(body).encode(
            'utf-8')) if body else io.BytesIO(b"")
        self.headers = headers or {}
        self.wfile = io.BytesIO()
        self.status_code = None
        self.response_headers = {}
        self.user_id = user_id
        self.user_role = user_role
        self.user_name = user_name

    def send_response(self, code):
        self.status_code = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def get_response_body(self):
        return json.loads(self.wfile.getvalue().decode('utf-8'))


@pytest.fixture(autouse=True)
def db_cleanup():
    database.users = {}
    database.transactions = []
    database.user_id_counter = 1
    database.transaction_id_counter = 1
    database.blocked_tokens = set()
    yield


@pytest.fixture
def mock_handler_factory():
    def _create_handler(body=None, headers=None, user_id=None, user_role=None, user_name=None, token=None):
        headers = headers or {}
        if body and "Content-Length" not in headers:
            headers["Content-Length"] = str(len(json.dumps(body)))

        if token and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {token}"

        return MockHandler(body, headers, user_id, user_role, user_name)
    return _create_handler
