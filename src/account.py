
class Account:
    def __init__(self):
        self.balance = 0.0
        self.history = []

    def outgoing_transfer(self, amount: float) -> None:
        if (amount < self.balance and amount > 0.0):
            self.balance -= amount
            self.history.append(f'-{amount}')

    def incoming_transfer(self, amount: float) -> None:
        if (amount > 0.0 ):
            self.balance += amount
            self.history.append(f'{amount}')

    def express_incoming(self, amount: float) -> None:
        if (amount > 0.0 ):
            self.balance += amount


