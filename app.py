from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime, timedelta, date
import threading
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1)  # wait a moment for the server to start
    webbrowser.get("C:/Program Files/Google/Chrome/Application/chrome.exe %s").open("http://127.0.0.1:5000")

threading.Thread(target=open_browser).start()


from collections import defaultdict

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Flask app initialization
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['DATABASE'] = os.path.join(app.instance_path, 'cafeteria.sqlite')
app.permanent_session_lifetime = timedelta(minutes=30)

def update_drinks():
    """Add drinks to the menu."""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    # Remove old beverages
    cursor.execute("DELETE FROM menu WHERE category = 'beverages'")
    # Add new drinks
    drinks = [
        # Fresh Juices
        ('Orange Juice', 50, 'Fresh orange juice', True, 'beverages', 'juice', '/static/images/orange-juice.jpg'),
        ('Apple Juice', 55, 'Fresh apple juice', True, 'beverages', 'juice', '/static/images/apple-juice.jpg'),
        ('Pineapple Juice', 50, 'Fresh pineapple juice', True, 'beverages', 'juice', '/static/images/pineapple-juice.jpg'),
        ('Watermelon Juice', 45, 'Fresh watermelon juice', True, 'beverages', 'juice', '/static/images/watermelon-juice.jpg'),
        ('Mosambi Juice', 50, 'Fresh sweet lime juice', True, 'beverages', 'juice', '/static/images/mosambi-juice.jpg'),
        ('Pomegranate Juice', 60, 'Fresh pomegranate juice', True, 'beverages', 'juice', '/static/images/pomegranate-juice.jpg'),
        ('Carrot Juice', 45, 'Fresh carrot juice', True, 'beverages', 'juice', '/static/images/carrot-juice.jpg'),
        ('Beetroot Juice', 55, 'Fresh beetroot juice', True, 'beverages', 'juice', '/static/images/beetroot-juice.jpg'),
        ('Cucumber Mint Juice', 50, 'Cucumber and mint juice', True, 'beverages', 'juice', '/static/images/cucumber-mint-juice.jpg'),
        ('Lemonade', 40, 'Refreshing lemonade', True, 'beverages', 'juice', '/static/images/lemonade.jpg'),
        # Classic Milkshakes
        ('Vanilla Milkshake', 60, 'Creamy vanilla milkshake', True, 'beverages', 'classic', '/static/images/vanilla-milkshake.jpg'),
        ('Chocolate Milkshake', 70, 'Rich chocolate milkshake', True, 'beverages', 'classic', '/static/images/chocolate-milkshake.jpg'),
        ('Strawberry Milkshake', 70, 'Fresh strawberry milkshake', True, 'beverages', 'classic', '/static/images/strawberry-milkshake.jpg'),
        ('Mango Milkshake', 65, 'Sweet mango milkshake', True, 'beverages', 'classic', '/static/images/mango-milkshake.jpg'),
        ('Banana Milkshake', 60, 'Creamy banana milkshake', True, 'beverages', 'classic', '/static/images/banana-milkshake.jpg'),
        ('Pista Milkshake', 75, 'Pistachio milkshake', True, 'beverages', 'classic', '/static/images/pista-milkshake.jpg'),
        ('Badam Milkshake', 75, 'Almond milkshake', True, 'beverages', 'classic', '/static/images/badam-milkshake.jpg'),
        ('Rose Milkshake', 65, 'Rose-flavored milkshake', True, 'beverages', 'classic', '/static/images/rose-milkshake.jpg'),
        ('Coffee Milkshake', 70, 'Coffee-flavored milkshake', True, 'beverages', 'classic', '/static/images/coffee-milkshake.jpg'),
        ('Oreo Milkshake', 80, 'Oreo cookie milkshake', True, 'beverages', 'classic', '/static/images/oreo-milkshake.jpg'),
        # Specialty Milkshakes
        ('KitKat Crunch Milkshake', 100, 'KitKat chocolate milkshake', True, 'beverages', 'special', '/static/images/kitkat-milkshake.jpg'),
        ('Ferrero Rocher Milkshake', 120, 'Ferrero Rocher milkshake', True, 'beverages', 'special', '/static/images/ferrero-milkshake.jpg'),
        ('Blueberry Cheesecake Milkshake', 110, 'Blueberry cheesecake milkshake', True, 'beverages', 'special', '/static/images/blueberry-milkshake.jpg'),
        ('Caramel Popcorn Milkshake', 95, 'Caramel popcorn milkshake', True, 'beverages', 'special', '/static/images/caramel-milkshake.jpg'),
        ('Cold Brew Milkshake', 90, 'Cold brew milkshake', True, 'beverages', 'special', '/static/images/coldbrew-milkshake.jpg'),
    ]
    cursor.executemany('INSERT INTO menu (name, price, description, is_veg, category, type, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)', drinks)
    conn.commit()
    conn.close()

def standardize_menu_categories():
    """Standardize all menu item categories."""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    category_map = {
        'breakfast': 'breakfast',
        'Breakfast': 'breakfast',
        'BREAKFAST': 'breakfast',
        'lunch': 'lunch',
        'Lunch': 'lunch',
        'LUNCH': 'lunch',
        'veg_lunch': 'lunch',
        'non_veg_lunch': 'lunch',
        'beverages': 'beverages',
        'Beverages': 'beverages',
        'BEVERAGES': 'beverages',
        'juice': 'beverages',
        'Juice': 'beverages',
        'JUICE': 'beverages'
    }
    
    # First, check current categories
    cursor.execute('SELECT DISTINCT category FROM menu')
    current_categories = [row[0] for row in cursor.fetchall()]
    print(f"[DEBUG] Current categories before standardization: {current_categories}")
    
    # Update categories
    cursor.execute('SELECT name, category FROM menu')
    items = cursor.fetchall()
    for name, category in items:
        std_category = category_map.get(category, category.lower())
        cursor.execute('UPDATE menu SET category = ? WHERE name = ?', (std_category, name))
        print(f"[DEBUG] Standardized category for {name}: {category} -> {std_category}")
    
    # Verify changes
    cursor.execute('SELECT DISTINCT category FROM menu')
    updated_categories = [row[0] for row in cursor.fetchall()]
    print(f"[DEBUG] Categories after standardization: {updated_categories}")
    
    conn.commit()
    conn.close()

