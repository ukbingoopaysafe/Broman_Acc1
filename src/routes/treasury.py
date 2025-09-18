from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from src.models.database import db
from src.models.treasury import Treasury
from src.models.transaction import Transaction
from src.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_

treasury_bp = Blueprint('treasury', __name__)

def require_permission(permission_name):
    """Decorator to require specific permission"""
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

@treasury_bp.route('/')
@login_required
@require_permission('view_treasury')
def treasury_dashboard():
    """Treasury dashboard page"""
    return render_template('treasury/dashboard.html')

@treasury_bp.route('/transactions')
@login_required
@require_permission('view_transactions')
def transactions_list():
    """Transactions list page"""
    return render_template('treasury/transactions.html')

@treasury_bp.route('/transactions/new')
@login_required
@require_permission('create_transactions')
def new_transaction():
    """New transaction page"""
    return render_template('treasury/transaction_form.html', transaction=None)

@treasury_bp.route('/transactions/<int:transaction_id>')
@login_required
@require_permission('view_transactions')
def transaction_detail(transaction_id):
    """Transaction detail page"""
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('treasury/transaction_detail.html', transaction=transaction)

@treasury_bp.route('/transactions/<int:transaction_id>/edit')
@login_required
@require_permission('edit_transactions')
def edit_transaction(transaction_id):
    """Edit transaction page"""
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('treasury/transaction_form.html', transaction=transaction)

# API Routes
@treasury_bp.route('/api/balance', methods=['GET'])
@login_required
@require_permission('view_treasury')
def get_balance():
    """Get current treasury balance"""
    try:
        treasury = Treasury.get_current()
        return jsonify({
            'balance': float(treasury.balance),
            'last_updated': treasury.last_updated.isoformat() if treasury.last_updated else None
        }), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب الرصيد: {str(e)}'}), 500

