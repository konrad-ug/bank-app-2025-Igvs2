import pytest
from src.personal_account import PersonalAccount


class TestPersonalAccount:
    @pytest.fixture
    def base_account(self):
        return PersonalAccount("John", "Doe", "00000000000")

    def test_account_creation(self, base_account):
        assert base_account.first_name == "John"
        assert base_account.last_name == "Doe"
        assert base_account.balance == 0.0
        assert base_account.pesel == "00000000000"

    @pytest.mark.parametrize("pesel", [
        "12345",
        "12345123451234512345",
        None,
    ])
    def test_invalid_pesel(self, pesel):
        account = PersonalAccount("John", "Doe", pesel)
        assert account.pesel == "Invalid"

    @pytest.mark.parametrize("pesel,promo_kod,expected_balance", [
        ("79530000000", "PROM_ABC", 50.0),
        ("00000000000", "KODY_XYS", 0.0),
        ("00000000000", "KODY", 0.0),
        ("60011111111", "PROM_KOD", 0.0),
        ("04290000000", "PROM_KOD", 50.0),
    ])
    def test_promo_code(self, pesel, promo_kod, expected_balance):
        account = PersonalAccount("John", "Doe", pesel, promo_kod)
        assert account.balance == expected_balance