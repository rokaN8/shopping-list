import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'
    DATABASE = 'shopping_list.db'