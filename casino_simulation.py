import random
import threading
import time


class Casino:
    def __init__(self):
        self.games = {
            'Game': {'wait_list': [], 'lock': threading.Lock()}
        }
        self.available_players = []
        self.lock = threading.Lock()


    def add_player(self, player):
        with self.lock:
            self.available_players.append(player)


class Player(threading.Thread):
    def __init__(self, id, casino, balance):
        super().__init__()
        self.casino = casino
        self.balance = balance
        self.id = id

    def play(self):
        print(f"Player-{self.id} playing")
        self.casino.add_player(self)

    def run(self):
        while True:
            # Player is waiting for game to start
            with self.casino.lock:
                if not self in self.casino.available_players:
                    time.sleep(2)
                    continue

            # Player leaves the casino
            if self.balance <= 0:
                print(f"🚪 {self.name} is out of money and leaves the casino.")
                break

            if random.random() < 0.20:  # 20% chance to leave
                print(f"🚪 {self.name} has decided to leave the casino.")
                break

            if random.random() < 0.10:  # 10% chance to leave strategically
                print(f"🚪 {self.name} is leaving the casino after strategizing.")
                break

            # Random selection of the game
            game = random.choice(list(self.casino.games.keys()))
            print(f"Player-{self.id} selected the game '{game}'")

            # Lock both available players and wait_list modification
            with self.casino.lock:
                game_dictionary = self.casino.games[game]
                with game_dictionary['lock']:  # Lock before modifying the wait_list
                    game_dictionary['wait_list'].append(self)
                    print(f"Player-{self.id} was added to the wait list for game {game}")

                self.casino.available_players.remove(self)  # Remove only after being fully added

            time.sleep(random.randint(1, 5))


class Game(threading.Thread):
    def __init__(self, casino, name, capacity):
        super().__init__()
        self.casino = casino
        self.name = name
        self.capacity = capacity

    def run(self):
        while True:
            game = self.casino.games[self.name]
            with game['lock']:
                players = len(game['wait_list'])
                if players == 0:
                    time.sleep(random.randint(1, 10))
                    print(f"No players in {self.name}")
                    continue

                # Wait briefly to allow other players to add themselves
                time.sleep(0.1)  # Small delay to let all players finish adding themselves

                num_players = min(players, self.capacity)
                print(f"Game {self.name} starting with {num_players} players")

                for _ in range(num_players):
                    player = game['wait_list'].pop(0)
                    player.play()

            time.sleep(random.randint(1, 10))


casino = Casino()

game = Game(casino, 'Game', capacity=3)

game.start()

players = [Player(i, casino, balance=random.randint(50, 200)) for i in range(5)]

for player in players:
    casino.add_player(player)
    player.start()

for player in players:
    player.join()
