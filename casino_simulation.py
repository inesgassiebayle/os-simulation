import random
import threading
import time


class Casino:
    def __init__(self):
        self.games = {}
        self.players = []
        self.players_lock = threading.Lock()

    def add_game(self, game):
        self.games[game.name] = {'wait_list': [], 'lock': threading.Lock()}

    def add_player(self, player):
        with self.players_lock:
            self.players.append(player)


class Player(threading.Thread):
    def __init__(self, id, casino, balance):
        super().__init__()
        self.id = id
        self.casino = casino
        self.balance = balance

    def play(self):
        print(f"Player-{self.id} playing")
        self.casino.add_player(self)

    def run(self):
        while True:
            # Player is playing or waiting to play
            with self.casino.players_lock:
                if self not in self.casino.players:
                    time.sleep(random.randint(1, 5))
                    continue

            # Player leaves the casino
            if self.balance <= 0:
                print(f"🚪 Player-{self.id} is out of money and leaves the casino.")
                break

            if random.random() < 0.20:  # 20% chance to leave
                print(f"🚪 Player-{self.id} has decided to leave the casino.")
                break

            if random.random() < 0.10:  # 10% chance to leave strategically
                print(f"🚪 Player-{self.id} is leaving the casino after strategizing.")
                break

            # Random selection of the game
            game = random.choice(list(self.casino.games.keys()))
            print(f"Player-{self.id} selected the game '{game}'")

            # Lock both available players and wait_list modification
            self.casino.games[game]['lock'].acquire()
            self.casino.players_lock.acquire()
            self.casino.games[game]['wait_list'].append(self)
            self.casino.players.remove(self)
            print(f"Player-{self.id} is ready to play the game '{game}'")
            self.casino.players_lock.release()
            self.casino.games[game]['lock'].release()

            time.sleep(random.randint(1, 5))


class Game(threading.Thread):
    def __init__(self, casino, name, capacity):
        super().__init__()
        self.casino = casino
        self.name = name
        self.capacity = capacity

    def run(self):
        while True:
            with self.casino.games[self.name]['lock']:
                players = len(self.casino.games[self.name]['wait_list'])
                if players == 0:
                    print(f"No players in {self.name}")
                    time.sleep(random.randint(1, 10))
                    continue

                num_players = min(players, self.capacity)
                print(f"Game {self.name} starting with {num_players} players")

                for _ in range(num_players):
                    player = self.casino.games[self.name]['wait_list'].pop(0)
                    player.play()
            time.sleep(random.randint(1, 5))


casino = Casino()

game = Game(casino, 'Game', capacity=3)

casino.add_game(game)


players = [Player(i, casino, balance=random.randint(50, 200)) for i in range(5)]

for player in players:
    casino.add_player(player)


game.start()
for player in players:
    player.start()
