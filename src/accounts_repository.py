from abc import ABC, abstractmethod


class AccountsRepository(ABC):
    """Interface for accounts repository implementations"""
    
    @abstractmethod
    def save_all(self, accounts):
        """Save all accounts to storage"""
        pass
    
    @abstractmethod
    def load_all(self):
        """Load all accounts from storage"""
        pass
