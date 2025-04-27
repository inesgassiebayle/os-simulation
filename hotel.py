import threading
from db import save_booking

class Room:
    def __init__(self, room_number, casino):
        self.room_number = room_number
        self.customer = None
        self.lock = threading.Lock()
        self.casino = casino

    def book(self, customer, duration_seconds):
        with self.lock:
            if self.customer is None:
                self.customer = customer
                print(f"Customer-{customer.id} booked Room-{self.room_number} for {duration_seconds}")
                save_booking(self.room_number, customer, duration_seconds)
                with self.casino.customers_lock:
                    self.casino.customers.remove(customer)
                timer = threading.Timer(duration_seconds, self.de_book)
                timer.start()
                return True
            else:
                return False

    def de_book(self):
        with self.lock:
            if self.customer is None:
                print(f"The room {self.room_number} was not booked.")
            with self.casino.customers_lock:
                self.casino.customers.append(self.customer)
                print(f"The room {self.room_number} is now available emptied by customer-{self.customer.id}.")
            self.customer = None

class Hotel:
    def __init__(self, num_rooms, casino, price_per_second=3):
        self.rooms = [Room(i, casino) for i in range(num_rooms)]
        self.price_per_second = price_per_second
        self.casino = casino

    def book_room(self, customer, duration_seconds):
        for room in self.rooms:
            if room.book(customer, duration_seconds):
                return room
        print(f"Customer-{customer.id} could not find a free room.")
        customer.increment(duration_seconds*self.price_per_second)
        return None