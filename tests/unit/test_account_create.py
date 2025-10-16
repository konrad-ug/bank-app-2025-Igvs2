from src.account import Account


class TestAccount:
    def test_account_creation_valid_pesel(self):
        account = Account("John", "Doe", "12345678901", 0)
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0
        assert account.pesel == "12345678901"

    def test_account_creation_invalid_pesel(self):
        account = Account("Jane", "Smith", "12345", 0)
        assert account.first_name == "Jane"
        assert account.last_name == "Smith"
        assert account.balance == 0
        assert account.pesel == "Invalid"
