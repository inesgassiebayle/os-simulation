import sqlite3
import os

def create_tables():
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            initial_balance INTEGER NOT NULL,
            customer_type TEXT NOT NULL,
            has_car BOOLEAN NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            num_tables INTEGER NOT NULL
        )
    """)
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_instance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE game_play (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        game_instance_id INTEGER NOT NULL,
        amount_bet REAL NOT NULL,
        result REAL NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customer(id),
        FOREIGN KEY(game_instance_id) REFERENCES game_instance(id))""")

    cursor.execute("""
        CREATE TABLE room_booking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        room_number INTEGER,
        duration_seconds INTEGER,
        price REAL,
        booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    cursor.execute("""
        CREATE TABLE car_parking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        slot_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP
        )""")

    cursor.execute("""
        CREATE TABLE casino_permanence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        departure_time TIMESTAMP)""")

    cursor.execute("""
        CREATE TABLE failed_parking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

    conn.commit()
    conn.close()


def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    return sqlite3.connect(db_path)

from collections import Counter

def save_order(customer_id, place_type, place_id, order):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO order_record (customer_id, place_type, place_id, total_spent)
        VALUES (?, ?, ?, ?)
    """, (customer_id, place_type, place_id, order.get_total()))

    order_id = cursor.lastrowid

    # Count how many times each item was ordered
    item_counter = Counter(item.name for item in order.items)

    for item_name, quantity in item_counter.items():
        cursor.execute("""
            SELECT id FROM menu_item
            WHERE name = ? AND source_type = ?
        """, (item_name, place_type))
        menu_item_row = cursor.fetchone()
        if menu_item_row:
            menu_item_id = menu_item_row[0]
            cursor.execute("""
                INSERT INTO order_item (order_id, menu_item_id, quantity)
                VALUES (?, ?, ?)
            """, (order_id, menu_item_id, quantity))

    conn.commit()
    conn.close()


def save_game_play(customer_id, game_instance_id, amount_bet, result):
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO game_play (customer_id, game_instance_id, amount_bet, result)
        VALUES (?, ?, ?, ?)
    """, (customer_id, game_instance_id, amount_bet, result))

    conn.commit()
    conn.close()

def save_booking(room_number, customer, duration_seconds):
    conn = get_db_connection()
    cursor = conn.cursor()
    price = duration_seconds * customer.casino.hotel.price_per_second
    cursor.execute("""
            INSERT INTO room_booking (customer_id, room_number, duration_seconds, price)
            VALUES (?, ?, ?, ?)
    """, (customer.id, room_number, duration_seconds, price))

    conn.commit()
    conn.close()

def save_parking_record(customer_id, slot_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO car_parking (customer_id, slot_id)
        VALUES (?, ?)
    """, (customer_id, slot_id))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()

    return record_id

def close_parking_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE car_parking
        SET end_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()


def save_permanence_record(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO casino_permanence (customer_id)
        VALUES (?)
    """, (customer_id,))

    conn.commit()
    record_id = cursor.lastrowid
    conn.close()

    return record_id

def close_permanence_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE casino_permanence
        SET departure_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (record_id,))

    conn.commit()
    conn.close()

def save_failed_parking(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO failed_parking (customer_id)
        VALUES (?)
    """, (customer_id,))

    conn.commit()
    conn.close()



if __name__ == "__main__":
    create_tables()
