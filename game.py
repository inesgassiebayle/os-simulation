import threading
import random
import time
import threading
import time
import random

class Game(threading.Thread):
    def __init__(self, casino, name, capacity, probability, prize, id):
        # Initialize the game thread and set its attributes
        super().__init__()
        self.casino = casino  # Reference to the casino object where the game is held
        self.name = name  # Name of the game (e.g., Poker, Blackjack)
        self.capacity = capacity  # Maximum number of players allowed in the game
        self.probability = probability  # Probability of the customer winning
        self.prize = prize  # Prize multiplier for a winning player
        self.id = id  # Unique game identifier
        # Add the game to the casino's game list
        casino.add_game(self)

    def run(self):
        # Main thread that handles the running of the game, continuously running as long as needed
        while True:
            # Acquire the game lock to ensure no other thread can modify the game during play
            with self.casino.games[self.name]['lock']:
                players = len(self.casino.games[self.name]['wait_list'])  # Get the number of players in the waitlist

                if players == 0:
                    # If no players are in the waitlist, the game will sleep for a random amount of time before checking again
                    time.sleep(random.randint(1, 10))
                    continue  # Skip to the next iteration

                # Determine how many players can actually play based on the game's capacity
                num_players = min(players, self.capacity)  # Start the game with as many players as the capacity allows
                print(f"Game {self.name}-{self.id} starting with {num_players} players")

                # For each player in the game, pop them from the waitlist and allow them to play
                for _ in range(num_players):
                    player = self.casino.games[self.name]['wait_list'].pop(0)  # Pop the first player from the waitlist
                    # Let the player play the game (this simulates the player's actions)
                    player.play(self.name, self.probability, self.prize, self.id)

            # Sleep for a random period between game rounds
            time.sleep(random.randint(1, 5))
