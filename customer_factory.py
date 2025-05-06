import random
from parking_lot import Car
from customer import Customer
from abc import ABC, abstractmethod


# Define customer profiles with specific behavior and attributes
customer_profiles = {
    "gambler": {
        "p_leaving": 0.05,
        "p_strategizing": 0.05,
        "p_ordering": 0.1,
        "p_restaurant": 0.1,
        "p_playing": 0.75,
        "p_sleeping": 0.05,
        "has_car_probability": 0.7,
        "min_bet": 50,
        "max_bet": 300,
        "game_preferences": {
            "Roulette": 0.5,
            "BlackJack": 0.3,
            "Slot Machine": 0.1,
            "Craps": 0.05,
            "Poker": 0.05
        }
    },
    "strategist": {
        "p_leaving": 0.1,
        "p_strategizing": 0.4,
        "p_ordering": 0.1,
        "p_restaurant": 0.15,
        "p_playing": 0.35,
        "p_sleeping": 0.05,
        "has_car_probability": 0.3,
        "min_bet": 10,
        "max_bet": 100,
        "game_preferences": {
            "Poker": 0.5,
            "BlackJack": 0.4,
            "Roulette": 0.05,
            "Craps": 0.05,
            "Slot Machine": 0.0
        }
    },
    # Additional customer profiles follow...
    "shopper": {
        "p_leaving": 0.2,
        "p_strategizing": 0.05,
        "p_ordering": 0.7,
        "p_restaurant": 0.2,
        "p_playing": 0.2,
        "p_sleeping": 0.05,
        "has_car_probability": 0.8,
        "min_bet": 5,
        "max_bet": 30,
        "game_preferences": {
            "Slot Machine": 0.7,
            "Roulette": 0.2,
            "BlackJack": 0.1,
            "Craps": 0.0,
            "Poker": 0.0
        }
    },
    "vip": {
        "p_leaving": 0.03,
        "p_strategizing": 0.1,
        "p_ordering": 0.2,
        "p_restaurant": 0.25,
        "p_playing": 0.6,
        "p_sleeping": 0.07,
        "has_car_probability": 0.95,
        "min_bet": 200,
        "max_bet": 2000,
        "game_preferences": {
            "Poker": 0.5,
            "Roulette": 0.3,
            "BlackJack": 0.15,
            "Craps": 0.05,
            "Slot Machine": 0.0
        }
    },
    "budget_player": {
        "p_leaving": 0.25,
        "p_strategizing": 0.1,
        "p_ordering": 0.2,
        "p_restaurant": 0.15,
        "p_playing": 0.4,
        "p_sleeping": 0.05,
        "has_car_probability": 0.2,
        "min_bet": 5,
        "max_bet": 20,
        "game_preferences": {
            "Slot Machine": 0.6,
            "Roulette": 0.2,
            "BlackJack": 0.15,
            "Craps": 0.05,
            "Poker": 0.0
        }
    },
    "drunken_gambler": {
        "p_leaving": 0.05,
        "p_strategizing": 0.01,
        "p_ordering": 0.5,
        "p_restaurant": 0.2,
        "p_playing": 0.8,
        "p_sleeping": 0.2,
        "has_car_probability": 0.1,
        "min_bet": 20,
        "max_bet": 150,
        "game_preferences": {
            "Slot Machine": 0.4,
            "Craps": 0.3,
            "Roulette": 0.2,
            "BlackJack": 0.1,
            "Poker": 0.0
        }
    },
    "ordering_addict": {
        "p_leaving": 0.1,
        "p_strategizing": 0.05,
        "p_ordering": 0.8,
        "p_restaurant": 0.4,
        "p_playing": 0.1,
        "p_sleeping": 0.05,
        "has_car_probability": 0.7,
        "min_bet": 10,
        "max_bet": 40,
        "game_preferences": {
            "Slot Machine": 0.7,
            "Roulette": 0.2,
            "BlackJack": 0.1,
            "Craps": 0.0,
            "Poker": 0.0
        }
    },
    "adventurer": {
        "p_leaving": 0.05,
        "p_strategizing": 0.15,
        "p_ordering": 0.2,
        "p_restaurant": 0.2,
        "p_playing": 0.6,
        "p_sleeping": 0.1,
        "has_car_probability": 0.8,
        "min_bet": 30,
        "max_bet": 120,
        "game_preferences": {
            "Poker": 0.4,
            "Roulette": 0.3,
            "BlackJack": 0.2,
            "Craps": 0.1,
            "Slot Machine": 0.0
        }
    },
    "minimalist": {
        "p_leaving": 0.3,
        "p_strategizing": 0.3,
        "p_ordering": 0.1,
        "p_restaurant": 0.1,
        "p_playing": 0.2,
        "p_sleeping": 0.1,
        "has_car_probability": 0.2,
        "min_bet": 1,
        "max_bet": 10,
        "game_preferences": {
            "Slot Machine": 0.8,
            "Roulette": 0.1,
            "BlackJack": 0.1,
            "Craps": 0.0,
            "Poker": 0.0
        }
    },
    "risky_player": {
        "p_leaving": 0.05,
        "p_strategizing": 0.0,
        "p_ordering": 0.1,
        "p_restaurant": 0.05,
        "p_playing": 0.8,
        "p_sleeping": 0.05,
        "has_car_probability": 0.6,
        "min_bet": 20,
        "max_bet": 500,
        "game_preferences": {
            "Craps": 0.4,
            "Roulette": 0.3,
            "Poker": 0.2,
            "BlackJack": 0.1,
            "Slot Machine": 0.0
        }
    },
    "cheating_player": {
        "p_leaving": 0.05,
        "p_strategizing": 0.5,
        "p_ordering": 0.1,
        "p_restaurant": 0.1,
        "p_playing": 0.7,
        "p_sleeping": 0.05,
        "has_car_probability": 0.2,
        "min_bet": 10,
        "max_bet": 100,
        "game_preferences": {
            "BlackJack": 0.6,
            "Poker": 0.3,
            "Roulette": 0.1,
            "Craps": 0.0,
            "Slot Machine": 0.0
        }
    },
    "rich_player": {
        "p_leaving": 0.02,
        "p_strategizing": 0.05,
        "p_ordering": 0.2,
        "p_restaurant": 0.25,
        "p_playing": 0.7,
        "p_sleeping": 0.03,
        "has_car_probability": 0.95,
        "min_bet": 300,
        "max_bet": 5000,
        "game_preferences": {
            "Poker": 0.5,
            "Roulette": 0.3,
            "BlackJack": 0.15,
            "Craps": 0.05,
            "Slot Machine": 0.0
        }
    },
    "safe_player": {
        "p_leaving": 0.2,
        "p_strategizing": 0.2,
        "p_ordering": 0.1,
        "p_restaurant": 0.1,
        "p_playing": 0.4,
        "p_sleeping": 0.1,
        "has_car_probability": 0.3,
        "min_bet": 5,
        "max_bet": 50,
        "game_preferences": {
            "BlackJack": 0.5,
            "Roulette": 0.3,
            "Craps": 0.1,
            "Slot Machine": 0.1,
            "Poker": 0.0
        }
    },
    "tired_customer": {
        "p_leaving": 0.6,
        "p_strategizing": 0.1,
        "p_ordering": 0.2,
        "p_restaurant": 0.2,
        "p_playing": 0.2,
        "p_sleeping": 0.4,
        "has_car_probability": 0.8,
        "min_bet": 5,
        "max_bet": 50,
        "game_preferences": {
            "Slot Machine": 0.5,
            "Roulette": 0.2,
            "BlackJack": 0.2,
            "Craps": 0.1,
            "Poker": 0.0
        }
    }
}

