import sqlite3
import os
from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.instance_path, 'cafeteria.sqlite')

DB_PATH = app.config['DATABASE']

ALTERS = [
    "ALTER TABLE cart ADD COLUMN is_future_order INTEGER DEFAULT 0;",
    "ALTER TABLE cart ADD COLUMN pickup_date TEXT;",
    "ALTER TABLE cart ADD COLUMN pickup_time TEXT;"
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Add columns if they do not exist
        if not column_exists(cursor, 'cart', 'is_future_order'):
            cursor.execute(ALTERS[0])
            print('Added is_future_order column.')
        if not column_exists(cursor, 'cart', 'pickup_date'):
            cursor.execute(ALTERS[1])
            print('Added pickup_date column.')
        if not column_exists(cursor, 'cart', 'pickup_time'):
            cursor.execute(ALTERS[2])
            print('Added pickup_time column.')
        conn.commit()
        print('Migration completed successfully.')
    except Exception as e:
        print('Migration failed:', e)
    finally:
        conn.close()

def fix_null_is_future_order():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE cart SET is_future_order = 0 WHERE is_future_order IS NULL;')
        conn.commit()
        print('Updated NULL is_future_order values to 0.')
    except Exception as e:
        print('Failed to update NULL is_future_order:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
    fix_null_is_future_order() 