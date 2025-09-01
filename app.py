import os
import ssl
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from config import Config
import database

app = Flask(__name__)
app.config.from_object(Config)

def check_login(username, password):
    """Check if username and password are valid."""
    return username == Config.USERNAME and password == Config.PASSWORD

def requires_login(f):
    """Decorator that requires user to be logged in via session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and login processing."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if check_login(username, password):
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html', error=True)
    
    return render_template('login.html')

@app.route('/')
@requires_login
def index():
    """Render the main shopping list page."""
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
@requires_login
def get_items():
    """Get all shopping list items."""
    items = database.get_all_items()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
@requires_login
def add_item():
    """Add a new item to the shopping list."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Item name is required'}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({'error': 'Item name cannot be empty'}), 400
    
    item_id = database.add_item(name)
    return jsonify({'id': item_id, 'name': name, 'completed': False}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@requires_login
def update_item(item_id):
    """Update an existing item."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    completed = data.get('completed')
    
    if name is not None:
        name = name.strip()
        if not name:
            return jsonify({'error': 'Item name cannot be empty'}), 400
    
    database.update_item(item_id, name=name, completed=completed)
    return jsonify({'success': True})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@requires_login
def delete_item(item_id):
    """Delete an item from the shopping list."""
    database.delete_item(item_id)
    return jsonify({'success': True})

@app.route('/api/items/clear-completed', methods=['DELETE'])
@requires_login
def clear_completed():
    """Clear all completed items."""
    database.clear_completed_items()
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    """Logout endpoint that clears session and redirects to login."""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize database
    database.init_database()
    
    # Check if SSL certificates exist
    ssl_context = None
    if os.path.exists(Config.SSL_CERT) and os.path.exists(Config.SSL_KEY):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(Config.SSL_CERT, Config.SSL_KEY)
        print(f"Starting HTTPS server on https://localhost:{Config.PORT}")
    else:
        print(f"SSL certificates not found. Starting HTTP server on http://localhost:{Config.PORT}")
        print("Run the certificate generation script to enable HTTPS.")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        ssl_context=ssl_context
    )