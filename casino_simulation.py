import random
import threading
import time


class Casino:
    def __init__(self):
        self.games = {}
        self.players = []
        self.players_lock = threading.Lock()

    def add_game(self, game):
        if game.name not in self.games:
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
        self.lock = threading.Lock()

    def increment(self, amount):
        with self.lock:
            self.balance += amount
        print(f"💵 Player-{self.id} won ${amount}. (Balance: ${self.balance}).")

    def decrease(self, amount):
        with self.lock:
            if amount > self.balance:
                print(f"💵 Player-{self.id} does not have ${amount} to bet.")
                return False
            self.balance -= amount
            print(f"💵 Player-{self.id} has bet ${amount}. (Balance: ${self.balance}).")
            return True

    def get_balance(self):
        with self.lock:
            return self.balance

    def play(self, amount, name, logo, probability, prize):
        print(f"{logo} Player-{self.id} playing {name}")
        if not self.decrease(amount):
            self.casino.add_player(self)
            return

        if random.random() < probability:
            self.increment(amount * prize)
        else:
            print(f"💵 Player-{self.id} lost ${amount}. (Balance: ${self.balance})")

        self.casino.add_player(self)
        time.sleep(random.randint(1, 5))

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
            print(f"🎟️ Player-{self.id} selected the game '{game}'")

            # Lock both available players and wait_list modification
            self.casino.games[game]['lock'].acquire()
            self.casino.players_lock.acquire()
            self.casino.games[game]['wait_list'].append(self)
            self.casino.players.remove(self)
            print(f"🎟 Player-{self.id} is ready to play the game '{game}'")
            self.casino.players_lock.release()
            self.casino.games[game]['lock'].release()

            time.sleep(random.randint(1, 5))


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


class BlackJack(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "BlackJack", "🃏", 5, 0.49, 2, id)


class Roulette(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Roulette", "🎡", 10, 0.486, 2, id)


class SlotMachine(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Slot Machine", "🎰", 1, 0.3, 2, id)


class Craps(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Craps", "🎲", 20, 0.493, 2, id)


class Poker(Game):
    def __init__(self, casino, id):
        super().__init__(casino, "Poker", "♠️", random.randint(2, 10), 0.5, 2, id)



casino = Casino()

games = [Roulette(casino, i) for i in range(5)] + [SlotMachine(casino, i) for i in range(10)] + [BlackJack(casino, i) for i in range(2)]

players = [Player(i, casino, balance=random.randint(50, 200)) for i in range(5)]

for player in players:
    casino.add_player(player)

for game in games:
    game.start()

for player in players:
    player.start()
