import random
import threading
import time

# Define an item in the menu (drink, snack, etc.)
class Item:
    def __init__(self, name, price, prep_time):
        self.name = name
        self.price = price
        self.prep_time = prep_time #in seconds

# Represents a menu containing multiple items
class Menu:
    def __init__(self):
        self.products = [] # List to store all menu items

    def add_product(self, product: str, price: float, prep_time):
        self.products.append(Item(product, price, prep_time)) # Add a new item to the menu

# Represents a customer's order
class Order:
    def __init__(self, customer):
        self.status = 'waiting'       # Initial order status
        self.lock = threading.Lock()  # Lock to synchronize status updates
        self.items = []               # List of items in the order
        self.customer = customer      # Customer who placed the order

    def set_status(self, status):
        with self.lock: # update the order status using a lock
            self.status = status

    def add_item(self, item):
        self.items.append(item) # Add an item to the order

    def get_total(self):
        return sum(item.price for item in self.items) # Calculate the total price of the order

    def get_estimated_time(self):
        return sum(item.prep_time for item in self.items) # Calculate the total estimated preparation time for the order

# Represents a bar that can have multiple orders
class Bar:
    def __init__(self, menu, name):
        self.menu = menu               # The bar's menu
        self.orders = []               # List of current orders
        self.lock = threading.Lock()   # Lock to protect access to orders
        self.name = name               # Name of the bar


class Barista(threading.Thread):
    def __init__(self, id, bar):
        super().__init__()
        self.id = id  # Barista's ID
        self.bar = bar

    # Worker thread that processes orders in the bar# Worker thread that processes orders in the bar
    def run(self):
        while True:
            with self.bar.lock:
                if not self.bar.orders: # No orders to process, wait a bit
                    time.sleep(2)
                    continue
                order = self.bar.orders.pop(0) # Take the next order from the queue
                order.set_status("in_progress")
                print(f"Barista-{self.id} preparing order for customer-{order.customer.id} will take {order.get_estimated_time()} seconds")
            for item in order.items: # Take the next order from the queue
                time.sleep(item.prep_time)
            order.set_status("processed") # Order is done

            print(f"Barista-{self.id} done preparing order for customer-{order.customer.id}")


# Helper function to create multiple bars with pre-filled menus
def create_bars():
    drinks_menu = Menu() # drink menu
    drinks_menu.add_product("Beer", 5.00, random.randint(1,5))
    drinks_menu.add_product("Whiskey", 12.00, random.randint(1,5))
    drinks_menu.add_product("Martini", 15.00, random.randint(1,5))
    drinks_menu.add_product("Coke", 3.00, random.randint(1,5))

    snacks_menu = Menu()
    snacks_menu.add_product("Nachos", 8.00, random.randint(1,5))
    snacks_menu.add_product("French Fries", 6.00, random.randint(1,5))
    snacks_menu.add_product("Chicken Wings", 10.00, random.randint(1,5))
    snacks_menu.add_product("Peanuts", 4.00, random.randint(1,5))

    cocktails_menu = Menu()
    cocktails_menu.add_product("Old Fashioned", 18.00, random.randint(1,5))
    cocktails_menu.add_product("Mojito", 16.00, random.randint(1,5))
    cocktails_menu.add_product("Negroni", 20.00, random.randint(1,5))
    cocktails_menu.add_product("Margarita", 14.00, random.randint(1,5))


    drinks_bar = Bar(drinks_menu, "Drinks Bar")
    snacks_bar = Bar(snacks_menu, "Snacks Bar")
    cocktails_bar = Bar(cocktails_menu, "Cocktails Bar")

    return [drinks_bar, snacks_bar, cocktails_bar] # Return list of all bars