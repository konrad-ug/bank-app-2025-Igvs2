from flask import Flask, request, jsonify
from src.accounts_registry import AccountsRegistry
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount

app = Flask(__name__)
registry = AccountsRegistry()


@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    
    is_company = "nip" in data
    
    if is_company:
        nip = data.get("nip")
        
        if not nip or len(nip) != 10:
            return jsonify({"error": "Invalid NIP format. NIP must be exactly 10 digits."}), 400
        
        if any(hasattr(acc, 'nip') and acc.nip == nip for acc in registry.get_all_accounts()):
            return jsonify({"error": "Account with this NIP already exists"}), 409
        
        try:
            account = CompanyAccount(data["name"], nip)
            registry.add_account(account)
            return jsonify({"message": "Account created"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        if registry.pesel_exists(data["pesel"]):
            return jsonify({"error": "Account with this PESEL already exists"}), 409
        
        account = PersonalAccount(data["name"], data["surname"], data["pesel"])
        registry.add_account(account)
        return jsonify({"message": "Account created"}), 201


@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.get_all_accounts()
    accounts_data = [
        {
            "name": acc.first_name,
            "surname": acc.last_name,
            "pesel": acc.pesel,
            "balance": acc.balance
        } for acc in accounts
    ]
    return jsonify(accounts_data), 200


@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Get account count request received")
    count = registry.get_accounts_count()
    return jsonify({"count": count}), 200


@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    print(f"Get account by PESEL request: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    account_data = {
        "name": account.first_name,
        "surname": account.last_name,
        "pesel": account.pesel,
        "balance": account.balance
    }
    return jsonify(account_data), 200


@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    print(f"Update account request for PESEL: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    
    if "name" in data:
        account.first_name = data["name"]
    if "surname" in data:
        account.last_name = data["surname"]
    
    return jsonify({"message": "Account updated"}), 200


@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    print(f"Delete account request for PESEL: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    registry.accounts.remove(account)
    return jsonify({"message": "Account deleted"}), 200


@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer(pesel):
    print(f"Transfer request for PESEL: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = data.get("amount")
    transfer_type = data.get("type")
    
    valid_types = ["incoming", "outgoing", "express"]
    if transfer_type not in valid_types:
        return jsonify({"error": f"Invalid transfer type. Must be one of: {', '.join(valid_types)}"}), 400
    
    balance_before = account.balance
    
    if transfer_type == "incoming":
        account.incoming_transfer(amount)
    elif transfer_type == "outgoing":
        account.outgoing_transfer(amount)
    elif transfer_type == "express":
        account.express_outgoing(amount)
    
    balance_after = account.balance
    
    if transfer_type in ["outgoing", "express"]:
        if balance_before == balance_after:
            return jsonify({"error": "Transaction failed. Check balance and amount."}), 422
    
    return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200


@app.route("/api/transfer", methods=['POST'])
def transfer_between_accounts():
    print("Transfer between accounts request received")
    data = request.get_json()
    
    from_account = data.get("from_account")
    to_account = data.get("to_account")
    amount = data.get("amount")
    express = data.get("express", False)
    
    if not from_account or not to_account or not amount:
        return jsonify({"error": "Missing required fields: from_account, to_account, amount"}), 400
    
    # Handle external transfers (for setting initial balance)
    if from_account == "external":
        recipient = registry.find_account_by_pesel(to_account)
        if recipient is None:
            return jsonify({"error": "Account not found"}), 404
        recipient.incoming_transfer(amount)
        return jsonify({"message": "Transfer completed"}), 200
    
    # Regular transfer between accounts
    sender = registry.find_account_by_pesel(from_account)
    recipient = registry.find_account_by_pesel(to_account)
    
    if sender is None or recipient is None:
        return jsonify({"error": "One or both accounts not found"}), 404
    
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    
    if express:
        # Express transfer with fee
        fee = 1.0
        total_amount = amount + fee
        if total_amount > sender.balance:
            return jsonify({"error": "Insufficient funds"}), 400
        sender.express_outgoing(amount)
        recipient.incoming_transfer(amount)
    else:
        # Standard transfer
        if amount > sender.balance:
            return jsonify({"error": "Insufficient funds"}), 400
        sender.outgoing_transfer(amount)
        recipient.incoming_transfer(amount)
    
    return jsonify({"message": "Transfer completed"}), 200


if __name__ == '__main__':
    app.run(debug=True)
