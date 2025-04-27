import random
from parking_lot import Car
from customer import Customer
from abc import ABC, abstractmethod


customer_profiles = {
    "gambler": {
        "p_leaving": 0.1,
        "p_strategizing": 0.05,
        "p_ordering": 0.2,
        "p_playing": 0.8,
        "p_sleeping": 0.1,
        "has_car": True,
        "min_bet": 50,
        "max_bet": 200
    },
    "strategist": {
        "p_leaving": 0.1,
        "p_strategizing": 0.3,
        "p_ordering": 0.2,
        "p_playing": 0.4,
        "p_sleeping": 0.1,
        "has_car": False,
        "min_bet": 10,
        "max_bet": 50
    },
    "shopper": {
        "p_leaving": 0.2,
        "p_strategizing": 0.05,
        "p_ordering": 0.8,
        "p_playing": 0.2,
        "p_sleeping": 0.1,
        "has_car": True,
        "min_bet": 5,
        "max_bet": 30
    },
    "vip": {
        "p_leaving": 0.05,
        "p_strategizing": 0.1,
        "p_ordering": 0.5,
        "p_playing": 0.5,
        "p_sleeping": 0.2,
        "has_car": True,
        "min_bet": 100,
        "max_bet": 1000
    },
    "budget_player": {
        "p_leaving": 0.25,
        "p_strategizing": 0.1,
        "p_ordering": 0.3,
        "p_playing": 0.3,
        "p_sleeping": 0.05,
        "has_car": False,
        "min_bet": 5,
        "max_bet": 15
    },
    "drunken_gambler": {
        "p_leaving": 0.05,
        "p_strategizing": 0.01,
        "p_ordering": 0.9,
        "p_playing": 0.9,
        "p_sleeping": 0.2,
        "has_car": False,
        "min_bet": 20,
        "max_bet": 150
    },
    "ordering_addict": {
        "p_leaving": 0.15,
        "p_strategizing": 0.05,
        "p_ordering": 0.9,
        "p_playing": 0.1,
        "p_sleeping": 0.5,
        "has_car": True,
        "min_bet": 10,
        "max_bet": 40
    },
    "adventurer": {
        "p_leaving": 0.05,
        "p_strategizing": 0.2,
        "p_ordering": 0.4,
        "p_playing": 0.6,
        "p_sleeping": 0.3,
        "has_car": True,
        "min_bet": 30,
        "max_bet": 100
    },
    "minimalist": {
        "p_leaving": 0.4,
        "p_strategizing": 0.4,
        "p_ordering": 0.1,
        "p_playing": 0.1,
        "p_sleeping": 0.1,
        "has_car": False,
        "min_bet": 1,
        "max_bet": 10
    },
    # New types you asked for 👇
    "risky_player": {
        "p_leaving": 0.1,
        "p_strategizing": 0.0,
        "p_ordering": 0.5,
        "p_playing": 0.9,
        "p_sleeping": 0.1,
        "has_car": True,
        "min_bet": 1,
        "max_bet": 200
    },
    "cheating_player": {
        "p_leaving": 0.1,
        "p_strategizing": 0.8,
        "p_ordering": 0.5,
        "p_playing": 0.9,
        "p_sleeping": 0.1,
        "has_car": False,
        "min_bet": 1,
        "max_bet": 100
    },
    "rich_player": {
        "p_leaving": 0.1,
        "p_strategizing": 0.3,
        "p_ordering": 0.9,
        "p_playing": 0.9,
        "p_sleeping": 0.2,
        "has_car": True,
        "min_bet": 100,
        "max_bet": 1000
    },
    "safe_player": {
        "p_leaving": 0.4,
        "p_strategizing": 0.0,
        "p_ordering": 0.2,
        "p_playing": 0.5,
        "p_sleeping": 0.1,
        "has_car": False,
        "min_bet": 1,
        "max_bet": 100
    },
    "tired_customer": {
        "p_leaving": 0.8,
        "p_strategizing": 0.0,
        "p_ordering": 0.5,
        "p_playing": 0.3,
        "p_sleeping": 0.1,
        "has_car": True,
        "min_bet": 1,
        "max_bet": 100
    }
}


class CustomerFactory(ABC):
    def __init__(self, casino):
        self.casino = casino

    @abstractmethod
    def create_customer(self, id):
        pass

    def _build_customer(self, id, name):
        profile = customer_profiles[name]
        customer = Customer(
            id=id,
            casino=self.casino,
            balance=random.randint(100, 1000),
            p_leaving=profile["p_leaving"],
            p_strategizing=profile["p_strategizing"],
            p_ordering=profile["p_ordering"],
            p_playing=profile["p_playing"],
            p_sleeping=profile["p_sleeping"],
            min_bet=profile["min_bet"],
            max_bet=profile["max_bet"],
            type=name
        )
        customer.car = Car(id) if profile["has_car"] else None
        return customer

class GamblerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "gambler"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class StrategistFactory(CustomerFactory):
    def create_customer(self, id):
        name = "strategist"
        print(f"Customer-{id} is type {name}")
        return self._build_customer(id, name)

class ShopperFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "shopper"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class VipFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "vip"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class BudgetPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "budget_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class DrunkenGamblerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "drunken_gambler"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class OrderingAddictFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "ordering_addict"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class AdventurerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "adventurer"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class MinimalistFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "minimalist"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RiskyPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "risky_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RiskyCheatingFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "cheating_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RichPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "rich_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class SafePlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "safe_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class TiredCustomerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "tired_customer"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)