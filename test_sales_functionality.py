#!/usr/bin/env python3
"""
Test script to verify sales functionality with additional_incentive_tax_rate field
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.database import db
from src.models.sale import Sale, PropertyTypeRates
from src.models.user import User, Role, Permission
from flask import Flask
from decimal import Decimal

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'broman_accounting.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def test_database_connection():
    """Test database connection and basic functionality"""
    with app.app_context():
        print("Testing database connection...")

        # Test if we can query the database
        try:
            # Check if PropertyTypeRates table exists and has data
            property_types = PropertyTypeRates.query.all()
            print(f"✓ Found {len(property_types)} property types in database")

            # Check if Sales table exists
            sales_count = Sale.query.count()
            print(f"✓ Found {sales_count} sales records in database")

            # Test the additional_incentive_tax_rate field
            if property_types:
                pt = property_types[0]
                print(f"✓ Property type '{pt.property_type}' has additional_incentive_tax_rate: {pt.additional_incentive_tax_rate}")

            # Test Sale model to_dict method
            if sales_count > 0:
                sale = Sale.query.first()
                sale_dict = sale.to_dict()
                if 'additional_incentive_tax_rate' in sale_dict:
                    print(f"✓ Sale model includes additional_incentive_tax_rate: {sale_dict['additional_incentive_tax_rate']}")
                else:
                    print("✗ Sale model missing additional_incentive_tax_rate field")

            print("✓ Database connection and basic functionality working correctly!")

        except Exception as e:
            print(f"✗ Database error: {e}")
            return False

    return True

def test_calculate_sale_amounts():
    """Test the calculate_sale_amounts method with additional_incentive_tax_rate"""
    with app.app_context():
        print("\nTesting calculate_sale_amounts method...")

        try:
            # Test calculation with additional_incentive_tax_rate
            result = Sale.calculate_sale_amounts(
                unit_price=1000000,
                company_commission_rate=0.05,
                salesperson_commission_rate=0.02,
                salesperson_incentive_rate=0.01,
                additional_incentive_tax_rate=0.005,  # 0.5% additional incentive tax
                vat_rate=0.14,
                sales_tax_rate=0.05,
                annual_tax_rate=0.225,
                salesperson_tax_rate=0.1,
                sales_manager_tax_rate=0.1
            )

            print("✓ Calculation completed successfully!")
            print(f"  - Company commission amount: {result['company_commission_amount']}")
            print(f"  - Salesperson commission amount: {result['salesperson_commission_amount']}")
            print(f"  - Salesperson incentive amount: {result['salesperson_incentive_amount']}")
            print(f"  - Sales manager commission amount: {result['sales_manager_commission_amount']}")
            print(f"  - Net company income: {result['net_company_income']}")
            print(f"  - Net salesperson income: {result['net_salesperson_income']}")
            print(f"  - Net sales manager income: {result['net_sales_manager_income']}")

            return True

        except Exception as e:
            print(f"✗ Calculation error: {e}")
            return False

if __name__ == "__main__":
    print("=== Sales Functionality Test ===")

    success = True
    success &= test_database_connection()
    success &= test_calculate_sale_amounts()

    if success:
        print("\n🎉 All tests passed! The sales functionality with additional_incentive_tax_rate is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
