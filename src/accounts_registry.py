from src.personal_account import PersonalAccount


class AccountsRegistry:
    
    def __init__(self):
        self.accounts = []
    
    def add_account(self, account: PersonalAccount) -> None:
        self.accounts.append(account)
    
    def find_account_by_pesel(self, pesel: str) -> PersonalAccount | None:
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return None
    
    def pesel_exists(self, pesel: str) -> bool:
        return self.find_account_by_pesel(pesel) is not None
    
    def get_all_accounts(self) -> list:
        return self.accounts
    
    def get_accounts_count(self) -> int:
        return len(self.accounts)
