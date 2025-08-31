import os

class Config:
    # Basic Auth credentials
    USERNAME = os.environ.get('SHOPPING_USERNAME', 'admin')
    PASSWORD = os.environ.get('SHOPPING_PASSWORD', 'password123')
    
    # Database
    DATABASE_PATH = 'shopping_list.db'
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 7666
    DEBUG = False
    
    # SSL settings
    SSL_CERT = 'certs/cert.pem'
    SSL_KEY = 'certs/key.pem'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')