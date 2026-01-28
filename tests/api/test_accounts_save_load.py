import pytest
from app.api import app, registry, mongo_repo
from src.personal_account import PersonalAccount


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_registry():
    registry.accounts.clear()
    yield
    registry.accounts.clear()


@pytest.fixture(autouse=True)
def clear_mongo():
    """Clear MongoDB collection before and after tests"""
    try:
        mongo_repo._collection.delete_many({})
    except:
        pass
    yield
    try:
        mongo_repo._collection.delete_many({})
    except:
        pass


class TestAccountsSaveLoad:
    def test_save_accounts_to_database(self, client):
        # Create accounts
        response1 = client.post('/api/accounts', json={
            "name": "Alice",
            "surname": "Wonder",
            "pesel": "92031512345"
        })
        assert response1.status_code == 201
        
        response2 = client.post('/api/accounts', json={
            "name": "Bob",
            "surname": "Builder",
            "pesel": "88102298765"
        })
        assert response2.status_code == 201
        
        # Save to database
        response = client.post('/api/accounts/save')
        assert response.status_code == 200
        data = response.get_json()
        assert "Saved 2 accounts" in data["message"]
    
    def test_load_accounts_from_database(self, client):
        # Create and save accounts
        client.post('/api/accounts', json={
            "name": "Charlie",
            "surname": "Chaplin",
            "pesel": "89040512876"
        })
        client.post('/api/accounts', json={
            "name": "Diana",
            "surname": "Prince",
            "pesel": "90050698543"
        })
        
        # Make transfers to add history
        client.post('/api/transfer', json={
            "from_account": "external",
            "to_account": "89040512876",
            "amount": 500.0
        })
        
        client.post('/api/accounts/save')
        
        # Clear registry
        registry.accounts.clear()
        response = client.get('/api/accounts')
        assert len(response.get_json()) == 0
        
        # Load from database
        response = client.post('/api/accounts/load')
        assert response.status_code == 200
        data = response.get_json()
        assert "Loaded 2 accounts" in data["message"]
        
        # Verify accounts are loaded
        response = client.get('/api/accounts')
        accounts = response.get_json()
        assert len(accounts) == 2
        
        # Find Charlie's account and verify balance
        charlie = next(acc for acc in accounts if acc["pesel"] == "89040512876")
        assert charlie["balance"] == 500.0
    
    def test_save_preserves_account_history(self, client):
        # Create account and make transfers
        client.post('/api/accounts', json={
            "name": "Eve",
            "surname": "Adams",
            "pesel": "91061212345"
        })
        
        client.post('/api/transfer', json={
            "from_account": "external",
            "to_account": "91061212345",
            "amount": 1000.0
        })
        
        client.post('/api/transfer', json={
            "from_account": "external",
            "to_account": "91061212345",
            "amount": 500.0
        })
        
        # Save, clear, and load
        client.post('/api/accounts/save')
        registry.accounts.clear()
        client.post('/api/accounts/load')
        
        # Verify history is preserved
        response = client.get('/api/accounts/91061212345')
        account = response.get_json()
        assert account["balance"] == 1500.0
    
    def test_load_clears_existing_accounts(self, client):
        # Create accounts in registry
        client.post('/api/accounts', json={
            "name": "Frank",
            "surname": "Sinatra",
            "pesel": "93071512987"
        })
        
        # Save different account to database manually
        account = PersonalAccount("George", "Clooney", "94081298765")
        mongo_repo.save_all([account])
        
        # Load from database
        response = client.post('/api/accounts/load')
        assert response.status_code == 200
        
        # Verify only database account exists
        response = client.get('/api/accounts')
        accounts = response.get_json()
        assert len(accounts) == 1
        assert accounts[0]["name"] == "George"
        assert accounts[0]["surname"] == "Clooney"
    
    def test_save_empty_registry(self, client):
        # Save empty registry
        response = client.post('/api/accounts/save')
        assert response.status_code == 200
        assert "Saved 0 accounts" in response.get_json()["message"]
    
    def test_load_from_empty_database(self, client):
        # Ensure database is empty
        mongo_repo._collection.delete_many({})
        
        # Load from empty database
        response = client.post('/api/accounts/load')
        assert response.status_code == 200
        assert "Loaded 0 accounts" in response.get_json()["message"]
        
        # Verify registry is empty
        response = client.get('/api/accounts')
        assert len(response.get_json()) == 0
    
    def test_save_overwrites_previous_data(self, client):
        # Create first account and save
        client.post('/api/accounts', json={
            "name": "Henry",
            "surname": "Ford",
            "pesel": "95091512876"
        })
        client.post('/api/accounts/save')
        
        # Clear and create different account
        registry.accounts.clear()
        client.post('/api/accounts', json={
            "name": "Isaac",
            "surname": "Newton",
            "pesel": "96101298543"
        })
        client.post('/api/accounts/save')
        
        # Load and verify only second account exists
        registry.accounts.clear()
        client.post('/api/accounts/load')
        
        response = client.get('/api/accounts')
        accounts = response.get_json()
        assert len(accounts) == 1
        assert accounts[0]["name"] == "Isaac"
