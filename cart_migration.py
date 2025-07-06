import sqlite3
import os
from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'cafeteria.sqlite')

def migrate_cart_table():
    # Create instance directory if it doesn't exist
    os.makedirs(app.instance_path, exist_ok=True)
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Backup existing cart data
    cursor.execute('SELECT * FROM cart')
    cart_data = cursor.fetchall()
    
    # Drop and recreate cart table with new schema
    cursor.execute('DROP TABLE IF EXISTS cart')
    cursor.execute('''
        CREATE TABLE cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            is_future_order BOOLEAN DEFAULT 0,
            pickup_date TEXT,
            pickup_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, item_name, is_future_order, pickup_date, pickup_time)
        )
    ''')
    
    # Restore cart data if any, setting future order fields to NULL
    if cart_data:
        for item in cart_data:
            cursor.execute('''
                INSERT INTO cart (user_id, item_name, quantity, is_future_order, pickup_date, pickup_time)
                VALUES (?, ?, ?, 0, NULL, NULL)
            ''', (item[1], item[2], item[3]))
    
    conn.commit()
    conn.close()
    print("Cart table migration completed successfully!")

if __name__ == '__main__':
    migrate_cart_table() 