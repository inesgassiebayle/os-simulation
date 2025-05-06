import random
import threading
import time
import threading
import time

# Item class represents a single menu item (food or drink)
class Item:
    def __init__(self, name, price, prep_time):
        # Initialize the item with its name, price, and preparation time
        self.name = name
        self.price = price
        self.prep_time = prep_time  # Time it takes to prepare the item in seconds

# Menu class represents a collection of items available in a restaurant
class Menu:
    def __init__(self):
        # Initialize the menu with an empty list of products (items)
        self.products = []

    def add_product(self, product: str, price: float, prep_time):
        # Add a new product (item) to the menu
        self.products.append(Item(product, price, prep_time))

# Order class represents an order placed by a customer
class Order:
    def __init__(self, customer):
        # Initialize the order with a 'waiting' status and an empty list of items
        self.status = 'waiting'
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to order status
        self.items = []  # List of items in the order
        self.customer = customer  # The customer who placed the order

    def set_status(self, status):
        # Change the status of the order (e.g., waiting, in progress, processed)
        with self.lock:
            self.status = status

    def add_item(self, item):
        # Add an item to the order
        self.items.append(item)

    def get_total(self):
        # Calculate the total price of all items in the order
        return sum(item.price for item in self.items)

    def get_estimated_time(self):
        # Calculate the total estimated preparation time for all items in the order
        return sum(item.prep_time for item in self.items)

# Restaurant class represents a restaurant in the casino with a menu, tables, and customers
class Restaurant:
    def __init__(self, menu, name, num_tables, casino):
        # Initialize the restaurant with its menu, name, number of tables, and reference to the casino
        self.menu = menu
        self.orders = []  # List to store orders placed at the restaurant
        self.lock = threading.Lock()  # Lock to ensure thread-safety for seating customers
        self.name = name  # The name of the restaurant
        self.num_tables = num_tables  # Number of tables in the restaurant
        self.customers = 0  # Number of customers currently seated at the restaurant
        self.casino = casino  # Reference to the casino

    def seat_customer(self, customer):
        # Attempt to seat a customer at the restaurant
        self.lock.acquire()
        if self.customers == self.num_tables:
            # If no tables are available, print a message and return False
            print(f"Customer-{customer.id} was not seated at {self.name}.")
            self.lock.release()
            return False
        # If a table is available, seat the customer
        self.casino.customers_lock.acquire()
        self.casino.customers.remove(customer)  # Remove the customer from the casino's available customers list
        self.customers += 1  # Increment the number of customers seated
        print(f"Customer-{customer.id} was seated at {self.name}.")
        self.casino.customers_lock.release()
        self.lock.release()
        return True

    def de_seat_customer(self, customer):
        # Remove a customer from the restaurant and free up their table
        self.lock.acquire()
        self.casino.customers_lock.acquire()
        self.customers -= 1  # Decrease the number of seated customers
        self.casino.customers.append(customer)  # Add the customer back to the casino's list of available customers
        print(f"Customer-{customer.id} left {self.name}.")
        self.casino.customers_lock.release()
        self.lock.release()

# Waiter class represents a waiter working in the restaurant, serving orders
class Waiter(threading.Thread):
    def __init__(self, id, bar):
        super().__init__()
        self.id = id  # The unique identifier for the waiter
        self.bar = bar  # Reference to the bar (or restaurant) where the waiter works

    def run(self):
        # The main thread that keeps processing orders
        while True:
            with self.bar.lock:
                if not self.bar.orders:
                    # If there are no orders, wait for a moment before checking again
                    time.sleep(2)
                    continue
                order = self.bar.orders.pop(0)  # Get the first order from the queue
                order.set_status("in_progress")  # Set the order status to 'in progress'
                print(f"Waiter-{self.id} preparing order for customer-{order.customer.id} will take {order.get_estimated_time()} seconds")

            # Simulate preparing each item in the order
            for item in order.items:
                time.sleep(item.prep_time)

            order.set_status("processed")  # Mark the order as processed once it's completed
            print(f"Waiter-{self.id} done preparing order for customer-{order.customer.id}")

# Function to create multiple restaurants with predefined menus
def create_restaurants(casino):
    # Create menus for two restaurants
    menu1 = Menu()
    menu1.add_product("Burger", 5.99, 2)
    menu1.add_product("Fries", 2.99, 1)
    menu1.add_product("Soda", 1.50, 1)

    menu2 = Menu()
    menu2.add_product("Pizza", 8.99, 4)
    menu2.add_product("Salad", 4.99, 2)
    menu2.add_product("Water", 0.00, 0)

    # Create two restaurants with the menus
    restaurant1 = Restaurant(menu1, "FastBurger", num_tables=10, casino=casino)
    restaurant2 = Restaurant(menu2, "PizzaPlace", num_tables=10, casino=casino)

    # Return the list of created restaurants
    return [restaurant1, restaurant2]



