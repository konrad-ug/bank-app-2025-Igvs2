from src.company_account import CompanyAccount


class TestCompanyAccount:
    def test_account_creation(self):
        account = CompanyAccount("metalex", "1234567890")
        assert account.company_name == "metalex"
        assert account.nip == "1234567890"
        assert account.balance == 0.0
    def test_nip_too_short(self):
        account = CompanyAccount("zwiripiach", "99999")
        assert account.company_name == "zwiripiach" 
        assert account.nip == "Invalid"
        assert account.balance == 0.0
    def test_nip_too_long(self):
        account = CompanyAccount("plastikowe", "44444444444444")
        assert account.company_name == "plastikowe" 
        assert account.nip == "Invalid"
        assert account.balance == 0.0