import threading
import random
import concurrent.futures
import time

class Car:
    def __init__(self, id):
        self.id = id
        self.parked = False

    def enter(self):
        print(f"Car {self.id} is entering the Parking")

    def exit(self):
        print(f"Car {self.id} is exiting the Parking")

class ParkingSlot:
    def __init__(self, id):
        self.id = id
        self.is_available = True
        self.lock = threading.Lock()

    def occupy(self, car):
        with self.lock:
            if self.is_available:
                print(f"Car {car.id} is occupying slot {self.id}")
                self.is_available = False
                car.parked = True
    def vacate(self, car):
        with self.lock:
            self.is_available = True
            print(f"Car {car.id} is vacating slot {self.id}")

    def available(self):
        with self.lock:
            return self.is_available


class Parking:
    def __init__(self):
        self.list_cars = [Car(id) for id in range(1,10)]
        self.list_slots = [ParkingSlot(id) for id in range(1,5)]

    def start_parking_process(self, car):
        car.enter()
        chosen_slot = None
        while True:
            try:
                random.shuffle(self.list_slots)
                for slot in self.list_slots:
                    if slot.available:
                        slot.occupy(car)
                        time.sleep(random.randrange(1,5))
                        slot.vacate(car)
                        car.exit()
                        break # here breaks from for loop

                if car.parked == False:
                    print(f"No slots currently available, car {car.id} is waiting")
                    time.sleep(3)
                else:
                    break # here breaks from while loop
            except Exception as e:
                print(f"Error occurred: {e}")

my_parking = Parking()

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for car in my_parking.list_cars:
        executor.submit(my_parking.start_parking_process, car)







