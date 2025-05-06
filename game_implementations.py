from abc import ABC, abstractmethod
from game import Game
import random
from abc import ABC, abstractmethod
import random

# Abstract base class for creating casino games
class GameFactory(ABC):
    def __init__(self, casino):
        # Initialize the factory with the casino reference
        self.casino = casino

    # Abstract method to create a specific type of game
    @abstractmethod
    def create_game(self, id):
        pass  # Each subclass will implement this method to create a specific game

# Factory class for creating BlackJack games
class BlackJackFactory(GameFactory):
    def create_game(self, id):
        # Create and return a new BlackJack game with specified parameters
        return Game(self.casino, "BlackJack", capacity=5, probability=0.49, prize=2, id=id)

# Factory class for creating Roulette games
class RouletteFactory(GameFactory):
    def create_game(self, id):
        # Create and return a new Roulette game with specified parameters
        return Game(self.casino, "Roulette", capacity=30, probability=0.486, prize=2, id=id)

# Factory class for creating Slot Machine games
class SlotMachineFactory(GameFactory):
    def create_game(self, id):
        # Create and return a new Slot Machine game with specified parameters
        return Game(self.casino, "Slot Machine", capacity=1, probability=0.1, prize=2, id=id)

# Factory class for creating Craps games
class CrapsFactory(GameFactory):
    def create_game(self, id):
        # Create and return a new Craps game with specified parameters
        return Game(self.casino, "Craps", capacity=20, probability=0.493, prize=2, id=id)

# Factory class for creating Poker games
class PokerFactory(GameFactory):
    def create_game(self, id):
        # Create and return a new Poker game with random capacity between 2 and 10 players
        return Game(self.casino, "Poker", capacity=random.randint(2, 10), probability=0.5, prize=2, id=id)
