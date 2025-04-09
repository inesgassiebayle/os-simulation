import threading
import random
from game_implementations import Roulette, SlotMachine, BlackJack, Craps, Poker
from customer import TiredCustomer, RiskyPlayer, RichPlayer, CheatingPlayer, SafePlayer
from bar import create_bars, Barista
from parking_lot import Parking
from restaurant import create_restaurants, Waiter

class Casino:
    def __init__(self):
        self.games = {}
        self.bars = {}
        self.customers = []
        self.customers_lock = threading.Lock()
        self.parking = Parking()
        self.restaurants = []


    def add_game(self, game):
        if game.name not in self.games:
            self.games[game.name] = {'wait_list': [], 'lock': threading.Lock()}

    def add_bar(self, bar):
        self.bars[bar.name] = bar

    def add_restaurant(self, restaurant):
        self.restaurants.append(restaurant)

    def add_customer(self, customer):
        with self.customers_lock:
            self.customers.append(customer)

    def open_casino(self):
        games = ([Roulette(self, i) for i in range(5)]
                 + [SlotMachine(self, i) for i in range(10)]
                 + [BlackJack(self, i) for i in range(2)]
                 + [Craps(self, i) for i in range(7)]
                 + [Poker(self, i) for i in range(10)])
        customers = []
        customer_types = [TiredCustomer, RiskyPlayer, CheatingPlayer, RichPlayer, SafePlayer]

        for i in range(50):
            customer_type = random.choice(customer_types)
            customers.append(customer_type(i, self, random.randint(50, 200)))
            print(f"Customer-{i} is type {customer_type}")

        restaurants = create_restaurants(self)

        waiters = []

        for restaurant in restaurants:
            for i in range(5):
                waiters.append(Waiter(i, restaurant))

        for restaurant in restaurants:
            self.add_restaurant(restaurant)

        bars = create_bars()

        baristas = []

        for bar in bars:
            for i in range(5):
                baristas.append(Barista(i, bar))

        for bar in bars:
            self.add_bar(bar)

        for customer in customers:
            self.add_customer(customer)

        for barista in baristas:
            barista.start()

        for waiter in waiters:
            waiter.start()

        for game in games:
            game.start()

        for customer in customers:
            customer.start()


casino = Casino()
casino.open_casino()
