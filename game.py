import threading
import random
import time


class Game(threading.Thread):
    def __init__(self, casino, name, logo, capacity, probability, prize, id):
        super().__init__()
        self.casino = casino
        self.name = name
        self.capacity = capacity
        self.probability = probability
        self.prize = prize
        self.logo = logo
        self.id = id
        casino.add_game(self)

    def run(self):
        while True:
            with self.casino.games[self.name]['lock']:
                players = len(self.casino.games[self.name]['wait_list'])
                if players == 0:
                    print(f"{self.logo} No players in {self.name} {self.id}")
                    time.sleep(random.randint(1, 10))
                    continue

                num_players = min(players, self.capacity)
                print(f"{self.logo} Game {self.name} {self.id} starting with {num_players} players")

                for _ in range(num_players):
                    player = self.casino.games[self.name]['wait_list'].pop(0)
                    bet_amount = random.randint(5, player.get_balance())
                    player.play(bet_amount, self.name, self.logo, self.probability, self.prize)
            time.sleep(random.randint(1, 5))