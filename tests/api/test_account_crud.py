import pytest
import requests
from app.api import app, registry


@pytest.fixture(autouse=True)
def clear_registry():
    registry.accounts.clear()
    yield
    registry.accounts.clear()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def base_url():
    return "/api/accounts"


@pytest.fixture
def sample_account_data():
    return {
        "name": "james",
        "surname": "hetfield",
        "pesel": "89092909825"
    }


class TestAccountCreation:
    def test_create_account_success(self, client, base_url, sample_account_data):
        response = client.post(base_url, json=sample_account_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Account created"
    
    def test_create_multiple_accounts(self, client, base_url):
        accounts = [
            {"name": "john", "surname": "doe", "pesel": "12345678901"},
            {"name": "jane", "surname": "smith", "pesel": "98765432109"},
            {"name": "bob", "surname": "johnson", "pesel": "55555555555"}
        ]
        
        for account_data in accounts:
            response = client.post(base_url, json=account_data)
            assert response.status_code == 201


class TestPeselUniqueness:
    def test_create_account_with_duplicate_pesel_returns_409(self, client, base_url, sample_account_data):
        response1 = client.post(base_url, json=sample_account_data)
        assert response1.status_code == 201
        
        response2 = client.post(base_url, json=sample_account_data)
        assert response2.status_code == 409
        
        data = response2.get_json()
        assert "error" in data
        assert "PESEL" in data["error"]
    
    def test_create_account_with_duplicate_pesel_different_names(self, client, base_url):
        account1 = {"name": "john", "surname": "doe", "pesel": "12345678901"}
        account2 = {"name": "jane", "surname": "smith", "pesel": "12345678901"}  # Same PESEL
        
        response1 = client.post(base_url, json=account1)
        assert response1.status_code == 201
        
        response2 = client.post(base_url, json=account2)
        assert response2.status_code == 409
    
    def test_duplicate_pesel_does_not_create_account(self, client, base_url):
        account_data = {"name": "john", "surname": "doe", "pesel": "12345678901"}
        
        client.post(base_url, json=account_data)
        
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 1
        
        client.post(base_url, json=account_data)
        
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 1
    
    def test_multiple_accounts_with_unique_pesels_succeeds(self, client, base_url):
        accounts = [
            {"name": "john", "surname": "doe", "pesel": "11111111111"},
            {"name": "jane", "surname": "smith", "pesel": "22222222222"},
            {"name": "bob", "surname": "johnson", "pesel": "33333333333"}
        ]
        
        for account_data in accounts:
            response = client.post(base_url, json=account_data)
            assert response.status_code == 201
        
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 3


class TestGetAccounts:
    def test_get_all_accounts_empty(self, client, base_url):
        response = client.get(base_url)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
    
    def test_get_all_accounts_with_data(self, client, base_url, sample_account_data):
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
        response = client.get(f"{base_url}/count")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0
    
    def test_count_with_accounts(self, client, base_url):
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
        response = client.get(f"{base_url}/99999999999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


class TestUpdateAccount:
    def test_update_account_name(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        update_data = {"name": "lars"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Account updated"
        
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "lars"
        assert account["surname"] == "hetfield" 
    
    def test_update_account_surname(self, client, base_url, sample_account_data):

        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        update_data = {"surname": "ulrich"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "james"
        assert account["surname"] == "ulrich"
    
    def test_update_both_name_and_surname(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        update_data = {"name": "kirk", "surname": "hammett"}
        response = client.patch(f"{base_url}/{pesel}", json=update_data)
        
        assert response.status_code == 200
        
        get_response = client.get(f"{base_url}/{pesel}")
        account = get_response.get_json()
        assert account["name"] == "kirk"
        assert account["surname"] == "hammett"
    
    def test_update_nonexistent_account_returns_404(self, client, base_url):
        update_data = {"name": "test"}
        response = client.patch(f"{base_url}/99999999999", json=update_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data


class TestDeleteAccount:
    def test_delete_existing_account(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        get_response = client.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 200
        
        response = client.delete(f"{base_url}/{pesel}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Account deleted"
        
        get_response = client.get(f"{base_url}/{pesel}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_account_returns_404(self, client, base_url):
        response = client.delete(f"{base_url}/99999999999")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_delete_account_reduces_count(self, client, base_url):

        accounts = [
            {"name": "john", "surname": "doe", "pesel": "12345678901"},
            {"name": "jane", "surname": "smith", "pesel": "98765432109"}
        ]
        
        for account_data in accounts:
            client.post(base_url, json=account_data)
        
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 2
        
        client.delete(f"{base_url}/12345678901")
        
        count_response = client.get(f"{base_url}/count")
        assert count_response.get_json()["count"] == 1


