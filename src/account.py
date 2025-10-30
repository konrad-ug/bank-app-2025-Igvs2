class Account:
    def __init__(self, first_name, last_name, pesel, balance = 0, promo_code = None):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance
        self.promo_code = promo_code

        if promo_code and promo_code.startswith("promo_"):
            year = self.extract_birth_year(pesel)
            if year and year > 1960:
                self.balance += 50

        if len(pesel) != 11:
            self.pesel = "Invalid"
        else:
            self.pesel = pesel

    def extract_birth_year(self, pesel):
        s = str(pesel)
        if len(s) != 11 or not s.isdigit():
            return None

        yy = int(s[0:2])
        mm = int(s[2:4])

        if 1 <= mm <= 12:
            century = 1900
        elif 21 <= mm <= 32:
            century = 2000
            mm -= 20
        elif 41 <= mm <= 52:
            century = 2100
            mm -= 40
        elif 61 <= mm <= 72:
            century = 2200
            mm -= 60
        elif 81 <= mm <= 92:
            century = 1800
            mm -= 80
        else:
            return None

        return century + yy
