import threading
import random
import time

class Car:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.parked = False
        self.slot = None

    def enter(self):
        print(f"Customer-{self.customer_id} is entering the Parking")

    def exit(self):
        print(f"Customer-{self.customer_id} is exiting the Parking")

    def park(self, parking):
        self.enter()
        while True:
            random.shuffle(parking.list_slots)
            for slot in parking.list_slots:
                with slot.lock:
                    if slot.available():
                        slot.occupy(self)
                        return True

            if not self.slot:
                if random.choice([True, False]):
                    print(f"No slots currently available, customer {self.customer_id} decides to leave.")
                    return False
                print(f"No slots currently available, customer {self.customer_id} is waiting")

            time.sleep(2)

    def de_park(self):
        slot = self.slot
        if not slot:
            print(f"Customer-{self.customer_id} does not have a car parked")
        else:
            with slot.lock:
                slot.vacate(self)
            self.exit()


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
        self.list_slots = [ParkingSlot(id) for id in range(20)]






