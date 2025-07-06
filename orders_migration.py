import sqlite3
import os
from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'cafeteria.sqlite')

def migrate_orders_table():
    # Create instance directory if it doesn't exist
    os.makedirs(app.instance_path, exist_ok=True)
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    try:
        # Add new columns if they don't exist
        cursor.execute('''
            ALTER TABLE orders ADD COLUMN is_future_order BOOLEAN DEFAULT 0
        ''')
    except sqlite3.OperationalError:
        print("Column is_future_order already exists")
    
    try:
        cursor.execute('''
            ALTER TABLE orders ADD COLUMN scheduled_pickup_date TEXT
        ''')
    except sqlite3.OperationalError:
        print("Column scheduled_pickup_date already exists")
    
    try:
        cursor.execute('''
            ALTER TABLE orders ADD COLUMN scheduled_pickup_time TEXT
        ''')
    except sqlite3.OperationalError:
        print("Column scheduled_pickup_time already exists")
    
    conn.commit()
    conn.close()
    print("Orders table migration completed successfully!")

if __name__ == '__main__':
    migrate_orders_table() 