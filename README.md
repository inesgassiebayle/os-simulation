# Casino Simulation: Concurrency in Python

A multi-threaded simulation of a casino resort, built for the **Operating Systems & Parallel Computing** course at IE University (Madrid, 2025).

Every customer, barista and waiter runs as its own thread and competes for shared resources: game tables, bar and restaurant orders, parking spots and hotel rooms. Each event is recorded in SQLite and analyzed at the end of the run.

## What it does
- **Customers as threads.** 14 customer profiles (VIP, budget player, risky cheater, drunken gambler, strategist and more), each with its own probabilities for betting, ordering, eating, sleeping and leaving.
- **Dynamic arrivals.** New customers keep arriving at random intervals during the run, up to 300.
- **Shared resources protected by locks.** Game tables, the customer list, balances and order status are all synchronized to avoid race conditions.
- **Producer/consumer services.** Baristas and waiters are worker threads that process order queues.
- **Limited capacity.** A parking lot (failed parkings are logged) and a 10-room hotel.
- **Persistence.** 12 SQLite tables: customers, game plays, orders, bookings, parking, time spent in the casino and more.
- **Analytics.** `stats.py` queries the database and plots average gains and losses per customer type and per game.

## Design
- **Factory pattern** for creating both games (Roulette, Blackjack, Craps, Slots, Poker) and customer profiles.
- Modules: `casino.py` (orchestration) · `customer.py` · `customer_factory.py` · `game.py` / `game_implementations.py` · `bar.py` · `restaurant.py` · `parking_lot.py` · `hotel.py` · `db.py` · `stats.py`

## Run it
```bash
pip install pandas matplotlib
python db.py        # create the tables
python casino.py    # run the simulation
python stats.py     # print and plot the results
```

**Stack:** Python · `threading` · SQLite · pandas · matplotlib
