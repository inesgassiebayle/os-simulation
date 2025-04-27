import threading
import random
import time
import sqlite3
import os

from game_implementations import RouletteFactory, BlackJackFactory, CrapsFactory, SlotMachineFactory, PokerFactory
from customer_factory import (
    GamblerFactory, OrderingAddictFactory, StrategistFactory, BudgetPlayerFactory, DrunkenGamblerFactory,
    AdventurerFactory, MinimalistFactory, RichPlayerFactory, RiskyCheatingFactory, RiskyPlayerFactory,
    ShopperFactory, SafePlayerFactory, TiredCustomerFactory, VipFactory
)
from bar import create_bars, Barista
from parking_lot import Parking
from restaurant import create_restaurants, Waiter
from hotel import Hotel

class Casino:
    def __init__(self):
        self.games = {}
        self.bars = {}
        self.customers = []
        self.customers_lock = threading.Lock()
        self.parking = Parking()
        self.restaurants = []
        self.hotel = Hotel(10, casino=self)
        self.db_path = os.path.join(os.path.dirname(__file__), "casino.db")

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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        customers = []
        factories_with_weights = [
            (GamblerFactory(self), 20),
            (DrunkenGamblerFactory(self), 10),
            (BudgetPlayerFactory(self), 15),
            (ShopperFactory(self), 10),
            (StrategistFactory(self), 5),
            (OrderingAddictFactory(self), 5),
            (AdventurerFactory(self), 5),
            (MinimalistFactory(self), 5),
            (VipFactory(self), 5),
            (RichPlayerFactory(self), 5),
            (SafePlayerFactory(self), 5),
            (RiskyPlayerFactory(self), 3),
            (RiskyCheatingFactory(self), 1),
            (TiredCustomerFactory(self), 1),
        ]
        total_customers_initial = 80
        self.total_customers_generated = 0

        factory_choices, weights = zip(*factories_with_weights)

        for i in range(1, total_customers_initial+1):
            factory = random.choices(factory_choices, weights=weights, k=1)[0]
            customer = factory.create_customer(i)
            customers.append(customer)
            cursor.execute("""
                INSERT INTO customer (initial_balance, customer_type, has_car)
                VALUES (?, ?, ?)
            """, (customer.balance, customer.type, 1 if customer.car else 0))
            self.total_customers_generated += 1

        bars = create_bars()[:3]
        for bar in bars:
            cursor.execute("""
                INSERT INTO bar (name) VALUES (?)
            """, (bar.name,))
            bar_id = cursor.lastrowid
            for item in bar.menu.products:
                cursor.execute("""
                    INSERT INTO menu_item (name, price, prep_time, source_type, source_id)
                    VALUES (?, ?, ?, 'bar', ?)
                """, (item.name, item.price, item.prep_time, bar_id))

        restaurants = create_restaurants(self)[:2]
        for restaurant in restaurants:
            cursor.execute("""
                INSERT INTO restaurant (name, num_tables) VALUES (?, ?)
            """, (restaurant.name, restaurant.num_tables))
            restaurant_id = cursor.lastrowid
            for item in restaurant.menu.products:
                cursor.execute("""
                    INSERT INTO menu_item (name, price, prep_time, source_type, source_id)
                    VALUES (?, ?, ?, 'restaurant', ?)
                """, (item.name, item.price, item.prep_time, restaurant_id))

        n_games = 0
        games = []
        for _ in range(4):
            games.append(RouletteFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(25):
            games.append(SlotMachineFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(6):
            games.append(BlackJackFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(3):
            games.append(CrapsFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(5):
            games.append(PokerFactory(self).create_game(n_games))
            n_games += 1

        for game in games:
            cursor.execute("""
                INSERT INTO game_instance (game_name)
                VALUES (?)
            """, (game.name,))

        conn.commit()
        conn.close()

        waiters = []
        for restaurant in restaurants:
            for i in range(4):
                waiters.append(Waiter(i, restaurant))

        for restaurant in restaurants:
            self.add_restaurant(restaurant)

        baristas = []
        for bar in bars:
            for i in range(3):
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
            self.add_game(game)
            game.start()

        for customer in customers:
            customer.start()

        threading.Thread(target=self.spawn_customers_dynamically, args=(factory_choices, weights)).start()

    def spawn_customers_dynamically(self, factory_choices, weights, delay_range=(5, 15), max_customers=300):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        while self.total_customers_generated < max_customers:
            customer_id = self.total_customers_generated + 1
            factory = random.choices(factory_choices, weights=weights, k=1)[0]
            customer = factory.create_customer(customer_id)
            print(f"New Customer-{customer_id} ({customer.type}) arrived at the casino.")
            self.add_customer(customer)
            customer.start()

            cursor.execute("""
                INSERT INTO customer (initial_balance, customer_type, has_car)
                VALUES (?, ?, ?)
            """, (customer.balance, customer.type, 1 if customer.car else 0))
            conn.commit()

            self.total_customers_generated += 1  # move to next id
            time.sleep(random.randint(*delay_range))

        conn.close()


if __name__ == "__main__":
    casino = Casino()
    casino.open_casino()
