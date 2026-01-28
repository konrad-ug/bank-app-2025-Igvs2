import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestPersonalAccountEmailHistory:
    
    def test_send_history_calls_smtp_with_correct_parameters(self, mocker):
        mock_smtp = mocker.patch('src.personal_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = PersonalAccount("John", "Doe", "12345678901")
        account.history = ["100", "-50", "200"]
        
        result = account.send_history_via_email("test@example.com")
        
        mock_instance.send.assert_called_once()
        
        call_args = mock_instance.send.call_args
        subject = call_args[0][0]
        text = call_args[0][1]
        email = call_args[0][2]
        
        today = datetime.now().strftime('%Y-%m-%d')
        assert subject == f"Account Transfer History {today}"
        assert text == "Personal account history: ['100', '-50', '200']"
        assert email == "test@example.com"
        assert result == True
    
    def test_send_history_returns_true_on_success(self, mocker):
        mock_smtp = mocker.patch('src.personal_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = PersonalAccount("Jane", "Smith", "98765432109")
        account.history = ["500"]
        
        result = account.send_history_via_email("success@test.com")
        
        assert result == True
    
    def test_send_history_returns_false_on_failure(self, mocker):
        mock_smtp = mocker.patch('src.personal_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = False
        
        account = PersonalAccount("Bob", "Jones", "11122233344")
        account.history = ["-100", "50"]
        
        result = account.send_history_via_email("fail@test.com")
        
        assert result == False
    
    def test_send_history_with_empty_history(self, mocker):
        mock_smtp = mocker.patch('src.personal_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = PersonalAccount("Alice", "Brown", "55566677788")
        
        result = account.send_history_via_email("empty@test.com")
        
        call_args = mock_instance.send.call_args[0]
        assert "Personal account history: []" in call_args[1]
        assert result == True


class TestCompanyAccountEmailHistory:
    
    def test_send_history_calls_smtp_with_correct_parameters(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        mock_smtp = mocker.patch('src.company_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = CompanyAccount("TechCorp", "1234567890")
        account.history = ["5000", "-1000", "500"]
        
        result = account.send_history_via_email("company@example.com")
        
        mock_instance.send.assert_called_once()
        
        call_args = mock_instance.send.call_args
        subject = call_args[0][0]
        text = call_args[0][1]
        email = call_args[0][2]
        
        today = datetime.now().strftime('%Y-%m-%d')
        assert subject == f"Account Transfer History {today}"
        assert text == "Company account history: ['5000', '-1000', '500']"
        assert email == "company@example.com"
        assert result == True
    
    def test_send_history_returns_true_on_success(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        mock_smtp = mocker.patch('src.company_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = CompanyAccount("BuildCorp", "9876543210")
        account.history = ["10000"]
        
        result = account.send_history_via_email("success@company.com")
        
        assert result == True
    
    def test_send_history_returns_false_on_failure(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        mock_smtp = mocker.patch('src.company_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = False
        
        account = CompanyAccount("FailCorp", "1111111111")
        account.history = ["-5000", "2000"]
        
        result = account.send_history_via_email("fail@company.com")
        
        assert result == False
    
    def test_send_history_with_empty_history(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        mock_smtp = mocker.patch('src.company_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = CompanyAccount("EmptyCorp", "2222222222")
        
        result = account.send_history_via_email("empty@company.com")
        
        call_args = mock_instance.send.call_args[0]
        assert "Company account history: []" in call_args[1]
        assert result == True
    
    def test_send_history_date_format(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {'subject': {'statusVat': 'Czynny'}}}
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        mock_smtp = mocker.patch('src.company_account.SMTPClient')
        mock_instance = mock_smtp.return_value
        mock_instance.send.return_value = True
        
        account = CompanyAccount("DateCorp", "3333333333")
        
        account.send_history_via_email("date@test.com")
        
        call_args = mock_instance.send.call_args[0]
        subject = call_args[0]
        
        import re
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        assert re.search(date_pattern, subject) is not None
