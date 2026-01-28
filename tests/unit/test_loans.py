import pytest
from src.account import Account
from src.personal_account import PersonalAccount

class TestPersonalLoans:
    @pytest.fixture
    def account(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 200.0
        return account
    
    @pytest.mark.parametrize("transactions,loan_amount,expected_approved,expected_balance", [
        ([("incoming", 50.0), ("incoming", 20.0), ("incoming", 80.0)], 500, True, 850.0),
        ([("incoming", 50.0), ("incoming", 20.0)], 500, False, 270.0),
        ([("incoming", 100.0), ("incoming", 100.0), ("incoming", 100.0), ("outgoing", 50.0), ("outgoing", 40.0)], 200, True, 610.0),
        ([("incoming", 100.0), ("incoming", 100.0), ("incoming", 100.0), ("outgoing", 20.0), ("outgoing", 20.0)], 500, False, 460.0),
    ])
    def test_loan_submission(self, account, transactions, loan_amount, expected_approved, expected_balance):
        for transaction_type, amount in transactions:
            if transaction_type == "incoming":
                account.incoming_transfer(amount)
            else:
                account.outgoing_transfer(amount)
        
        result = account.submit_for_loan(loan_amount)
        assert result == expected_approved
        assert account.balance == expected_balance


