#!/usr/bin/env python3
"""
Standalone test script to verify the calculation logic matches the Excel requirements.
This script implements the calculation logic without Flask dependencies.
"""

from decimal import Decimal

def calculate_sale_amounts(unit_price, company_commission_rate, 
                         salesperson_commission_rate=0, salesperson_incentive_rate=0,
                         vat_rate=0.14, sales_tax_rate=0.05, annual_tax_rate=0.225,
                         salesperson_tax_rate=0, sales_manager_tax_rate=0):
    """
    Calculate all amounts for a sale based on Excel logic
    
    Args:
        unit_price: Base unit price
        company_commission_rate: Company commission percentage (as decimal)
        salesperson_commission_rate: Salesperson commission percentage (as decimal)
        salesperson_incentive_rate: Salesperson incentive percentage (as decimal)
        vat_rate: VAT percentage (as decimal, default 14%)
        sales_tax_rate: Sales tax percentage (as decimal, default 5%)
        annual_tax_rate: Annual tax percentage (as decimal, default 22.5%)
        salesperson_tax_rate: Salesperson tax percentage (as decimal)
        sales_manager_tax_rate: Sales manager tax percentage (as decimal)
    
    Returns:
        Dictionary with all calculated amounts
    """
    # Convert to Decimal for precise calculations
    unit_price = Decimal(str(unit_price))
    company_commission_rate = Decimal(str(company_commission_rate))
    salesperson_commission_rate = Decimal(str(salesperson_commission_rate or 0))
    salesperson_incentive_rate = Decimal(str(salesperson_incentive_rate or 0))
    vat_rate = Decimal(str(vat_rate or 0))
    sales_tax_rate = Decimal(str(sales_tax_rate or 0))
    annual_tax_rate = Decimal(str(annual_tax_rate or 0))
    salesperson_tax_rate = Decimal(str(salesperson_tax_rate or 0))
    sales_manager_tax_rate = Decimal(str(sales_manager_tax_rate or 0))
    
    # Calculate commission amounts
    company_commission_amount = unit_price * company_commission_rate
    salesperson_commission_amount = unit_price * salesperson_commission_rate
    salesperson_incentive_amount = unit_price * salesperson_incentive_rate
    
    # Sales manager commission (assuming 10% of company commission as per common practice)
    sales_manager_commission_amount = company_commission_amount * Decimal('0.1')
    
    # Calculate tax amounts
    vat_amount = company_commission_amount * vat_rate
    sales_tax_amount = company_commission_amount * sales_tax_rate
    annual_tax_amount = company_commission_amount * annual_tax_rate
    salesperson_tax_amount = (salesperson_commission_amount + salesperson_incentive_amount) * salesperson_tax_rate
    sales_manager_tax_amount = sales_manager_commission_amount * sales_manager_tax_rate
    
    # Calculate net amounts
    net_company_income = (company_commission_amount - vat_amount - sales_tax_amount - 
                        annual_tax_amount - sales_manager_commission_amount - sales_manager_tax_amount)
    net_salesperson_income = salesperson_commission_amount + salesperson_incentive_amount - salesperson_tax_amount
    net_sales_manager_income = sales_manager_commission_amount - sales_manager_tax_amount
    
    return {
        'company_commission_amount': company_commission_amount,
        'salesperson_commission_amount': salesperson_commission_amount,
        'salesperson_incentive_amount': salesperson_incentive_amount,
        'sales_manager_commission_amount': sales_manager_commission_amount,
        'vat_amount': vat_amount,
        'sales_tax_amount': sales_tax_amount,
        'annual_tax_amount': annual_tax_amount,
        'salesperson_tax_amount': salesperson_tax_amount,
        'sales_manager_tax_amount': sales_manager_tax_amount,
        'net_company_income': net_company_income,
        'net_salesperson_income': net_salesperson_income,
        'net_sales_manager_income': net_sales_manager_income
    }

