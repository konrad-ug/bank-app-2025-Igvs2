import pytest
from unittest.mock import patch, MagicMock
from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount 

class TestTransfers:
    @pytest.fixture
    def personal_account(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        return account

    @pytest.fixture
    def company_account(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        
        with patch('src.company_account.requests.get', return_value=mock_response):
            account = CompanyAccount("firmex", "1234567890")
            account.balance = 150.0
            return account

    def test_outgoing_personal_express(self, personal_account):
        personal_account.express_outgoing(50.0)
        assert personal_account.balance == 99.0
        assert personal_account.history == ["-50.0", "-1"]

    def test_outgoing_company_express(self, company_account):
        company_account.express_outgoing(50.0)
        assert company_account.balance == 95.0
        assert company_account.history == ["-50.0", "-5"]

    @pytest.mark.parametrize("transfer_type,amount,expected_balance,expected_history", [
        ("outgoing", 50.0, 100.0, ["-50.0"]),
        ("incoming", 50.0, 200.0, ["50.0"]),
    ])
    def test_transfers_with_history(self, company_account, transfer_type, amount, expected_balance, expected_history):
        if transfer_type == "outgoing":
            company_account.outgoing_transfer(amount)
        else:
            company_account.incoming_transfer(amount)
        assert company_account.balance == expected_balance
        assert company_account.history == expected_history