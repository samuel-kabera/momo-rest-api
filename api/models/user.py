import database
import datetime

class User:
    def __init__(self, id, name, email, password, balance, role):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.balance = balance
        self.role = role

    @staticmethod
    def get_by_email(email):
        for user_data in database.users.values():
            if user_data['email'] == email:
                return User(**user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        user_data = database.users.get(user_id)
        if user_data:
            return User(**user_data)
        return None

    @staticmethod
    def create(name, email, hashed_password, role='USER', balance=0.0):
      
        for user_data in database.users.values():
            if user_data['email'] == email:
                return None
        
        user_id = database.user_id_counter
        database.user_id_counter += 1
        
        user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': hashed_password,
            'balance': balance,
            'role': role
        }
        
        database.users[user_id] = user_data
        return user_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "balance": self.balance,
            "role": self.role
        }