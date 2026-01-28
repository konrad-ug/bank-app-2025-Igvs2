import pytest
from src.personal_account import PersonalAccount


class TestAccount:
    @pytest.mark.parametrize("first_name,last_name,pesel,expected_pesel", [
        ("John", "Doe", "12345678901", "12345678901"),
        ("Jane", "Smith", "12345", "Invalid"),
    ])
    def test_account_creation(self, first_name, last_name, pesel, expected_pesel):
        account = PersonalAccount(first_name, last_name, pesel)
        assert account.first_name == first_name
        assert account.last_name == last_name
        assert account.balance == 0
        assert account.pesel == expected_pesel

    @pytest.mark.parametrize("pesel,promo_kod,expected_balance", [
        ("61071512345", "PROM_123", 50),
        ("51071512345", "PROM_213", 0),
        ("61071512345", None, 0),
        ("61071512345", "promo223", 0),
        ("41071512345", "promo123", 0),
    ])
    def test_promo_code(self, pesel, promo_kod, expected_balance):
        account = PersonalAccount("Jane", "Smith", pesel, promo_kod)
        assert account.balance == expected_balance

