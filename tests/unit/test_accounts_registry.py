import pytest
from src.personal_account import PersonalAccount
from src.accounts_registry import AccountsRegistry


class TestAccountsRegistry:
    @pytest.fixture
    def registry(self):
        return AccountsRegistry()
    
    @pytest.fixture
    def sample_accounts(self):
        account1 = PersonalAccount("John", "Doe", "12345678901")
        account2 = PersonalAccount("Jane", "Smith", "98765432109")
        account3 = PersonalAccount("Bob", "Johnson", "55555555555")
        return [account1, account2, account3]
    
    def test_registry_initialization(self, registry):
        assert registry.accounts == []
        assert registry.get_accounts_count() == 0
    
    def test_add_single_account(self, registry, sample_accounts):
        registry.add_account(sample_accounts[0])
        assert registry.get_accounts_count() == 1
        assert sample_accounts[0] in registry.accounts
    
    def test_add_multiple_accounts(self, registry, sample_accounts):
        for account in sample_accounts:
            registry.add_account(account)
        
        assert registry.get_accounts_count() == 3
        assert len(registry.get_all_accounts()) == 3
    
    def test_find_account_by_pesel_found(self, registry, sample_accounts):
        for account in sample_accounts:
            registry.add_account(account)
        
        found_account = registry.find_account_by_pesel("12345678901")
        assert found_account is not None
        assert found_account.first_name == "John"
        assert found_account.last_name == "Doe"
    
    def test_find_account_by_pesel_not_found(self, registry, sample_accounts):
        for account in sample_accounts:
            registry.add_account(account)
        
        found_account = registry.find_account_by_pesel("99999999999")
        assert found_account is None
    
    def test_find_account_in_empty_registry(self, registry):
        found_account = registry.find_account_by_pesel("12345678901")
        assert found_account is None
    
    def test_get_all_accounts(self, registry, sample_accounts):
        for account in sample_accounts:
            registry.add_account(account)
        
        all_accounts = registry.get_all_accounts()
        assert len(all_accounts) == 3
        assert all_accounts == sample_accounts
    
    def test_get_all_accounts_empty_registry(self, registry):
        all_accounts = registry.get_all_accounts()
        assert all_accounts == []
    
    def test_get_accounts_count_empty(self, registry):
        assert registry.get_accounts_count() == 0
    
    def test_get_accounts_count_with_accounts(self, registry, sample_accounts):
        registry.add_account(sample_accounts[0])
        assert registry.get_accounts_count() == 1
        
        registry.add_account(sample_accounts[1])
        assert registry.get_accounts_count() == 2
        
        registry.add_account(sample_accounts[2])
        assert registry.get_accounts_count() == 3
    
    @pytest.mark.parametrize("first_name,last_name,pesel", [
        ("Alice", "Brown", "11111111111"),
        ("Charlie", "Davis", "22222222222"),
        ("Diana", "Evans", "33333333333"),
    ])
    def test_add_and_find_parametrized(self, registry, first_name, last_name, pesel):
        account = PersonalAccount(first_name, last_name, pesel)
        registry.add_account(account)
        
        found = registry.find_account_by_pesel(pesel)
        assert found is not None
        assert found.first_name == first_name
        assert found.last_name == last_name
        assert found.pesel == pesel


class TestPeselUniqueness:
    @pytest.fixture
    def registry(self):
        """Fixture that creates an empty accounts registry."""
        return AccountsRegistry()
    
    def test_pesel_exists_returns_false_for_empty_registry(self, registry):
        """Test that pesel_exists returns False when registry is empty."""
        assert registry.pesel_exists("12345678901") is False
    
    def test_pesel_exists_returns_true_when_pesel_exists(self, registry):
        """Test that pesel_exists returns True when PESEL is in registry."""
        account = PersonalAccount("John", "Doe", "12345678901")
        registry.add_account(account)
        
        assert registry.pesel_exists("12345678901") is True
    
    def test_pesel_exists_returns_false_when_pesel_not_found(self, registry):
        """Test that pesel_exists returns False when PESEL is not in registry."""
        account = PersonalAccount("John", "Doe", "12345678901")
        registry.add_account(account)
        
        assert registry.pesel_exists("99999999999") is False
    
    @pytest.mark.parametrize("pesel", [
        "11111111111",
        "22222222222",
        "33333333333",
    ])
    def test_pesel_exists_multiple_accounts(self, registry, pesel):
        """Test pesel_exists with multiple accounts in registry."""
        accounts = [
            PersonalAccount("Alice", "Brown", "11111111111"),
            PersonalAccount("Charlie", "Davis", "22222222222"),
            PersonalAccount("Diana", "Evans", "33333333333"),
        ]
        
        for account in accounts:
            registry.add_account(account)
        
        assert registry.pesel_exists(pesel) is True
        assert registry.pesel_exists("99999999999") is False
