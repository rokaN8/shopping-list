import os
import ssl
import time
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from config import Config
import database

app = Flask(__name__)
app.config.from_object(Config)

# In-memory rate limiting storage
login_attempts = {}

def clean_old_attempts(ip):
    """Clean attempts older than 15 minutes for the given IP."""
    current_time = time.time()
    cutoff_time = current_time - 900  # 15 minutes in seconds
    
    if ip in login_attempts:
        login_attempts[ip]['attempt_times'] = [
            attempt_time for attempt_time in login_attempts[ip]['attempt_times']
            if attempt_time > cutoff_time
        ]
        
        # Update attempt count
        login_attempts[ip]['attempts'] = len(login_attempts[ip]['attempt_times'])
        
        # Remove IP entry if no recent attempts
        if login_attempts[ip]['attempts'] == 0:
            del login_attempts[ip]

def is_ip_rate_limited(ip):
    """Check if IP is currently rate limited and return status."""
    current_time = time.time()
    
    # Clean old attempts first
    clean_old_attempts(ip)
    
    # Check if IP exists and is currently locked
    if ip in login_attempts:
        if login_attempts[ip].get('locked_until', 0) > current_time:
            remaining_time = int(login_attempts[ip]['locked_until'] - current_time)
            return True, remaining_time
    
    return False, 0

def record_failed_attempt(ip):
    """Record a failed login attempt and apply progressive lockout."""
    current_time = time.time()
    
    # Initialize IP entry if it doesn't exist
    if ip not in login_attempts:
        login_attempts[ip] = {
            'attempts': 0,
            'locked_until': 0,
            'attempt_times': []
        }
    
    # Add current attempt
    login_attempts[ip]['attempt_times'].append(current_time)
    login_attempts[ip]['attempts'] += 1
    
    # Apply progressive lockout based on attempt count
    attempts = login_attempts[ip]['attempts']
    if attempts >= 5:
        if attempts <= 6:
            lockout_duration = 60  # 1 minute
        elif attempts <= 8:
            lockout_duration = 300  # 5 minutes  
        elif attempts <= 10:
            lockout_duration = 900  # 15 minutes
        else:
            lockout_duration = 3600  # 1 hour
        
        login_attempts[ip]['locked_until'] = current_time + lockout_duration

def clear_ip_attempts(ip):
    """Clear all attempts for an IP (called on successful login)."""
    if ip in login_attempts:
        del login_attempts[ip]

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
        client_ip = request.remote_addr
        
        # Check if IP is currently rate limited
        is_limited, remaining_time = is_ip_rate_limited(client_ip)
        if is_limited:
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            if minutes > 0:
                time_msg = f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"
            else:
                time_msg = f"{seconds} second{'s' if seconds != 1 else ''}"
            
            flash(f'Too many failed login attempts. Please try again in {time_msg}.', 'error')
            return render_template('login.html', error=True)
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if check_login(username, password):
            # Successful login - clear any failed attempts
            clear_ip_attempts(client_ip)
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            return redirect(url_for('index'))
        else:
            # Failed login - record the attempt
            record_failed_attempt(client_ip)
            
            # Check current attempt count to provide appropriate message
            clean_old_attempts(client_ip)
            if client_ip in login_attempts:
                attempts = login_attempts[client_ip]['attempts']
                remaining_attempts = max(0, 5 - attempts)
                
                if remaining_attempts > 0:
                    flash(f'Invalid username or password. {remaining_attempts} attempt{"s" if remaining_attempts != 1 else ""} remaining before temporary lockout.', 'error')
                else:
                    flash('Invalid username or password. Account temporarily locked due to too many failed attempts.', 'error')
            else:
                flash('Invalid username or password.', 'error')
            
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