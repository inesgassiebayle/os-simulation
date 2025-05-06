import sqlite3
import os

import sqlite3
import os
from collections import Counter

# Function to create all the necessary tables in the database if they do not already exist
def create_tables():
    # Define the database path (casino.db)
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create customer table to store customer information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initial_balance INTEGER NOT NULL,
            customer_type TEXT NOT NULL,
            has_car BOOLEAN NOT NULL
        )
    """)

    # Create bar table to store information about bars in the casino
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    # Create restaurant table to store information about restaurants in the casino
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            num_tables INTEGER NOT NULL
        )
    """)

    # Create menu item table to store items available in bars and restaurants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            prep_time INTEGER NOT NULL,
            source_type TEXT NOT NULL CHECK(source_type IN ('bar', 'restaurant')),
            source_id INTEGER NOT NULL
        )
    """)

    # Create order record table to store customer orders in bars or restaurants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            place_type TEXT NOT NULL CHECK(place_type IN ('bar', 'restaurant')),
            place_id INTEGER NOT NULL,
            total_spent REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customer(id)
        )
    """)

    # Create order item table to store individual items ordered in a record
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES order_record(id),
            FOREIGN KEY(menu_item_id) REFERENCES menu_item(id)
        )
    """)

    # Create game instance table to store information about active game instances
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_instance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL
        )
    """)

    # Create game play table to store information about customer game plays
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_play (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            game_instance_id INTEGER NOT NULL,
            amount_bet REAL NOT NULL,
            result REAL NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customer(id),
            FOREIGN KEY(game_instance_id) REFERENCES game_instance(id)
        )
    """)

    # Create room booking table to store room booking details for customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_booking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            room_number INTEGER,
            duration_seconds INTEGER,
            price REAL,
            booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create car parking table to store information about parked cars
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_parking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP
        )
    """)

    # Create casino permanence table to store customer arrival and departure times
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS casino_permanence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            departure_time TIMESTAMP
        )
    """)

    # Create failed parking table to record failed parking attempts by customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failed_parking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Commit the changes and close the connection to the database
    conn.commit()
    conn.close()


# Function to get a database connection
def get_db_connection():
    # Define the database path and return a connection to the database
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    return sqlite3.connect(db_path)


# Function to save an order made by a customer
def save_order(customer_id, place_type, place_id, order):
    conn = get_db_connection()  # Get a database connection
    cursor = conn.cursor()

    # Insert the order record into the database
    cursor.execute("""
        INSERT INTO order_record (customer_id, place_type, place_id, total_spent)
        VALUES (?, ?, ?, ?)
    """, (customer_id, place_type, place_id, order.get_total()))

    order_id = cursor.lastrowid  # Get the last inserted row ID

    # Count how many times each item was ordered
    item_counter = Counter(item.name for item in order.items)

    # Insert each item in the order into the order_item table
    for item_name, quantity in item_counter.items():
        cursor.execute("""
            SELECT id FROM menu_item
            WHERE name = ? AND source_type = ?
        """, (item_name, place_type))  # Get the menu item ID based on the item name and source type
        menu_item_row = cursor.fetchone()
        if menu_item_row:
            menu_item_id = menu_item_row[0]
            cursor.execute("""
                INSERT INTO order_item (order_id, menu_item_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, menu_item_id, quantity))  # Insert the order item

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Function to save a game play record
def save_game_play(customer_id, game_instance_id, amount_bet, result):
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert the game play record into the database
    cursor.execute("""
        INSERT INTO game_play (customer_id, game_instance_id, amount_bet, result)
        VALUES (?, ?, ?, ?)
    """, (customer_id, game_instance_id, amount_bet, result))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Function to save room booking record
def save_booking(room_number, customer, duration_seconds):
    conn = get_db_connection()
    cursor = conn.cursor()
    price = duration_seconds * customer.casino.hotel.price_per_second  # Calculate the price for the booking
    cursor.execute("""
            INSERT INTO room_booking (customer_id, room_number, duration_seconds, price)
            VALUES (?, ?, ?, ?)
    """, (customer.id, room_number, duration_seconds, price))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Function to save a car parking record
def save_parking_record(customer_id, slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the car parking record into the database
    cursor.execute("""
        INSERT INTO car_parking (customer_id, slot_id)
        VALUES (?, ?)
    """, (customer_id, slot_id))

    conn.commit()  # Commit the transaction
    record_id = cursor.lastrowid  # Get the last inserted row ID
    conn.close()  # Close the connection

    return record_id  # Return the record ID


# Function to close a car parking record when the customer leaves the parking
def close_parking_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the end time of the parking record
    cursor.execute("""
        UPDATE car_parking
        SET end_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (record_id,))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Function to save a customer's permanence record when they enter the casino
def save_permanence_record(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the permanence record into the casino_permanence table
    cursor.execute("""
        INSERT INTO casino_permanence (customer_id)
        VALUES (?)
    """, (customer_id,))

    conn.commit()  # Commit the transaction
    record_id = cursor.lastrowid  # Get the last inserted row ID
    conn.close()  # Close the connection

    return record_id  # Return the record ID


# Function to close a customer's permanence record when they leave the casino
def close_permanence_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the departure time of the permanence record
    cursor.execute("""
        UPDATE casino_permanence
        SET departure_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (record_id,))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Function to save a failed parking attempt record
def save_failed_parking(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the failed parking attempt record into the failed_parking table
    cursor.execute("""
        INSERT INTO failed_parking (customer_id)
        VALUES (?)
    """, (customer_id,))

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection


# Create the necessary tables if they do not exist
if __name__ == "__main__":
    create_tables()

