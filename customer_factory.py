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
    # More customer types can be added here following the same pattern...
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
