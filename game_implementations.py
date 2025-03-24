import random
from game import Game


class BlackJack(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "BlackJack", "🃏", 5, 0.49, 2, id)


class Roulette(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Roulette", "🎡", 30, 0.486, 2, id)


class SlotMachine(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Slot Machine", "🎰", 1, 0.1, 2, id)


class Craps(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Craps", "🎲", 20, 0.493, 2, id)


class Poker(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Poker", "♠️", random.randint(2, 10), 0.5, 2, id)

