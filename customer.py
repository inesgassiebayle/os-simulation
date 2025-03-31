import threading
import time
import random
from bar import Order


class Customer(threading.Thread):
    def __init__(self, id, casino, balance):
        super().__init__()
        self.id = id
        self.casino = casino
        self.balance = balance
        self.lock = threading.Lock()

    def increment(self, amount):
        with self.lock:
            self.balance += amount
        print(f"Customer-{self.id} won ${amount}. (Balance: ${self.balance}).")

    def decrease(self, amount):
        with self.lock:
            if amount > self.balance:
                print(f"Customer-{self.id} does not have ${amount} to spend.")
                return False
            self.balance -= amount
            print(f"Customer-{self.id} has spent ${amount}. (Balance: ${self.balance}).")
            return True

    def get_balance(self):
        with self.lock:
            return self.balance

    def play(self, amount, name, probability, prize):
        print(f"Customer-{self.id} playing {name}")
        if not self.decrease(amount):
            self.casino.add_customer(self)
            return

        if random.random() < probability:
            self.increment(amount * prize)
        else:
            print(f"Customer-{self.id} lost ${amount}. (Balance: ${self.balance})")

        self.casino.add_customer(self)
        time.sleep(random.randint(1, 5))

    def place_order(self):
        bar_name = random.choice(list(self.casino.bars.keys()))
        order = Order(self)
        num_items = random.randint(1, 7)
        bar = self.casino.bars[bar_name]
        items = random.choices(bar.menu.products, k=num_items)
        for item in items:
            order.add_item(item)
        with self.lock:
            if order.get_total() > self.balance:
                print(f"Customer-{self.id} could not place order of ${order.get_total()}. (Balance: ${self.balance})")
                return
        with bar.lock:
            self.decrease(order.get_total())
            bar.orders.append(order)
        print(f"Customer-{self.id} ordered {[item.name for item in order.items]} (Total: ${order.get_total()}, Balance: ${self.balance})")

    def run(self):
        while True:
            # Customer is playing or waiting to play
            with self.casino.customers_lock:
                if self not in self.casino.customers:
                    time.sleep(random.randint(1, 5))
                    continue

            # Player leaves the casino
            if self.balance <= 0:
                print(f"Customer-{self.id} is out of money and leaves the casino.")
                break

            if random.random() < 0.20:  # 20% chance to leave
                print(f"Customer-{self.id} has decided to leave the casino.")
                break

            if random.random() < 0.10:  # 10% chance to leave strategically
                print(f"Customer-{self.id} is leaving the casino after strategizing.")
                break

            # Random probability of purchasing something in a bar
            if random.random() < 0.40:
               self.place_order()

            if random.random() < 0.6:
                # Random selection of the game
                game = random.choice(list(self.casino.games.keys()))
                print(f"Customer-{self.id} selected the game '{game}'")

                # Lock both available players and wait_list modification
                self.casino.games[game]['lock'].acquire()
                self.casino.customers_lock.acquire()
                self.casino.games[game]['wait_list'].append(self)
                self.casino.customers.remove(self)
                print(f"Customer-{self.id} is ready to play the game '{game}'")
                self.casino.customers_lock.release()
                self.casino.games[game]['lock'].release()

            time.sleep(random.randint(1, 5))
