from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_talisman import Talisman
from models import Database
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# HTTPS enforcement and security headers
Talisman(app, 
    force_https=app.config.get('FORCE_HTTPS', True),
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data:",
        'connect-src': "'self'"
    }
)

@app.before_request
def force_https():
    if app.config.get('FORCE_HTTPS', True) and not request.is_secure and request.headers.get('X-Forwarded-Proto') != 'https':
        return redirect(request.url.replace('http://', 'https://', 1), code=301)

db = Database(app.config['DATABASE'])

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def require_login(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/items', methods=['GET'])
@require_login
def get_items():
    items = db.get_all_items()
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
@require_login
def add_item():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Item name is required'}), 400
    
    item_id = db.add_item(data['name'])
    return jsonify({'id': item_id, 'name': data['name'], 'completed': False}), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@require_login
def update_item(item_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Item name is required'}), 400
    
    db.update_item(item_id, data['name'])
    return jsonify({'id': item_id, 'name': data['name']})

@app.route('/api/items/<int:item_id>/toggle', methods=['PUT'])
@require_login
def toggle_item(item_id):
    db.toggle_item(item_id)
    return jsonify({'success': True})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@require_login
def delete_item(item_id):
    db.delete_item(item_id)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)