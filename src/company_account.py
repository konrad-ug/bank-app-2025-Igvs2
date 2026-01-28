import os
import requests
from datetime import datetime
from src.account import Account
from smtp.smtp import SMTPClient


class CompanyAccount(Account):
    MF_API_URL = os.getenv('BANK_APP_MF_URL', 'https://wl-test.mf.gov.pl')
    
    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        
        if len(nip) != 10:
            self.nip = "Invalid"
        else:
            if not self._validate_nip_with_mf(nip):
                raise ValueError("Company not registered!!")
            self.nip = nip
    
    def _validate_nip_with_mf(self, nip: str) -> bool:
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.MF_API_URL}/api/search/nip/{nip}?date={today}"
            
            response = requests.get(url)
            
            print(f"MF API Response for NIP {nip}: {response.text}")
            
            if response.status_code != 200:
                return False
            
            data = response.json()
            
            if 'result' in data and 'subject' in data['result']:
                subject = data['result']['subject']
                status_vat = subject.get('statusVat')
                return status_vat == "Czynny"
            
            return False
            
        except Exception as e:
            print(f"Error validating NIP with MF API: {e}")
            return False
    
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
        text = f"Company account history: {self.history}"
        
        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)
    
    def to_dict(self):
        return {
            "type": "company",
            "company_name": self.company_name,
            "nip": self.nip,
            "balance": self.balance,
            "history": self.history
        }
    
    @staticmethod
    def from_dict(data):
        # Skip NIP validation when loading from DB
        account = object.__new__(CompanyAccount)
        Account.__init__(account)
        account.company_name = data["company_name"]
        account.nip = data["nip"]
        account.balance = data["balance"]
        account.history = data["history"]
        return account