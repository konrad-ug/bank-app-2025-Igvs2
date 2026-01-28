from datetime import datetime
from src.account import Account
from smtp.smtp import SMTPClient


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
        if amount > 0:
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
    
    def send_history_via_email(self, email_address: str) -> bool:
        """
        Send account transfer history via email.
        
        Args:
            email_address: Recipient email address
            
        Returns:
            True if email sent successfully, False otherwise
        """
        today = datetime.now().strftime('%Y-%m-%d')
        subject = f"Account Transfer History {today}"
        text = f"Personal account history: {self.history}"
        
        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)
    
    def to_dict(self):
        return {
            "type": "personal",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "pesel": self.pesel,
            "balance": self.balance,
            "history": self.history,
            "promo_kod": self.promo_kod
        }
    
    @staticmethod
    def from_dict(data):
        account = PersonalAccount(data["first_name"], data["last_name"], data["pesel"], data.get("promo_kod"))
        account.balance = data["balance"]
        account.history = data["history"]
        return account


