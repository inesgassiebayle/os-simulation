import threading
import random
from game_implementations import RouletteFactory, BlackJackFactory, CrapsFactory, SlotMachineFactory, PokerFactory
from customer_factory import GamblerFactory, OrderingAddictFactory, StrategistFactory, BudgetPlayerFactory, DrunkenGamblerFactory, AdventurerFactory, MinimalistFactory, RichPlayerFactory, RiskyCheatingFactory, RiskyPlayerFactory, ShopperFactory, SafePlayerFactory, TiredCustomerFactory, VipFactory
from bar import create_bars, Barista
from parking_lot import Parking
from restaurant import create_restaurants, Waiter
from hotel import Hotel
import sqlite3
import os

class Casino:
    def __init__(self):
        self.games = {}
        self.bars = {}
        self.customers = []
        self.customers_lock = threading.Lock()
        self.parking = Parking()
        self.restaurants = []
        self.hotel = Hotel(10, casino=self)

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
        db_path = os.path.join(os.path.dirname(__file__), "casino.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        customers = []
        factories = [GamblerFactory(self), OrderingAddictFactory(self), StrategistFactory(self), BudgetPlayerFactory(self), DrunkenGamblerFactory(self), AdventurerFactory(self), MinimalistFactory(self), RichPlayerFactory(self), RiskyCheatingFactory(self), RiskyPlayerFactory(self), ShopperFactory(self), SafePlayerFactory(self), TiredCustomerFactory(self), VipFactory(self)]

        # Crear customers
        for i in range(50):
            factory = random.choice(factories)
            customer = factory.create_customer(i)
            customers.append(customer)
            cursor.execute("""
                INSERT INTO customer (initial_balance, customer_type, has_car)
                VALUES (?, ?, ?)
            """, (customer.balance, customer.type, 1 if customer.car else 0))


        bars = create_bars()
        bar_id_map = {}
        for bar in bars:
            cursor.execute("""
                INSERT INTO bar (name) VALUES (?)
            """, (bar.name,))
            bar_id = cursor.lastrowid
            bar_id_map[bar.name] = bar_id
            for item in bar.menu.products:
                cursor.execute("""
                    INSERT INTO menu_item (name, price, prep_time, source_type, source_id)
                    VALUES (?, ?, ?, 'bar', ?)
                """, (item.name, item.price, item.prep_time, bar_id))

        restaurants = create_restaurants(self)
        restaurant_id_map = {}
        for restaurant in restaurants:
            cursor.execute("""
                INSERT INTO restaurant (name, num_tables) VALUES (?, ?)
            """, (restaurant.name, restaurant.num_tables))
            restaurant_id = cursor.lastrowid
            restaurant_id_map[restaurant.name] = restaurant_id
            for item in restaurant.menu.products:
                cursor.execute("""
                    INSERT INTO menu_item (name, price, prep_time, source_type, source_id)
                    VALUES (?, ?, ?, 'restaurant', ?)
                """, (item.name, item.price, item.prep_time, restaurant_id))

        n_games = 0
        games = []
        for _ in range(5):
            games.append(RouletteFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(10):
            games.append(SlotMachineFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(2):
            games.append(BlackJackFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(7):
            games.append(CrapsFactory(self).create_game(n_games))
            n_games += 1
        for _ in range(10):
            games.append(PokerFactory(self).create_game(n_games))
            n_games +=1

        for game in games:
            cursor.execute("""
                INSERT INTO game_instance (game_name)
                VALUES (?)
            """, (game.name,))

        conn.commit()
        conn.close()

        waiters = []
        for restaurant in restaurants:
            for i in range(5):
                waiters.append(Waiter(i, restaurant))

        for restaurant in restaurants:
            self.add_restaurant(restaurant)

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
            self.add_game(game)

        for game in games:
            game.start()

        for customer in customers:
            customer.start()

if __name__ == "__main__":
    casino = Casino()
    casino.open_casino()
