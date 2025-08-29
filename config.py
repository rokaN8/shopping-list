import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'
    DATABASE = 'shopping_list.db'
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
    SESSION_COOKIE_SECURE = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour