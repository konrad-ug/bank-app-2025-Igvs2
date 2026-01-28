import pytest
from src.company_account import CompanyAccount


class TestCompanyAccount:
    @pytest.mark.parametrize("company_name,nip,expected_nip", [
        ("metalex", "1234567890", "1234567890"),
        ("zwiripiach", "99999", "Invalid"),
        ("plastikowe", "44444444444444", "Invalid"),
    ])
    def test_account_creation(self, company_name, nip, expected_nip, mocker):
        if len(nip) == 10:
            mock_response = mocker.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'result': {'subject': {'statusVat': 'Czynny'}}
            }
            mocker.patch('src.company_account.requests.get', return_value=mock_response)
        
        account = CompanyAccount(company_name, nip)
        assert account.company_name == company_name
        assert account.nip == expected_nip
        assert account.balance == 0.0