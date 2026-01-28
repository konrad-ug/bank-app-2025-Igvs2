from behave import *
import requests

URL = "http://localhost:5000"


@step('Account with pesel "{pesel}" has balance of "{balance}"') 
def set_account_balance(context, pesel, balance):
    """Set account balance by making an incoming transfer"""
    json_body = {
        "from_account": "external",
        "to_account": pesel,
        "amount": float(balance)
    }
    response = requests.post(URL + "/api/transfer", json=json_body)
    print(f"Balance transfer response: {response.status_code}, body: {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


@when('I make a transfer from pesel: "{from_pesel}" to pesel: "{to_pesel}" with amount: "{amount}"')
def make_transfer(context, from_pesel, to_pesel, amount):
    json_body = {
        "from_account": from_pesel,
        "to_account": to_pesel,
        "amount": float(amount)
    }
    response = requests.post(URL + "/api/transfer", json=json_body)
    assert response.status_code == 200
    context.last_response = response


@when('I make an express transfer from pesel: "{from_pesel}" to pesel: "{to_pesel}" with amount: "{amount}"')
def make_express_transfer(context, from_pesel, to_pesel, amount):
    json_body = {
        "from_account": from_pesel,
        "to_account": to_pesel,
        "amount": float(amount),
        "express": True
    }
    response = requests.post(URL + "/api/transfer", json=json_body)
    assert response.status_code == 200
    context.last_response = response


@when('I attempt a transfer from pesel: "{from_pesel}" to pesel: "{to_pesel}" with amount: "{amount}"')
def attempt_transfer(context, from_pesel, to_pesel, amount):
    json_body = {
        "from_account": from_pesel,
        "to_account": to_pesel,
        "amount": float(amount)
    }
    response = requests.post(URL + "/api/transfer", json=json_body)
    context.last_response = response


@then('Transfer fails with error')
def check_transfer_failed(context):
    assert context.last_response.status_code == 400
