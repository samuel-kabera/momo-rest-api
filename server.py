from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.auth import handle_register, handle_login, handle_logout
from handlers.transactions import (
    handle_add_transaction, 
    handle_get_transactions,
    handle_get_transaction_by_id,
    handle_get_transaction_by_id_indexed,
    handle_get_my_transactions,
    handle_update_transaction,
    handle_delete_transaction
)
from parsers.xml_parser import parse_xml_file

def parse_transaction_path(path):
    """Extract route type and ID from path like /transactions/123 or /indexed_transactions/123"""
    parts = path.strip('/').split('/')
    if len(parts) == 2:
        route_type = parts[0]
        if route_type in ['transactions', 'indexed_transactions']:
            try:
                return route_type, int(parts[1])
            except ValueError:
                return route_type, None
    return None, None

class APIRRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/auth/register':
            handle_register(self)
        elif self.path == '/auth/login':
            handle_login(self)
        elif self.path == '/auth/logout':
            handle_logout(self)
        elif self.path == '/transactions/':
            handle_add_transaction(self)
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        if self.path == '/transactions/':
            handle_get_transactions(self)
        elif self.path == '/transactions/me':
            handle_get_my_transactions(self)
        else:
            route_type, txn_id = parse_transaction_path(self.path)
            if txn_id is not None:
                if route_type == 'transactions':
                    handle_get_transaction_by_id(self, txn_id)
                elif route_type == 'indexed_transactions':
                    handle_get_transaction_by_id_indexed(self, txn_id)
            else:
                self.send_error(404, "Not Found")

    def do_PUT(self):
        route_type, txn_id = parse_transaction_path(self.path)
        if txn_id is not None and route_type == 'transactions':
            handle_update_transaction(self, txn_id)
        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        route_type, txn_id = parse_transaction_path(self.path)
        if txn_id is not None and route_type == 'transactions':
            handle_delete_transaction(self, txn_id)
        else:
            self.send_error(404, "Not Found")

def run(server_class=HTTPServer, handler_class=APIRRequestHandler, port=5000):
    # Load seed data from XML
    xml_file = os.path.join(os.path.dirname(__file__), 'parsers', 'modified_sms_v2.xml')
    if os.path.exists(xml_file):
        count = parse_xml_file(xml_file)
        print(f"Loaded {count} seed transactions from xml file")
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
