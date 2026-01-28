from flask import Flask, request, jsonify
from src.accounts_registry import AccountsRegistry
from src.personal_account import PersonalAccount

app = Flask(__name__)
registry = AccountsRegistry()


@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    
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
    """Process a transfer (incoming, outgoing, or express) for an account."""
    print(f"Transfer request for PESEL: {pesel}")
    account = registry.find_account_by_pesel(pesel)
    
    if account is None:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = data.get("amount")
    transfer_type = data.get("type")
    
    # Validate transfer type
    valid_types = ["incoming", "outgoing", "express"]
    if transfer_type not in valid_types:
        return jsonify({"error": f"Invalid transfer type. Must be one of: {', '.join(valid_types)}"}), 400
    
    # Store balance before transfer to check if it succeeded
    balance_before = account.balance
    
    # Execute transfer based on type
    if transfer_type == "incoming":
        account.incoming_transfer(amount)
    elif transfer_type == "outgoing":
        account.outgoing_transfer(amount)
    elif transfer_type == "express":
        account.express_outgoing(amount)
    
    # Check if transfer was successful
    balance_after = account.balance
    
    # For outgoing transfers, check if balance changed (transaction succeeded)
    if transfer_type in ["outgoing", "express"]:
        if balance_before == balance_after:
            # Transaction failed (insufficient balance or invalid amount)
            return jsonify({"error": "Transaction failed. Check balance and amount."}), 422
    
    return jsonify({"message": "Zlecenie przyjęto do realizacji"}), 200


if __name__ == '__main__':
    app.run(debug=True)
