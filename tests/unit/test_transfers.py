from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount 

class TestTransfers:
    def test_incoming_transfer(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.incoming_transfer(100.0)
        assert account.balance == 100.0

    def test_outgoing_transfer_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        
        account.outgoing_transfer(50.0)
        assert account.balance == 50.0

    def test_incoming_transfer_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        
        account.incoming_transfer(50.0)
        assert account.balance == 150.0

    def test_outgoing_transfer_exceeding_balance_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0
        account.outgoing_transfer(50.0)
        assert account.balance == 30.0

    def test_incoming_transfer_negative_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.incoming_transfer(-20.0)
        assert account.balance == 0.0

    def test_outgoing_transfer_negative_personal(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.outgoing_transfer(-20.0)
        assert account.balance == 0.0

    def test_outgoing_transfer_company(self):
        account = CompanyAccount("metalex", "123456890")
        account.balance = 100.0
        
        account.outgoing_transfer(50.0)
        assert account.balance == 50.0

    def test_incoming_transfer_company(self):
        account = CompanyAccount("metalex", "123456890")
        account.balance = 100.0
        
        account.incoming_transfer(50.0)
        assert account.balance == 150.0

    def test_outgoing_transfer_exceeding_balance_company(self):
        account = CompanyAccount("metalex", "123456890")
        account.balance = 30.0
        account.outgoing_transfer(50.0)
        assert account.balance == 30.0

    def test_incoming_transfer_negative_company(self):
        account = CompanyAccount("metalex", "123456890")
        account.incoming_transfer(-20.0)
        assert account.balance == 0.0

    def test_outgoing_transfer_negative_company(self):
        account = CompanyAccount("metalex", "123456890")
        account.outgoing_transfer(-20.0)
        assert account.balance == 0.0