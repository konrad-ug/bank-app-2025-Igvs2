import pytest
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
        account = CompanyAccount("firmex", "1234567899")
        account.balance = 150.0
        return account

    @pytest.mark.parametrize("account_type,initial_balance,amount,expected_balance", [
        ("personal", 150.0, 50.0, 99.0),
        ("company", 150.0, 50.0, 95.0),
        ("personal", 50.0, 50.0, -1.0),
        ("company", 50.0, 50.0, -5.0),
    ])
    def test_express_outgoing(self, account_type, initial_balance, amount, expected_balance):
        if account_type == "personal":
            account = PersonalAccount("Alice", "Johnson", "12345678901")
        else:
            account = CompanyAccount("firmex", "1234567899")
        
        account.balance = initial_balance
        account.express_outgoing(amount)
        assert account.balance == expected_balance

    @pytest.mark.parametrize("account_type", ["personal", "company"])
    def test_express_incoming(self, account_type):
        if account_type == "personal":
            account = PersonalAccount("Alice", "Johnson", "12345678901")
        else:
            account = CompanyAccount("firmex", "1234567899")
        
        account.balance = 100.0
        account.express_incoming(50.0)
        assert account.balance == 150.0


