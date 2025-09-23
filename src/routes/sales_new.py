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

def _to_decimal(value, default=0):
    """Robustly convert incoming form values to Decimal.
    - Treat None/"" as default
    - Strip spaces, commas, percent signs
    - Accept numeric types directly
    """
    if value is None or value == "":
        return Decimal(str(default))
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip()
        # Replace common formatting
        cleaned = cleaned.replace(',', '').replace('%', '')
        # Convert Arabic numerals to Western if present
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        for i, d in enumerate(arabic_digits):
            cleaned = cleaned.replace(d, str(i))
        if cleaned == '':
            return Decimal(str(default))
        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal(str(default))
    return Decimal(str(default))

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
    return render_template('sales/form_new.html', sale=None)

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
    return render_template('sales/form_new.html', sale=sale)

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

@sales_bp.route('/api/sales', methods=['POST'])
@login_required
@require_permission('create_sales')
def create_sale():
    """Create new sale with enhanced calculation logic"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400

        # Validate required fields
        required_fields = [
            'client_name', 'unit_code', 'property_type', 'unit_price',
            'sale_date', 'company_commission_rate'
        ]

        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400

        # Check if unit code already exists
        existing_sale = Sale.query.filter_by(unit_code=data['unit_code']).first()
        if existing_sale:
            return jsonify({'error': 'كود الوحدة موجود بالفعل'}), 400

        # Parse sale date
        try:
            sale_date = datetime.strptime(data['sale_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'تاريخ البيع غير صحيح'}), 400

        # Extract rates from form data (convert from percentage to decimal)
        unit_price = _to_decimal(data.get('unit_price'), 0)
        company_commission_rate = _to_decimal(data.get('company_commission_rate'), 0)
        salesperson_commission_rate = _to_decimal(data.get('salesperson_commission_rate'), 0)
        salesperson_incentive_rate = _to_decimal(data.get('salesperson_incentive_rate'), 0)
        additional_incentive_tax_rate = _to_decimal(data.get('additional_incentive_tax_rate'), 0)
        vat_rate = _to_decimal(data.get('vat_rate'), 0.14)
        sales_tax_rate = _to_decimal(data.get('sales_tax_rate'), 0.05)
        annual_tax_rate = _to_decimal(data.get('annual_tax_rate'), 0.225)
        salesperson_tax_rate = _to_decimal(data.get('salesperson_tax_rate'), 0)
        sales_manager_tax_rate = _to_decimal(data.get('sales_manager_tax_rate'), 0)

        # Calculate all amounts using the enhanced logic
        calculated_amounts = Sale.calculate_sale_amounts(
            unit_price=unit_price,
            company_commission_rate=company_commission_rate,
            salesperson_commission_rate=salesperson_commission_rate,
            salesperson_incentive_rate=salesperson_incentive_rate,
            vat_rate=vat_rate,
            sales_tax_rate=sales_tax_rate,
            annual_tax_rate=annual_tax_rate,
            salesperson_tax_rate=salesperson_tax_rate,
            sales_manager_tax_rate=sales_manager_tax_rate
        )

        # Create treasury transaction for net company income first
        transaction = None
        net_company_income = calculated_amounts['net_company_income']
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

        # Create sale record
        sale = Sale(
            client_name=data['client_name'],
            unit_code=data['unit_code'],
            property_type=data['property_type'],
            unit_price=unit_price,
            sale_date=sale_date,
            project_name=data.get('project_name', ''),
            salesperson_name=data.get('salesperson_name', ''),
            sales_manager_name=data.get('sales_manager_name', ''),
            notes=data.get('notes', ''),

            # Store rates
            company_commission_rate=company_commission_rate,
            salesperson_commission_rate=salesperson_commission_rate,
            salesperson_incentive_rate=salesperson_incentive_rate,
            additional_incentive_tax_rate=additional_incentive_tax_rate,
            vat_rate=vat_rate,
            sales_tax_rate=sales_tax_rate,
            annual_tax_rate=annual_tax_rate,
            salesperson_tax_rate=salesperson_tax_rate,
            sales_manager_tax_rate=sales_manager_tax_rate,

            # Store calculated amounts
            company_commission_amount=calculated_amounts['company_commission_amount'],
            salesperson_commission_amount=calculated_amounts['salesperson_commission_amount'],
            salesperson_incentive_amount=calculated_amounts['salesperson_incentive_amount'],
            total_company_commission_before_tax=calculated_amounts['total_company_commission_before_tax'],
            total_salesperson_incentive_paid=calculated_amounts['total_salesperson_incentive_paid'],
            sales_manager_commission_amount=calculated_amounts['sales_manager_commission_amount'],
            vat_amount=calculated_amounts['vat_amount'],
            sales_tax_amount=calculated_amounts['sales_tax_amount'],
            annual_tax_amount=calculated_amounts['annual_tax_amount'],
            salesperson_tax_amount=calculated_amounts['salesperson_tax_amount'],
            sales_manager_tax_amount=calculated_amounts['sales_manager_tax_amount'],
            net_company_income=calculated_amounts['net_company_income'],
            net_salesperson_income=calculated_amounts['net_salesperson_income'],
            net_sales_manager_income=calculated_amounts['net_sales_manager_income'],

            transaction_id=transaction.id if transaction is not None else None,
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

@sales_bp.route('/api/sales/<int:sale_id>', methods=['PUT'])
@login_required
@require_permission('edit_sales')
def update_sale(sale_id):
    """Update sale with enhanced calculation logic"""
    try:
        sale = Sale.query.get_or_404(sale_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400

        # Check if unit code already exists (excluding current sale)
        if 'unit_code' in data and data['unit_code'] != sale.unit_code:
            existing_sale = Sale.query.filter(
                Sale.unit_code == data['unit_code'],
                Sale.id != sale_id
            ).first()
            if existing_sale:
                return jsonify({'error': 'كود الوحدة موجود بالفعل'}), 400

        # Store old net company income for treasury adjustment
        old_net_company_income = sale.net_company_income

        # Update basic fields
        updatable_fields = [
            'client_name', 'unit_code', 'property_type', 'unit_price',
            'sale_date', 'project_name', 'salesperson_name',
            'sales_manager_name', 'notes'
        ]

        recalculate_needed = False

        for field in updatable_fields:
            if field in data:
                if field == 'sale_date':
                    try:
                        sale.sale_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'تاريخ البيع غير صحيح'}), 400
                elif field in ['unit_price', 'property_type']:
                    setattr(sale, field, data[field])
                    recalculate_needed = True
                else:
                    setattr(sale, field, data[field])

        # Update rates if provided
        rate_fields = [
            'company_commission_rate', 'salesperson_commission_rate',
            'salesperson_incentive_rate', 'additional_incentive_tax_rate', 'vat_rate', 'sales_tax_rate',
            'annual_tax_rate', 'salesperson_tax_rate', 'sales_manager_tax_rate'
        ]

        for field in rate_fields:
            if field in data:
                setattr(sale, field, Decimal(str(data[field])))
                recalculate_needed = True

        # Recalculate amounts if needed
        if recalculate_needed:
            calculated_amounts = Sale.calculate_sale_amounts(
                unit_price=sale.unit_price,
                company_commission_rate=sale.company_commission_rate,
                salesperson_commission_rate=sale.salesperson_commission_rate or 0,
                salesperson_incentive_rate=sale.salesperson_incentive_rate or 0,
                vat_rate=sale.vat_rate or 0,
                sales_tax_rate=sale.sales_tax_rate or 0,
                annual_tax_rate=sale.annual_tax_rate or 0,
                salesperson_tax_rate=sale.salesperson_tax_rate or 0,
                sales_manager_tax_rate=sale.sales_manager_tax_rate or 0
            )

            # Update calculated amounts
            for field, value in calculated_amounts.items():
                setattr(sale, field, value)

            # Update treasury balance (subtract old, add new)
            if old_net_company_income > 0:
                Treasury.subtract_from_balance(old_net_company_income)
            if calculated_amounts['net_company_income'] > 0:
                Treasury.add_to_balance(calculated_amounts['net_company_income'])

            # Update transaction amount if exists
            if sale.transaction_id:
                transaction = Transaction.query.get(sale.transaction_id)
                if transaction:
                    transaction.amount = calculated_amounts['net_company_income']
                    transaction.description = f'صافي إيراد من بيع الوحدة {sale.unit_code} - {sale.client_name}'
                    db.session.add(transaction)

        sale.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            'message': 'تم تحديث معاملة البيع بنجاح',
            'sale': sale.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث معاملة البيع: {str(e)}'}), 500

@sales_bp.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
@require_permission('delete_sales')
def delete_sale(sale_id):
    """Delete sale"""
    try:
        sale = Sale.query.get_or_404(sale_id)

        # Delete related transactions
        if sale.transaction_id:
            transaction = Transaction.query.get(sale.transaction_id)
            if transaction:
                db.session.delete(transaction)

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

@sales_bp.route('/api/calculate-preview', methods=['POST'])
@login_required
@require_permission('view_sales')
def calculate_preview():
    """Calculate preview of sale amounts without saving"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400

        # Validate required fields for calculation
        if not data.get('unit_price') or not data.get('company_commission_rate'):
            return jsonify({'error': 'سعر الوحدة ونسبة عمولة الشركة مطلوبان'}), 400

        # Extract rates from form data
        unit_price = _to_decimal(data.get('unit_price'), 0)
        company_commission_rate = _to_decimal(data.get('company_commission_rate'), 0)
        salesperson_commission_rate = _to_decimal(data.get('salesperson_commission_rate'), 0)
        salesperson_incentive_rate = _to_decimal(data.get('salesperson_incentive_rate'), 0)
        additional_incentive_tax_rate = _to_decimal(data.get('additional_incentive_tax_rate'), 0)
        vat_rate = _to_decimal(data.get('vat_rate'), 0.14)
        sales_tax_rate = _to_decimal(data.get('sales_tax_rate'), 0.05)
        annual_tax_rate = _to_decimal(data.get('annual_tax_rate'), 0.225)
        salesperson_tax_rate = _to_decimal(data.get('salesperson_tax_rate'), 0)
        sales_manager_tax_rate = _to_decimal(data.get('sales_manager_tax_rate'), 0)

        # Calculate all amounts
        calculated_amounts = Sale.calculate_sale_amounts(
            unit_price=unit_price,
            company_commission_rate=company_commission_rate,
            salesperson_commission_rate=salesperson_commission_rate,
            salesperson_incentive_rate=salesperson_incentive_rate,
            vat_rate=vat_rate,
            sales_tax_rate=sales_tax_rate,
            annual_tax_rate=annual_tax_rate,
            salesperson_tax_rate=salesperson_tax_rate,
            sales_manager_tax_rate=sales_manager_tax_rate
        )

        # Convert Decimal to float for JSON serialization
        result = {}
        for key, value in calculated_amounts.items():
            result[key] = float(value)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'خطأ في حساب المعاينة: {str(e)}'}), 500

@sales_bp.route('/api/sales/stats', methods=['GET'])
@login_required
@require_permission('view_sales')
def get_sales_stats():
    """Get sales statistics"""
    try:
        # Total sales count
        total_sales = Sale.query.count()

        # Total revenue (sum of unit prices)
        total_revenue = db.session.query(func.sum(Sale.unit_price)).scalar() or 0

        # Total company income (sum of net company income)
        total_company_income = db.session.query(func.sum(Sale.net_company_income)).scalar() or 0

        # Sales by property type
        sales_by_type = db.session.query(
            Sale.property_type,
            func.count(Sale.id).label('count'),
            func.sum(Sale.unit_price).label('revenue')
        ).group_by(Sale.property_type).all()

        # Monthly sales for current year
        current_year = datetime.now().year
        monthly_sales = db.session.query(
            func.extract('month', Sale.sale_date).label('month'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.unit_price).label('revenue')
        ).filter(
            func.extract('year', Sale.sale_date) == current_year
        ).group_by(func.extract('month', Sale.sale_date)).all()

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
