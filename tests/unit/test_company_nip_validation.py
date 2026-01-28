import pytest
from src.company_account import CompanyAccount


class TestCompanyAccountNIPValidation:
    
    def test_invalid_nip_length_does_not_call_mf_api(self, mocker):
        mock_get = mocker.patch('src.company_account.requests.get')
        
        account = CompanyAccount("TestCorp", "123")
        
        mock_get.assert_not_called()
        assert account.nip == "Invalid"
    
    def test_valid_nip_length_calls_mf_api(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Czynny'
                }
            }
        }
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        account = CompanyAccount("TestCorp", "8461627563")
        assert account.nip == "8461627563"
    
    def test_nip_validation_success_active_status(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Czynny'
                }
            }
        }
        
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        account = CompanyAccount("TestCorp", "8461627563")
        assert account.nip == "8461627563"
    
    def test_nip_validation_failure_inactive_status(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Zwolniony'
                }
            }
        }
        
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("TestCorp", "8461627563")
    
    def test_nip_validation_failure_missing_subject(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'result': {}}
        
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("TestCorp", "8461627563")
    
    def test_nip_validation_failure_api_error(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("TestCorp", "8461627563")
    
    def test_nip_validation_failure_network_error(self, mocker):
        mocker.patch('src.company_account.requests.get', side_effect=ConnectionError("Network error"))
        
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("TestCorp", "8461627563")
    
    def test_nip_api_url_uses_default_test_environment(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Czynny'
                }
            }
        }
        mock_get = mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        account = CompanyAccount("TestCorp", "8461627563")
        
        call_args = mock_get.call_args[0][0]
        assert 'wl-test.mf.gov.pl' in call_args
    
    def test_nip_api_request_includes_date_parameter(self, mocker):
        """Test that API request includes date parameter in correct format."""
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Czynny'
                }
            }
        }
        mock_get = mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        CompanyAccount("TestCorp", "8461627563")
        
        call_args = mock_get.call_args[0][0]
        assert '?date=' in call_args
        date_part = call_args.split('?date=')[1]
        assert len(date_part) == 10
        assert date_part.count('-') == 2


class TestCompanyAccountBasic:
    
    def test_company_account_creation_with_valid_registered_nip(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Czynny'
                }
            }
        }
        
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        account = CompanyAccount("TechCorp", "1234567890")
        assert account.company_name == "TechCorp"
        assert account.nip == "1234567890"
        assert account.balance == 0.0
    
    def test_company_account_with_invalid_nip_length_still_creates_account(self):
        account = CompanyAccount("TechCorp", "123")
        assert account.company_name == "TechCorp"
        assert account.nip == "Invalid"
        assert account.balance == 0.0
    
    def test_constructor_raises_value_error_for_unregistered_nip(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': {
                'subject': {
                    'statusVat': 'Zwolniony'
                }
            }
        }
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        with pytest.raises(ValueError) as exc_info:
            CompanyAccount("FakeCorp", "9999999999")
        
        assert "Company not registered!!" in str(exc_info.value)
    
    def test_constructor_raises_value_error_on_network_error(self, mocker):
        mocker.patch('src.company_account.requests.get', side_effect=ConnectionError("Network unavailable"))
        
        with pytest.raises(ValueError) as exc_info:
            CompanyAccount("TestCorp", "8461627563")
        
        assert "Company not registered!!" in str(exc_info.value)
    
    def test_constructor_raises_value_error_on_api_error(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        with pytest.raises(ValueError) as exc_info:
            CompanyAccount("TestCorp", "8461627563")
        
        assert "Company not registered!!" in str(exc_info.value)
