import threading
import time
import random

class Customer(threading.Thread):
    def __init__(self, name,customer_id,table_number,restaurant):
        super().__init__(name=customer_id)
        self.name = name
        self.customer_id = customer_id
        self.table_number = table_number
        self.restaurant = restaurant

    def place_order(self):
        print(f"Customer {self.customer_id}  is ordering")
        self.restaurant.assign_waiter(self)

    def pay_bill(self):
        print(f"{self.customer_id} is paying their bill")

    def request_service(self):
        print(f"Customer {self.customer_id} is requesting service.")

    def run(self):
        self.place_order()
        time.sleep(random.randint(1, 4))
        self.pay_bill()
        self.request_service()

class Waiter:
    def __init__(self, waiter_id):
        self.waiter_id = waiter_id
        self.is_available = True

    def process_order(self, customer):
        self.is_available = False
        print(f"Waiter {self.waiter_id} is processing order for customer {customer.customer_id}.")
        time.sleep(random.randint(1, 4))
        print(f"Waiter {self.waiter_id} has completed the order for customer {customer.customer_id}.")
        self.is_available = True

class Restaurant:
    def __init__(self, num_waiters):
        self.customers = []
        self.waiters = [Waiter(waiter_id=i) for i in range(num_waiters)]
        self.customers_lock = threading.Lock()

    def seat_customer(self,customer):
        with self.customers_lock:
            self.customers.append(customer)
        print(f"Customer {customer.customer_id} is seated at table {customer.table_number}.")

    def assign_waiter(self,customer):
        available_waiter = None
        for waiter in self.waiters:
            if waiter.is_available:
                available_waiter = waiter
                break

        if available_waiter:
            available_waiter.process_order(customer)
        else:
            print(f"There arent any waiters for customer {customer.customer_id}. Give me a minute")

    def restaurant_open (self):
        for customer in self.customers:
            customer.start()

        for customer in self.customers:
            customer.join()

if __name__ == "__main__":
    restaurant = Restaurant(num_waiters=2)
    customers = [
        Customer(customer_id=1, name="Jose", table_number=1, restaurant=restaurant),
        Customer(customer_id=2, name="Manuel", table_number=2, restaurant=restaurant),
        Customer(customer_id=3, name="Majo", table_number=3, restaurant=restaurant),
        Customer(customer_id=4, name="Cesar", table_number=4, restaurant=restaurant)
    ]

    for customer in customers:
        restaurant.seat_customer(customer)

    restaurant.restaurant_open()
    print("Restaurant is closed.")