from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from src.models.sale import PropertyTypeRates
from src.utils.excel_calculator import ExcelCalculationEngine
from decimal import Decimal

sales_api_bp = Blueprint('sales_api', __name__)

@sales_api_bp.route('/api/calculate-preview', methods=['POST'])
@login_required
def calculate_preview():
    """
    Calculate financial preview using Excel logic
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        property_type = data.get('property_type')
        unit_price = data.get('unit_price')
        
        if not property_type or not unit_price:
            return jsonify({'error': 'نوع العقار وسعر الوحدة مطلوبان'}), 400
        
        try:
            unit_price = Decimal(str(unit_price))
        except (ValueError, TypeError):
            return jsonify({'error': 'سعر الوحدة غير صحيح'}), 400
        
        if unit_price <= 0:
            return jsonify({'error': 'سعر الوحدة يجب أن يكون أكبر من صفر'}), 400
        
        # Get property type rates
        rates = PropertyTypeRates.query.filter_by(property_type=property_type).first()
        if not rates:
            return jsonify({'error': f'لم يتم العثور على أسعار نوع العقار: {property_type}'}), 400
        
        # Convert rates to dictionary
        rates_dict = {
            'company_commission_rate': float(rates.company_commission_rate),
            'salesperson_commission_rate': float(rates.salesperson_commission_rate),
            'salesperson_incentive_rate': float(rates.salesperson_incentive_rate),
            'additional_incentive_tax_rate': float(rates.additional_incentive_tax_rate),
            'vat_rate': float(rates.vat_rate),
            'sales_tax_rate': float(rates.sales_tax_rate),
            'annual_tax_rate': float(rates.annual_tax_rate),
            'sales_manager_commission_rate': float(rates.sales_manager_commission_rate)
        }
        
        # Calculate using Excel logic
        calculator = ExcelCalculationEngine()
        calculations = calculator.calculate_sale_financials(unit_price, rates_dict)
        
        # Convert Decimal values to float for JSON serialization
        result = {}
        for key, value in calculations.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            else:
                result[key] = value
        
        return jsonify({
            'success': True,
            'calculations': result,
            'unit_price': float(unit_price),
            'property_type': property_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في حساب المعاينة: {str(e)}'}), 500

@sales_api_bp.route('/api/validate-calculation', methods=['POST'])
@login_required
def validate_calculation():
    """
    Validate calculation results against expected values
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        property_type = data.get('property_type')
        unit_price = data.get('unit_price')
        expected_results = data.get('expected_results', {})
        
        if not property_type or not unit_price:
            return jsonify({'error': 'نوع العقار وسعر الوحدة مطلوبان'}), 400
        
        try:
            unit_price = Decimal(str(unit_price))
        except (ValueError, TypeError):
            return jsonify({'error': 'سعر الوحدة غير صحيح'}), 400
        
        # Get property type rates
        rates = PropertyTypeRates.query.filter_by(property_type=property_type).first()
        if not rates:
            return jsonify({'error': f'لم يتم العثور على أسعار نوع العقار: {property_type}'}), 400
        
        # Convert rates to dictionary
        rates_dict = {
            'company_commission_rate': float(rates.company_commission_rate),
            'salesperson_commission_rate': float(rates.salesperson_commission_rate),
            'salesperson_incentive_rate': float(rates.salesperson_incentive_rate),
            'additional_incentive_tax_rate': float(rates.additional_incentive_tax_rate),
            'vat_rate': float(rates.vat_rate),
            'sales_tax_rate': float(rates.sales_tax_rate),
            'annual_tax_rate': float(rates.annual_tax_rate),
            'sales_manager_commission_rate': float(rates.sales_manager_commission_rate)
        }
        
        # Validate using Excel logic
        calculator = ExcelCalculationEngine()
        validation_result = calculator.validate_calculation(unit_price, rates_dict, expected_results)
        
        # Convert Decimal values to float for JSON serialization
        if 'calculated' in validation_result:
            calculated = {}
            for key, value in validation_result['calculated'].items():
                if isinstance(value, Decimal):
                    calculated[key] = float(value)
                else:
                    calculated[key] = value
            validation_result['calculated'] = calculated
        
        if 'errors' in validation_result:
            for error in validation_result['errors']:
                for key, value in error.items():
                    if isinstance(value, Decimal):
                        error[key] = float(value)
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        return jsonify({'error': f'خطأ في التحقق من الحساب: {str(e)}'}), 500

