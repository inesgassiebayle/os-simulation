import random
import threading
import time


# Class that represents a Customer in the Casino
# Attributes: id, money
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
            if amount > self.money:
                print(f"Player {self.id} does not have enough money.")
                return False
            self.money -= amount
            return True


# Class that represents a Game
class Game(threading.Thread):
    def __init__(self, name, minimum_bet):
        super().__init__()
        self.name = name
        self.minimum_bet = minimum_bet


# Class that represents a Slot Machine Game
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
            transaction_fulfilled = customer.decrease(bet)
            if not transaction_fulfilled:
                return

            print(f"Customer {customer.id} is playing {self.name} with a bet of {bet}.")

            symbols = [random.randint(1, self.symbols_per_reel) for _ in range(self.reels)]
            print(f"Customer {customer.id} got symbols: {symbols}")

            if all(symbol == symbols[0] for symbol in symbols):
                payout = bet * 2
                customer.increase(payout)
                print(f"Customer {customer.id} WON {payout}!")
            else:
                print(f"Customer {customer.id} lost.")



# Class that represents a Roulette Game
class Roulette(Game):
    def __init__(self, type, minimum_bet, wheel_numbers, colors):
        super().__init__(type + ' Roulette', minimum_bet)
        self.lock = threading.Lock()
        self.players = []
        self.wheel_numbers = wheel_numbers
        self.colors = colors

    def add_player(self, customer, bet_type, bet_value, bet_amount):
        if bet_amount < self.minimum_bet:
            print(f"Customer {customer.id} cannot bet {bet_amount}. Minimum bet is {self.minimum_bet}.")
            return

        with self.lock:
            transaction_fulfilled = customer.decrease(bet_amount)
            if not transaction_fulfilled:
                return
            self.players.append((customer, bet_type, bet_value, bet_amount))
            print(f"Customer {customer.id} placed a {bet_type} bet on {bet_value} with {bet_amount}.")

    def spin_wheel(self):
        with self.lock:
            winning_number = random.choice(self.wheel_numbers)
            winning_color = self.colors[winning_number]
            print(f"\nRoulette spin result: {winning_number} ({winning_color})")

            for player, bet_type, bet_value, bet_amount in self.players:
                payout = 0

                if bet_type == "number" and bet_value == winning_number:
                    payout = bet_amount * (len(self.wheel_numbers) - 1)
                elif bet_type == "color" and bet_value == winning_color:
                    payout = bet_amount * 2
                elif bet_type == "even" and winning_number != 0 and winning_number % 2 == 0 and bet_value == "even":
                    payout = bet_amount * 2
                elif bet_type == "odd" and winning_number != 0 and winning_number % 2 == 1 and bet_value == "odd":
                    payout = bet_amount * 2
                elif bet_type == "low" and 1 <= winning_number <= 18 and bet_value == "low":
                    payout = bet_amount * 2
                elif bet_type == "high" and 19 <= winning_number <= 36 and bet_value == "high":
                    payout = bet_amount * 2

                if payout > 0:
                    print(f"Customer {player.id} WINS {payout}!")
                    player.increment(payout)
                else:
                    print(f"Customer {player.id} lost the bet.")

            self.players.clear()

    def run(self):
        while True:
            if self.players:
                time.sleep(3)
                self.spin_wheel()
            time.sleep(2)


class EuropeanRoulette(Roulette):
    def __init__(self, minimum_bet):
        wheel_numbers = list(range(37))
        colors = {0: 'Green',
                  **dict.fromkeys([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36], 'Red'),
                  **dict.fromkeys([2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35], 'Black')}
        super().__init__('European', minimum_bet, wheel_numbers, colors)


class AmericanRoulette(Roulette):
    def __init__(self, minimum_bet):
        wheel_numbers = list(range(37)) + ["00"]
        colors = {0: 'Green', "00": 'Green',
                  **dict.fromkeys([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36], 'Red'),
                  **dict.fromkeys([2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35], 'Black')}
        super().__init__('American', minimum_bet, wheel_numbers, colors)