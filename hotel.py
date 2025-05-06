import threading
from db import save_booking
import threading
import time

# Room class represents a hotel room in the casino
class Room:
    def __init__(self, room_number, casino):
        # Initialize the room with a unique room number and casino reference
        self.room_number = room_number
        self.customer = None  # Initially, no customer is assigned to the room
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to room status
        self.casino = casino  # Reference to the casino

    def book(self, customer, duration_seconds):
        # Attempt to book the room for a customer
        with self.lock:  # Ensure thread-safety while checking and assigning the room
            if self.customer is None:
                # If the room is not already booked, assign it to the customer
                self.customer = customer
                print(f"Customer-{customer.id} booked Room-{self.room_number} for {duration_seconds} seconds.")
                save_booking(self.room_number, customer, duration_seconds)  # Save the booking in the database
                with self.casino.customers_lock:
                    # Remove the customer from the casino's available customer list
                    self.casino.customers.remove(customer)
                # Set a timer to de-book the room after the specified duration
                timer = threading.Timer(duration_seconds, self.de_book)
                timer.start()
                return True
            else:
                # If the room is already booked, return False
                return False

    def de_book(self):
        # De-book the room when the booking duration expires
        with self.lock:  # Ensure thread-safety while de-booking
            if self.customer is None:
                print(f"The room {self.room_number} was not booked.")
            else:
                with self.casino.customers_lock:
                    # Re-add the customer to the casino's list of available customers
                    self.casino.customers.append(self.customer)
                    print(f"The room {self.room_number} is now available, emptied by customer-{self.customer.id}.")
                self.customer = None  # Room is now available, so set customer to None

# Hotel class represents the hotel within the casino, managing multiple rooms
class Hotel:
    def __init__(self, num_rooms, casino, price_per_second=3):
        # Initialize the hotel with a set number of rooms, the casino reference, and a price per second for bookings
        self.rooms = [Room(i, casino) for i in range(num_rooms)]  # Create a list of rooms in the hotel
        self.price_per_second = price_per_second  # Price per second for booking a room
        self.casino = casino  # Reference to the casino

    def book_room(self, customer, duration_seconds):
        # Attempt to book a room for the customer
        for room in self.rooms:
            # Try to book each room until a free one is found
            if room.book(customer, duration_seconds):
                return room  # Return the room that was successfully booked
        print(f"Customer-{customer.id} could not find a free room.")  # If no room is available
        customer.increment(duration_seconds * self.price_per_second)  # Refund the customer if no room is available
        return None  # Return None if no room could be booked
