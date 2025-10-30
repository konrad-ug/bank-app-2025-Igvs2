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
        if (amount > 0 and total_amount <= self.balance + fee):
            self.balance -= total_amount