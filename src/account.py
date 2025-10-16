class Account:
    def __init__(self, first_name, last_name, pesel, balance = 0, promo_code = None):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance
        self.promo_code = promo_code

        if promo_code and promo_code.startswith("promo_"):
            self.balance = balance + 50

        if len(pesel) != 11:
            self.pesel = "Invalid"
        else:
            self.pesel = pesel
