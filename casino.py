# Standard library imports
import threading
import random
import time
import sqlite3
import os

# Game factories
from game_implementations import RouletteFactory, BlackJackFactory, CrapsFactory, SlotMachineFactory, PokerFactory

# Customer factories
from customer_factory import (
    GamblerFactory, OrderingAddictFactory, StrategistFactory, BudgetPlayerFactory, DrunkenGamblerFactory,
    AdventurerFactory, MinimalistFactory, RichPlayerFactory, RiskyCheatingFactory, RiskyPlayerFactory,
    ShopperFactory, SafePlayerFactory, TiredCustomerFactory, VipFactory
)

# Bar, parking, restaurant, and hotel modules
from bar import create_bars, Barista
from parking_lot import Parking
from restaurant import create_restaurants, Waiter
from hotel import Hotel


# Casino main class
class Casino:
    def __init__(self):
        # Initialize key components of the casino
        self.games = {}  # Dictionary to hold games by name
        self.bars = {}  # Dictionary to hold bars by name
        self.customers = []  # List of customers currently in casino
        self.customers_lock = threading.Lock()  # Lock for safe multi-threaded access to customers
        self.parking = Parking()  # Parking lot instance
        self.restaurants = []  # List of restaurants
        self.hotel = Hotel(10, casino=self)  # Hotel with 10 rooms
        self.db_path = os.path.join(os.path.dirname(__file__), "casino.db")  # Database file path

    def add_game(self, game):
        #Add a game to the casino if it's not already added
        if game.name not in self.games:
            self.games[game.name] = {'wait_list': [], 'lock': threading.Lock()}

    def add_bar(self, bar):
        #Add a bar to the casino
        self.bars[bar.name] = bar

    def add_restaurant(self, restaurant):
        # Add a restaurant to the casino
        self.restaurants.append(restaurant)

    def add_customer(self, customer):
        #Safely add a customer to the casino
        with self.customers_lock:
            self.customers.append(customer)

    def open_casino(self):
        #Set up and start the casino environment

        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        customers = []

        # Define customer creation factories and associated spawn weights
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

        # Generate initial batch of customers
        for i in range(1, total_customers_initial + 1):
            factory = random.choices(factory_choices, weights=weights, k=1)[0]
            customer = factory.create_customer(i)
            customers.append(customer)
            cursor.execute("""
                INSERT INTO customer (initial_balance, customer_type, has_car)
                VALUES (?, ?, ?)
            """, (customer.balance, customer.type, 1 if customer.car else 0))
            self.total_customers_generated += 1

        # Create and set up bars
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

        # Create and set up restaurants
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

        # Create and set up games
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

        # Insert created games into the database
        for game in games:
            cursor.execute("""
                INSERT INTO game_instance (game_name)
                VALUES (?)
            """, (game.name,))

        # Finalize and close database connection
        conn.commit()
        conn.close()

        # Set up waiters for restaurants
        waiters = []
        for restaurant in restaurants:
            for i in range(4):
                waiters.append(Waiter(i, restaurant))

        for restaurant in restaurants:
            self.add_restaurant(restaurant)

        # Set up baristas for bars
        baristas = []
        for bar in bars:
            for i in range(3):
                baristas.append(Barista(i, bar))

        for bar in bars:
            self.add_bar(bar)

        # Add all customers
        for customer in customers:
            self.add_customer(customer)

        # Start baristas
        for barista in baristas:
            barista.start()

        # Start waiters
        for waiter in waiters:
            waiter.start()

        # Add and start all games
        for game in games:
            self.add_game(game)
            game.start()

        # Start all customers
        for customer in customers:
            customer.start()

        # Start background thread for spawning new customers dynamically
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

            self.total_customers_generated += 1
            time.sleep(random.randint(*delay_range))

        conn.close()


if __name__ == "__main__":
    casino = Casino()
    casino.open_casino()

