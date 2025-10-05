from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.database import db
from src.models.sale import Sale, PropertyTypeRates
from src.models.treasury import Treasury
from src.models.transaction import Transaction
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from src.utils.number_utils import convert_arabic_to_english_digits

def _to_decimal(value, default=0):
    """Converts a value to a Decimal, handling various input types."""
    if value is None or value == "":
        return Decimal(str(default))
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace(',', '').replace('%', '')
        if cleaned == '':
            return Decimal(str(default))
        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal(str(default))
    return Decimal(str(default))

def calculate_financials(unit_price, rates):
    """
    Calculates all financial amounts for a real estate sale based on provided rates.

    Args:
        unit_price (Decimal): The sale price of the unit.
        rates (dict): A dictionary containing all applicable commission and tax rates.

    Returns:
        dict: A dictionary with all calculated financial amounts.
    """
    # --- Rate Conversions ---
    company_commission_rate = _to_decimal(rates.get('company_commission_rate', 0)) / 100
    salesperson_commission_rate = _to_decimal(rates.get('salesperson_commission_rate', 0)) / 100
    salesperson_incentive_rate = _to_decimal(rates.get('salesperson_incentive_rate', 0)) / 100
    sales_manager_commission_rate = _to_decimal(rates.get('sales_manager_commission_rate', 0)) / 100
    vat_rate = _to_decimal(rates.get('vat_rate', 14)) / 100
    sales_tax_rate = _to_decimal(rates.get('sales_tax_rate', 5)) / 100
    annual_tax_rate = _to_decimal(rates.get('annual_tax_rate', 22.5)) / 100
    salesperson_tax_rate = _to_decimal(rates.get('salesperson_tax_rate', 19)) / 100
    sales_manager_tax_rate = _to_decimal(rates.get('sales_manager_tax_rate', 19)) / 100

    # --- Commission Calculations ---
    company_commission = unit_price * company_commission_rate
    salesperson_commission = unit_price * salesperson_commission_rate
    salesperson_incentive = unit_price * salesperson_incentive_rate
    sales_manager_commission = unit_price * sales_manager_commission_rate

    # --- Tax Calculations ---
    vat_amount = company_commission * vat_rate
    sales_tax_amount = company_commission * sales_tax_rate
    annual_tax = company_commission * annual_tax_rate
    salesperson_tax = salesperson_commission * salesperson_tax_rate
    sales_manager_tax = sales_manager_commission * sales_manager_tax_rate

    # --- Net Income Calculations ---
    net_salesperson_income = salesperson_commission - salesperson_tax
    net_sales_manager_income = sales_manager_commission - sales_manager_tax

    net_company_income = (
        company_commission
        - vat_amount
        - sales_tax_amount
        - annual_tax
        - salesperson_commission
        - salesperson_incentive
        - sales_manager_commission
    )

    def round_decimal(value):
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        'company_commission': round_decimal(company_commission),
        'salesperson_commission': round_decimal(salesperson_commission),
        'salesperson_incentive': round_decimal(salesperson_incentive),
        'sales_manager_commission': round_decimal(sales_manager_commission),
        'vat_amount': round_decimal(vat_amount),
        'sales_tax_amount': round_decimal(sales_tax_amount),
        'annual_tax': round_decimal(annual_tax),
        'salesperson_tax': round_decimal(salesperson_tax),
        'sales_manager_tax': round_decimal(sales_manager_tax),
        'net_company_income': round_decimal(net_company_income),
        'net_salesperson_income': round_decimal(net_salesperson_income),
        'net_sales_manager_income': round_decimal(net_sales_manager_income),
    }

