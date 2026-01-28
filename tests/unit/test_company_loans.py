import pytest
from unittest.mock import patch, MagicMock
from src.company_account import CompanyAccount


class TestCompanyLoans:
    @pytest.fixture
    def company_account(self):
        account = CompanyAccount("TechCorp", "1234567890")
        account.balance = 1000.0
        return account

    @pytest.mark.parametrize("balance,loan_amount,has_zus,expected_approved,expected_balance", [
        (3000.0, 500.0, True, True, 3500.0),
        (3000.0, 1000.0, True, True, 4000.0),
        (500.0, 500.0, True, False, 500.0),
        (900.0, 500.0, True, False, 900.0),
        (2000.0, 500.0, False, False, 2000.0),
        (500.0, 500.0, False, False, 500.0),
        (3000.0, 500.0, True, True, 3500.0),
    ])
    def test_loan_submission(self, balance, loan_amount, has_zus, expected_approved, expected_balance):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        
        with patch('src.company_account.requests.get', return_value=mock_response):
            account = CompanyAccount("TechCorp", "1234567890")
            account.balance = balance
            
            if has_zus:
                account.history.append("-1775.0")
            
            result = account.take_loan(loan_amount)
            assert result == expected_approved
            assert account.balance == expected_balance

    def test_loan_approved_with_multiple_transfers(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        
        with patch('src.company_account.requests.get', return_value=mock_response):
            account = CompanyAccount("TechCorp", "1234567890")
            account.balance = 3000.0
            
            account.outgoing_transfer(100.0)
            account.incoming_transfer(500.0)
            account.outgoing_transfer(1775.0)
            account.incoming_transfer(200.0)
            
            assert account.balance == 1825.0
            result = account.take_loan(800.0)
            assert result == True
            assert account.balance == 2625.0

    def test_loan_rejected_multiple_outgoings_but_no_zus(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        
        with patch('src.company_account.requests.get', return_value=mock_response):
            account = CompanyAccount("TechCorp", "1234567890")
            account.balance = 2000.0
            
            account.outgoing_transfer(100.0)
            account.outgoing_transfer(500.0)
            account.outgoing_transfer(1000.0)
            
            assert account.balance == 400.0
            result = account.take_loan(200.0)
            assert result == False
            assert account.balance == 400.0
