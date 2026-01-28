import pytest
from src.mongo_accounts_repository import MongoAccountsRepository
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestMongoAccountsRepository:
    def setup_method(self):
        self.account1 = PersonalAccount("John", "Doe", "90010112345")
        self.account1.balance = 1000.0
        self.account1.history = ["100", "-50"]
        
        self.account2 = PersonalAccount("Jane", "Smith", "85020298765")
        self.account2.balance = 2000.0
        self.account2.history = ["200", "300"]
    
    def test_save_all_clears_collection_and_saves_accounts(self, mocker):
        # Arrange
        mock_collection = mocker.Mock()
        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        
        accounts = [self.account1, self.account2]
        
        # Act
        repo.save_all(accounts)
        
        # Assert
        mock_collection.delete_many.assert_called_once_with({})
        assert mock_collection.update_one.call_count == 2
        
        # Verify first account was saved
        first_call = mock_collection.update_one.call_args_list[0]
        assert first_call[0][0] == {"pesel": "90010112345"}
        assert first_call[0][1]["$set"]["first_name"] == "John"
        assert first_call[0][1]["$set"]["balance"] == 1000.0
        assert first_call[1]["upsert"] is True
    
    def test_load_all_returns_accounts_from_database(self, mocker):
        # Arrange
        mock_collection = mocker.Mock()
        mock_collection.find.return_value = [
            self.account1.to_dict(),
            self.account2.to_dict()
        ]
        
        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        
        # Act
        accounts = repo.load_all()
        
        # Assert
        assert len(accounts) == 2
        assert accounts[0].first_name == "John"
        assert accounts[0].pesel == "90010112345"
        assert accounts[0].balance == 1000.0
        assert accounts[0].history == ["100", "-50"]
        
        assert accounts[1].first_name == "Jane"
        assert accounts[1].pesel == "85020298765"
        assert accounts[1].balance == 2000.0
    
    def test_save_and_load_company_account(self, mocker):
        # Arrange
        mock_collection = mocker.Mock()
        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        
        # Create company account without NIP validation
        company = object.__new__(CompanyAccount)
        CompanyAccount.__bases__[0].__init__(company)
        company.company_name = "Test Corp"
        company.nip = "1234567890"
        company.balance = 5000.0
        company.history = ["1000", "-500"]
        
        # Mock find to return company account
        mock_collection.find.return_value = [company.to_dict()]
        
        # Act - Save
        repo.save_all([company])
        
        # Assert - Save
        mock_collection.delete_many.assert_called_once()
        assert mock_collection.update_one.call_count == 1
        
        # Act - Load
        loaded_accounts = repo.load_all()
        
        # Assert - Load
        assert len(loaded_accounts) == 1
        assert loaded_accounts[0].company_name == "Test Corp"
        assert loaded_accounts[0].nip == "1234567890"
        assert loaded_accounts[0].balance == 5000.0
        assert loaded_accounts[0].history == ["1000", "-500"]
    
    def test_load_all_with_empty_database(self, mocker):
        # Arrange
        mock_collection = mocker.Mock()
        mock_collection.find.return_value = []
        
        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        
        # Act
        accounts = repo.load_all()
        
        # Assert
        assert len(accounts) == 0
        mock_collection.find.assert_called_once()
    
    def test_save_all_with_empty_list(self, mocker):
        # Arrange
        mock_collection = mocker.Mock()
        repo = MongoAccountsRepository()
        repo._collection = mock_collection
        
        # Act
        repo.save_all([])
        
        # Assert
        mock_collection.delete_many.assert_called_once_with({})
        assert mock_collection.update_one.call_count == 0
    def test_save_all_with_personal_account(self):
        # Test saving a PersonalAccount to ensure 'pesel' branch is covered
        personal_account = PersonalAccount("12345678901", "Jan", "Kowalski")
        repo = MongoAccountsRepository()
        repo.save_all([personal_account])
        loaded = repo.load_all()
        assert len(loaded) == 1
        assert loaded[0].pesel == "12345678901"
        repo.close()

    def test_save_all_with_company_account(self):
        #Test saving a CompanyAccount to ensure 'nip' branch is covered
        company_account = CompanyAccount("1234567890", "Company Ltd")
        repo = MongoAccountsRepository()
        repo.save_all([company_account])
        loaded = repo.load_all()
        assert len(loaded) == 1
        assert loaded[0].nip == "1234567890"
        repo.close()