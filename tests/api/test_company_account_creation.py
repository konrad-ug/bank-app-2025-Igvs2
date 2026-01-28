import pytest
from unittest.mock import patch, MagicMock, MagicMock
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
def mock_mf_active_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'result': {
            'subject': {
                'statusVat': 'Czynny'
            }
        }
    }
    return mock_response


@pytest.fixture
def mock_mf_inactive_response():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'result': {
            'subject': {
                'statusVat': 'Zwolniony'
            }
        }
    }
    return mock_response


class TestCompanyAccountCreationAPI:
    
    def test_create_company_account_with_valid_nip(self, client, base_url, mock_mf_active_response):
        company_data = {
            "name": "TechCorp",
            "nip": "1234567890"
        }
        
        with patch('src.company_account.requests.get', return_value=mock_mf_active_response):
            response = client.post(base_url, json=company_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Account created"
    
    def test_create_company_account_with_unregistered_nip_returns_400(self, client, base_url, mock_mf_inactive_response):
        """Test that creating company account with unregistered NIP returns 400."""
        company_data = {
            "name": "FakeCorp",
            "nip": "9999999999"
        }
        
        with patch('src.company_account.requests.get', return_value=mock_mf_inactive_response):
            response = client.post(base_url, json=company_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_create_company_account_with_invalid_nip_length_returns_400(self, client, base_url):
        """Test that creating company account with invalid NIP length returns 400."""
        company_data = {
            "name": "TechCorp",
            "nip": "123" 
        }
        
        response = client.post(base_url, json=company_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_create_company_account_api_error_returns_400(self, client, base_url):
        company_data = {
            "name": "TechCorp",
            "nip": "1234567890"
        }
        
        with patch('src.company_account.requests.get', side_effect=ConnectionError("Network error")):
            response = client.post(base_url, json=company_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_create_multiple_company_accounts_with_valid_nips(self, client, base_url, mock_mf_active_response):
        companies = [
            {"name": "TechCorp", "nip": "1111111111"},
            {"name": "BuildCorp", "nip": "2222222222"},
            {"name": "TradeInc", "nip": "3333333333"}
        ]
        
        with patch('src.company_account.requests.get', return_value=mock_mf_active_response):
            for company in companies:
                response = client.post(base_url, json=company)
                assert response.status_code == 201
