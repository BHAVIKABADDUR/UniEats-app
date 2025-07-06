import sqlite3
import datetime

DB_PATH = 'instance/cafeteria.db'

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def migrate_orders_nullable():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # 1. Create new table with nullable pickup fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                items TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL,
                is_future_order INTEGER NOT NULL DEFAULT 0,
                scheduled_pickup_date TEXT,
                scheduled_pickup_time TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 2. Check if timestamp column exists in old table
        has_timestamp = column_exists(cursor, 'orders', 'timestamp')
        if has_timestamp:
            cursor.execute('''
                INSERT INTO orders_new (id, user_id, items, total_amount, status, is_future_order, scheduled_pickup_date, scheduled_pickup_time, timestamp)
                SELECT id, user_id, items, total_amount, status, is_future_order, scheduled_pickup_date, scheduled_pickup_time, timestamp FROM orders
            ''')
        else:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO orders_new (id, user_id, items, total_amount, status, is_future_order, scheduled_pickup_date, scheduled_pickup_time, timestamp)
                SELECT id, user_id, items, total_amount, status, is_future_order, scheduled_pickup_date, scheduled_pickup_time, ? FROM orders
            ''', (now,))
        # 3. Drop old orders table
        cursor.execute('DROP TABLE orders')
        # 4. Rename new table
        cursor.execute('ALTER TABLE orders_new RENAME TO orders')
        conn.commit()
        print('Migration completed successfully!')
    except Exception as e:
        print('Migration failed:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_orders_nullable() 