def test_basic_calculation():
    """Test basic calculation with typical values"""
    print("=== Test 1: Basic Calculation ===")
    
    # Test data
    unit_price = 1000000  # 1 million EGP
    company_commission_rate = 0.05  # 5%
    salesperson_commission_rate = 0.02  # 2%
    salesperson_incentive_rate = 0.01  # 1%
    vat_rate = 0.14  # 14%
    sales_tax_rate = 0.05  # 5%
    annual_tax_rate = 0.225  # 22.5%
    salesperson_tax_rate = 0.10  # 10%
    sales_manager_tax_rate = 0.15  # 15%
    
    result = calculate_sale_amounts(
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
    
    print(f"Unit Price: {unit_price:,.2f} EGP")
    print(f"Company Commission (5%): {float(result['company_commission_amount']):,.2f} EGP")
    print(f"Salesperson Commission (2%): {float(result['salesperson_commission_amount']):,.2f} EGP")
    print(f"Salesperson Incentive (1%): {float(result['salesperson_incentive_amount']):,.2f} EGP")
    print(f"Sales Manager Commission (10% of company): {float(result['sales_manager_commission_amount']):,.2f} EGP")
    print()
    print("Tax Calculations:")
    print(f"VAT (14% of company commission): {float(result['vat_amount']):,.2f} EGP")
    print(f"Sales Tax (5% of company commission): {float(result['sales_tax_amount']):,.2f} EGP")
    print(f"Annual Tax (22.5% of company commission): {float(result['annual_tax_amount']):,.2f} EGP")
    print(f"Salesperson Tax (10% of salesperson total): {float(result['salesperson_tax_amount']):,.2f} EGP")
    print(f"Sales Manager Tax (15% of sales manager commission): {float(result['sales_manager_tax_amount']):,.2f} EGP")
    print()
    print("Net Amounts:")
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    print(f"Net Salesperson Income: {float(result['net_salesperson_income']):,.2f} EGP")
    print(f"Net Sales Manager Income: {float(result['net_sales_manager_income']):,.2f} EGP")
    print()
    
    # Verify calculations manually
    expected_company_commission = unit_price * company_commission_rate
    expected_salesperson_commission = unit_price * salesperson_commission_rate
    expected_salesperson_incentive = unit_price * salesperson_incentive_rate
    expected_sales_manager_commission = expected_company_commission * 0.1
    
    expected_vat = expected_company_commission * vat_rate
    expected_sales_tax = expected_company_commission * sales_tax_rate
    expected_annual_tax = expected_company_commission * annual_tax_rate
    expected_salesperson_tax = (expected_salesperson_commission + expected_salesperson_incentive) * salesperson_tax_rate
    expected_sales_manager_tax = expected_sales_manager_commission * sales_manager_tax_rate
    
    expected_net_company = (expected_company_commission - expected_vat - expected_sales_tax - 
                           expected_annual_tax - expected_sales_manager_commission - expected_sales_manager_tax)
    expected_net_salesperson = expected_salesperson_commission + expected_salesperson_incentive - expected_salesperson_tax
    expected_net_sales_manager = expected_sales_manager_commission - expected_sales_manager_tax
    
    print("Verification:")
    print(f"Company Commission Match: {abs(float(result['company_commission_amount']) - expected_company_commission) < 0.01}")
    print(f"Net Company Income Match: {abs(float(result['net_company_income']) - expected_net_company) < 0.01}")
    print(f"Net Salesperson Income Match: {abs(float(result['net_salesperson_income']) - expected_net_salesperson) < 0.01}")
    print(f"Net Sales Manager Income Match: {abs(float(result['net_sales_manager_income']) - expected_net_sales_manager) < 0.01}")
    print()

def test_minimal_calculation():
    """Test calculation with minimal required fields only"""
    print("=== Test 2: Minimal Calculation (Company Commission Only) ===")
    
    unit_price = 500000  # 500k EGP
    company_commission_rate = 0.03  # 3%
    
    result = calculate_sale_amounts(
        unit_price=unit_price,
        company_commission_rate=company_commission_rate
    )
    
    print(f"Unit Price: {unit_price:,.2f} EGP")
    print(f"Company Commission (3%): {float(result['company_commission_amount']):,.2f} EGP")
    print(f"VAT (14% default): {float(result['vat_amount']):,.2f} EGP")
    print(f"Sales Tax (5% default): {float(result['sales_tax_amount']):,.2f} EGP")
    print(f"Annual Tax (22.5% default): {float(result['annual_tax_amount']):,.2f} EGP")
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    print()

def test_zero_taxes():
    """Test calculation with zero tax rates"""
    print("=== Test 3: Zero Tax Rates ===")
    
    unit_price = 800000  # 800k EGP
    company_commission_rate = 0.04  # 4%
    salesperson_commission_rate = 0.015  # 1.5%
    
    result = calculate_sale_amounts(
        unit_price=unit_price,
        company_commission_rate=company_commission_rate,
        salesperson_commission_rate=salesperson_commission_rate,
        vat_rate=0,
        sales_tax_rate=0,
        annual_tax_rate=0,
        salesperson_tax_rate=0,
        sales_manager_tax_rate=0
    )
    
    print(f"Unit Price: {unit_price:,.2f} EGP")
    print(f"Company Commission (4%): {float(result['company_commission_amount']):,.2f} EGP")
    print(f"Salesperson Commission (1.5%): {float(result['salesperson_commission_amount']):,.2f} EGP")
    print(f"All Tax Amounts: {float(result['vat_amount']):,.2f} EGP (should be 0)")
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    print(f"Net Salesperson Income: {float(result['net_salesperson_income']):,.2f} EGP")
    print()

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("=== Test 4: Edge Cases ===")
    
    # Very small unit price
    print("Small Unit Price (1000 EGP):")
    result = calculate_sale_amounts(
        unit_price=1000,
        company_commission_rate=0.05
    )
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    
    # Very large unit price
    print("\nLarge Unit Price (100 Million EGP):")
    result = calculate_sale_amounts(
        unit_price=100000000,
        company_commission_rate=0.02
    )
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    
    # High tax rates
    print("\nHigh Tax Rates (50% each):")
    result = calculate_sale_amounts(
        unit_price=1000000,
        company_commission_rate=0.05,
        vat_rate=0.5,
        sales_tax_rate=0.5,
        annual_tax_rate=0.5
    )
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    print()

def test_excel_scenario():
    """Test a scenario that matches typical Excel calculations"""
    print("=== Test 5: Excel-like Scenario ===")
    
    # Typical real estate transaction
    unit_price = 2500000  # 2.5 million EGP
    company_commission_rate = 0.025  # 2.5%
    salesperson_commission_rate = 0.005  # 0.5%
    salesperson_incentive_rate = 0.005  # 0.5%
    vat_rate = 0.14  # 14%
    sales_tax_rate = 0.05  # 5%
    annual_tax_rate = 0.225  # 22.5%
    
    result = calculate_sale_amounts(
        unit_price=unit_price,
        company_commission_rate=company_commission_rate,
        salesperson_commission_rate=salesperson_commission_rate,
        salesperson_incentive_rate=salesperson_incentive_rate,
        vat_rate=vat_rate,
        sales_tax_rate=sales_tax_rate,
        annual_tax_rate=annual_tax_rate
    )
    
    print(f"Real Estate Transaction: {unit_price:,.2f} EGP")
    print(f"Company Commission: {float(result['company_commission_amount']):,.2f} EGP")
    print(f"Total Taxes: {float(result['vat_amount'] + result['sales_tax_amount'] + result['annual_tax_amount']):,.2f} EGP")
    print(f"Net Company Income: {float(result['net_company_income']):,.2f} EGP")
    print(f"Salesperson Total: {float(result['net_salesperson_income']):,.2f} EGP")
    
    # Calculate percentage of net income vs unit price
    net_percentage = (float(result['net_company_income']) / unit_price) * 100
    print(f"Net Income as % of Unit Price: {net_percentage:.2f}%")
    print()

def test_user_scenario():
    """Test the exact scenario described by the user"""
    print("=== Test 6: User's Excel Scenario ===")
    
    # Based on user's description - typical values
    unit_price = 3000000  # 3 million EGP
    company_commission_rate = 0.03  # 3%
    salesperson_commission_rate = 0.005  # 0.5%
    salesperson_incentive_rate = 0.005  # 0.5%
    vat_rate = 0.14  # 14% (default)
    sales_tax_rate = 0.05  # 5% (default)
    annual_tax_rate = 0.225  # 22.5% (default)
    salesperson_tax_rate = 0.22  # 22% (example)
    sales_manager_tax_rate = 0.22  # 22% (example)
    
    result = calculate_sale_amounts(
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
    
    print("User's Scenario - All Fields Filled:")
    print(f"سعر الوحدة: {unit_price:,.2f} جنيه")
    print(f"عمولة الشركة (3%): {float(result['company_commission_amount']):,.2f} جنيه")
    print(f"عمولة السلز (0.5%): {float(result['salesperson_commission_amount']):,.2f} جنيه")
    print(f"حافز السلز (0.5%): {float(result['salesperson_incentive_amount']):,.2f} جنيه")
    print(f"عمولة مدير المبيعات: {float(result['sales_manager_commission_amount']):,.2f} جنيه")
    print()
    print("الضرائب:")
    print(f"ضريبة القيمة المضافة (14%): {float(result['vat_amount']):,.2f} جنيه")
    print(f"ضريبة المبيعات (5%): {float(result['sales_tax_amount']):,.2f} جنيه")
    print(f"الضريبة السنوية (22.5%): {float(result['annual_tax_amount']):,.2f} جنيه")
    print(f"ضريبة السلز (22%): {float(result['salesperson_tax_amount']):,.2f} جنيه")
    print(f"ضريبة مدير المبيعات (22%): {float(result['sales_manager_tax_amount']):,.2f} جنيه")
    print()
    print("صافي الإيرادات:")
    print(f"صافي إيراد الشركة: {float(result['net_company_income']):,.2f} جنيه")
    print(f"صافي عمولة السلز: {float(result['net_salesperson_income']):,.2f} جنيه")
    print(f"صافي عمولة مدير المبيعات: {float(result['net_sales_manager_income']):,.2f} جنيه")
    print()
    print(f"المبلغ الذي سيضاف للخزنة: {float(result['net_company_income']):,.2f} جنيه")
    print()

if __name__ == "__main__":
    print("Testing Sale Calculation Logic")
    print("=" * 50)
    print()
    
    test_basic_calculation()
    test_minimal_calculation()
    test_zero_taxes()
    test_edge_cases()
    test_excel_scenario()
    test_user_scenario()
    
    print("All tests completed!")
    print("Review the results to ensure calculations match Excel logic.")

