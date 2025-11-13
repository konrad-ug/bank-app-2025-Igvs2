from src.account import Account
from src.personal_account import PersonalAccount

class TestPersonalLoans:
    def test_loan_accepted_one(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 200.0
        
        account.incoming_transfer(50.0)
        account.incoming_transfer(20.0)
        account.incoming_transfer(80.0)
        assert account.balance == 350.0
        assert account.submit_for_loan(500) == True
        assert account.balance == 850.0
    
    def test_loan_refused_one(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 200.0
        
        account.incoming_transfer(50.0)
        account.incoming_transfer(20.0)
        assert account.submit_for_loan(500) == False
    
    def test_loan_accepted_two(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 200.0
        
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.outgoing_transfer(50.0)
        account.outgoing_transfer(40.0)
        assert account.balance == 410.0
        assert account.submit_for_loan(200) == True
        assert account.balance == 610.0
    
    def test_loan_refused_two(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 200.0
        
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.outgoing_transfer(20.0)
        account.outgoing_transfer(20.0)
        assert account.balance == 460.0
        assert account.submit_for_loan(500) == False
        assert account.balance == 460.0


