import sqlite3
import os

def init_db():
    # Ensure the instance folder exists
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Connect to the database
    conn = sqlite3.connect(os.path.join('instance', 'cafeteria.sqlite'))
    cursor = conn.cursor()
    
    # Drop existing tables to start fresh
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS menu')
    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('DROP TABLE IF EXISTS user_item_interactions')
    cursor.execute('DROP TABLE IF EXISTS cart')
    
    # Create users table with all required columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            reminder_time TEXT
        )
    ''')
    
    # Create menu table with image_url column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            is_veg BOOLEAN,
            category TEXT NOT NULL,
            type TEXT,
            image_url TEXT
        )
    ''')
    
    # Create orders table
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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user_item_interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_item_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert initial menu items with image_url
    menu_items = [
        # Breakfast items
        ('Dosa', 35, 'Crispy South Indian crepe', True, 'breakfast', None, '/static/images/dosa.jpg'),
        ('Idli', 35, 'Steamed rice cakes', True, 'breakfast', None, '/static/images/idli.jpg'),
        ('Puri', 35, 'Deep-fried bread', True, 'breakfast', None, '/static/images/puri.jpg'),
        ('Bonda', 30, 'Spiced potato fritters', True, 'breakfast', None, '/static/images/bonda.jpg'),
        ('Vada', 35, 'Crispy lentil donuts', True, 'breakfast', None, '/static/images/vada.jpg'),
        
        # Veg lunch items
        ('Veg Fried Rice', 60, 'Stir-fried rice with vegetables', True, 'lunch', 'veg', '/static/images/veg-fried-rice.jpg'),
        ('Meals', 70, 'Complete South Indian thali', True, 'lunch', 'veg', '/static/images/meals.jpg'),
        ('Jeera Rice', 50, 'Fragrant cumin rice', True, 'lunch', 'veg', '/static/images/jeera-rice.jpg'),
        ('Manchuria', 60, 'Vegetable dumplings in spicy sauce', True, 'lunch', 'veg', '/static/images/manchuria.jpg'),
        ('Manchurian Fried Rice', 70, 'Rice with vegetable manchurian', True, 'lunch', 'veg', '/static/images/manchurian-fried-rice.jpg'),
        
        # Non-veg lunch items
        ('Egg Fried Rice', 60, 'Stir-fried rice with egg', False, 'lunch', 'non_veg', '/static/images/egg-fried-rice.jpg'),
        ('Chicken Fried Rice', 70, 'Stir-fried rice with chicken', False, 'lunch', 'non_veg', '/static/images/chicken-fried-rice.jpg'),
        ('Omelette', 20, 'Fluffy egg omelette', False, 'lunch', 'non_veg', '/static/images/omelette.jpg'),
        ('Chicken Manchurian', 70, 'Chicken dumplings in spicy sauce', False, 'lunch', 'non_veg', '/static/images/chicken-manchurian.jpg'),
        ('Egg Puff', 30, 'Flaky pastry with egg filling', False, 'lunch', 'non_veg', '/static/images/egg-puff.jpg'),
        ('Chicken Puff', 60, 'Flaky pastry with chicken filling', False, 'lunch', 'non_veg', '/static/images/chicken-puff.jpg'),
        
        # Fresh Juices
        ('Orange Juice', 50, 'Fresh orange juice', True, 'beverages', 'juice', '/static/images/orange-juice.jpg'),
        ('Apple Juice', 55, 'Fresh apple juice', True, 'beverages', 'juice', '/static/images/apple-juice.jpg'),
        ('Pineapple Juice', 50, 'Fresh pineapple juice', True, 'beverages', 'juice', '/static/images/pineapple-juice.jpg'),
        ('Watermelon Juice', 45, 'Fresh watermelon juice', True, 'beverages', 'juice', '/static/images/watermelon-juice.jpg'),
        ('Mosambi Juice', 50, 'Fresh sweet lime juice', True, 'beverages', 'juice', '/static/images/mosambi-juice.jpg'),
        
        # Classic Milkshakes
        ('Vanilla Milkshake', 60, 'Creamy vanilla milkshake', True, 'beverages', 'classic', '/static/images/vanilla-milkshake.jpg'),
        ('Chocolate Milkshake', 70, 'Rich chocolate milkshake', True, 'beverages', 'classic', '/static/images/chocolate-milkshake.jpg'),
        ('Strawberry Milkshake', 70, 'Fresh strawberry milkshake', True, 'beverages', 'classic', '/static/images/strawberry-milkshake.jpg'),
        ('Mango Milkshake', 65, 'Sweet mango milkshake', True, 'beverages', 'classic', '/static/images/mango-milkshake.jpg'),
        ('Banana Milkshake', 60, 'Creamy banana milkshake', True, 'beverages', 'classic', '/static/images/banana-milkshake.jpg'),
        
        # Specialty Milkshakes
        ('KitKat Crunch Milkshake', 100, 'Crunchy KitKat milkshake', True, 'beverages', 'special', '/static/images/kitkat-milkshake.jpg'),
        ('Ferrero Rocher Milkshake', 120, 'Luxurious Ferrero Rocher milkshake', True, 'beverages', 'special', '/static/images/ferrero-milkshake.jpg'),
        ('Blueberry Cheesecake Milkshake', 110, 'Creamy blueberry cheesecake milkshake', True, 'beverages', 'special', '/static/images/blueberry-milkshake.jpg'),
        ('Caramel Popcorn Milkshake', 95, 'Sweet caramel popcorn milkshake', True, 'beverages', 'special', '/static/images/caramel-milkshake.jpg'),
        ('Cold Brew Coffee Milkshake', 90, 'Smooth cold brew coffee milkshake', True, 'beverages', 'special', '/static/images/coldbrew-milkshake.jpg')
    ]
    
    for item in menu_items:
        cursor.execute('''
            INSERT OR IGNORE INTO menu (name, price, description, is_veg, category, type, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', item)
    
    conn.commit()
    conn.close()
    print("✅ Database and tables created successfully!")

if __name__ == '__main__':
    init_db()
