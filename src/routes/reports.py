from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.sale import Sale
from src.models.transaction import Transaction
from datetime import datetime
from sqlalchemy import func, and_

reports_bp = Blueprint('reports', __name__)

def require_permission(permission_name):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'غير مصرح لك بالوصول'}), 401
            if not current_user.has_permission(permission_name):
                return jsonify({'error': 'ليس لديك صلاحية للقيام بهذا الإجراء'}), 403
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@reports_bp.route('/')
@login_required
@require_permission('view_reports')
def index():
    return render_template('reports/index.html')

@reports_bp.route('/api/sales-summary')
@login_required
@require_permission('view_reports')
def sales_summary():
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        q = db.session.query(func.count(Sale.id).label('count'), func.sum(Sale.unit_price).label('revenue'))
        if date_from:
            q = q.filter(Sale.sale_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        if date_to:
            q = q.filter(Sale.sale_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        row = q.one()
        return jsonify({'count': int(row.count or 0), 'revenue': float(row.revenue or 0)}), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في تقرير المبيعات: {str(e)}'}), 500

@reports_bp.route('/api/transactions-summary')
@login_required
@require_permission('view_reports')
def transactions_summary():
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        q_income = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount > 0)
        q_exp = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount < 0)
        if date_from:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d')
            q_income = q_income.filter(Transaction.transaction_date >= dt_from)
            q_exp = q_exp.filter(Transaction.transaction_date >= dt_from)
        if date_to:
            dt_to = datetime.strptime(date_to, '%Y-%m-%d')
            q_income = q_income.filter(Transaction.transaction_date <= dt_to)
            q_exp = q_exp.filter(Transaction.transaction_date <= dt_to)
        income = q_income.scalar() or 0
        expenses = q_exp.scalar() or 0
        return jsonify({'income': float(income), 'expenses': float(abs(expenses))}), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في تقرير المعاملات: {str(e)}'}), 500


