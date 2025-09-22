from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from src.models.database import db
from src.models.sale import Sale, PropertyTypeRates
from src.models.treasury import Treasury
from src.models.transaction import Transaction
from src.models.user import User
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, desc

sales_bp = Blueprint('sales', __name__)

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

@sales_bp.route('/')
@login_required
@require_permission('view_sales')
def sales_list():
    """Sales list page"""
    return render_template('sales/list.html')

@sales_bp.route('/new')
@login_required
@require_permission('create_sales')
def new_sale():
    """New sale page with enhanced form"""
    return render_template("sales/form_enhanced.html", sale=None)

@sales_bp.route('/<int:sale_id>')
@login_required
@require_permission('view_sales')
def sale_detail(sale_id):
    """Sale detail page"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template('sales/detail.html', sale=sale)

@sales_bp.route('/<int:sale_id>/edit')
@login_required
@require_permission('edit_sales')
def edit_sale(sale_id):
    """Edit sale page with enhanced form"""
    sale = Sale.query.get_or_404(sale_id)
    return render_template("sales/form_enhanced.html", sale=sale)

# API Routes
@sales_bp.route('/api/sales', methods=['GET'])
@login_required
@require_permission('view_sales')
def get_sales():
    """Get all sales with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        search = request.args.get('search', '')
        property_type = request.args.get('property_type', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = Sale.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Sale.client_name.contains(search),
                    Sale.unit_code.contains(search),
                    Sale.project_name.contains(search)
                )
            )
        
        if property_type:
            query = query.filter(Sale.property_type == property_type)
        
        if date_from:
            query = query.filter(Sale.sale_date >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            query = query.filter(Sale.sale_date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        # Order by creation date (newest first)
        query = query.order_by(desc(Sale.created_at))
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'sales': [sale.to_dict() for sale in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المبيعات: {str(e)}'}), 500

from src.routes.sales_new import create_sale as create_sale_new

@sales_bp.route("/api/sales", methods=["POST"])
@login_required
@require_permission("create_sales")
def create_sale():
    """Create new sale with enhanced calculation logic"""
    return create_sale_new()

        # Company commission
        company_commission = unit_price * Decimal(str(rates.company_commission_rate))

        # Salesperson commission
        salesperson_commission = unit_price * Decimal(str(rates.salesperson_commission_rate))

        # Salesperson incentive
        salesperson_incentive = unit_price * Decimal(str(rates.salesperson_incentive_rate))

        # Additional incentive tax
        additional_incentive_tax = salesperson_incentive * Decimal(str(rates.additional_incentive_tax_rate))

        # VAT
        vat_amount = company_commission * Decimal(str(rates.vat_rate))

        # Sales tax
        sales_tax = company_commission * Decimal(str(rates.sales_tax_rate))

        # Annual tax
        annual_tax = company_commission * Decimal(str(rates.annual_tax_rate))

        # Sales manager commission
        sales_manager_commission = unit_price * Decimal(str(rates.sales_manager_commission_rate))

        # Net company income
        net_company_income = (company_commission - vat_amount - sales_tax - 
                    annual_tax - salesperson_commission - 
                    salesperson_incentive - additional_incentive_tax - 
                    sales_manager_commission)
        
        # Create treasury transaction for net company income first (so we can link it)
        transaction = None
        if net_company_income > 0:
            transaction = Transaction(
                type='إيراد من بيع عقار',
                amount=net_company_income,
                description=f'صافي إيراد من بيع الوحدة {data["unit_code"]} - {data["client_name"]}',
                transaction_date=datetime.now(),
                related_entity_type='sale',
                user_id=current_user.id
            )
            db.session.add(transaction)
            db.session.flush()  # ensure transaction.id is available

        # Create sale record using model column names
        sale = Sale(
            client_name=data['client_name'],
            unit_code=data['unit_code'],
            property_type=data['property_type'],
            unit_price=unit_price,
            sale_date=sale_date,
            project_name=data['project_name'],
            salesperson_name=data.get('salesperson_name', ''),
            sales_manager_name=data.get('sales_manager_name', ''),
            company_commission_rate=rates.company_commission_rate,
            salesperson_commission_rate=rates.salesperson_commission_rate,
            salesperson_incentive_rate=rates.salesperson_incentive_rate,
            additional_incentive_tax_rate=rates.additional_incentive_tax_rate,
            vat_rate=rates.vat_rate,
            sales_tax_rate=rates.sales_tax_rate,
            annual_tax_rate=rates.annual_tax_rate,
            sales_manager_commission_rate=rates.sales_manager_commission_rate,
            company_commission_amount=company_commission,
            salesperson_commission_amount=salesperson_commission,
            salesperson_incentive_amount=salesperson_incentive,
            total_company_commission_before_tax=company_commission,
            total_salesperson_incentive_paid=salesperson_incentive,
            vat_amount=vat_amount,
            sales_tax_amount=sales_tax,
            annual_tax_amount=annual_tax,
            sales_manager_commission_amount=sales_manager_commission,
            transaction_id=transaction.id if transaction is not None else None,
            notes=data.get('notes', ''),
            created_by=current_user.id
        )

        db.session.add(sale)
        db.session.flush()  # Get the sale ID

        # Link transaction to sale (set related_entity_id)
        if transaction is not None:
            transaction.related_entity_id = sale.id
            db.session.add(transaction)

        # Update treasury balance
        if net_company_income > 0:
            Treasury.add_to_balance(net_company_income)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء معاملة البيع بنجاح',
            'sale': sale.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء معاملة البيع: {str(e)}'}), 500

@sales_bp.route('/api/sales/<int:sale_id>', methods=['GET'])
@login_required
@require_permission('view_sales')
def get_sale(sale_id):
    """Get specific sale"""
    try:
        sale = Sale.query.get_or_404(sale_id)
        return jsonify(sale.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب معاملة البيع: {str(e)}'}), 500

from src.routes.sales_new import update_sale as update_sale_new

@sales_bp.route('/api/sales/<int:sale_id>', methods=['PUT'])
@login_required
@require_permission('edit_sales')
def update_sale(sale_id):
    """Update sale with enhanced calculation logic"""
    return update_sale_new(sale_id)

@sales_bp.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
@require_permission('delete_sales')
def delete_sale(sale_id):
    """Delete sale"""
    try:
        sale = Sale.query.get_or_404(sale_id)
        
        # Delete related transactions
        Transaction.query.filter_by(reference_type='sale', reference_id=sale_id).delete()
        
        # Update treasury balance (subtract the net income)
        if sale.net_company_income > 0:
            Treasury.subtract_from_balance(sale.net_company_income)
        
        db.session.delete(sale)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف معاملة البيع بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف معاملة البيع: {str(e)}'}), 500

@sales_bp.route('/api/property-types', methods=['GET'])
@login_required
@require_permission('view_sales')
def get_property_types():
    """Get all property types with their rates"""
    try:
        property_types = PropertyTypeRates.query.all()
        return jsonify([pt.to_dict() for pt in property_types]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب أنواع العقارات: {str(e)}'}), 500

@sales_bp.route('/api/property-types', methods=['POST'])
@login_required
@require_permission('manage_property_rates')
def create_property_type():
    """Create new property type rates"""
    try:
        data = request.get_json()
        
        if not data or not data.get('property_type'):
            return jsonify({'error': 'نوع العقار مطلوب'}), 400
        
        # Check if property type already exists
        existing = PropertyTypeRates.query.filter_by(property_type=data['property_type']).first()
        if existing:
            return jsonify({'error': 'نوع العقار موجود بالفعل'}), 400
        
        property_type = PropertyTypeRates(
            property_type=data['property_type'],
            company_commission_rate=data.get('company_commission_rate', 0.0),
            salesperson_commission_rate=data.get('salesperson_commission_rate', 0.0),
            salesperson_incentive_rate=data.get('salesperson_incentive_rate', 0.0),
            additional_incentive_tax_rate=data.get('additional_incentive_tax_rate', 0.0),
            vat_rate=data.get('vat_rate', 0.14),
            sales_tax_rate=data.get('sales_tax_rate', 0.05),
            annual_tax_rate=data.get('annual_tax_rate', 0.225),
            sales_manager_commission_rate=data.get('sales_manager_commission_rate', 0.003)
        )
        
        db.session.add(property_type)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء نوع العقار بنجاح',
            'property_type': property_type.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء نوع العقار: {str(e)}'}), 500

@sales_bp.route('/api/property-types/<int:type_id>', methods=['PUT'])
@login_required
@require_permission('manage_property_rates')
def update_property_type(type_id):
    """Update property type rates"""
    try:
        property_type = PropertyTypeRates.query.get_or_404(type_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Update rates
        updatable_fields = [
            'company_commission_rate', 'salesperson_commission_rate',
            'salesperson_incentive_rate', 'additional_incentive_tax_rate',
            'vat_rate', 'sales_tax_rate', 'annual_tax_rate',
            'sales_manager_commission_rate'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(property_type, field, float(data[field]))
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث أسعار نوع العقار بنجاح',
            'property_type': property_type.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث أسعار نوع العقار: {str(e)}'}), 500

@sales_bp.route('/api/sales-stats', methods=['GET'])
@login_required
@require_permission('view_sales')
def get_sales_stats():
    """Get sales statistics"""
    try:
        # Total sales
        total_sales = Sale.query.count()
        
        # Total revenue
        total_revenue = db.session.query(func.sum(Sale.unit_price)).scalar() or 0
        
        # Total company income
        total_company_income = db.session.query(func.sum(Sale.net_company_income)).scalar() or 0
        
        # Sales by property type
        sales_by_type = db.session.query(
            Sale.property_type,
            func.count(Sale.id).label('count'),
            func.sum(Sale.unit_price).label('revenue')
        ).group_by(Sale.property_type).all()
        
        # Monthly sales (last 12 months)
        monthly_sales = db.session.query(
            func.strftime('%Y-%m', Sale.sale_date).label('month'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.unit_price).label('revenue')
        ).filter(
            Sale.sale_date >= datetime.now().replace(day=1, month=1) - timedelta(days=365)
        ).group_by(
            func.strftime('%Y-%m', Sale.sale_date)
        ).all()
        
        return jsonify({
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'total_company_income': float(total_company_income),
            'sales_by_type': [
                {
                    'property_type': row.property_type,
                    'count': row.count,
                    'revenue': float(row.revenue or 0)
                } for row in sales_by_type
            ],
            'monthly_sales': [
                {
                    'month': row.month,
                    'count': row.count,
                    'revenue': float(row.revenue or 0)
                } for row in monthly_sales
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب إحصائيات المبيعات: {str(e)}'}), 500

