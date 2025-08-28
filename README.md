# Shopping List Web App

A simple, single-user shopping list web application optimized for Raspberry Pi deployment.

## Features

- Single shopping list with add/edit/delete/check-off functionality
- Basic authentication (configurable username/password)
- SQLite database for persistent storage
- Responsive design for mobile and desktop
- Lightweight and Pi-optimized

## Installation

1. Install Python 3 and pip on your Raspberry Pi
2. Clone or copy this project to your Pi
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set environment variables (optional):
```bash
export SECRET_KEY="your-secret-key-here"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin"
```

Or modify `config.py` directly.

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode (Recommended for Pi)
```bash
pip install gunicorn
gunicorn -w 1 -b 0.0.0.0:5000 app:app
```

The app will be available at `http://your-pi-ip:5000`

## Default Login
- Username: `admin`
- Password: `admin`

**Change these credentials before deployment!**

## File Structure
```
shopping-list/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css      # Styling
│   └── script.js      # Frontend JavaScript
└── templates/
    ├── login.html     # Login page
    └── index.html     # Main shopping list page
```

## API Endpoints

- `GET /` - Main shopping list page (requires auth)
- `POST /login` - User authentication
- `GET /logout` - Logout user
- `GET /api/items` - Get all items
- `POST /api/items` - Add new item
- `PUT /api/items/<id>` - Update item name
- `PUT /api/items/<id>/toggle` - Toggle completed status
- `DELETE /api/items/<id>` - Delete item

## Security

- Session-based authentication
- CSRF protection via Flask sessions
- Input validation and sanitization
- No external dependencies for security

## Performance

Optimized for Raspberry Pi:
- Minimal dependencies
- SQLite for low resource usage
- Lightweight frontend
- Single-threaded deployment suitable for single user