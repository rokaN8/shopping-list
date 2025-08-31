import sqlite3
from datetime import datetime
from config import Config

def init_database():
    """Initialize the database and create the items table if it doesn't exist."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_items():
    """Get all shopping list items."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, completed, created_at FROM items ORDER BY created_at ASC')
    items = cursor.fetchall()
    
    conn.close()
    
    return [{'id': item[0], 'name': item[1], 'completed': bool(item[2]), 'created_at': item[3]} for item in items]

def add_item(name):
    """Add a new item to the shopping list."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO items (name) VALUES (?)', (name,))
    item_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return item_id

def update_item(item_id, name=None, completed=None):
    """Update an existing item."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if name is not None:
        updates.append('name = ?')
        params.append(name)
    
    if completed is not None:
        updates.append('completed = ?')
        params.append(completed)
    
    if updates:
        params.append(item_id)
        query = f'UPDATE items SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        
        conn.commit()
    
    conn.close()

def delete_item(item_id):
    """Delete an item from the shopping list."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    
    conn.commit()
    conn.close()

def clear_completed_items():
    """Remove all completed items from the shopping list."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM items WHERE completed = 1')
    
    conn.commit()
    conn.close()