from pymongo import MongoClient
from src.accounts_repository import AccountsRepository
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class MongoAccountsRepository(AccountsRepository):
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="bank_app"):
        self._client = MongoClient(connection_string)
        self._db = self._client[db_name]
        self._collection = self._db["accounts"]
    
    def save_all(self, accounts):
        """
        Save all accounts to MongoDB.
        Clears the collection before saving.
        
        Args:
            accounts: List of Account objects to save
        """
        self._collection.delete_many({})
        for account in accounts:
            self._collection.update_one(
                {"pesel": account.pesel if hasattr(account, 'pesel') else account.nip},
                {"$set": account.to_dict()},
                upsert=True,
            )
    
    def load_all(self):
        """
        Load all accounts from MongoDB.
        
        Returns:
            List of Account objects (PersonalAccount or CompanyAccount)
        """
        accounts = []
        for doc in self._collection.find():
            if doc.get("type") == "personal":
                accounts.append(PersonalAccount.from_dict(doc))
            elif doc.get("type") == "company":
                accounts.append(CompanyAccount.from_dict(doc))
        return accounts
    
    def close(self):
        """Close MongoDB connection"""
        self._client.close()
