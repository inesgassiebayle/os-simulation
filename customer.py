import threading
import random
from bar import Order
from abc import abstractmethod
from parking_lot import Car
from db import save_order, save_game_play, save_permanence_record, close_permanence_record, save_failed_parking
import time

# Base Customer class inheriting from threading.Thread to simulate concurrent customer behavior
class Customer(threading.Thread):
    def __init__(self, id, casino, balance, p_leaving, p_strategizing, p_ordering, p_playing, type, p_sleeping, min_bet, max_bet, has_car_probability, p_restaurant, game_preferences):
        super().__init__() # Initialize the thread with the parent class
        self.id = id # Customer's unique ID
        self.casino = casino # The casino where the customer is playing
        self.balance = balance  # The customer's balance
        self.lock = threading.Lock() # Lock to synchronize access to the customer's balance
        self.p_leaving = p_leaving # Probability of the customer leaving the casino
        self.p_strategizing = p_strategizing   # Probability of the customer strategizing when playing
        self.p_ordering = p_ordering   # Probability of the customer ordering food or drinks
        self.p_playing = p_playing # Probability of the customer playing a game
        self.p_sleeping = p_sleeping  # Probability of the customer sleeping
        self.min_bet = min_bet # Minimum bet the customer can make
        self.max_bet = max_bet # Maximum bet the customer can make
        self.car = Car(id) if random.random() < has_car_probability else None # Assign a car to the customer
        self.booked_room = None # The room the customer has booked, if any
        self.permanence_id = None  # ID for the customer's permanence record in the casino
        self.type = type
        self.p_restaurant = p_restaurant
        self.game_preferences = game_preferences

    def amount_bet(self):
        # Returns a random amount the customer is willing to bet based on their balance and bet limits
        return random.randint(min(self.min_bet, self.get_balance()) , min(self.max_bet, self.get_balance()))

    def increment(self, amount):
        # Increase the customer's balance by the specified amount (if they win)
        with self.lock:
            self.balance += amount
        print(f"Customer-{self.id} won ${amount}. (Balance: ${self.balance}).")

    def decrease(self, amount):
        # Decrease the customer's balance by the specified amount (if they lose)
        with self.lock:
            if amount > self.balance:
                print(f"Customer-{self.id} does not have ${amount} to spend.")
                return False
            self.balance -= amount
            print(f"Customer-{self.id} has spent ${amount}. (Balance: ${self.balance}).")
            return True

    def get_balance(self):
        # Return the customer's current balance
        with self.lock:
            return self.balance

    def choose_game(self):
        # Choose a game based on the customer's game preferences (probabilities)
        games = list(self.game_preferences.keys())
        probs = list(self.game_preferences.values())
        selected_game = random.choices(games, weights=probs, k=1)[0]
        return selected_game

    def play(self, name, probability, prize, game_id):
        # Simulate playing game
        print(f"Customer-{self.id} playing {name}")
        amount = self.amount_bet()
        if not self.decrease(amount):
            self.casino.add_customer(self)
            return
        if random.random() < probability:
            # If the customer wins, increase their balance by the prize
            self.increment(amount * prize)
            save_game_play(self.id, game_id, amount, "won")
        else:
            # If the customer loses, save the loss
            print(f"Customer-{self.id} lost ${amount}. (Balance: ${self.balance})")
            save_game_play(self.id, game_id, amount, "lost")
        self.casino.add_customer(self)
        time.sleep(random.randint(1, 5))

    def place_order(self):
        # Simulate the customer placing an order at the bar
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
        # Simulate the customer placing an order at the restaurant
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
        # Simulate the customer entering a restaurant and ordering food
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
        # The main simulation logic for the customer
        # Perform the customer's action (e.g., play, order)
        if self.car:
            # If the customer has a car, attempt to park it in the casino's parking lot
            parked = self.car.park(self.casino.parking)
            if not parked:
                # If the car could not be parked, the customer decides to leave the casino
                print(f"Customer-{self.id} could not park the car and decided to leave")
                save_failed_parking(self.id) # Save the failed parking attempt
                return
        else:
            # If the customer does not have a car, save the customer's permanence record
            self.permanence_id = save_permanence_record(self.id)

        while True:
            # Lock the list of customers to check if the customer is still in the casino
            with self.casino.customers_lock:
                if self not in self.casino.customers:
                    # If the customer is no longer in the casino, wait before checking again
                    time.sleep(random.randint(1, 5))
                    continue  # Check again after the sleep

            # If the customer has no balance, they leave the casino
            if self.balance <= 0:
                print(f"Customer-{self.id} is out of money and leaves the casino.")
                break  # Exit the loop (customer leaves)

            # Random chance for the customer to leave the casino
            if random.random() < self.p_leaving:  # 20% chance to leave
                print(f"Customer-{self.id} has decided to leave the casino.")
                break  # Exit the loop (customer leaves)

            # Random chance for the customer to leave the casino strategically (after thinking)
            if random.random() < self.p_strategizing:  # 10% chance to leave strategically
                print(f"Customer-{self.id} is leaving the casino after strategizing.")
                break  # Exit the loop (customer leaves)

            # Random chance for the customer to play a game
            if random.random() < self.p_playing:
                game = self.choose_game()  # Select a game based on preferences
                print(f"Customer-{self.id} selected the game '{game}'")
                self.casino.games[game]['lock'].acquire()  # Lock the game to avoid conflicts
                self.casino.customers_lock.acquire()  # Lock the customers list to remove the customer
                self.casino.games[game]['wait_list'].append(self)  # Add customer to game wait list
                self.casino.customers.remove(self)  # Remove the customer from the casino
                print(f"Customer-{self.id} is ready to play the game '{game}'")
                self.casino.customers_lock.release()  # Release the customers list lock
                self.casino.games[game]['lock'].release()  # Release the game lock
                continue  # Proceed to the next iteration (customer is now playing)

            # Random chance for the customer to place an order (food/drinks)
            if random.random() < self.p_ordering:
                self.place_order()  # Place an order for food or drinks
                continue  # Proceed to the next iteration

            # Random chance for the customer to sleep (if they don't have a booked room yet)
            if random.random() < self.p_sleeping and self.booked_room is None:
                sleep_duration = random.randint(1, 50)  # Random sleep duration between 1 and 50 seconds
                price = sleep_duration * self.casino.hotel.price_per_second  # Calculate cost of sleep

                # Check if the customer has enough balance to pay for the sleep
                with self.lock:
                    if price > self.balance:
                        print(
                            f"Customer-{self.id} does not have enough money to book the hotel for {sleep_duration} seconds.")
                        continue  # Skip to the next iteration if not enough money

                # Deduct the cost of the sleep and book the room for the customer
                print(f"Customer-{self.id} will book hotel for {sleep_duration} seconds")
                self.decrease(price)  # Deduct the cost of the sleep
                self.booked_room = self.casino.hotel.book_room(self, sleep_duration)  # Book the room
                continue  # Proceed to the next iteration

            # Random chance for the customer to enter a restaurant and place orders
            if random.random() < self.p_restaurant:
                self.enter_restaurant()  # Enter a restaurant and place orders
                continue  # Proceed to the next iteration

            # Sleep for a random time between 1 and 5 seconds before checking again
            time.sleep(random.randint(1, 5))

            # After the customer leaves the casino, if they have a car, they un-park it
        if self.car and self.car.slot is not None:
            self.car.de_park()  # De-park the car if it's parked

            # If the customer doesn't have a car and has a permanence ID, close the permanence record
        if not self.car and self.permanence_id is not None:
            close_permanence_record(self.permanence_id)  # Close the customer's permanence record





