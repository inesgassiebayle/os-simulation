import threading
import random
import time
from db import save_parking_record, close_parking_record
import threading
import time
import random

# Car class represents a customer's car in the casino parking lot
class Car:
    def __init__(self, customer_id):
        # Initialize the car with a unique customer ID
        self.customer_id = customer_id
        self.parked = False  # Initially, the car is not parked
        self.slot = None  # The car is not parked in any slot
        self.parking_record_id = None  # No parking record exists initially

    def enter(self):
        # Simulate the car entering the parking lot
        print(f"Customer-{self.customer_id} is entering the Parking")

    def exit(self):
        # Simulate the car exiting the parking lot
        print(f"Customer-{self.customer_id} is exiting the Parking")

    def park(self, parking):
        # Attempt to park the car in the parking lot
        self.enter()
        attempts = 0
        max_attempts = 3  # Maximum number of attempts to find an available parking slot

        while attempts < max_attempts:
            random.shuffle(parking.list_slots)  # Shuffle the list of slots randomly for each attempt
            for slot in parking.list_slots:
                with slot.lock:  # Lock the parking slot to ensure thread safety
                    if slot.available():  # Check if the slot is available
                        slot.occupy(self)  # Occupy the slot with the car
                        self.parking_record_id = save_parking_record(self.customer_id, slot.id)  # Save the parking record
                        return True  # Successfully parked the car

            attempts += 1  # Increment the attempt counter if no slot was available
            print(
                f"No slots available (attempt {attempts}/{max_attempts}), customer {self.customer_id} keeps waiting...")
            time.sleep(random.randrange(1, 10))  # Wait for a random time before trying again

        print(f"Customer {self.customer_id} gave up after {max_attempts} attempts.")  # Failed to park after max attempts
        return False  # Return False if the car could not be parked

    def de_park(self):
        # Attempt to de-park the car and vacate the parking slot
        slot = self.slot
        if not slot:
            print(f"Customer-{self.customer_id} does not have a car parked")  # No car is parked
        else:
            with slot.lock:  # Lock the slot to ensure thread safety while vacating
                slot.vacate(self)  # Vacate the parking slot
            self.exit()  # Simulate the car exiting the parking lot

            # Close the parking record if it exists
            if self.parking_record_id is not None:
                close_parking_record(self.parking_record_id)  # Close the parking record
                self.parking_record_id = None  # Reset the parking record ID

# ParkingSlot class represents an individual parking slot in the parking lot
class ParkingSlot:
    def __init__(self, id):
        # Initialize the parking slot with a unique ID
        self.id = id
        self.car = None  # No car is occupying the slot initially
        self.lock = threading.Lock()  # Lock to ensure thread-safe access to the slot

    def occupy(self, car):
        # Occupy the parking slot with a car
        print(f"Customer-{car.customer_id} is occupying slot {self.id}")
        car.slot = self  # Set the car's slot to this one
        self.car = car  # Set this slot's car to the given car

    def vacate(self, car):
        # Vacate the parking slot when the car exits
        print(f"Customer-{car.customer_id} is vacating slot {self.id}")
        self.car = None  # No car in the slot now
        car.slot = None  # The car is no longer assigned to this slot

    def available(self):
        # Check if the slot is available (i.e., no car is parked in it)
        return self.car is None

# Parking class represents the parking lot of the casino
class Parking:
    def __init__(self):
        # Initialize the parking lot with a list of cars and slots
        self.list_cars = []  # List to store all cars in the parking lot
        self.list_slots = [ParkingSlot(id) for id in range(30)]  # Create 30 parking slots (you can change this number)







