import pytest
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


@pytest.fixture
def account_with_balance(client, base_url):
    account_data = {"name": "john", "surname": "doe", "pesel": "12345678901"}
    client.post(base_url, json=account_data)
    
    transfer_data = {"amount": 1000.0, "type": "incoming"}
    client.post(f"{base_url}/12345678901/transfer", json=transfer_data)
    
    return "12345678901"


class TestTransfers:
    def test_incoming_transfer_success(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        initial_balance = account["balance"]

        transfer_data = {"amount": 500.0, "type": "incoming"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Zlecenie przyjęto do realizacji"
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == initial_balance + 500.0
    
    def test_outgoing_transfer_success(self, client, base_url, account_with_balance):
        pesel = account_with_balance
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        initial_balance = account["balance"]
        
        transfer_data = {"amount": 300.0, "type": "outgoing"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Zlecenie przyjęto do realizacji"
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == initial_balance - 300.0
    
    def test_express_transfer_success(self, client, base_url, account_with_balance):
        pesel = account_with_balance
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        initial_balance = account["balance"]
        
        transfer_data = {"amount": 200.0, "type": "express"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Zlecenie przyjęto do realizacji"
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == initial_balance - 200.0 - 1.0
    
    def test_transfer_for_nonexistent_account_returns_404(self, client, base_url):
        transfer_data = {"amount": 100.0, "type": "incoming"}
        response = client.post(f"{base_url}/99999999999/transfer", json=transfer_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_transfer_with_invalid_type_returns_400(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        transfer_data = {"amount": 100.0, "type": "invalid_type"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Invalid transfer type" in data["error"]
    
    def test_outgoing_transfer_insufficient_balance_returns_422(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        transfer_data = {"amount": 500.0, "type": "outgoing"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 422
        data = response.get_json()
        assert "error" in data
        assert "Transaction failed" in data["error"]
    
    def test_express_transfer_allows_overdraft(self, client, base_url, account_with_balance):
        pesel = account_with_balance
        
        transfer_data = {"amount": 1000.0, "type": "express"} 
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Zlecenie przyjęto do realizacji"
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == -1.0
    
    def test_outgoing_transfer_with_negative_amount_returns_422(self, client, base_url, account_with_balance):
        pesel = account_with_balance
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        initial_balance = account["balance"]
        
        transfer_data = {"amount": -100.0, "type": "outgoing"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 422
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == initial_balance
    
    def test_incoming_transfer_with_negative_amount_does_not_change_balance(self, client, base_url, sample_account_data):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        initial_balance = account["balance"]
        
        transfer_data = {"amount": -100.0, "type": "incoming"}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200
        
        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == initial_balance
    
    @pytest.mark.parametrize("transfer_type,amount", [
        ("incoming", 100.0),
        ("incoming", 500.0),
        ("incoming", 1000.0),
    ])
    def test_multiple_incoming_transfers(self, client, base_url, sample_account_data, transfer_type, amount):
        client.post(base_url, json=sample_account_data)
        pesel = sample_account_data["pesel"]
        
        transfer_data = {"amount": amount, "type": transfer_type}
        response = client.post(f"{base_url}/{pesel}/transfer", json=transfer_data)
        
        assert response.status_code == 200

        account = client.get(f"{base_url}/{pesel}").get_json()
        assert account["balance"] == amount
