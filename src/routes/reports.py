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




@reports_bp.route("/api/profit-loss")
@login_required
@require_permission("view_reports")
def profit_loss_report():
    try:
        date_from_str = request.args.get("date_from")
        date_to_str = request.args.get("date_to")

        date_from = datetime.strptime(date_from_str, "%Y-%m-%d") if date_from_str else None
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d") if date_to_str else None

        # Calculate total income
        income_query = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount > 0)
        if date_from: income_query = income_query.filter(Transaction.transaction_date >= date_from)
        if date_to: income_query = income_query.filter(Transaction.transaction_date <= date_to)
        total_income = income_query.scalar() or 0

        # Calculate total expenses
        expenses_query = db.session.query(func.sum(Transaction.amount)).filter(Transaction.amount < 0)
        if date_from: expenses_query = expenses_query.filter(Transaction.transaction_date >= date_from)
        if date_to: expenses_query = expenses_query.filter(Transaction.transaction_date <= date_to)
        total_expenses = abs(expenses_query.scalar() or 0)

        net_profit = total_income - total_expenses

        return jsonify({
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_profit": float(net_profit)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error generating Profit & Loss report: {str(e)}"}), 500

@reports_bp.route("/api/sales-by-property-type")
@login_required
@require_permission("view_reports")
def sales_by_property_type_report():
    try:
        date_from_str = request.args.get("date_from")
        date_to_str = request.args.get("date_to")

        date_from = datetime.strptime(date_from_str, "%Y-%m-%d") if date_from_str else None
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d") if date_to_str else None

        query = db.session.query(
            Sale.property_type,
            func.count(Sale.id).label("total_sales"),
            func.sum(Sale.unit_price).label("total_revenue"),
            func.sum(Sale.net_company_income).label("total_net_income")
        ).group_by(Sale.property_type)

        if date_from: query = query.filter(Sale.sale_date >= date_from)
        if date_to: query = query.filter(Sale.sale_date <= date_to)

        results = query.all()

        report_data = [
            {
                "property_type": row.property_type,
                "total_sales": row.total_sales,
                "total_revenue": float(row.total_revenue or 0),
                "total_net_income": float(row.total_net_income or 0)
            }
            for row in results
        ]

        return jsonify(report_data), 200
    except Exception as e:
        return jsonify({"error": f"Error generating Sales by Property Type report: {str(e)}"}), 500

@reports_bp.route("/api/commissions-report")
@login_required
@require_permission("view_reports")
def commissions_report():
    try:
        date_from_str = request.args.get("date_from")
        date_to_str = request.args.get("date_to")

        date_from = datetime.strptime(date_from_str, "%Y-%m-%d") if date_from_str else None
        date_to = datetime.strptime(date_to_str, "%Y-%m-%d") if date_to_str else None

        query = db.session.query(
            Sale.salesperson_name,
            Sale.sales_manager_name,
            func.sum(Sale.salesperson_commission_amount).label("total_salesperson_commission"),
            func.sum(Sale.salesperson_incentive_amount).label("total_salesperson_incentive"),
            func.sum(Sale.salesperson_tax_amount).label("total_salesperson_tax"),
            func.sum(Sale.net_salesperson_income).label("total_net_salesperson_income"),
            func.sum(Sale.sales_manager_commission_amount).label("total_sales_manager_commission"),
            func.sum(Sale.sales_manager_tax_amount).label("total_sales_manager_tax"),
            func.sum(Sale.net_sales_manager_income).label("total_net_sales_manager_income")
        ).group_by(Sale.salesperson_name, Sale.sales_manager_name)

        if date_from: query = query.filter(Sale.sale_date >= date_from)
        if date_to: query = query.filter(Sale.sale_date <= date_to)

        results = query.all()

        report_data = [
            {
                "salesperson_name": row.salesperson_name or "غير محدد",
                "sales_manager_name": row.sales_manager_name or "غير محدد",
                "total_salesperson_commission": float(row.total_salesperson_commission or 0),
                "total_salesperson_incentive": float(row.total_salesperson_incentive or 0),
                "total_salesperson_tax": float(row.total_salesperson_tax or 0),
                "total_net_salesperson_income": float(row.total_net_salesperson_income or 0),
                "total_sales_manager_commission": float(row.total_sales_manager_commission or 0),
                "total_sales_manager_tax": float(row.total_sales_manager_tax or 0),
                "total_net_sales_manager_income": float(row.total_net_sales_manager_income or 0)
            }
            for row in results
        ]

        return jsonify(report_data), 200
    except Exception as e:
        return jsonify({"error": f"Error generating Commissions report: {str(e)}"}), 500