@treasury_bp.route('/api/balance', methods=['POST'])
@login_required
@require_permission('manage_treasury')
def set_balance():
    """Set treasury balance (Admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'balance' not in data:
            return jsonify({'error': 'الرصيد مطلوب'}), 400
        
        new_balance = float(data['balance'])
        reason = data.get('reason', 'تعديل الرصيد من قبل الإدارة')
        
        # Get current balance
        treasury = Treasury.get_current()
        old_balance = float(treasury.balance)
        
        # Update balance
        Treasury.set_balance(new_balance)
        
        # Create transaction record
        transaction = Transaction(
            type='تعديل رصيد',
            amount=float(new_balance - old_balance),
            description=f'{reason} - الرصيد السابق: {old_balance:,.2f} جنيه',
            transaction_date=datetime.now(),
            related_entity_type='manual',
            related_entity_id=None,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الرصيد بنجاح',
            'balance': float(new_balance),
            'old_balance': float(old_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث الرصيد: {str(e)}'}), 500

@treasury_bp.route('/api/transactions', methods=['GET'])
@login_required
@require_permission('view_transactions')
def get_transactions():
    """Get all transactions with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        search = request.args.get('search', '')
        transaction_type = request.args.get('type', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = Transaction.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Transaction.description.contains(search),
                    Transaction.type.contains(search)
                )
            )
        
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        
        if date_from:
            query = query.filter(Transaction.transaction_date >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            query = query.filter(Transaction.transaction_date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        # Order by transaction date (newest first)
        query = query.order_by(desc(Transaction.transaction_date))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المعاملات: {str(e)}'}), 500

@treasury_bp.route('/api/transactions', methods=['POST'])
@login_required
@require_permission('create_transactions')
def create_transaction():
    """Create new transaction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Validate required fields
        required_fields = ['type', 'amount', 'description']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        amount = float(data['amount'])
        
        # Parse transaction date
        transaction_date = datetime.now()
        if data.get('transaction_date'):
            try:
                transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'تاريخ المعاملة غير صحيح'}), 400
        
        # Create transaction record
        transaction = Transaction(
            type=data['type'],
            amount=amount,
            description=data['description'],
            transaction_date=transaction_date,
            reference_type='manual',
            reference_id=None,
            created_by=current_user.id
        )
        
        db.session.add(transaction)
        db.session.flush()  # Get the transaction ID
        
        # Update treasury balance
        if amount > 0:
            Treasury.add_to_balance(float(amount))
        else:
            Treasury.subtract_from_balance(float(abs(amount)))
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المعاملة بنجاح',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء المعاملة: {str(e)}'}), 500

@treasury_bp.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@login_required
@require_permission('view_transactions')
def get_transaction(transaction_id):
    """Get specific transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        return jsonify(transaction.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المعاملة: {str(e)}'}), 500

@treasury_bp.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@login_required
@require_permission('edit_transactions')
def update_transaction(transaction_id):
    """Update transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Store old amount for balance adjustment
        old_amount = transaction.amount
        
        # Update basic fields
        updatable_fields = ['type', 'amount', 'description', 'transaction_date']
        
        for field in updatable_fields:
            if field in data:
                if field == 'transaction_date':
                    try:
                        transaction.transaction_date = datetime.strptime(data[field], '%Y-%m-%d')
                    except ValueError:
                        return jsonify({'error': 'تاريخ المعاملة غير صحيح'}), 400
                elif field == 'amount':
                    transaction.amount = float(data[field])
                else:
                    setattr(transaction, field, data[field])
        
        # Adjust treasury balance if amount changed
        if old_amount != transaction.amount:
            # Reverse old amount
            if old_amount > 0:
                Treasury.subtract_from_balance(old_amount)
            else:
                Treasury.add_to_balance(abs(old_amount))
            
            # Apply new amount
            if transaction.amount > 0:
                Treasury.add_to_balance(transaction.amount)
            else:
                Treasury.subtract_from_balance(abs(transaction.amount))
        
        transaction.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المعاملة بنجاح',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث المعاملة: {str(e)}'}), 500

@treasury_bp.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
@require_permission('delete_transactions')
def delete_transaction(transaction_id):
    """Delete transaction"""
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # Don't allow deletion of system-generated transactions
        if transaction.reference_type in ['sale', 'system']:
            return jsonify({'error': 'لا يمكن حذف المعاملات المولدة تلقائياً من النظام'}), 400
        
        # Reverse the transaction amount from treasury
        if transaction.amount > 0:
            Treasury.subtract_from_balance(transaction.amount)
        else:
            Treasury.add_to_balance(abs(transaction.amount))
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المعاملة بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف المعاملة: {str(e)}'}), 500

@treasury_bp.route('/api/transaction-types', methods=['GET'])
@login_required
@require_permission('view_transactions')
def get_transaction_types():
    """Get all transaction types"""
    try:
        # Get distinct transaction types from database
        types = db.session.query(Transaction.type).distinct().all()
        
        # Add common transaction types
        common_types = [
            'إيراد من بيع عقار',
            'مصروف تشغيلي',
            'راتب موظف',
            'إيجار مكتب',
            'فواتير خدمات',
            'مصروف تسويق',
            'عمولة خارجية',
            'إيراد متنوع',
            'مصروف متنوع',
            'تعديل رصيد'
        ]
        
        # Combine and remove duplicates
        all_types = list(set([t[0] for t in types] + common_types))
        all_types.sort()
        
        return jsonify(all_types), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب أنواع المعاملات: {str(e)}'}), 500

@treasury_bp.route('/api/treasury-stats', methods=['GET'])
@login_required
@require_permission('view_treasury')
def get_treasury_stats():
    """Get treasury statistics"""
    try:
        # Current balance
        treasury = Treasury.get_current()
        current_balance = float(treasury.balance)
        
        # Today's transactions
        today = datetime.now().date()
        today_income = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_date >= today,
                Transaction.amount > 0
            )
        ).scalar() or 0
        
        today_expenses = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_date >= today,
                Transaction.amount < 0
            )
        ).scalar() or 0
        
        # This month's transactions
        month_start = datetime.now().replace(day=1)
        month_income = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_date >= month_start,
                Transaction.amount > 0
            )
        ).scalar() or 0
        
        month_expenses = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.transaction_date >= month_start,
                Transaction.amount < 0
            )
        ).scalar() or 0
        
        # Recent transactions
        recent_transactions = Transaction.query.order_by(
            desc(Transaction.transaction_date)
        ).limit(10).all()
        
        # Monthly balance history (last 12 months)
        monthly_balances = []
        for i in range(12):
            month_date = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_transactions = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_date <= month_date
            ).scalar() or 0
            
            monthly_balances.append({
                'month': month_date.strftime('%Y-%m'),
                'balance': float(month_transactions)
            })
        
        monthly_balances.reverse()
        
        # Transaction types summary
        type_summary = db.session.query(
            Transaction.type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.transaction_date >= month_start
        ).group_by(Transaction.type).all()
        
        return jsonify({
            'current_balance': current_balance,
            'today_income': float(today_income),
            'today_expenses': float(abs(today_expenses)),
            'month_income': float(month_income),
            'month_expenses': float(abs(month_expenses)),
            'recent_transactions': [t.to_dict() for t in recent_transactions],
            'monthly_balances': monthly_balances,
            'type_summary': [
                {
                    'type': row.type,
                    'count': row.count,
                    'total': float(row.total or 0)
                } for row in type_summary
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب إحصائيات الخزنة: {str(e)}'}), 500

@treasury_bp.route('/api/balance-history', methods=['GET'])
@login_required
@require_permission('view_treasury')
def get_balance_history():
    """Get balance history over time"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get transactions for the specified period
        start_date = datetime.now() - timedelta(days=days)
        transactions = Transaction.query.filter(
            Transaction.transaction_date >= start_date
        ).order_by(Transaction.transaction_date).all()
        
        # Calculate running balance
        current_balance = Treasury.get_current().balance
        
        # Start with current balance and work backwards
        balance_history = []
        running_balance = current_balance
        
        # Work backwards from current balance
        for transaction in reversed(transactions):
            balance_history.append({
                'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                'balance': float(running_balance),
                'transaction_amount': float(transaction.amount),
                'transaction_type': transaction.type,
                'description': transaction.description
            })
            running_balance -= transaction.amount
        
        balance_history.reverse()
        
        return jsonify(balance_history), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب تاريخ الرصيد: {str(e)}'}), 500

