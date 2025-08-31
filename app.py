import os
import ssl
from flask import Flask, render_template, request, jsonify, abort
from functools import wraps
import base64
from config import Config
import database

app = Flask(__name__)
app.config.from_object(Config)

def check_auth(username, password):
    """Check if username and password are valid."""
    return username == Config.USERNAME and password == Config.PASSWORD

def authenticate():
    """Send a 401 response that enables basic auth."""
    return '', 401, {'WWW-Authenticate': 'Basic realm="Shopping List"'}

def requires_auth(f):
    """Decorator that requires basic authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    """Render the main shopping list page."""
    return render_template('index.html')

@app.route('/api/items', methods=['GET'])
@requires_auth
def get_items():
    """Get all shopping list items."""
    items = database.get_all_items()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
@requires_auth
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
@requires_auth
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
@requires_auth
def delete_item(item_id):
    """Delete an item from the shopping list."""
    database.delete_item(item_id)
    return jsonify({'success': True})

@app.route('/api/items/clear-completed', methods=['DELETE'])
@requires_auth
def clear_completed():
    """Clear all completed items."""
    database.clear_completed_items()
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    """Logout endpoint that forces re-authentication."""
    return '', 401, {'WWW-Authenticate': 'Basic realm="Shopping List - Logged Out"'}

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