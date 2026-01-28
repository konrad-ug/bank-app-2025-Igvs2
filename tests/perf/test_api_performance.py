"""Performance tests for API endpoints."""
import pytest
import time
from app.api import app, registry


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before each test."""
    registry.accounts.clear()


class TestAPIPerformance:
    """Performance tests for API endpoints."""
    
    def test_create_and_delete_account_100_times(self, client):
        """Test creating and deleting account 100 times. Each request should take < 0.5s."""
        timeout = 0.5
        iterations = 100
        
        for i in range(iterations):
            pesel = f"{i:011d}"
            
            account_data = {
                "name": "TestUser",
                "surname": "Performance",
                "pesel": pesel
            }
            
            start_time = time.time()
            response = client.post('/api/accounts', json=account_data)
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 201, f"Create failed on iteration {i}"
            assert elapsed_time < timeout, f"Create took {elapsed_time:.3f}s (> {timeout}s) on iteration {i}"
            

            start_time = time.time()
            response = client.delete(f'/api/accounts/{pesel}')
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200, f"Delete failed on iteration {i}"
            assert elapsed_time < timeout, f"Delete took {elapsed_time:.3f}s (> {timeout}s) on iteration {i}"
    
    def test_create_account_and_100_incoming_transfers(self, client):
        """Test creating account and processing 100 incoming transfers. Each request should take < 0.5s."""
        timeout = 0.5
        transfers_count = 100
        transfer_amount = 100.0
        pesel = "12345678901"
        
        account_data = {
            "name": "TestUser",
            "surname": "Transfers",
            "pesel": pesel
        }
        
        start_time = time.time()
        response = client.post('/api/accounts', json=account_data)
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 201, "Account creation failed"
        assert elapsed_time < timeout, f"Account creation took {elapsed_time:.3f}s (> {timeout}s)"
        
        for i in range(transfers_count):
            transfer_data = {
                "type": "incoming",
                "amount": transfer_amount
            }
            
            start_time = time.time()
            response = client.post(f'/api/accounts/{pesel}/transfer', json=transfer_data)
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200, f"Transfer {i} failed with status {response.status_code}"
            assert elapsed_time < timeout, f"Transfer {i} took {elapsed_time:.3f}s (> {timeout}s)"
        
        # Verify final balance
        response = client.get(f'/api/accounts/{pesel}')
        assert response.status_code == 200, "Failed to get account"
        
        account = response.get_json()
        expected_balance = transfers_count * transfer_amount
        actual_balance = account.get('balance', 0)
        
        assert actual_balance == expected_balance, \
            f"Expected balance {expected_balance}, but got {actual_balance}"
