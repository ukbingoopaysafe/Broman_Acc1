from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

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
    
    with app.app_context():
        db.create_all()

