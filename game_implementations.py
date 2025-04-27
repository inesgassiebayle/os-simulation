from abc import ABC, abstractmethod
from game import Game
import random

class GameFactory(ABC):
    def __init__(self, casino):
        self.casino = casino

    @abstractmethod
    def create_game(self, id):
        pass

class BlackJackFactory(GameFactory):
    def create_game(self, id):
        return Game(self.casino, "BlackJack", capacity=5, probability=0.49, prize=2, id=id)

class RouletteFactory(GameFactory):
    def create_game(self, id):
        return Game(self.casino, "Roulette", capacity=30, probability=0.486, prize=2, id=id)

class SlotMachineFactory(GameFactory):
    def create_game(self, id):
        return Game(self.casino, "Slot Machine", capacity=1, probability=0.1, prize=2, id=id)

class CrapsFactory(GameFactory):
    def create_game(self, id):
        return Game(self.casino, "Craps", capacity=20, probability=0.493, prize=2, id=id)

class PokerFactory(GameFactory):
    def create_game(self, id):
        return Game(self.casino, "Poker", capacity=random.randint(2, 10), probability=0.5, prize=2, id=id)
