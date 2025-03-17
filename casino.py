import random
import threading


class Customer(threading.Thread):
    def __init__(self, customer_id, money):
        super().__init__()
        self.id = customer_id
        self.money = money
        self.lock = threading.Lock()

    def increment(self, amount):
        with self.lock:
            self.money += amount

    def decrease(self, amount):
        with self.lock:
            self.money -= amount


class Game(threading.Thread):
    def __init__(self, name, minimum_bet):
        super().__init__()
        self.name = name
        self.minimum_bet = minimum_bet


class SlotMachine(Game):
    def __init__(self, minimum_bet, reels, symbols_per_reel):
        super().__init__('Slot Machine', minimum_bet)
        self.lock = threading.Lock()
        self.reels = reels
        self.symbols_per_reel = symbols_per_reel

    def play(self, customer, bet):
        if bet < self.minimum_bet:
            print(f"Customer {customer.id} cannot bet {bet} on {self.name}. Minimum bet is {self.minimum_bet}.")
            return

        with self.lock:
            customer.decrease(bet)
            print(f"Customer {customer.id} is playing {self.name} with a bet of {bet}.")

            symbols = [random.randint(1, self.symbols_per_reel) for _ in range(self.reels)]
            print(f"Customer {customer.id} got symbols: {symbols}")

            if all(symbol == symbols[0] for symbol in symbols):
                payout = bet * 2
                customer.increase(payout)
                print(f"Customer {customer.id} WON {payout}!")
            else:
                print(f"Customer {customer.id} lost.")


class BlackJack(Game):
    def __init__(self, minimum_bet, reels, symbols_per_reel):
        super().__init__('Black Jack', minimum_bet)