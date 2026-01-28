import pytest
import requests
from app.api import app, registry


@pytest.fixture
def client():
    """Fixture that provides Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Cleanup after each test
    registry.accounts.clear()


@pytest.fixture
def base_url():
    """Base URL for API endpoints."""
    return "/api/accounts"


@pytest.fixture
def sample_account_data():
    """Sample account data for testing."""
    return {
        "name": "james",
        "surname": "hetfield",
        "pesel": "89092909825"
    }


class TestAccountCreation:
    def test_create_account_success(self, client, base_url, sample_account_data):
        """Test creating a new account via POST."""
        response = client.post(base_url, json=sample_account_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Account created"
    
    def test_create_multiple_accounts(self, client, base_url):
        """Test creating multiple accounts."""
        accounts = [
            {"name": "john", "surname": "doe", "pesel": "12345678901"},
            {"name": "jane", "surname": "smith", "pesel": "98765432109"},
            {"name": "bob", "surname": "johnson", "pesel": "55555555555"}
        ]
        
        for account_data in accounts:
            response = client.post(base_url, json=account_data)
            assert response.status_code == 201


class TestGetAccounts:
    def test_get_all_accounts_empty(self, client, base_url):
        """Test getting all accounts when registry is empty."""
        response = client.get(base_url)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
    
    def test_get_all_accounts_with_data(self, client, base_url, sample_account_data):
        """Test getting all accounts after creating some."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        
        response = client.get(base_url)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "james"
        assert data[0]["surname"] == "hetfield"
        assert data[0]["pesel"] == "89092909825"
        assert "balance" in data[0]


class TestAccountCount:
    def test_count_empty_registry(self, client, base_url):
        """Test getting count when registry is empty."""
        response = client.get(f"{base_url}/count")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0
    
    def test_count_with_accounts(self, client, base_url):
        """Test getting count after adding accounts."""
        accounts = [
            {"name": "john", "surname": "doe", "pesel": "12345678901"},
            {"name": "jane", "surname": "smith", "pesel": "98765432109"}
        ]
        
        for account_data in accounts:
            client.post(base_url, json=account_data)
        
        response = client.get(f"{base_url}/count")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 2


class TestGetAccountByPesel:
    def test_get_existing_account(self, client, base_url, sample_account_data):
        """Test getting an account by PESEL when it exists."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        
        pesel = sample_account_data["pesel"]
        response = client.get(f"{base_url}/{pesel}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "james"
        assert data["surname"] == "hetfield"
        assert data["pesel"] == "89092909825"
        assert data["balance"] == 0.0
    
    def test_get_nonexistent_account_returns_404(self, client, base_url):
        """Test getting account that doesn't exist returns 404."""
        response = client.get(f"{base_url}/99999999999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


class TestUpdateAccount:
    def test_update_account_name(self, client, base_url, sample_account_data):
        """Test updating only account name."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        # Update name only
        update_data = {"name": "lars"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Account updated"
        
        # Verify the update
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "lars"
        assert account["surname"] == "hetfield"  # Should remain unchanged
    
    def test_update_account_surname(self, client, base_url, sample_account_data):
        """Test updating only account surname."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        # Update surname only
        update_data = {"surname": "ulrich"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        
        # Verify the update
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "james"  # Should remain unchanged
        assert account["surname"] == "ulrich"
    
    def test_update_both_name_and_surname(self, client, base_url, sample_account_data):
        """Test updating both name and surname."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        # Update both fields
        update_data = {"name": "kirk", "surname": "hammett"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        
        # Verify the update
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "kirk"
        assert account["surname"] == "hammett"
    
    def test_update_nonexistent_account_returns_404(self, client, base_url):
        """Test updating account that doesn't exist returns 404."""
        update_data = {"name": "test"}
        response = client.patch(f"{base_url}/99999999999", json=update_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


class TestDeleteAccount:
    def test_delete_existing_account(self, client, base_url, sample_account_data):
        """Test deleting an existing account."""
        # Create account first
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        # Verify account exists
        get_response = client.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 200
        
        # Delete account
        response = client.delete(f"{base_url}/{pesel}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Account deleted"
        
        # Verify account no longer exists
        get_response = client.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_account_returns_404(self, client, base_url):
        """Test deleting account that doesn't exist returns 404."""
        response = client.delete(f"{base_url}/99999999999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_delete_account_reduces_count(self, client, base_url):
        """Test that deleting account reduces the count."""
        # Create two accounts
        accounts = [
            {"name": "john", "surname": "doe", "pesel": "12345678901"},
            {"name": "jane", "surname": "smith", "pesel": "98765432109"}
        ]
        
        for account_data in accounts:
            client.post(base_url, json=account_data)
        
        # Verify count is 2
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 2
        
        # Delete one account
        client.delete(f"{base_url}/12345678901")
        
        # Verify count is now 1
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 1
