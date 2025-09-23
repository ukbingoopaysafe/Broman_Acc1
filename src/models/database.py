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

        # Backfill missing columns for existing SQLite DBs when model changed but migrations
        # were not run. This is a small, safe add-only routine: it checks the `sales` table
        # and adds columns that are defined on the SQLAlchemy model but missing in the
        # SQLite schema. This avoids runtime "no such column" errors.
        try:
            engine = db.engine
            inspector = __import__('sqlalchemy').inspect(engine)
            if 'sales' in inspector.get_table_names():
                existing_cols = {c['name'] for c in inspector.get_columns('sales')}

                # Define columns we expect in the sales table: mapping to SQLite column SQL
                expected_columns = {
                    'company_commission_rate': 'NUMERIC',
                    'salesperson_commission_rate': 'NUMERIC',
                    'salesperson_incentive_rate': 'NUMERIC',
                    'vat_rate': 'NUMERIC',
                    'sales_tax_rate': 'NUMERIC',
                    'annual_tax_rate': 'NUMERIC',
                    'salesperson_tax_rate': 'NUMERIC',
                    'sales_manager_tax_rate': 'NUMERIC',
                    'company_commission_amount': 'NUMERIC',
                    'salesperson_commission_amount': 'NUMERIC',
                    'salesperson_incentive_amount': 'NUMERIC',
                    'sales_manager_commission_amount': 'NUMERIC',
                    'vat_amount': 'NUMERIC',
                    'sales_tax_amount': 'NUMERIC',
                    'annual_tax_amount': 'NUMERIC',
                    'salesperson_tax_amount': 'NUMERIC',
                    'sales_manager_tax_amount': 'NUMERIC',
                    'net_company_income': 'NUMERIC',
                    'net_salesperson_income': 'NUMERIC',
                    'net_sales_manager_income': 'NUMERIC'
                }

                missing = [col for col in expected_columns.keys() if col not in existing_cols]
                if missing:
                    conn = engine.connect()
                    for col in missing:
                        col_type = expected_columns[col]
                        # SQLite ALTER TABLE ADD COLUMN is limited but supports adding simple columns
                        try:
                            conn.execute(f'ALTER TABLE sales ADD COLUMN {col} {col_type}');
                        except Exception:
                            # If add fails, ignore and continue — we'll surface runtime errors elsewhere
                            pass
                    conn.close()
        except Exception:
            # Don't break app initialization on best-effort migration attempt
            pass