def fix_item_names_in_interactions():
    """Fix inconsistencies in item names."""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Get all distinct item names from both tables
    cursor.execute('SELECT DISTINCT item_name FROM user_item_interactions')
    interaction_items = {row[0] for row in cursor.fetchall()}
    
    cursor.execute('SELECT name FROM menu')
    menu_items = {row[0] for row in cursor.fetchall()}
    
    print(f"[DEBUG] Items in interactions: {interaction_items}")
    print(f"[DEBUG] Items in menu: {menu_items}")
    
    # Fix any mismatches
    for int_item in interaction_items:
        if int_item not in menu_items:
            matches = [menu_item for menu_item in menu_items 
                      if menu_item.lower() == int_item.lower()]
            if matches:
                cursor.execute('''
                    UPDATE user_item_interactions 
                    SET item_name = ? 
                    WHERE item_name = ?
                ''', (matches[0], int_item))
                print(f"[DEBUG] Fixed item name: {int_item} -> {matches[0]}")
    
    conn.commit()
    conn.close()

def init_db():
    """Initialize the database with required tables."""
    os.makedirs(app.instance_path, exist_ok=True)
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Create users table first since other tables reference it
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    # Create user_preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            preference_type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create user_item_interactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_item_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
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
            pickup_time DATETIME,
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
            notification_type TEXT NOT NULL,
            is_acknowledged BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    ''')

    # Create cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
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

    # Create menu table if it doesn't exist
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
    
    conn.commit()
    conn.close()

def initialize_app():
    """Initialize the app with necessary setup."""
    init_db()
    update_drinks()  # Add drinks to the menu
    standardize_menu_categories()
    fix_item_names_in_interactions()
    print("[DEBUG] App initialization completed")

# Initialize the app
initialize_app()

# Password hashing setup
bcrypt = Bcrypt(app)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def update_breakfast_lunch_images():
    """
    Utility function to set image_url for breakfast and lunch items if images exist in static/images/.
    """
    import os
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    # Map item names to image filenames (final menu items only)
    image_map = {
        # Breakfast
        'Dosa': 'dosa.jpg',
        'Idli': 'idli.jpg',
        'Vada': 'vada.jpg',
        'Bonda': 'bonda.jpg',
        'Puri': 'puri.jpg',
        # Lunch
        'Veg Fried Rice': 'veg-fried-rice.jpg',
        'Veg Noodles': 'veg-noodles.jpg',
        'Manchurian Fried Rice': 'manchurian-fried-rice.jpg',
        'Manchuria': 'manchuria.jpg',
        'Jeera rice': 'jeera-rice.jpg',
        'Meals': 'meals.jpg',
        'Chicken Manchurian': 'chicken-manchurian.jpg',
        'Egg puff': 'egg-puff.jpg',
        'Chicken puff': 'chicken-puff.jpg',
        'Chicken Fried Rice': 'chicken-fried-rice.jpg',
        'Egg Fried Rice': 'egg-fried-rice.jpg',
        'Chicken Noodles': 'chicken-noodles.jpg',
        'Egg Noodles': 'egg-noodles.jpg',
        'Omelette': 'omelette.jpg',
    }
    for item, filename in image_map.items():
        image_path = f'static/images/{filename}'
        if os.path.exists(image_path):
            cursor.execute('UPDATE menu SET image_url = ? WHERE name = ?', (f'/{image_path}', item))
    conn.commit()
    conn.close()

@app.route('/admin/update_breakfast_lunch_images')
def admin_update_breakfast_lunch_images():
    update_breakfast_lunch_images()
    return "Breakfast and lunch images updated!"

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify the order belongs to the current user
    cursor.execute('SELECT user_id FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    if not order or order[0] != session['user_id']:
        conn.close()
        return jsonify({'success': False, 'message': 'Order not found or unauthorized'})
    
    try:
        # Cancel the order
        cursor.execute('UPDATE orders SET status = "cancelled" WHERE id = ?', (order_id,))
        
        # Cancel any associated notifications
        cursor.execute('DELETE FROM notifications WHERE order_id = ?', (order_id,))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/running_late/<int:order_id>', methods=['POST'])
@login_required
def running_late(order_id):
    delay_minutes = int(request.form.get('delay_minutes', 15))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the order details
        cursor.execute('''
            SELECT user_id, scheduled_pickup_date, scheduled_pickup_time
            FROM orders 
            WHERE id = ? AND user_id = ?
        ''', (order_id, session['user_id']))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'})
        
        # Calculate new pickup time
        pickup_datetime = datetime.strptime(f"{order[1]} {order[2]}", "%Y-%m-%d %H:%M")
        new_pickup_time = pickup_datetime + timedelta(minutes=delay_minutes)
        
        # Update order pickup time
        cursor.execute('''
            UPDATE orders 
            SET scheduled_pickup_time = ?
            WHERE id = ?
        ''', (new_pickup_time.strftime("%H:%M"), order_id))
        
        # Update notification time
        reminder_time = new_pickup_time - timedelta(minutes=15)
        cursor.execute('''
            UPDATE notifications
            SET scheduled_time = ?
            WHERE order_id = ? AND is_sent = 0
        ''', (reminder_time.strftime("%Y-%m-%d %H:%M:%S"), order_id))
        
        conn.commit()
        
        # Send notification to staff
        staff_notification = f"Order #{order_id} pickup delayed by {delay_minutes} minutes. New pickup time: {new_pickup_time.strftime('%I:%M %p')}"
        cursor.execute('''
            INSERT INTO notifications (user_id, order_id, message, scheduled_time, is_sent, notification_type)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1, ?, ?)
        ''', (session['user_id'], order_id, staff_notification, 'running_late'))
        
        conn.commit()
        conn.close()
        
        flash('Pickup time updated successfully!', 'success')
        return redirect(url_for('pending_orders'))
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)})

def get_category_specific_recommendations(user_id, category, limit=5):
    import random
    from sklearn.neighbors import NearestNeighbors
    
    # Auto-clean data before generating recommendations
    auto_clean_data()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Map category variations
        category_mapping = {
            'breakfast': 'breakfast', 'Breakfast': 'breakfast', 'BREAKFAST': 'breakfast',
            'lunch': 'lunch', 'Lunch': 'lunch', 'LUNCH': 'lunch', 'veg_lunch': 'lunch', 'non_veg_lunch': 'lunch',
            'beverages': 'beverages', 'Beverages': 'beverages', 'BEVERAGES': 'beverages',
            'juice': 'beverages', 'Juice': 'beverages', 'JUICE': 'beverages'
        }
        standardized_category = category_mapping.get(category, category.lower())
        
        # Get not interested items
        cursor.execute('SELECT item_name FROM user_preferences WHERE user_id = ? AND preference_type = ?', (user_id, 'not_interested'))
        not_interested = {row[0].lower() for row in cursor.fetchall()}
        
        # Get all users who have ordered in this category
        cursor.execute('''
            SELECT DISTINCT ui.user_id 
            FROM user_item_interactions ui 
            JOIN menu m ON LOWER(ui.item_name) = LOWER(m.name) 
            WHERE LOWER(m.category) = LOWER(?)
        ''', (standardized_category,))
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Get all items in this category
        cursor.execute('SELECT name FROM menu WHERE LOWER(category) = LOWER(?)', (standardized_category,))
        item_names = [row[0] for row in cursor.fetchall()]
        
        # Create user and item index mappings
        user_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        item_idx = {iname: idx for idx, iname in enumerate(item_names)}
        
        # Build user-item matrix
        matrix = np.zeros((len(user_ids), len(item_names)), dtype=int)
        cursor.execute('''
            SELECT ui.user_id, ui.item_name, COUNT(*) as order_count 
            FROM user_item_interactions ui 
            JOIN menu m ON LOWER(ui.item_name) = LOWER(m.name) 
            WHERE LOWER(m.category) = LOWER(?) 
            GROUP BY ui.user_id, ui.item_name
        ''', (standardized_category,))
        
        for row in cursor.fetchall():
            uid, iname, count = row
            if uid in user_idx and iname in item_idx:
                matrix[user_idx[uid], item_idx[iname]] = count
        
        recommendations = []
        recommended_names = set()
        
        # 1. User's own most-ordered items (Personal History)
        cursor.execute('''
            SELECT m.name, COUNT(*) as order_count
            FROM user_item_interactions ui
            JOIN menu m ON LOWER(ui.item_name) = LOWER(m.name)
            WHERE ui.user_id = ? AND LOWER(m.category) = LOWER(?)
            GROUP BY m.name
            ORDER BY order_count DESC, MAX(ui.timestamp) DESC
        ''', (user_id, standardized_category))
        
        past_orders = cursor.fetchall()
        print(f"[DEBUG] User {user_id} past orders in {category}: {past_orders}")
        
        for item_name, count in past_orders:
            if (item_name.lower() not in not_interested and 
                item_name not in recommended_names and 
                len(recommendations) < limit):
                
                cursor.execute('''
                    SELECT name, price, description, is_veg, category, type, image_url 
                    FROM menu WHERE name = ?
                ''', (item_name,))
                item = cursor.fetchone()
                if item:
                    recommendations.append({
                        'name': item[0], 'price': item[1], 'description': item[2], 
                        'is_veg': item[3], 'category': item[4], 'type': item[5], 'image_url': item[6]
                    })
                    recommended_names.add(item[0])
                    print(f"[DEBUG] Added personal recommendation: {item_name} (count: {count})")
        
        # 2. Collaborative Filtering (ML: Nearest Neighbors)
        if user_id in user_idx and len(user_ids) > 1 and len(recommendations) < limit:
            nn = NearestNeighbors(n_neighbors=min(4, len(user_ids)), metric='cosine')
            nn.fit(matrix)
            user_vector = matrix[user_idx[user_id]].reshape(1, -1)
            distances, indices = nn.kneighbors(user_vector)
            
            # Get similar users (excluding self)
            neighbor_indices = [idx for idx in indices[0] if idx != user_idx[user_id]][:3]
            
            # Get items the user has already ordered
            user_items = set([item_names[i] for i, val in enumerate(matrix[user_idx[user_id]]) if val > 0])
            
            # Get items from similar users
            neighbor_items = set()
            for nidx in neighbor_indices:
                for i, val in enumerate(matrix[nidx]):
                    if (val > 0 and 
                        item_names[i] not in user_items and 
                        item_names[i].lower() not in not_interested and 
                        item_names[i] not in recommended_names):
                        neighbor_items.add(item_names[i])
            
            for item_name in neighbor_items:
                if len(recommendations) >= limit:
                    break
                cursor.execute('''
                    SELECT name, price, description, is_veg, category, type, image_url 
                    FROM menu WHERE name = ?
                ''', (item_name,))
                item = cursor.fetchone()
                if item:
                    recommendations.append({
                        'name': item[0], 'price': item[1], 'description': item[2], 
                        'is_veg': item[3], 'category': item[4], 'type': item[5], 'image_url': item[6]
                    })
                    recommended_names.add(item[0])
                    print(f"[DEBUG] Added ML recommendation: {item_name}")
        
        # 3. Most Popular Items (All Users)
        if len(recommendations) < limit:
            cursor.execute('''
                SELECT m.name, COUNT(*) as order_count 
                FROM user_item_interactions ui 
                JOIN menu m ON LOWER(ui.item_name) = LOWER(m.name) 
                WHERE LOWER(m.category) = LOWER(?) 
                GROUP BY m.name 
                ORDER BY order_count DESC
            ''', (standardized_category,))
            popular_items = cursor.fetchall()
            
            for item_name, count in popular_items:
                if (item_name.lower() not in not_interested and 
                    item_name not in recommended_names and 
                    len(recommendations) < limit):
                    
                    cursor.execute('''
                        SELECT name, price, description, is_veg, category, type, image_url 
                        FROM menu WHERE name = ?
                    ''', (item_name,))
                    item = cursor.fetchone()
                    if item:
                        recommendations.append({
                            'name': item[0], 'price': item[1], 'description': item[2], 
                            'is_veg': item[3], 'category': item[4], 'type': item[5], 'image_url': item[6]
                        })
                        recommended_names.add(item[0])
                        print(f"[DEBUG] Added popular recommendation: {item_name} (count: {count})")
        
        # 4. Random Items (Fallback)
        if len(recommendations) < limit:
            cursor.execute('''
                SELECT name, price, description, is_veg, category, type, image_url 
                FROM menu WHERE LOWER(category) = LOWER(?)
            ''', (standardized_category,))
            all_items = cursor.fetchall()
            random.shuffle(all_items)
            
            for item in all_items:
                if (item[0].lower() not in not_interested and 
                    item[0] not in recommended_names and 
                    len(recommendations) < limit):
                    
                    recommendations.append({
                        'name': item[0], 'price': item[1], 'description': item[2], 
                        'is_veg': item[3], 'category': item[4], 'type': item[5], 'image_url': item[6]
                    })
                    recommended_names.add(item[0])
                    print(f"[DEBUG] Added random recommendation: {item[0]}")
        
        print(f"[DEBUG] Final recommendations for user {user_id} in {category}: {[r['name'] for r in recommendations]}")
        return recommendations
        
    finally:
        conn.close()

@app.route('/get_time_slots')
def get_time_slots():
    slots = generate_time_slots()
    return jsonify(slots)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get cart items
        cursor.execute('''
            SELECT c.item_name, c.quantity, m.price, c.is_future_order,
                   c.pickup_date, c.pickup_time
            FROM cart c
            JOIN menu m ON c.item_name = m.name
            WHERE c.user_id = ?
        ''', (user_id,))
        
        cart_items = cursor.fetchall()
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Group items by pickup time
        future_orders = {}
        regular_items = []
        
        for item in cart_items:
            if item[3]:  # is_future_order
                key = f"{item[4]} {item[5]}"
                if key not in future_orders:
                    future_orders[key] = []
                future_orders[key].append({
                    'name': item[0],
                    'quantity': item[1],
                    'price': item[2]
                })
            else:
                regular_items.append({
                    'name': item[0],
                    'quantity': item[1],
                    'price': item[2]
                })
        
        # Process regular items (immediate orders)
        if regular_items:
            regular_total = sum(item['quantity'] * item['price'] for item in regular_items)
            cursor.execute('''
                INSERT INTO orders (
                    user_id, items, total_amount, status, timestamp, pickup_time
                ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, datetime('now'))
            ''', (
                user_id,
                json.dumps(regular_items),
                regular_total,
                'completed'
            ))
            print(f"[DEBUG] Inserted immediate order: user_id={user_id}, items={regular_items}, total={regular_total}")
        
        # Process future orders
        for pickup_time, items in future_orders.items():
            pickup_date, pickup_time = pickup_time.split(' ')
            future_total = sum(item['quantity'] * item['price'] for item in items)
            if not pickup_date or not pickup_time:
                continue  # skip if missing
            cursor.execute('''
                INSERT INTO orders (
                    user_id, items, total_amount, status,
                    is_future_order, scheduled_pickup_date,
                    scheduled_pickup_time, pickup_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                user_id,
                json.dumps(items),
                future_total,
                'pending',
                1,
                pickup_date,
                pickup_time
            ))
            order_id = cursor.lastrowid
            print(f"[DEBUG] Inserted future order: user_id={user_id}, items={items}, total={future_total}, pickup_date={pickup_date}, pickup_time={pickup_time}")
            # Calculate reminder time (15 minutes before pickup)
            pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
            reminder_time = pickup_datetime - timedelta(minutes=15)
            cursor.execute('''
                INSERT INTO notifications (
                    user_id, order_id, message, scheduled_time, is_sent,
                    notification_type, is_acknowledged
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                order_id,
                f"Your order #{order_id} will be ready for pickup in 15 minutes!",
                reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
                0,
                'reminder',
                0
            ))
        # Clear the cart
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        # Decide redirect target
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Order placed successfully',
                'redirect': url_for('pending_orders') if future_orders else url_for('order_confirmation', pending=0)
            })
        else:
            if future_orders:
                return redirect(url_for('pending_orders'))
            else:
                return redirect(url_for('order_confirmation', pending=0))
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/order_confirmation')
def order_confirmation():
    show_pending_orders_button = request.args.get('pending', '0') == '1'
    return render_template('order_confirmation.html', show_pending_orders_button=show_pending_orders_button)

def check_and_send_notifications():
    """Check for notifications that need to be sent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = datetime.now()

    # Get orders that are scheduled for pickup
    cursor.execute('''
        SELECT o.id, o.user_id, o.scheduled_pickup_date, o.scheduled_pickup_time, o.status
        FROM orders o
        WHERE o.status = 'scheduled'
        AND o.is_future_order = 1
    ''')
    scheduled_orders = cursor.fetchall()

    for order in scheduled_orders:
        pickup_datetime_str = f"{order['scheduled_pickup_date']} {order['scheduled_pickup_time']}"
        pickup_datetime = datetime.strptime(pickup_datetime_str, "%Y-%m-%d %H:%M")
        
        # Check for reminder notification (15 minutes before pickup)
        reminder_time = pickup_datetime - timedelta(minutes=15)
        if current_time >= reminder_time and current_time <= pickup_datetime:
            # Check if reminder notification already exists
            cursor.execute('''
                SELECT id FROM notifications
                WHERE order_id = ? AND notification_type = 'reminder' AND is_sent = 0
            ''', (order['id'],))
            if not cursor.fetchone():
                # Create reminder notification
                cursor.execute('''
                    INSERT INTO notifications (
                        user_id, order_id, message, scheduled_time, is_sent,
                        notification_type
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    order['user_id'],
                    order['id'],
                    f"Your order #{order['id']} will be ready for pickup in 15 minutes!",
                    reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
                    0,
                    'reminder'
                ))

        # Check for running late notification (5 minutes after pickup time)
        late_notification_time = pickup_datetime + timedelta(minutes=5)
        if current_time >= late_notification_time:
            # Check if running late notification already exists
            cursor.execute('''
                SELECT id FROM notifications
                WHERE order_id = ? AND notification_type = 'running_late' AND is_sent = 0
            ''', (order['id'],))
            if not cursor.fetchone():
                # Create running late notification
                cursor.execute('''
                    INSERT INTO notifications (
                        user_id, order_id, message, scheduled_time, is_sent,
                        notification_type
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    order['user_id'],
                    order['id'],
                    f"Your order #{order['id']} is ready for pickup. Are you running late?",
                    late_notification_time.strftime("%Y-%m-%d %H:%M:%S"),
                    0,
                    'running_late'
                ))

    conn.commit()
    conn.close()

# Add the notification check job to the scheduler
scheduler.add_job(
    func=check_and_send_notifications,
    trigger='interval',
    minutes=1,
    id='check_notifications'
)

@app.route('/check_notifications')
@login_required
def check_notifications():
    """Check for pending notifications for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        current_time = datetime.now()
        # Get notifications that are due and not sent
        cursor.execute('''
            SELECT n.id, n.order_id, n.message, n.notification_type
            FROM notifications n
            WHERE n.user_id = ? 
            AND n.is_sent = 0 
            AND n.scheduled_time <= ?
        ''', (user_id, current_time.strftime("%Y-%m-%d %H:%M:%S")))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'order_id': row[1],
                'message': row[2],
                'type': row[3]
            })
        
        return jsonify({'notifications': notifications})
        
    except Exception as e:
        print(f"Error checking notifications: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
        
    finally:
        conn.close()

@app.route('/mark_notifications_sent', methods=['POST'])
@login_required
def mark_notifications_sent():
    """Mark notifications as sent and acknowledged"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        order_id = data.get('order_id')
    else:
        order_id = request.form.get('order_id')
    
    if not order_id:
        return jsonify({'error': 'No order ID provided'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Mark notifications as sent and acknowledged
        cursor.execute('''
            UPDATE notifications 
            SET is_sent = 1, is_acknowledged = 1
            WHERE order_id = ? AND user_id = ? AND is_sent = 0
        ''', (order_id, user_id))
        
        # Update order status if it was a running late notification
        cursor.execute('''
            UPDATE orders
            SET status = 'processing'
            WHERE id = ? AND user_id = ? AND status = 'scheduled'
        ''', (order_id, user_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error marking notifications: {str(e)}")
        conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
        
    finally:
        conn.close()

@app.route('/clear_notification/<int:notification_id>', methods=['POST'])
@login_required
def clear_notification():
    """Clear a specific notification without taking any action"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    notification_id = request.view_args.get('notification_id')
    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify the notification belongs to the user
        cursor.execute('''
            SELECT id FROM notifications 
            WHERE id = ? AND user_id = ? AND is_sent = 0
        ''', (notification_id, user_id))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Notification not found or unauthorized'}), 404
        
        # Mark the notification as sent and acknowledged
        cursor.execute('''
            UPDATE notifications 
            SET is_sent = 1, is_acknowledged = 1
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        
        conn.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error clearing notification: {str(e)}")
        conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
        
    finally:
        conn.close()

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def generate_time_slots():
    """Generate available time slots for orders."""
    # Get current time
    now = datetime.now()
    current_time = now.time()
    current_date = now.date()
    
    # Define cafeteria operating hours
    opening_time = datetime.strptime('08:00', '%H:%M').time()
    closing_time = datetime.strptime('20:00', '%H:%M').time()
    
    # Generate slots at 15-minute intervals
    time_slots = []
    dates = [current_date + timedelta(days=i) for i in range(3)]  # Allow booking for next 3 days
    
    for date in dates:
        slot_time = datetime.combine(date, opening_time)
        end_time = datetime.combine(date, closing_time)
        
        while slot_time < end_time:
            # For current date, only show future slots
            if date == current_date and slot_time.time() <= current_time:
                slot_time += timedelta(minutes=15)
                continue
                
            time_slots.append({
                'date': date.strftime('%Y-%m-%d'),
                'time': slot_time.strftime('%H:%M'),
                'display_time': slot_time.strftime('%I:%M %p'),
                'display_date': date.strftime('%B %d, %Y')
            })
            slot_time += timedelta(minutes=15)
    
    return time_slots

@app.route('/')
def welcome():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('welcome.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE student_id = ?', (student_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session.permanent = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        
        flash('Invalid student ID or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Use bcrypt for password hashing instead of Werkzeug's generate_password_hash
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute(
                'INSERT INTO users (student_id, name, email, password) VALUES (?, ?, ?, ?)',
                (student_id, name, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Student ID already exists!', 'error')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('welcome'))

@app.route('/menu')
@login_required
def menu():
    category = request.args.get('category', 'all')
    search_query = request.args.get('q', '').strip()
    
    # If there's a search query, redirect to search results page
    if search_query:
        return redirect(url_for('search_results', q=search_query))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    recommendations = []
    not_interested = []
    likes = []
    if category == 'all':
        cursor.execute('SELECT * FROM menu')
        menu_items = cursor.fetchall()
        conn.close()
        return render_template('menu.html', menu_items=menu_items, category=category)
    elif category.lower() in ['beverages', 'juice']:
        cursor.execute('SELECT * FROM menu WHERE LOWER(category) IN (?, ?)', ('beverages', 'juice'))
        menu_items = cursor.fetchall()
        # Group by type
        grouped = {'juice': [], 'classic': [], 'special': []}
        for item in menu_items:
            if item['type'] == 'juice':
                grouped['juice'].append(item)
            elif item['type'] == 'classic':
                grouped['classic'].append(item)
            elif item['type'] == 'special':
                grouped['special'].append(item)
        # Get recommendations for this user and beverages category
        recommendations = get_category_specific_recommendations(session['user_id'], 'beverages', limit=6)
        # Get not interested and likes for this user
        cursor.execute('SELECT item_name FROM user_preferences WHERE user_id = ? AND preference_type = "not_interested"', (session['user_id'],))
        not_interested = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT item_name FROM user_preferences WHERE user_id = ? AND preference_type = "like"', (session['user_id'],))
        likes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('menu_juice.html', juices=grouped['juice'], classics=grouped['classic'], specials=grouped['special'], category=category, recommendations=recommendations, not_interested=not_interested, likes=likes)
    else:
        cursor.execute('SELECT * FROM menu WHERE LOWER(category) = LOWER(?)', (category,))
        menu_items = cursor.fetchall()
        # Get recommendations for this user and category
        recommendations = get_category_specific_recommendations(session['user_id'], category, limit=6)
        # Get not interested and likes for this user
        cursor.execute('SELECT item_name FROM user_preferences WHERE user_id = ? AND preference_type = "not_interested"', (session['user_id'],))
        not_interested = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT item_name FROM user_preferences WHERE user_id = ? AND preference_type = "like"', (session['user_id'],))
        likes = [row[0] for row in cursor.fetchall()]
        conn.close()
        if category.lower() == 'lunch':
            return render_template('menu_lunch.html', menu_items=menu_items, category=category, recommendations=recommendations, not_interested=not_interested, likes=likes)
        elif category.lower() == 'breakfast':
            return render_template('menu_breakfast.html', menu_items=menu_items, category=category, recommendations=recommendations, not_interested=not_interested, likes=likes)
        return render_template('menu.html', menu_items=menu_items, category=category, recommendations=recommendations, not_interested=not_interested, likes=likes)

@app.route('/search')
@login_required
def search_results():
    search_query = request.args.get('q', '').strip()
    
    if not search_query:
        return redirect(url_for('menu'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Search in both name and description
    cursor.execute('SELECT * FROM menu WHERE name LIKE ? OR description LIKE ?', (f'%{search_query}%', f'%{search_query}%'))
    menu_items = cursor.fetchall()
    
    conn.close()
    
    return render_template('search_results.html', menu_items=menu_items, search_query=search_query)

@app.route('/cart')
@login_required
def cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.*, m.price, m.name, m.description, m.is_veg, m.category, m.image_url
        FROM cart c
        JOIN menu m ON c.item_name = m.name
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    
    cart_items = cursor.fetchall()
    total = sum(item['quantity'] * item['price'] for item in cart_items)
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_id = session['user_id']
    
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        item_name = clean_item_name(data.get('item_name', ''))
        quantity = int(data.get('quantity', 1))
        is_future_order = data.get('is_future_order', False)
        pickup_date = data.get('pickup_date', '')
        pickup_time = data.get('pickup_time', '')
    else:
        # Handle form data
        item_name = clean_item_name(request.form.get('item_name', ''))
        quantity = int(request.form.get('quantity', 1))
        is_future_order = request.form.get('is_future_order', 'false') == 'true'
        pickup_date = request.form.get('pickup_date', '')
        pickup_time = request.form.get('pickup_time', '')
    
    if not item_name:
        if request.is_json:
            return jsonify({'error': 'Item name is required'}), 400
        else:
            flash('Item name is required', 'error')
            return redirect(request.referrer or url_for('menu'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if item exists in menu
        cursor.execute('SELECT * FROM menu WHERE name = ?', (item_name,))
        menu_item = cursor.fetchone()
        
        if not menu_item:
            return jsonify({'error': 'Item not found in menu'}), 404
        
        # Check if item is already in cart
        cursor.execute('SELECT quantity FROM cart WHERE user_id = ? AND item_name = ? AND is_future_order = ? AND pickup_date = ? AND pickup_time = ?', 
                      (user_id, item_name, is_future_order, pickup_date, pickup_time))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item[0] + quantity
            cursor.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND item_name = ? AND is_future_order = ? AND pickup_date = ? AND pickup_time = ?', 
                          (new_quantity, user_id, item_name, is_future_order, pickup_date, pickup_time))
        else:
            # Add new item to cart
            cursor.execute('INSERT INTO cart (user_id, item_name, quantity, is_future_order, pickup_date, pickup_time) VALUES (?, ?, ?, ?, ?, ?)', 
                          (user_id, item_name, quantity, is_future_order, pickup_date, pickup_time))
        
        # Record interaction for recommendations
        cursor.execute('INSERT INTO user_item_interactions (user_id, item_name) VALUES (?, ?)', (user_id, item_name))
        
        conn.commit()
        
        if request.is_json:
            return jsonify({'message': 'Item added to cart successfully'})
        else:
            flash('Item added to cart successfully!', 'success')
            return redirect(url_for('cart'))
        
    except Exception as e:
        conn.rollback()
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error adding item to cart: {str(e)}', 'error')
            return redirect(request.referrer or url_for('menu'))
    finally:
        conn.close()

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    # Handle both JSON and form POSTs, but default to form POST
    if request.is_json:
        data = request.get_json()
        item_name = data.get('item_name')
        quantity = int(data.get('quantity', 1))
        is_future_order = data.get('is_future_order', False)
        pickup_date = data.get('pickup_date')
        pickup_time = data.get('pickup_time')
    else:
        item_name = request.form.get('item_name')
        quantity = int(request.form.get('quantity', 1))
        is_future_order = request.form.get('is_future_order', 'false') == 'true'
        pickup_date = request.form.get('pickup_date')
        pickup_time = request.form.get('pickup_time')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if quantity > 0:
            cursor.execute('''
                UPDATE cart 
                SET quantity = ? 
                WHERE user_id = ? AND item_name = ? AND is_future_order = ? AND pickup_date IS ?
                AND pickup_time IS ?
            ''', (quantity, session['user_id'], item_name, is_future_order, pickup_date, pickup_time))
        else:
            cursor.execute('''
                DELETE FROM cart 
                WHERE user_id = ? AND item_name = ? AND is_future_order = ? AND pickup_date IS ?
                AND pickup_time IS ?
            ''', (session['user_id'], item_name, is_future_order, pickup_date, pickup_time))
        conn.commit()
        if request.is_json:
            return jsonify({'success': True})
        else:
            return redirect(url_for('cart'))
    except Exception as e:
        print(f"Error updating cart: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        else:
            return redirect(url_for('cart'))
    finally:
        conn.close()

@app.route('/pending_orders')
@login_required
def pending_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        AND is_future_order = 1
        AND status = 'pending'
        AND (scheduled_pickup_date || ' ' || scheduled_pickup_time) > ?
        ORDER BY scheduled_pickup_date, scheduled_pickup_time
    ''', (session['user_id'], now))
    orders = cursor.fetchall()
    detailed_orders = []
    for order in orders:
        # Parse the items JSON field
        try:
            items = json.loads(order['items'])
        except Exception:
            items = []
        
        # Format pickup date and time for display
        formatted_pickup_time = None
        if order['scheduled_pickup_date'] and order['scheduled_pickup_time']:
            try:
                pickup_datetime = datetime.strptime(
                    f"{order['scheduled_pickup_date']} {order['scheduled_pickup_time']}", 
                    '%Y-%m-%d %H:%M'
                )
                formatted_pickup_time = pickup_datetime.strftime('%B %d, %Y at %I:%M %p')
            except ValueError:
                formatted_pickup_time = f"{order['scheduled_pickup_date']} {order['scheduled_pickup_time']}"
        
        detailed_orders.append({
            **dict(order),
            'order_items': items,
            'formatted_pickup_time': formatted_pickup_time
        })
    conn.close()
    return render_template('pending_orders.html', orders=detailed_orders)

@app.route('/order_history')
@login_required
def order_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        AND status = 'completed'
        ORDER BY timestamp DESC
    ''', (session['user_id'],))
    orders = cursor.fetchall()
    print("Orders fetched for history:", [dict(order) for order in orders])
    # Parse items and fetch details for each order
    detailed_orders = []
    for order in orders:
        try:
            items = json.loads(order['items'])
        except Exception:
            items = []
        detailed_items = []
        for item in items:
            if isinstance(item, dict):
                item_name = item.get('name', item.get('item_name', ''))
                quantity = item.get('quantity', 1)
            else:
                item_name = str(item)
                quantity = 1
            cursor.execute('SELECT price, image_url FROM menu WHERE name = ?', (item_name,))
            menu_item = cursor.fetchone()
            price = menu_item['price'] if menu_item else 0
            image_url = menu_item['image_url'] if menu_item else ''
            detailed_items.append({
                'name': item_name,
                'quantity': quantity,
                'price': price,
                'image_url': image_url
            })
        # Format pickup date and time for future orders
        formatted_pickup_time = None
        if order['is_future_order'] and order['scheduled_pickup_date'] and order['scheduled_pickup_time']:
            try:
                pickup_datetime = datetime.strptime(
                    f"{order['scheduled_pickup_date']} {order['scheduled_pickup_time']}", 
                    '%Y-%m-%d %H:%M'
                )
                formatted_pickup_time = pickup_datetime.strftime('%B %d, %Y at %I:%M %p')
            except ValueError:
                formatted_pickup_time = f"{order['scheduled_pickup_date']} {order['scheduled_pickup_time']}"
        # Parse timestamp string to datetime object
        timestamp_obj = None
        if order['timestamp']:
            try:
                timestamp_obj = datetime.strptime(order['timestamp'], '%Y-%m-%d %H:%M:%S')
            except Exception:
                # If parsing fails, try alternative formats or set to None
                try:
                    timestamp_obj = datetime.strptime(order['timestamp'], '%Y-%m-%d %H:%M')
                except Exception:
                    timestamp_obj = None
        detailed_orders.append({
            'id': order['id'],
            'timestamp': timestamp_obj,
            'status': order['status'],
            'items': detailed_items,
            'total_amount': order['total_amount'],
            'is_future_order': order['is_future_order'],
            'formatted_pickup_time': formatted_pickup_time
        })
    conn.close()
    return render_template('history.html', orders=detailed_orders)

def reset_db():
    """Reset the database by dropping all tables and reinitializing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop all tables
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS user_preferences")
    cursor.execute("DROP TABLE IF EXISTS user_item_interactions")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS notifications")
    cursor.execute("DROP TABLE IF EXISTS cart")
    cursor.execute("DROP TABLE IF EXISTS menu")
    
    conn.commit()
    conn.close()
    
    # Reinitialize the database
    init_db()
    update_drinks()
    standardize_menu_categories()
    print("[DEBUG] Database has been reset and reinitialized")

# Add a route to reset the database (you can remove this in production)
@app.route('/reset_db')
def reset_database():
    reset_db()
    flash('Database has been reset successfully.', 'success')
    return redirect(url_for('welcome'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user information
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get order history
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''', (session['user_id'],))
    recent_orders = cursor.fetchall()
    
    # Get favorite items (most ordered)
    cursor.execute('''
        SELECT item_name, COUNT(*) as order_count
        FROM user_item_interactions
        WHERE user_id = ?
        GROUP BY item_name
        ORDER BY order_count DESC
        LIMIT 5
    ''', (session['user_id'],))
    favorite_items = cursor.fetchall()

    # Get total spent and total orders (completed only)
    cursor.execute('''
        SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE user_id = ? AND status = 'completed'
    ''', (session['user_id'],))
    total_orders, total_spent = cursor.fetchone()
    
    conn.close()
    
    return render_template('profile.html', 
                         user=user, 
                         recent_orders=recent_orders,
                         favorite_items=favorite_items,
                         total_orders=total_orders,
                         total_spent=total_spent)

@app.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    if request.is_json:
        data = request.get_json()
        item_name = data.get('item_name')
        is_future_order = data.get('is_future_order', False)
        pickup_date = data.get('pickup_date')
        pickup_time = data.get('pickup_time')
    else:
        item_name = request.form.get('item_name')
        is_future_order = request.form.get('is_future_order', 'false') == 'true'
        pickup_date = request.form.get('pickup_date')
        pickup_time = request.form.get('pickup_time')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if is_future_order:
            cursor.execute('''
                DELETE FROM cart 
                WHERE user_id = ? AND item_name = ? AND is_future_order = 1 AND pickup_date = ? AND pickup_time = ?
            ''', (session['user_id'], item_name, pickup_date, pickup_time))
        else:
            cursor.execute('''
                DELETE FROM cart 
                WHERE user_id = ? AND item_name = ? AND is_future_order = 0
            ''', (session['user_id'], item_name))
        conn.commit()
        if request.is_json:
            return jsonify({'success': True})
        else:
            flash('Item removed from cart.', 'success')
            return redirect(request.referrer or url_for('cart'))
    except Exception as e:
        print(f"Error removing from cart: {str(e)}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        else:
            flash('Failed to remove item from cart.', 'danger')
            return redirect(request.referrer or url_for('cart'))
    finally:
        conn.close()

@app.context_processor
def inject_cart_count():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(quantity) FROM cart WHERE user_id = ?', (session['user_id'],))
        count = cursor.fetchone()[0]
        conn.close()
        return dict(cart_count=count or 0)
    return dict(cart_count=0)

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, m.price, m.name, m.description, m.is_veg, m.category, m.image_url
            FROM cart c
            JOIN menu m ON c.item_name = m.name
            WHERE c.user_id = ?
        ''', (session['user_id'],))
        cart_items = cursor.fetchall()
        if not cart_items:
            conn.close()
            flash('Your cart is empty.', 'danger')
            return redirect(url_for('cart'))
        # Separate immediate and future orders
        immediate_items = [item for item in cart_items if not item['is_future_order']]
        future_items = [item for item in cart_items if item['is_future_order']]
        order_ids = []
        # Process immediate order
        if immediate_items:
            items_json = json.dumps([
                {
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price']
                } for item in immediate_items
            ])
            total_amount = sum(item['quantity'] * item['price'] for item in immediate_items)
            cursor.execute('''
                INSERT INTO orders (user_id, items, total_amount, status, is_future_order, pickup_time)
                VALUES (?, ?, ?, 'completed', 0, datetime('now'))
            ''', (session['user_id'], items_json, total_amount))
            order_ids.append(cursor.lastrowid)
        # Process future orders (group by pickup_date and pickup_time)
        from collections import defaultdict
        future_groups = defaultdict(list)
        for item in future_items:
            key = (item['pickup_date'], item['pickup_time'])
            future_groups[key].append(item)
        for (pickup_date, pickup_time), items in future_groups.items():
            items_json = json.dumps([
                {
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'price': item['price']
                } for item in items
            ])
            total_amount = sum(item['quantity'] * item['price'] for item in items)
            cursor.execute('''
                INSERT INTO orders (user_id, items, total_amount, status, is_future_order, scheduled_pickup_date, scheduled_pickup_time, pickup_time)
                VALUES (?, ?, ?, 'pending', 1, ?, ?, datetime('now'))
            ''', (session['user_id'], items_json, total_amount, pickup_date, pickup_time))
            order_ids.append(cursor.lastrowid)
        # Remove all items from cart
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, m.price, m.name, m.description, m.is_veg, m.category, m.image_url
            FROM cart c
            JOIN menu m ON c.item_name = m.name
            WHERE c.user_id = ?
        ''', (session['user_id'],))
        cart_items = cursor.fetchall()
        conn.close()
        total = sum(item['quantity'] * item['price'] for item in cart_items)
        return render_template('payment.html', cart_items=cart_items, total=total)

# Add a background job to update status of future orders
def update_future_orders_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    print("Background job running at:", now)
    
    # Get orders that have passed their pickup time
    cursor.execute('''
        SELECT id, user_id, scheduled_pickup_date, scheduled_pickup_time, items, total_amount
        FROM orders
        WHERE is_future_order = 1 
        AND status = 'pending'
        AND datetime(scheduled_pickup_date || ' ' || scheduled_pickup_time) <= datetime(?)
    ''', (now,))
    expired_orders = cursor.fetchall()
    
    for order in expired_orders:
        order_id, user_id, pickup_date, pickup_time, items, total_amount = order
        
        # Move order to history (completed status)
        cursor.execute('''
            UPDATE orders
            SET status = 'completed'
            WHERE id = ?
        ''', (order_id,))
        
        # Create notification for the user
        try:
            items_list = json.loads(items)
            item_names = [item.get('name', '') for item in items_list if isinstance(item, dict)]
            items_summary = ', '.join(item_names[:3])  # Show first 3 items
            if len(item_names) > 3:
                items_summary += f" and {len(item_names) - 3} more"
            
            notification_message = f"Your order #{order_id} ({items_summary}) has been moved to order history. Pickup time was {pickup_date} at {pickup_time}."
            
            cursor.execute('''
                INSERT INTO notifications (
                    user_id, order_id, message, scheduled_time, is_sent,
                    notification_type
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                order_id,
                notification_message,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                0,
                'order_moved_to_history'
            ))
            
            print(f"[DEBUG] Moved order {order_id} to history and created notification for user {user_id}")
            
        except Exception as e:
            print(f"[ERROR] Failed to create notification for order {order_id}: {e}")
    
    conn.commit()
    
    # Log the update
    if expired_orders:
        print(f"[DEBUG] Moved {len(expired_orders)} expired orders to history")
    else:
        print("[DEBUG] No expired orders found")
    
    conn.close()

scheduler.add_job(
    func=update_future_orders_status,
    trigger='interval',
    minutes=1,
    id='update_future_orders_status'
)

# Note: check_and_send_notifications job is already added elsewhere in the code

@app.route('/reorder/<int:order_id>', methods=['POST'])
@login_required
def reorder(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT items FROM orders WHERE id = ? AND user_id = ?', (order_id, session['user_id']))
    order = cursor.fetchone()
    if not order:
        conn.close()
        flash('Order not found.', 'danger')
        return redirect(url_for('order_history'))
    items = json.loads(order['items'])
    for item in items:
        # Check if item already exists in cart
        cursor.execute('''
            SELECT quantity FROM cart 
            WHERE user_id = ? AND item_name = ? AND is_future_order = 0 
            AND pickup_date IS NULL AND pickup_time IS NULL
        ''', (session['user_id'], item['name']))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity if item exists
            new_quantity = existing_item[0] + item['quantity']
            cursor.execute('''
                UPDATE cart SET quantity = ? 
                WHERE user_id = ? AND item_name = ? AND is_future_order = 0 
                AND pickup_date IS NULL AND pickup_time IS NULL
            ''', (new_quantity, session['user_id'], item['name']))
        else:
            # Insert new item
            cursor.execute('''
                INSERT INTO cart (user_id, item_name, quantity, is_future_order, pickup_date, pickup_time)
                VALUES (?, ?, ?, 0, NULL, NULL)
            ''', (session['user_id'], item['name'], item['quantity']))
    
    conn.commit()
    conn.close()
    flash('Items added to cart!', 'success')
    return redirect(url_for('cart'))

def clean_item_name(item_name):
    """Clean and standardize item names by removing extra whitespace and normalizing case."""
    if not item_name:
        return item_name
    # Remove extra whitespace and normalize case
    cleaned = ' '.join(item_name.strip().split())
    return cleaned

def clean_category_name(category):
    """Standardize category names."""
    if not category:
        return category
    category_mapping = {
        'breakfast': 'breakfast', 'Breakfast': 'breakfast', 'BREAKFAST': 'breakfast',
        'lunch': 'lunch', 'Lunch': 'lunch', 'LUNCH': 'lunch', 'veg_lunch': 'lunch', 'non_veg_lunch': 'lunch',
        'beverages': 'beverages', 'Beverages': 'beverages', 'BEVERAGES': 'beverages',
        'juice': 'beverages', 'Juice': 'beverages', 'JUICE': 'beverages'
    }
    return category_mapping.get(category.strip().lower(), category.strip().lower())

def auto_clean_data():
    """Automatically clean and standardize all data for consistency."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("[DEBUG] Starting automatic data cleaning...")
        
        # 1. Clean menu item names and categories
        cursor.execute('SELECT name, category FROM menu')
        menu_items = cursor.fetchall()
        for name, category in menu_items:
            cleaned_name = clean_item_name(name)
            cleaned_category = clean_category_name(category)
            
            if cleaned_name != name or cleaned_category != category:
                cursor.execute('UPDATE menu SET name = ?, category = ? WHERE name = ?', 
                             (cleaned_name, cleaned_category, name))
                print(f"[DEBUG] Cleaned menu item: '{name}' -> '{cleaned_name}', category: '{category}' -> '{cleaned_category}'")
        
        # 2. Clean user_item_interactions
        cursor.execute('SELECT DISTINCT item_name FROM user_item_interactions')
        interaction_items = cursor.fetchall()
        for (item_name,) in interaction_items:
            cleaned_name = clean_item_name(item_name)
            if cleaned_name != item_name:
                cursor.execute('UPDATE user_item_interactions SET item_name = ? WHERE item_name = ?', 
                             (cleaned_name, item_name))
                print(f"[DEBUG] Cleaned interaction item: '{item_name}' -> '{cleaned_name}'")
        
        # 3. Clean user_preferences
        cursor.execute('SELECT DISTINCT item_name FROM user_preferences')
        preference_items = cursor.fetchall()
        for (item_name,) in preference_items:
            cleaned_name = clean_item_name(item_name)
            if cleaned_name != item_name:
                cursor.execute('UPDATE user_preferences SET item_name = ? WHERE item_name = ?', 
                             (cleaned_name, item_name))
                print(f"[DEBUG] Cleaned preference item: '{item_name}' -> '{cleaned_name}'")
        
        # 4. Fix any remaining mismatches between interactions and menu
        cursor.execute('''
            SELECT DISTINCT ui.item_name 
            FROM user_item_interactions ui 
            LEFT JOIN menu m ON LOWER(ui.item_name) = LOWER(m.name)
            WHERE m.name IS NULL
        ''')
        orphaned_items = cursor.fetchall()
        
        for (item_name,) in orphaned_items:
            # Try to find a close match in menu
            cursor.execute('SELECT name FROM menu WHERE LOWER(name) = LOWER(?)', (item_name,))
            match = cursor.fetchone()
            if match:
                cursor.execute('UPDATE user_item_interactions SET item_name = ? WHERE item_name = ?', 
                             (match[0], item_name))
                print(f"[DEBUG] Fixed orphaned interaction: '{item_name}' -> '{match[0]}'")
            else:
                # If no match found, remove orphaned interactions
                cursor.execute('DELETE FROM user_item_interactions WHERE item_name = ?', (item_name,))
                print(f"[DEBUG] Removed orphaned interaction: '{item_name}'")
        
        conn.commit()
        print("[DEBUG] Automatic data cleaning completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Data cleaning failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize database and clean data on startup
    init_db()
    auto_clean_data()
    app.run(debug=True) 