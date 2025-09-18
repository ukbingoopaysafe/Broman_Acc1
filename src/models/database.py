from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# Initialize database
db = SQLAlchemy()

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    login_manager.init_app(app)
    
    # SQLite connection tuning to reduce "database is locked" errors
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        # Apply only for SQLite
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            # WAL allows concurrent readers and a single writer
            cursor.execute("PRAGMA journal_mode=WAL")
            # Reasonable sync level and lock wait timeout
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=5000")  # ms
            cursor.close()
    
    with app.app_context():
        db.create_all()

