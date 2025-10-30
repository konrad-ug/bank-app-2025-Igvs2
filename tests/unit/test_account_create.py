from src.personal_account import PersonalAccount


class TestAccount:
    def test_account_creation_valid_pesel(self):
        account = PersonalAccount("John", "Doe", "12345678901")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0
        assert account.pesel == "12345678901"

    def test_account_creation_invalid_pesel(self):
        account = PersonalAccount("Jane", "Smith", "12345")
        assert account.first_name == "Jane"
        assert account.last_name == "Smith"
        assert account.balance == 0
        assert account.pesel == "Invalid"

    def test_promo_code_valid_year_valid(self):
        account = PersonalAccount("Jane", "Smith", "61071512345", "PROM_123")
        assert account.balance == 50


    def test_promo_code_valid_year_invalid(self):
        account = PersonalAccount("Jane", "Smith", "51071512345", "promo_213")
        assert account.balance == 0

    def test_promo_code_none(self):
        account = PersonalAccount("Jane", "Smith", "61071512345")
        assert account.balance == 0

    def test_promo_code_invalid_year_valid(self):
        account = PersonalAccount("Jane", "Smith", "61071512345", "promo223")
        assert account.balance == 0

    def test_promo_code_invalid_year_invalid(self):
        account = PersonalAccount("Jane", "Smith", "41071512345", "promo123")
        assert account.balance == 0

