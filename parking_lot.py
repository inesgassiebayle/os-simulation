import threading
import random
import time
from db import save_parking_record, close_parking_record

class Car:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.parked = False
        self.slot = None
        self.parking_record_id = None

    def enter(self):
        print(f"Customer-{self.customer_id} is entering the Parking")

    def exit(self):
        print(f"Customer-{self.customer_id} is exiting the Parking")

    def park(self, parking):
        self.enter()
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            random.shuffle(parking.list_slots)
            for slot in parking.list_slots:
                with slot.lock:
                    if slot.available():
                        slot.occupy(self)
                        self.parking_record_id = save_parking_record(self.customer_id, slot.id)
                        return True

            attempts += 1
            print(
                f"No slots available (attempt {attempts}/{max_attempts}), customer {self.customer_id} keeps waiting...")
            time.sleep(random.randrange(1, 10))

        print(f"Customer {self.customer_id} gave up after {max_attempts} attempts.")
        return False

    def de_park(self):
        slot = self.slot
        if not slot:
            print(f"Customer-{self.customer_id} does not have a car parked")
        else:
            with slot.lock:
                slot.vacate(self)
            self.exit()

            if self.parking_record_id is not None:
                close_parking_record(self.parking_record_id)
                self.parking_record_id = None

class ParkingSlot:
    def __init__(self, id):
        self.id = id
        self.car = None
        self.lock = threading.Lock()

    def occupy(self, car):
      print(f"Customer-{car.customer_id} is occupying slot {self.id}")
      car.slot = self
      self.car = car

    def vacate(self, car):
        print(f"Customer-{car.customer_id} is vacating slot {self.id}")
        self.car = None
        car.slot = None

    def available(self):
        return self.car is None


class Parking:
    def __init__(self):
        self.list_cars = []
        self.list_slots = [ParkingSlot(id) for id in range(30)]






