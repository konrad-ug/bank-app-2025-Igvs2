from src.account import Account

class PersonalAccount(Account):
    def __init__(self, first_name, last_name, pesel, promo_kod=None):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        if pesel and len(pesel) == 11:
            self.pesel = pesel
        else:
            self.pesel = "Invalid"
        self.promo_kod = promo_kod
        
        self.valid_promo()

                
                
    def valid_promo(self):
            if self.pesel == "Invalid":
                return 
        
            yy = int(self.pesel[0:2])
            mm = int(self.pesel[2:4])

            if (yy <= 60 and (1 <= mm <= 12)):
                self.balance = 0.0
            else:
                if (self.promo_kod and self.promo_kod.startswith("PROM") and len(self.promo_kod) == len("PROM_XYZ")):
                    self.balance += 50.0

    def express_outgoing(self, amount):
        fee = 1.0
        total_amount = amount + fee
        if (amount > 0 and total_amount <= self.balance):
            self.balance -= total_amount
            self.history.append(f'-{amount}')
            self.history.append(f"-{int(fee)}")

    def _last_three_are_deposits(self):
        return len(self.history) >= 3 and all(float(x) > 0 for x in self.history[-3:])

    def _sum_of_last_five_exceeds_amount(self, amount):
        return len(self.history) >= 5 and sum(float(x) for x in self.history[-5:]) > amount

    def submit_for_loan(self, amount):
        approved = self._last_three_are_deposits() or self._sum_of_last_five_exceeds_amount(amount)

        if approved:
            self.balance += amount

        return approved


