from src.account import Account


class TestAccount:
    def test_account_creation_valid_pesel(self):
        account = Account("John", "Doe", "12345678901", 0,)
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

    def test_promo_code_valid(self):
        account = Account("Jane", "Smith", "12345", 0, "promo_123")
        assert account.balance == 50


    def test_promo_code_invalid(self):
        account = Account("Jane", "Smith", "12345", 0, "promo213")
        assert account.balance == 0

    def test_promo_code_none(self):
        account = Account("Jane", "Smith", "12345", 0)
        assert account.balance == 0

