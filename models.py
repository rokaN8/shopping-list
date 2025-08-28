import sqlite3
from datetime import datetime

class ShoppingItem:
    def __init__(self, name, completed=False, id=None, created_at=None):
        self.id = id
        self.name = name
        self.completed = completed
        self.created_at = created_at or datetime.now()

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_all_items(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, completed, created_at FROM shopping_items ORDER BY completed, created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': row[1],
                'completed': bool(row[2]),
                'created_at': row[3]
            })
        return items
    
    def add_item(self, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO shopping_items (name) VALUES (?)', (name,))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def update_item(self, item_id, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE shopping_items SET name = ? WHERE id = ?', (name, item_id))
        conn.commit()
        conn.close()
    
    def toggle_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE shopping_items SET completed = NOT completed WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
    
    def delete_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM shopping_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()