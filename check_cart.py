import sqlite3
import os

def check_cart():
    # Connect to the database
    conn = sqlite3.connect('instance/cafeteria.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check cart table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cart'")
    schema = cursor.fetchone()
    print("Cart table schema:")
    print(schema[0])
    print("\nCart table contents:")
    
    # Get cart contents
    cursor.execute('''
        SELECT c.*, m.price, m.image_url
        FROM cart c
        JOIN menu m ON c.item_name = m.name
    ''')
    rows = cursor.fetchall()
    
    if not rows:
        print("No items in cart")
    else:
        for row in rows:
            print(dict(row))
    
    conn.close()

if __name__ == '__main__':
    check_cart() 