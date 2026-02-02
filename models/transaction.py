import database
import datetime

TRANSACTION_TYPES = ['transfer', 'payment', 'withdrawal', 'deposit']

class Transaction:
    @staticmethod
    def create(sender_id, receiver_id, amount, transaction_type='transfer'):
        sender = database.users.get(sender_id)
        receiver = database.users.get(receiver_id)
        
        if not sender or not receiver:
            return None, "Invalid sender or receiver"
        
        if sender['balance'] < amount:
            return None, "Insufficient balance"
        
      
        sender['balance'] -= amount
        receiver['balance'] += amount
        
       
        transaction_id = database.transaction_id_counter
        database.transaction_id_counter += 1
        
        transaction = {
            'id': transaction_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'type': transaction_type,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        database.transactions.append(transaction)
        database.transactions_dictionary[transaction_id] = transaction
        
        return transaction_id, None

    @staticmethod
    def get_all():
        return database.transactions.copy()

    @staticmethod
    def get_by_id(transaction_id):
        for transaction in database.transactions:
            if transaction['id'] == transaction_id:
                return transaction
        return None

    @staticmethod
    def get_by_id_indexed(transaction_id):
        """Get transaction by ID using the dictionary index"""
        return database.transactions_dictionary.get(transaction_id)

    @staticmethod
    def get_by_user():
        """Get all transactions where user is sender or receiver"""
        my_transactions = []
        for transaction in database.transactions:
            if transaction['sender'] == "Me" or transaction['receiver'] == "Me":
                my_transactions.append(transaction)
        return my_transactions

    @staticmethod
    def update(transaction_id, user_id, role, **kwargs):
        """Update a transaction. Only Admins can update a transaction."""
        if role != 'ADMIN':
            return None, "Only Admins can update transactions"

        for i, transaction in enumerate(database.transactions):
            if transaction['id'] == transaction_id:
                
                allowed_fields = ['type']
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        if key == 'type' and value not in TRANSACTION_TYPES:
                            return None, f"Invalid transaction type. Must be one of: {', '.join(TRANSACTION_TYPES)}"
                        database.transactions[i][key] = value
              
                database.transactions_dictionary[transaction_id] = database.transactions[i]
                
                return database.transactions[i], None
        return None, "Transaction not found"

    @staticmethod
    def delete(transaction_id, user_id, role):
        """Delete a transaction. Only Admins can delete a transaction."""
        if role != "ADMIN":
            return False, "Only Admins can delete transactions"

        for i, transaction in enumerate(database.transactions):
            if transaction['id'] == transaction_id:
                deleted_transaction = database.transactions.pop(i)
              
                if transaction_id in database.transactions_dictionary:
                    del database.transactions_dictionary[transaction_id]
                return True, deleted_transaction
        return False, "Transaction not found"