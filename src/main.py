import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.database import init_db, login_manager
from src.routes.user import user_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'broman_accounting_secret_key_2024'
app.config['WTF_CSRF_ENABLED'] = True

# Database configuration - using SQLite for now, can be changed to PostgreSQL later
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'broman_accounting.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app)

# Initialize database and login manager
init_db(app)

# Import models to ensure they are registered with SQLAlchemy
from src.models.user import User, Role, Permission
from src.models.treasury import Treasury
from src.models.transaction import Transaction
from src.models.sale import Sale, PropertyTypeRates

# Create all tables
with app.app_context():
    from src.models.database import db
    db.create_all()

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')

from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.sales import sales_bp
from src.routes.treasury import treasury_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(sales_bp, url_prefix='/sales')
app.register_blueprint(treasury_bp, url_prefix='/treasury')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # Redirect to login if not authenticated
            from flask_login import current_user
            if not current_user.is_authenticated:
                from flask import redirect, url_for
                return redirect(url_for('auth.login'))
            else:
                return redirect(url_for('dashboard.index'))

@app.route('/test')
def test():
    return "Flask is working!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
