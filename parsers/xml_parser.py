import xml.etree.ElementTree as ET
import sys
import os

# Add parent directory to path so we can import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

from parsers.helper import parse_sms_body


def parse_xml_file(file_path):
    """
    Parse the SMS backup XML file and add transactions to the database.
    Transactions with IDs in XML keep those IDs.
    Transactions without IDs get auto-incremented IDs starting from 1.
    Updates transaction_id_counter for future transactions.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    auto_id = 1  # Counter for transactions without IDs
    count = 0

    for sms in root.findall('sms'):
        body = sms.get('body', '')

        parsed = parse_sms_body(body)

        if parsed and parsed['amount'] > 0:
            transaction_id = parsed['id']

            # If no ID from XML, assign auto-incremented ID
            if transaction_id is None:
                transaction_id = auto_id
                auto_id += 1

            transaction = {
                'id': transaction_id,
                'sender': parsed['sender'],
                'receiver': parsed['receiver'],
                'amount': parsed['amount'],
                'type': parsed['type'],
                'created_at': parsed['created_at'] or ''
            }

            database.transactions.append(transaction)
            database.transactions_dictionary[transaction_id] = transaction
            count += 1

    database.transaction_id_counter = auto_id

    return count


def print_transactions():
    """Print all transactions in a readable format."""
    print(f"\n{'='*80}")
    print(f"Total Transactions: {len(database.transactions)}")
    print(f"Transaction ID Counter: {database.transaction_id_counter}")
    print(f"{'='*80}\n")

    for transaction in database.transactions[:15]:
        print(transaction)
        print()


if __name__ == '__main__':
    xml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modified_sms_v2.xml')

    print(f"Parsing {xml_file}...")
    count = parse_xml_file(xml_file)
    print(f"Successfully parsed {count} transactions!")

    print_transactions()
