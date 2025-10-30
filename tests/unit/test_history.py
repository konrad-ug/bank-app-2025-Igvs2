from src.account import Account
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount 

class TestTransfers:
    def test_outgoing_personal_express(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.express_outgoing(50.0)
        assert account.balance == 99.0
        assert account.history == ["-50.0", "-1"]
    def test_outgoing_company_express(self):
        account = CompanyAccount("firmex", "1234567899")
        account.balance = 150.0
        account.express_outgoing(50.0)
        assert account.balance == 95.0
        assert account.history == ["-50.0", "-5"]