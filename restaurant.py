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


class Restaurant:
    def __init__(self, menu, name, num_tables, casino):
        self.menu = menu
        self.orders = []
        self.lock = threading.Lock()
        self.name = name
        self.num_tables = num_tables
        self.customers = 0
        self.casino = casino

    def seat_customer(self, customer):
        self.lock.acquire()
        if self.customers == self.num_tables:
            print(f"Customer-{customer.id} was not seated at {self.name}.")
            self.lock.release()
            return False
        self.casino.customers_lock.acquire()
        self.casino.customers.remove(customer)
        self.customers += 1
        print(f"Customer-{customer.id} was seated at {self.name}.")
        self.casino.customers_lock.release()
        self.lock.release()
        return True

    def de_seat_customer(self, customer):
        self.lock.acquire()
        self.casino.customers_lock.acquire()
        self.customers -= 1
        self.casino.customers.append(customer)
        print(f"Customer-{customer.id} left {self.name}.")
        self.casino.customers_lock.release()
        self.lock.release()

class Waiter(threading.Thread):
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
                print(f"Waiter-{self.id} preparing order for customer-{order.customer.id} will take {order.get_estimated_time()} seconds")
            for item in order.items:
                time.sleep(item.prep_time)
            order.set_status("processed")
            print(f"Waiter-{self.id} done preparing order for customer-{order.customer.id}")


def create_restaurants(casino):
    menu1 = Menu()
    menu1.add_product("Burger", 5.99, 2)
    menu1.add_product("Fries", 2.99, 1)
    menu1.add_product("Soda", 1.50, 1)

    menu2 = Menu()
    menu2.add_product("Pizza", 8.99, 4)
    menu2.add_product("Salad", 4.99, 2)
    menu2.add_product("Water", 0.00, 0)

    restaurant1 = Restaurant(menu1, "FastBurger", num_tables=10, casino=casino)
    restaurant2 = Restaurant(menu2, "PizzaPlace", num_tables=10, casino=casino)

    return [restaurant1, restaurant2]


