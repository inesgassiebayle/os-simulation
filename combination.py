import threading
import random
import time

class Player(threading.Thread):
    """Represents a casino player with a wallet."""
    def __init__(self, name, balance=500, casino=None):
        super().__init__()
        self.name = name
        self.balance = balance
        self.casino = casino
        self.lock = threading.Lock()
        self.current_game = None

    def place_bet(self, amount, game_name):
        """Player places a bet, deducting from wallet."""
        with self.lock:
            if amount > self.balance:
                print(f"❌ {self.name} does not have enough money to bet ${amount} on {game_name}.")
                return False
            self.balance -= amount
            print(f"🎲 {self.name} placed a bet of ${amount} on {game_name}. Remaining balance: ${self.balance}")
            return True

    def add_winnings(self, amount, game_name):
        """Player receives winnings."""
        with self.lock:
            self.balance += amount
            print(f"🎉 {self.name} won ${amount} on {game_name}! New balance: ${self.balance}")


    def play(self, game_name, game_logo, bet_amount, winning_probability, gain):
        print(f"{game_logo} {self.name} is playing on a {game_name}!")
        time.sleep(random.uniform(2, 5))  # Simulating waiting & playing time
        if not self.place_bet(bet_amount, game_name):
            return
        time.sleep(2)
        if random.random() < winning_probability:
            self.add_winnings(bet_amount * gain, self.name)
        else:
            print(f"😢 {self.name} lost ${bet_amount} in {game_name}.")
        self.current_game = None


    def run(self):
        """Simulates continuous play until the player runs out of money or decides to leave."""
        while True:
            # Player is already inside a game
            while self.current_game:
                time.sleep(2)
                continue

            # Cases in which the player decides to leave: out of money, cheating or own decision.
            if self.balance <= 0:
                print(f"🚪 {self.name} is out of money and leaves the casino.")
                break

            if random.random() < 0.20:  # 20% chance to leave
                print(f"🚪 {self.name} has decided to leave the casino with ${self.balance}.")
                break

            if random.random() < 0.10:  # 10% chance to leave strategically
                print(f"🚪 {self.name} is leaving the casino after strategizing.")
                break

            # Random selection of the game
            self.current_game = random.choice(list(self.casino.games.keys()))
            bet_amount = random.randint(5, self.balance)

            self.casino.play_game(self, self.current_game, bet_amount)

            time.sleep(random.uniform(0.5, 2))


class CasinoGame(threading.Thread):
    """Base class for a casino game."""
    def __init__(self, name, capacity):
        super().__init__()
        self.name = name
        self.capacity = capacity

    def play(self, player, bet_amount):
        raise NotImplementedError

class Blackjack(threading.Thread):
    """Simulates a continuously running Blackjack table with a capacity of 4 players."""

    def __init__(self, max_wait_time=10):
        super().__init__()
        self.name = "Blackjack"
        self.capacity = 5  # Maximum players
        self.table_lock = threading.Lock()
        self.winning_probability = 0.42
        self.logo = "🃏"
        self.gain = 2
        self.players = {}
        self.waiting_lock = threading.Lock()
        self.waiting = {}
        self.max_wait_time = max_wait_time

    def add_player(self, player, bet_amount):
        """Adds a player to the game and signals the thread to check if it can start."""
        with self.table_lock:
            if len(self.players) < self.capacity:
                self.players[player] = bet_amount
                print(f"🃏 {player.name} has joined the Blackjack table with a bet of ${bet_amount}.")
                return
        with self.waiting_lock:


    def start_game(self):
        """Starts the game with the current players."""
        for player, bet_amount in list(self.players.items()):
            player.play(self.name, self.logo, bet_amount, self.winning_probability, self.gain)
        self.players.clear()  # Reset the table for the next game

    def run(self):
        """Continuously runs the game, waiting for players and starting when conditions are met."""
        start_time = time.time()
        while True:
            # If the time exceeds max waiting time
            if (time.time() - start_time) > self.max_wait_time:
                with self.table_lock:
                    # Player in the game, then game starts
                    if len(self.players) > 0:
                        self.start_game()
                        start_time = time.time()
            with self.table_lock:
                if len(self.players) == self.capacity:
                    self.start_game()
                    start_time = time.time()


class Casino:
    """Casino manages players and games with multiple machines."""
    def __init__(self):
        self.players = []
        self.players_lock = threading.Lock()
        self.games = {
            # GAME : WAITING GAME
        }
        self.max_players = 0

    def add_game(self, game):
        self.games[game.name] = game
        self.max_players += game.capacity

    def add_player(self, player):
        with self.players_lock:
            self.players.append(player)

    def play_game(self, player, game_name, bet_amount):
        if game_name in self.games:
            game = self.games[game_name]
            game.add_player(player, bet_amount)
        else:
            print(f"❌ {game_name} is not available in the casino.")

    def start_simulation(self):
        """Starts the casino simulation with multiple players."""

        print(self.max_players)

        for i in range(self.max_players):
            player = Player(name=f"Player-{i+1}", balance=random.randint(500, 1500), casino=self)
            self.add_player(player)
            player.start()

        for player in self.players:
            player.join()




casino = Casino()
casino.add_game(Blackjack())
casino.start_simulation()