import random
import threading
import time

class Item:
    def __init__(self, name, price, prep_time):
        self.name = name
        self.price = price
        self.prep_time = prep_time


class Menu:
    def __init__(self):
        self.products = []

    def add_product(self, product: str, price: float, prep_time):
        self.products.append(Item(product, price, prep_time))


class Order:
    def __init__(self, customer):
        self.status = 'waiting'
        self.lock = threading.Lock()
        self.items = []
        self.customer = customer

    def set_status(self, status):
        with self.lock:
            self.status = status

    def add_item(self, item):
        self.items.append(item)

    def get_total(self):
        return sum(item.price for item in self.items)

    def get_estimated_time(self):
        return sum(item.prep_time for item in self.items)


class Bar:
    def __init__(self, menu, name):
        self.menu = menu
        self.orders = []
        self.lock = threading.Lock()
        self.name = name


class Barista(threading.Thread):
    def __init__(self, id, bar):
        super().__init__()
        self.id = id
        self.bar = bar

    def run(self):
        while True:
            with self.bar.lock:
                if not self.bar.orders:
                    time.sleep(2)
                    continue
                order = self.bar.orders.pop(0)
                order.set_status("in_progress")
                print(f"Barista-{self.id} preparing order for customer-{order.customer.id} will take {order.get_estimated_time()} seconds")
            for item in order.items:
                time.sleep(item.prep_time)
            order.set_status("processed")
            print(f"Barista-{self.id} done preparing order for customer-{order.customer.id}")



def create_bars():
    drinks_menu = Menu()
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

    return [drinks_bar, snacks_bar, cocktails_bar]