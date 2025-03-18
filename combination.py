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

    def run(self):
        """Simulates continuous play until the player runs out of money or decides to leave."""
        while self.balance > 0:
            if random.random() < 0.20:  # 20% chance to leave
                print(f"🚪 {self.name} has decided to leave the casino with ${self.balance}.")
                break

            if random.random() < 0.10:  # 10% chance to leave strategically
                print(f"🃏 {self.name} is leaving the casino after strategizing.")
                break

            game_name = random.choice(list(self.casino.games.keys()))
            bet_amount = random.randint(5, self.balance)

            self.casino.play_game(self, game_name, bet_amount)

            if self.balance <= 0:
                print(f"💸 {self.name} is out of money and leaves the casino.")
                break

            time.sleep(random.uniform(0.5, 2))

class CasinoGame:
    """Base class for a casino game."""
    def __init__(self, name):
        self.name = name

    def play(self, player, bet_amount):
        raise NotImplementedError

class Blackjack(CasinoGame):
    """Simulates a Blackjack table with a capacity of 4 players."""
    def __init__(self):
        super().__init__("Blackjack")
        self.table_lock = threading.Semaphore(50)  # Limits to 5 players and 10 tables

    def play(self, player, bet_amount):
        print(f"🃏 {player.name} is waiting for a Blackjack table...")
        with self.table_lock:
            print(f"🃏 {player.name} got a seat at the Blackjack table!")
            time.sleep(random.uniform(2, 5))  # Simulating waiting & playing time
            if not player.place_bet(bet_amount, self.name):
                return
            time.sleep(2)  # Simulate game time
            if random.random() < 0.42:
                player.add_winnings(bet_amount * 2, self.name)
            else:
                print(f"😢 {player.name} lost ${bet_amount} in {self.name}.")

class Roulette(CasinoGame):
    """Simulates Roulette with 5 machines."""
    def __init__(self):
        super().__init__("Roulette")
        self.machine_lock = threading.Semaphore(50)  # 30 machines available

    def play(self, player, bet_amount):
        print(f"🎡 {player.name} is waiting for a Roulette machine...")
        with self.machine_lock:
            print(f"🎡 {player.name} is playing Roulette!")
            time.sleep(random.uniform(2, 5))  # Simulating waiting & playing time
            if not player.place_bet(bet_amount, self.name):
                return
            time.sleep(2)
            winning_color = random.choices(["Red", "Black", "Green"], weights=[18, 18, 1])[0]
            chosen_color = random.choice(["Red", "Black"])
            print(f"🎡 {player.name} bet on {chosen_color} in {self.name}, result was {winning_color}.")
            if winning_color == chosen_color:
                player.add_winnings(bet_amount * 2, self.name)
            else:
                print(f"😢 {player.name} lost ${bet_amount} in {self.name}.")

class SlotMachine(CasinoGame):
    """Simulates Slot Machines with 5 machines."""
    def __init__(self):
        super().__init__("Slot Machine")
        self.machine_lock = threading.Semaphore(30)  # 20 machines available

    def play(self, player, bet_amount):
        print(f"🎰 {player.name} is waiting for a Slot Machine...")
        with self.machine_lock:
            print(f"🎰 {player.name} is playing on a Slot Machine!")
            time.sleep(random.uniform(2, 5))  # Simulating waiting & playing time
            if not player.place_bet(bet_amount, self.name):
                return
            time.sleep(2)
            if random.random() < 0.12:
                player.add_winnings(bet_amount * 10, self.name)
            else:
                print(f"😢 {player.name} lost ${bet_amount} in {self.name}.")


class Bingo(CasinoGame):
    """Simulates a Bingo game with 100 spots available per round."""
    def __init__(self):
        super().__init__("Bingo")
        self.spots_lock = threading.Semaphore(100)  # 100 spots available
        self.players_in_round = []
        self.round_lock = threading.Lock()
        self.round_active = False,
        self.round_thread = threading.Thread(target=self.run_bingo_rounds, daemon=True)
        self.round_thread.start()

    def play(self, player, bet_amount):
        """Allows players to join a Bingo round and waits for the round to start."""
        num_cards = random.randint(1,5)  # Each Bingo card costs $5
       
        print(f"⚪ {player.name} is waiting for a Bingo round with {num_cards} cards...")

        with self.spots_lock:
            with self.round_lock:
                if not player.place_bet(num_cards * 5, self.name):
                    return
                self.players_in_round.append((player, num_cards))

    def run_bingo_rounds(self):
        """Continuously runs Bingo rounds whenever enough players are ready."""
        while True:
            time.sleep(5)  # Wait for more players to join
            self.start_round()

    def start_round(self):
        """Begins a new Bingo round if there are players."""
        with self.round_lock:
            if self.round_active or len(self.players_in_round) < 2:
                return  # Avoid multiple rounds or starting with one player

            self.round_active = True
            print(f"🎱 Bingo round is starting with {len(self.players_in_round)} players!")
            time.sleep(5)  # Simulate Bingo game duration

            # Pick a single winner weighted by number of cards owned
            players, weights = zip(*self.players_in_round)
            winner = random.choices(players, weights=weights, k=1)[0]

            print(f"🎉 ⚪ {winner.name} won the Bingo round and received $100!")
            winner.add_winnings(100, self.name)

            # Ask players if they want to stay
            staying_players = []
            for player, num_cards in self.players_in_round:
                if random.random() < 0.70:  # 70% chance to stay for another round
                    print(f"⚪ {player.name} decides to stay for another Bingo round.")
                    staying_players.append((player, num_cards))
                else:
                    print(f"🚪 {player.name} leaves the Bingo game.")

            self.players_in_round = staying_players  # Keep only those staying
            self.round_active = False  # Allow new players to join

 
            



class Casino:
    """Casino manages players and games with multiple machines."""
    def __init__(self, max_players=230):
        self.players = []
        self.games = {
            "Blackjack": Blackjack(),
            "Roulette": Roulette(),
            "Slot Machine": SlotMachine(),
            "Bingo": Bingo()
        }
        self.max_players = max_players

    def add_player(self, player):
        self.players.append(player)

    def play_game(self, player, game_name, bet_amount):
        if game_name in self.games:
            game = self.games[game_name]
            thread = threading.Thread(target=game.play, args=(player, bet_amount))
            thread.start()
        else:
            print(f"❌ {game_name} is not available in the casino.")

    def start_simulation(self):
        """Starts the casino simulation with multiple players."""
        for i in range(self.max_players):
            player = Player(name=f"Player-{i+1}", balance=random.randint(500, 1500), casino=self)
            self.add_player(player)
            player.start()

        for player in self.players:
            player.join()

# Running the simulation
if __name__ == "__main__":
    casino = Casino(max_players=230)  # Simulate a casino with 230 players
    casino.start_simulation()
    print("🎰 Casino simulation complete!")
