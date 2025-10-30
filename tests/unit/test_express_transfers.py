from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount 

class TestTransfers:
    def test_outgoing_express(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.express_outgoing(50.0)
        assert account.balance == 99.0

    def test_outgoing_express(self):
        account = CompanyAccount("firmex", "1234567899")
        account.balance = 150.0
        account.express_outgoing(50.0)
        assert account.balance == 95.0


    def test_outgoing_debit_express(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 50.0
        account.express_outgoing(50.0)
        assert account.balance == -1.0

    def test_outgoing_debit_express(self):
        account = CompanyAccount("firmex", "1234567899")
        account.balance = 50.0
        account.express_outgoing(50.0)
        assert account.balance == -5.0

    def test_incoming_express(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        account.express_incoming(50.0)
        assert account.balance == 150.0


    def test_incoming_express(self):
        account = CompanyAccount("firmex", "1234567899")
        account.balance = 100.0
        account.express_incoming(50.0)
        assert account.balance == 150.0


