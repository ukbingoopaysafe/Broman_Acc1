from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from src.models.database import db
from src.models.user import User
from src.models.treasury import Treasury
from src.models.transaction import Transaction
from src.models.sale import Sale
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    return render_template('dashboard.html', user=current_user)

@dashboard_bp.route('/api/dashboard-stats', methods=['GET'])
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get treasury balance
        treasury_balance = Treasury.get_current_balance()
        
        # Get total sales count
        total_sales = Sale.query.count()
        
        # Get sales this month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        sales_this_month = Sale.query.filter(Sale.created_at >= current_month_start).count()
        
        # Get total revenue (sum of all sale unit prices)
        total_revenue = db.session.query(func.sum(Sale.unit_price)).scalar() or 0
        
        # Get recent transactions (last 10)
        recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(10).all()
        
        # Get recent sales (last 5)
        recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
        
        # Get monthly sales data for chart (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_sales = db.session.query(
            func.strftime('%Y-%m', Sale.created_at).label('month'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.unit_price).label('revenue')
        ).filter(Sale.created_at >= six_months_ago).group_by(
            func.strftime('%Y-%m', Sale.created_at)
        ).all()
        
        return jsonify({
            'treasury_balance': float(treasury_balance),
            'total_sales': total_sales,
            'sales_this_month': sales_this_month,
            'total_revenue': float(total_revenue),
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'recent_sales': [s.to_dict() for s in recent_sales],
            'monthly_sales': [
                {
                    'month': row.month,
                    'count': row.count,
                    'revenue': float(row.revenue or 0)
                } for row in monthly_sales
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب إحصائيات لوحة التحكم: {str(e)}'}), 500

@dashboard_bp.route('/api/user-permissions', methods=['GET'])
@login_required
def user_permissions():
    """Get current user permissions"""
    try:
        permissions = []
        if current_user.role:
            permissions = [perm.name for perm in current_user.role.permissions]
        
        return jsonify({
            'permissions': permissions,
            'is_admin': current_user.is_admin()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب صلاحيات المستخدم: {str(e)}'}), 500

