import sqlite3
import os
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt

# Function to connect to the SQLite database
def connect_db():
    # Define the path to the database file
    db_path = os.path.join(os.path.dirname(__file__), "casino.db")
    return sqlite3.connect(db_path)  # Connect to the database

# Function to plot a bar chart
def plot_bar(x, y, title, xlabel, ylabel):
    # Create a bar chart using the data provided
    plt.figure()
    plt.bar(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Ensure the layout is adjusted properly
    plt.show()  # Display the plot

# Main function that runs the queries and visualizes the results
def main():
    conn = connect_db()  # Connect to the database

    # 1. Gains and Losses per Customer Type
    df_customer = pd.read_sql_query('''
        SELECT c.customer_type,
               AVG(CASE WHEN result = 'lost' THEN amount_bet ELSE NULL END) AS avg_loss,
               AVG(CASE WHEN result = 'won' THEN amount_bet ELSE NULL END) AS avg_gain
        FROM game_play gp
        JOIN customer c ON gp.customer_id = c.id
        GROUP BY c.customer_type;
    ''', conn)
    print("\nAverage Gains and Losses per Customer Type:")
    print(df_customer)
    # Plot the average gain and loss per customer type
    plot_bar(df_customer['customer_type'], df_customer['avg_gain'], "Average Gain per Customer Type", "Customer Type", "Average Gain")
    plot_bar(df_customer['customer_type'], df_customer['avg_loss'], "Average Loss per Customer Type", "Customer Type", "Average Loss")

    # 2. Gains and Losses per Game Type
    df = pd.read_sql_query('''
        SELECT gi.game_name,
               AVG(CASE WHEN result = 'lost' THEN amount_bet ELSE NULL END) AS avg_loss,
               AVG(CASE WHEN result = 'won' THEN amount_bet ELSE NULL END) AS avg_gain
        FROM game_play gp
        JOIN game_instance gi ON gp.game_instance_id = gi.id
        GROUP BY gi.game_name;
    ''', conn)
    print("\nAverage Gains and Losses per Game Type:")
    print(df)
    # Plot the average gain and loss per game type
    plot_bar(df['game_name'], df['avg_gain'], "Average Gain per Game", "Game", "Average Gain")
    plot_bar(df['game_name'], df['avg_loss'], "Average Loss per Game", "Game", "Average Loss")

    # 5. Spending in Bars per Customer Type
    df = pd.read_sql_query('''
        SELECT customer_type, SUM(total_spent) AS total_spent_in_bar
        FROM order_record o
        JOIN customer c ON o.customer_id = c.id
        WHERE place_type = 'bar'
        GROUP BY customer_type;
    ''', conn)

    print("\nSpending in Bars per Customer Type:")
    print(df)
    # Plot total spending in bars per customer type
    plot_bar(df['customer_type'], df['total_spent_in_bar'], "Total Spending in Bars per Customer Type", "Customer Type", "Total Spent")

    # 6. Spending in each Bar/Restaurant
    df = pd.read_sql_query('''
        SELECT o.place_type,
               o.place_id,
               COALESCE(b.name, r.name) AS place_name,
               SUM(o.total_spent) AS total_spent
        FROM order_record o
        LEFT JOIN bar b ON o.place_type = 'bar' AND o.place_id = b.id
        LEFT JOIN restaurant r ON o.place_type = 'restaurant' AND o.place_id = r.id
        GROUP BY o.place_type, o.place_id, place_name;
    ''', conn)
    print("\nSpending in Each Bar/Restaurant:")
    print(df)
    # Plot total spending per bar/restaurant
    plot_bar(df['place_name'], df['total_spent'], "Total Spending per Bar/Restaurant", "Place Name", "Total Spent")

    # 7. Spending in Each Item
    df = pd.read_sql_query('''
        SELECT mi.name, SUM(oi.quantity * mi.price) AS total_spent
        FROM order_item oi
        JOIN menu_item mi ON oi.menu_item_id = mi.id
        GROUP BY mi.name;
    ''', conn)
    print("\nSpending per Item:")
    print(df)
    # Plot total spending per item
    plot_bar(df['name'], df['total_spent'], "Total Spending per Item", "Item", "Total Spent")

    # 8. Quantity of Players per Game
    df = pd.read_sql_query('''
        SELECT gi.game_name, COUNT(DISTINCT customer_id) AS players
        FROM game_play gp
        JOIN game_instance gi ON gp.game_instance_id = gi.id
        GROUP BY gi.game_name;
    ''', conn)
    print("\nQuantity of Players per Game:")
    print(df)
    # Plot number of players per game
    plot_bar(df['game_name'], df['players'], "Quantity of Players per Game", "Game", "Number of Players")

    # 9. Quantity and % of Each Customer Type per Game
    df = pd.read_sql_query('''
        SELECT gi.game_name, c.customer_type, COUNT(*) AS count,
               (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY gi.game_name)) AS percentage
        FROM game_play gp
        JOIN game_instance gi ON gp.game_instance_id = gi.id
        JOIN customer c ON gp.customer_id = c.id
        GROUP BY gi.game_name, c.customer_type;
    ''', conn)
    print("\nDistribution of Customer Types per Game:")
    print(df)

    # 10. Time spent per Type of Customer in the Casino
    df = pd.read_sql_query('''
        SELECT customer_type, AVG(strftime('%s', departure_time) - strftime('%s', arrival_time)) AS avg_seconds_spent
        FROM casino_permanence p
        JOIN customer c ON p.customer_id = c.id
        WHERE departure_time IS NOT NULL
        GROUP BY customer_type;
    ''', conn)
    print("\nAverage Time Spent per Customer Type (seconds):")
    print(df)
    # Plot average time spent per customer type
    plot_bar(df['customer_type'], df['avg_seconds_spent'], "Average Time Spent per Customer Type", "Customer Type", "Average Time (seconds)")

    # 11. Average time cars stayed in parking
    df = pd.read_sql_query('''
        SELECT AVG(strftime('%s', end_time) - strftime('%s', start_time)) AS avg_seconds_in_parking
        FROM car_parking
        WHERE end_time IS NOT NULL;
    ''', conn)
    print("\nAverage Time Cars Stayed in Parking (seconds):")
    print(df)

    # 12. Quantity of people that left because of no parking
    df = pd.read_sql_query('''
        SELECT COUNT(*) AS failed_parking_attempts FROM failed_parking;
    ''', conn)
    print("\nQuantity of People who Couldn't Park:")
    print(df)

    # Query to calculate how many customers have a car
    df = pd.read_sql_query('''
        SELECT COUNT(DISTINCT customer_id) AS customers_with_car
        FROM car_parking;
    ''', conn)

    print("\nNumber of Customers with a Car:")
    print(df)

    conn.close()  # Close the database connection after all operations are done


if __name__ == "__main__":
    main()

