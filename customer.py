import threading
import random
from bar import Order
from abc import abstractmethod
from parking_lot import Car
from db import save_order, save_game_play, save_permanence_record, close_permanence_record, save_failed_parking
import time

class Customer(threading.Thread):
    def __init__(self, id, casino, balance, p_leaving, p_strategizing, p_ordering, p_playing, p_sleeping=0.5):
        super().__init__()
        self.id = id
        self.casino = casino
        self.balance = balance
        self.lock = threading.Lock()
        self.p_leaving = p_leaving
        self.p_strategizing = p_strategizing
        self.p_ordering = p_ordering
        self.p_playing = p_playing
        self.car = random.choice([None, Car(id)])
        self.p_sleeping = p_sleeping
        self.booked_room = None
        self.permanence_id = None

    @abstractmethod
    def amount_bet(self):
        pass

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

    def play(self, name, probability, prize, game_id):
        print(f"Customer-{self.id} playing {name}")
        amount = self.amount_bet()
        if not self.decrease(amount):
            self.casino.add_customer(self)
            return
        if random.random() < probability:
            self.increment(amount * prize)
            save_game_play(self.id, game_id, amount, "won")
        else:
            print(f"Customer-{self.id} lost ${amount}. (Balance: ${self.balance})")
            save_game_play(self.id, game_id, amount, "lost")
        self.casino.add_customer(self)
        time.sleep(random.randint(1, 5))

    def place_order(self):
        bar_name = random.choice(list(self.casino.bars.keys()))
        print(f"Customer-{self.id} will place order in bar {bar_name}")
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
        print(
            f"Customer-{self.id} ordered {[item.name for item in order.items]} (Total: ${order.get_total()}, Balance: ${self.balance})")
        save_order(self.id, 'bar', list(self.casino.bars.keys()).index(bar_name) + 1, order)

    def place_restaurant_order(self, restaurant, total):
        order = Order(self)
        num_items = random.randint(1, 7)
        items = random.choices(restaurant.menu.products, k=num_items)
        for item in items:
            order.add_item(item)
        with self.lock:
            if order.get_total() + total > self.balance:
                print(f"Customer-{self.id} could not place order of ${order.get_total()}. (Balance: ${self.balance})")
                return 0
        with restaurant.lock:
            restaurant.orders.append(order)
        print(
            f"Customer-{self.id} ordered {[item.name for item in order.items]} (Total: ${order.get_total()}, Balance: ${self.balance - total - order.get_total()})")
        save_order(self.id, 'restaurant', list(self.casino.restaurants).index(restaurant) + 1, order)
        return order.get_total()

    def enter_restaurant(self):
        restaurant = random.choice(list(self.casino.restaurants))
        print(f"Customer-{self.id} is trying to seat at {restaurant.name}")
        seated = restaurant.seat_customer(self)
        if seated:
            total_payed = 0
            while True:
                if random.random() < self.p_ordering:
                    amount = self.place_restaurant_order(restaurant, total_payed)
                    total_payed += amount
                else:
                    break
                time.sleep(random.randint(1, 10))
            self.decrease(total_payed)
            restaurant.de_seat_customer(self)

    def run(self):
        if self.car:
            parked = self.car.park(self.casino.parking)
            if not parked:
                print(f"Customer-{self.id} could not park the car and decided to leave")
                save_failed_parking(self.id)
                return
        else:
            self.permanence_id = save_permanence_record(self.id)

        while True:
            with self.casino.customers_lock:
                if self not in self.casino.customers:
                    time.sleep(random.randint(1, 5))
                    continue

            if self.balance <= 0:
                print(f"Customer-{self.id} is out of money and leaves the casino.")
                break

            if random.random() < self.p_leaving:  # 20% chance to leave
                print(f"Customer-{self.id} has decided to leave the casino.")
                break

            if random.random() < self.p_strategizing:  # 10% chance to leave strategically
                print(f"Customer-{self.id} is leaving the casino after strategizing.")
                break

            if random.random() < self.p_playing:
                game = random.choice(list(self.casino.games.keys()))
                print(f"Customer-{self.id} selected the game '{game}'")
                self.casino.games[game]['lock'].acquire()
                self.casino.customers_lock.acquire()
                self.casino.games[game]['wait_list'].append(self)
                self.casino.customers.remove(self)
                print(f"Customer-{self.id} is ready to play the game '{game}'")
                self.casino.customers_lock.release()
                self.casino.games[game]['lock'].release()
                continue

            if random.random() < self.p_ordering:
                self.place_order()
                continue

            if random.random() < self.p_sleeping and self.booked_room is None:
                sleep_duration = random.randint(1, 50)
                price = sleep_duration * self.casino.hotel.price_per_second
                with self.lock:
                    if price > self.balance:
                        print(f"Customer-{self.id} does not have enough money to book the hotel for {sleep_duration} seconds.")
                print(f"Customer-{self.id} will book hotel for {sleep_duration} seconds")
                self.decrease(price)
                self.booked_room = self.casino.hotel.book_room(self, sleep_duration)
                continue

            if random.random() < self.p_ordering:
                self.enter_restaurant()
                continue

            time.sleep(random.randint(1, 5))

        if self.car and self.car.slot is not None:
            self.car.de_park()

        if not self.car and self.permanence_id is not None:
            close_permanence_record(self.permanence_id)


class TiredCustomer(Customer):
    def __init__(self, id, casino, balance):
        super().__init__(id, casino, balance, 0.8, 0, 0.5, 0.3)

    def amount_bet(self):
        return random.randint(1, round(self.get_balance()/2))


class RiskyPlayer(Customer):
    def __init__(self, id, casino, balance):
        super().__init__(id, casino, balance, 0.1, 0, 0.5, 0.9)
    def amount_bet(self):
        return random.randint(1, round(self.get_balance()))


class CheatingPlayer(Customer):
    def __init__(self, id, casino, balance):
        super().__init__(id, casino, balance, 0.1, 0.8, 0.5, 0.9)
    def amount_bet(self):
        return random.randint(1, round(self.get_balance()/2))


class RichPlayer(Customer):
    def __init__(self, id, casino, balance):
        super().__init__(id, casino, balance * 3, 0.1, 0.3, 0.9, 0.9)
    def amount_bet(self):
        return random.randint(1, round(self.get_balance()))


class SafePlayer(Customer):
    def __init__(self, id, casino, balance):
        super().__init__(id, casino, balance, 0.4, 0, 0.2, 0.5)
    def amount_bet(self):
        return random.randint(1, round(self.get_balance()/2))