from src.account import Account

class CompanyAccount(Account):
    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        if (len(nip) != 10):
            self.nip = "Invalid" 
        else:
            self.nip = nip
    def express_outgoing(self, amount):
        fee = 5.0
        total_amount = amount + fee
        if (amount > 0 and total_amount <= self.balance + fee):
            self.balance -= total_amount
            self.history.append(f'-{amount}')
            self.history.append(f"-{int(fee)}")

    def _balance_sufficient(self, amount):
        return self.balance >= amount * 2

    def _has_zus_transfer(self):
        return "-1775.0" in self.history

    def take_loan(self, amount):
        approved = self._balance_sufficient(amount) and self._has_zus_transfer()

        if approved:
            self.balance += amount

        return approved