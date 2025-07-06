import sqlite3
import os
from datetime import datetime
from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'cafeteria.sqlite')

def create_future_order_tables():
    """Create or update tables needed for future order functionality"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Create orders table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pickup_time TEXT NOT NULL,
            is_future_order BOOLEAN DEFAULT 0,
            scheduled_pickup_date TEXT,
            scheduled_pickup_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            scheduled_time DATETIME NOT NULL,
            is_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    # Create store_hours table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL,  -- 0 = Sunday, 6 = Saturday
            opening_time TEXT NOT NULL,
            closing_time TEXT NOT NULL,
            is_closed BOOLEAN DEFAULT 0
        )
    ''')

    # Insert default store hours (11 AM to 2 PM, Monday to Saturday)
    days = [(i, '11:00', '14:00', 0) for i in range(1, 7)]  # Monday to Saturday
    days.append((0, '11:00', '14:00', 1))  # Sunday closed
    cursor.executemany('''
        INSERT OR IGNORE INTO store_hours (day_of_week, opening_time, closing_time, is_closed)
        VALUES (?, ?, ?, ?)
    ''', days)

    conn.commit()
    conn.close()
    print("Future order tables created/updated successfully!")

if __name__ == '__main__':
    create_future_order_tables() 