# Abstract CustomerFactory class to define the interface for customer creation
class CustomerFactory(ABC):
    def __init__(self, casino):
        self.casino = casino  # Reference to the casino where the customer will be created

    @abstractmethod
    def create_customer(self, id):
        # Abstract method that subclasses must implement to create customers of various types
        pass

    def _build_customer(self, id, name):
        # Method to build and return a customer based on the given profile
        profile = customer_profiles[name]  # Fetch the profile based on the customer type (e.g., "gambler")
        customer = Customer(
            id=id,
            casino=self.casino,
            balance=random.randint(100, 1000),  # Randomly set the initial balance of the customer
            p_leaving=profile["p_leaving"],  # Set probabilities and preferences based on the profile
            p_strategizing=profile["p_strategizing"],
            p_ordering=profile["p_ordering"],
            p_playing=profile["p_playing"],
            p_sleeping=profile["p_sleeping"],
            min_bet=profile["min_bet"],
            max_bet=profile["max_bet"],
            type=name,  # Set the customer type (e.g., "gambler")
            p_restaurant=profile["p_restaurant"],
            game_preferences=profile["game_preferences"],  # Set the customer's game preferences
            has_car_probability=profile["has_car_probability"]  # Set the probability of the customer having a car
        )
        return customer

# Concrete Factory classes for creating specific customer types
class GamblerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "gambler"  # Set the profile to "gambler"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)  # Call _build_customer to create the customer

class StrategistFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "strategist"  # Set the profile to "strategist"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class ShopperFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "shopper"  # Set the profile to "shopper"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class VipFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "vip"  # Set the profile to "vip"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class BudgetPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "budget_player"  # Set the profile to "budget_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class DrunkenGamblerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "drunken_gambler"  # Set the profile to "drunken_gambler"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class OrderingAddictFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "ordering_addict"  # Set the profile to "ordering_addict"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class AdventurerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "adventurer"  # Set the profile to "adventurer"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class MinimalistFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "minimalist"  # Set the profile to "minimalist"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RiskyPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "risky_player"  # Set the profile to "risky_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RiskyCheatingFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "cheating_player"  # Set the profile to "cheating_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class RichPlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "rich_player"  # Set the profile to "rich_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class SafePlayerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "safe_player"  # Set the profile to "safe_player"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)

class TiredCustomerFactory(CustomerFactory):
    def create_customer(self, id):
        profile = "tired_customer"  # Set the profile to "tired_customer"
        print(f"Customer-{id} is type {profile}")
        return self._build_customer(id, profile)
