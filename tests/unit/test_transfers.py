import pytest
from unittest.mock import patch, MagicMock
from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount 

class TestTransfers:
    @pytest.fixture
    def personal_account(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        return account

    @pytest.fixture
    def company_account(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        
        with patch('src.company_account.requests.get', return_value=mock_response):
            account = CompanyAccount("metalex", "1234567890")
            account.balance = 100.0
            return account

    @pytest.mark.parametrize("account_type,initial_balance,transfer_type,amount,expected_balance", [
        ("personal", 0.0, "incoming", 100.0, 100.0),
        ("personal", 100.0, "outgoing", 50.0, 50.0),
        ("personal", 100.0, "incoming", 50.0, 150.0),
        ("personal", 30.0, "outgoing", 50.0, 30.0),
        ("personal", 0.0, "incoming", -20.0, 0.0),
        ("personal", 0.0, "outgoing", -20.0, 0.0),
        ("company", 100.0, "outgoing", 50.0, 50.0),
        ("company", 100.0, "incoming", 50.0, 150.0),
        ("company", 30.0, "outgoing", 50.0, 30.0),
        ("company", 0.0, "incoming", -20.0, 0.0),
        ("company", 0.0, "outgoing", -20.0, 0.0),
    ])
    def test_transfers(self, account_type, initial_balance, transfer_type, amount, expected_balance):
        if account_type == "personal":
            account = PersonalAccount("Alice", "Johnson", "12345678901")
        else:
            account = CompanyAccount("metalex", "123456890")
        
        account.balance = initial_balance
        
        if transfer_type == "incoming":
            account.incoming_transfer(amount)
        else:
            account.outgoing_transfer(amount)
        
        assert account.balance == expected_balance