def create_sale_with_excel_logic():
    """Create new sale using the refactored calculation logic"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['client_name', 'unit_code', 'unit_price', 'property_type', 'sale_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        if Sale.query.filter_by(unit_code=data['unit_code']).first():
            return jsonify({'error': 'Unit code already exists'}), 400

        unit_price = _to_decimal(data['unit_price'])
        if unit_price <= 0:
            return jsonify({'error': 'Unit price must be greater than zero'}), 400

        rates = {k: convert_arabic_to_english_digits(v) for k, v in data.items() if 'rate' in k}
        calculations = calculate_financials(unit_price, rates)

        sale = Sale(
            client_name=data['client_name'],
            sale_date=datetime.strptime(data['sale_date'], '%Y-%m-%d').date(),
            unit_code=data['unit_code'],
            unit_price=unit_price,
            property_type=data['property_type'],
            project_name=data.get('project_name', ''),
            salesperson_name=data.get('salesperson_name', ''),
            sales_manager_name=data.get('sales_manager_name', ''),
            notes=data.get('notes', ''),
            created_by=current_user.id,
            company_commission_rate=_to_decimal(rates.get('company_commission_rate', 0)) / 100,
            salesperson_commission_rate=_to_decimal(rates.get('salesperson_commission_rate', 0)) / 100,
            salesperson_incentive_rate=_to_decimal(rates.get('salesperson_incentive_rate', 0)) / 100,
            vat_rate=_to_decimal(rates.get('vat_rate', 14)) / 100,
            sales_tax_rate=_to_decimal(rates.get('sales_tax_rate', 5)) / 100,
            annual_tax_rate=_to_decimal(rates.get('annual_tax_rate', 22.5)) / 100,
            salesperson_tax_rate=_to_decimal(rates.get('salesperson_tax_rate', 19)) / 100,
            sales_manager_tax_rate=_to_decimal(rates.get('sales_manager_tax_rate', 19)) / 100,
            company_commission_amount=calculations['company_commission'],
            salesperson_commission_amount=calculations['salesperson_commission'],
            salesperson_incentive_amount=calculations['salesperson_incentive'],
            sales_manager_commission_amount=calculations['sales_manager_commission'],
            vat_amount=calculations['vat_amount'],
            sales_tax_amount=calculations['sales_tax_amount'],
            annual_tax_amount=calculations['annual_tax'],
            salesperson_tax_amount=calculations['salesperson_tax'],
            sales_manager_tax_amount=calculations['sales_manager_tax'],
            net_company_income=calculations['net_company_income'],
            net_salesperson_income=calculations['net_salesperson_income'],
            net_sales_manager_income=calculations['net_sales_manager_income']
        )

        db.session.add(sale)

        transaction = Transaction(
            type='Sale Revenue',
            amount=calculations['net_company_income'],
            description=f'Sale transaction - {data["client_name"]} - {data["unit_code"]}',
            transaction_date=datetime.now(),
            related_entity_type='sale',
            user_id=current_user.id
        )

        db.session.add(transaction)
        db.session.flush()

        transaction.related_entity_id = sale.id
        sale.transaction_id = transaction.id

        Treasury.add_to_balance(calculations['net_company_income'])

        db.session.commit()

        return jsonify({'message': 'Sale created successfully', 'sale': sale.to_dict(), 'calculations': calculations}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating sale: {str(e)}'}), 500



def update_sale_with_excel_logic(sale_id):
    """Update sale using the refactored calculation logic"""
    try:
        sale = Sale.query.get_or_404(sale_id)
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["client_name", "unit_code", "unit_price", "property_type", "sale_date"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        existing_sale = Sale.query.filter(
            Sale.unit_code == data["unit_code"],
            Sale.id != sale_id
        ).first()
        if existing_sale:
            return jsonify({"error": "Unit code already exists"}), 400

        unit_price = _to_decimal(data["unit_price"])
        if unit_price <= 0:
            return jsonify({"error": "Unit price must be greater than zero"}), 400

        rates = {k: convert_arabic_to_english_digits(v) for k, v in data.items() if "rate" in k}
        calculations = calculate_financials(unit_price, rates)

        # Store old net company income for treasury adjustment
        old_net_company_income = sale.net_company_income

        # Update sale object fields
        sale.client_name = data["client_name"]
        sale.sale_date = datetime.strptime(data["sale_date"], '%Y-%m-%d').date()
        sale.unit_code = data["unit_code"]
        sale.unit_price = unit_price
        sale.property_type = data["property_type"]
        sale.project_name = data.get("project_name", '').strip()
        sale.salesperson_name = data.get("salesperson_name", '').strip()
        sale.sales_manager_name = data.get("sales_manager_name", '').strip()
        sale.notes = data.get("notes", '').strip()
        sale.company_commission_rate = _to_decimal(rates.get("company_commission_rate", 0)) / 100
        sale.salesperson_commission_rate = _to_decimal(rates.get("salesperson_commission_rate", 0)) / 100
        sale.salesperson_incentive_rate = _to_decimal(rates.get("salesperson_incentive_rate", 0)) / 100
        sale.vat_rate = _to_decimal(rates.get("vat_rate", 14)) / 100
        sale.sales_tax_rate = _to_decimal(rates.get("sales_tax_rate", 5)) / 100
        sale.annual_tax_rate = _to_decimal(rates.get("annual_tax_rate", 22.5)) / 100
        sale.salesperson_tax_rate = _to_decimal(rates.get("salesperson_tax_rate", 19)) / 100
        sale.sales_manager_tax_rate = _to_decimal(rates.get("sales_manager_tax_rate", 19)) / 100

        # Update calculated amounts
        sale.company_commission_amount = calculations["company_commission"]
        sale.salesperson_commission_amount = calculations["salesperson_commission"]
        sale.salesperson_incentive_amount = calculations["salesperson_incentive"]
        sale.sales_manager_commission_amount = calculations["sales_manager_commission"]
        sale.vat_amount = calculations["vat_amount"]
        sale.sales_tax_amount = calculations["sales_tax_amount"]
        sale.annual_tax_amount = calculations["annual_tax"]
        sale.salesperson_tax_amount = calculations["salesperson_tax"]
        sale.sales_manager_tax_amount = calculations["sales_manager_tax"]
        sale.net_company_income = calculations["net_company_income"]
        sale.net_salesperson_income = calculations["net_salesperson_income"]
        sale.net_sales_manager_income = calculations["net_sales_manager_income"]
        sale.updated_at = datetime.utcnow()

        # Update associated transaction
        if sale.transaction:
            # Adjust treasury balance by reversing old amount and adding new amount
            Treasury.subtract_from_balance(old_net_company_income)
            Treasury.add_to_balance(calculations["net_company_income"])

            sale.transaction.amount = calculations["net_company_income"]
            sale.transaction.description = f'Updated Sale transaction - {data["client_name"]} - {data["unit_code"]}'
            sale.transaction.transaction_date = datetime.now()
            sale.transaction.user_id = current_user.id
        else:
            # If for some reason transaction is missing, create a new one
            transaction = Transaction(
                type='Sale Revenue',
                amount=calculations['net_company_income'],
                description=f'Sale transaction - {data["client_name"]} - {data["unit_code"]}',
                transaction_date=datetime.now(),
                related_entity_type='sale',
                related_entity_id=sale.id,
                user_id=current_user.id
            )
            db.session.add(transaction)
            db.session.flush()
            sale.transaction_id = transaction.id
            Treasury.add_to_balance(calculations['net_company_income'])

        db.session.commit()
        return jsonify({
            'message': 'Sale updated successfully',
            'sale': sale.to_dict(),
            'calculations': calculations
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating sale: {str(e)}'}), 500




def calculate_preview_excel_logic():
    """Calculate preview for sales using the refactored calculation logic"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        unit_price = _to_decimal(data.get("unit_price"))
        if unit_price <= 0:
            return jsonify({"error": "Unit price must be greater than zero"}), 400

        rates = {k: convert_arabic_to_english_digits(v) for k, v in data.items() if "rate" in k}
        calculations = calculate_financials(unit_price, rates)

        return jsonify({"message": "Preview calculated successfully", "calculations": calculations}), 200

    except Exception as e:
        return jsonify({"error": f"Error calculating preview: {str(e)}"}), 500

