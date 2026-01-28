import os
import requests
from datetime import datetime
from src.account import Account

class CompanyAccount(Account):
    # Default to test environment, can be overridden via environment variable
    MF_API_URL = os.getenv('BANK_APP_MF_URL', 'https://wl-test.mf.gov.pl')
    
    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        
        # If NIP has wrong length, mark as invalid but don't validate with API
        if len(nip) != 10:
            self.nip = "Invalid"
        else:
            # Valid length - validate with government API
            if not self._validate_nip_with_mf(nip):
                raise ValueError("Company not registered!!")
            self.nip = nip
    
    def _validate_nip_with_mf(self, nip: str) -> bool:
        """
        Validate NIP against Polish Ministry of Finance API.
        Returns True if NIP is registered and active, False otherwise.
        """
        try:
            # Get today's date in YYYY-MM-DD format
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Build the request URL
            url = f"{self.MF_API_URL}/api/search/nip/{nip}?date={today}"
            
            # Send request to MF API
            response = requests.get(url)
            
            # Print response for logging/debugging
            print(f"MF API Response for NIP {nip}: {response.text}")
            
            # Check if request was successful
            if response.status_code != 200:
                return False
            
            # Parse response
            data = response.json()
            
            # Check if result exists and statusVat is "Czynny" (active)
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