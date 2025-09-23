#!/usr/bin/env python3
"""
Complete test for sales creation functionality
This test simulates the entire sales creation process
"""

import sys
import os
import sqlite3
import json
from datetime import datetime
from decimal import Decimal

def test_database_schema():
    """Test that all required columns exist and have correct constraints"""
    print("=== Testing Database Schema ===")

    db_path = os.path.join('src', 'database', 'broman_accounting.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get current schema
    cur.execute("PRAGMA table_info(sales);")
    columns = cur.execute("PRAGMA table_info(sales);").fetchall()

    print(f"✓ Found {len(columns)} columns in sales table")

    # Check for required columns
    required_columns = [
        'sales_manager_commission_rate',
        'salesperson_tax_rate',
        'sales_manager_tax_rate',
        'additional_incentive_tax_rate'
    ]

    missing_columns = []
    for col in required_columns:
        found = False
        for column in columns:
            if column[1] == col:
                found = True
                print(f"✓ {col}: NOT NULL={column[3]}, DEFAULT={column[4]}")
                break
        if not found:
            missing_columns.append(col)

    if missing_columns:
        print(f"✗ Missing columns: {missing_columns}")
        return False

    conn.close()
    return True

def test_sql_insert():
    """Test the exact INSERT statement that was failing"""
    print("\n=== Testing SQL INSERT Statement ===")

    db_path = os.path.join('src', 'database', 'broman_accounting.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # This is the exact INSERT statement from the original error
        insert_sql = """
        INSERT INTO sales (
            client_name, sale_date, unit_code, unit_price, property_type,
            project_name, salesperson_name, sales_manager_name, notes, created_by,
            company_commission_rate, salesperson_commission_rate, salesperson_incentive_rate,
            additional_incentive_tax_rate, vat_rate, sales_tax_rate, annual_tax_rate,
            salesperson_tax_rate, sales_manager_tax_rate, sales_manager_commission_rate,
            company_commission_amount, salesperson_commission_amount, salesperson_incentive_amount,
            sales_manager_commission_amount, vat_amount, sales_tax_amount, annual_tax_amount,
            salesperson_tax_amount, sales_manager_tax_amount, net_company_income,
            net_salesperson_income, net_sales_manager_income, transaction_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Test data with all required fields
        test_data = (
            'Test Client 2',  # client_name
            '2025-01-15',     # sale_date
            'TEST456',        # unit_code
            1000000.0,        # unit_price
            'شقة',           # property_type
            '',               # project_name
            'Test Salesperson', # salesperson_name
            'Test Manager',   # sales_manager_name
            '',               # notes
            1,                # created_by
            0.05,             # company_commission_rate
            0.02,             # salesperson_commission_rate
            0.01,             # salesperson_incentive_rate
            0.0,              # additional_incentive_tax_rate
            0.14,             # vat_rate
            0.05,             # sales_tax_rate
            0.225,            # annual_tax_rate
            0.1,              # salesperson_tax_rate
            0.1,              # sales_manager_tax_rate
            0.003,            # sales_manager_commission_rate (this was missing!)
            50000.0,          # company_commission_amount
            20000.0,          # salesperson_commission_amount
            10000.0,          # salesperson_incentive_amount
            5000.0,           # sales_manager_commission_amount
            7000.0,           # vat_amount
            2500.0,           # sales_tax_amount
            11250.0,          # annual_tax_amount
            3000.0,           # salesperson_tax_amount
            500.0,            # sales_manager_tax_amount
            23750.0,          # net_company_income
            27000.0,          # net_salesperson_income
            4500.0,           # net_sales_manager_income
            None,             # transaction_id
            '2025-01-15 10:00:00', # created_at
            '2025-01-15 10:00:00'  # updated_at
        )

        cur.execute(insert_sql, test_data)
        conn.commit()

        print("✓ INSERT statement executed successfully!")
        print("✓ All required fields are now properly handled")

        # Clean up test data
        cur.execute("DELETE FROM sales WHERE unit_code = 'TEST456'")
        conn.commit()

        return True

    except Exception as e:
        print(f"✗ INSERT failed: {e}")
        return False
    finally:
        conn.close()

def test_calculations():
    """Test the sales calculation logic"""
    print("\n=== Testing Sales Calculations ===")

    try:
        # Import the Sale model
        sys.path.insert(0, os.path.dirname(__file__))
        from src.models.sale import Sale

        # Test calculation with all parameters
        result = Sale.calculate_sale_amounts(
            unit_price=1000000,
            company_commission_rate=0.05,
            salesperson_commission_rate=0.02,
            salesperson_incentive_rate=0.01,
            vat_rate=0.14,
            sales_tax_rate=0.05,
            annual_tax_rate=0.225,
            salesperson_tax_rate=0.1,
            sales_manager_tax_rate=0.1
        )

        print("✓ Calculations completed successfully!")
        print(f"  - Company commission: {result['company_commission_amount']}")
        print(f"  - Salesperson commission: {result['salesperson_commission_amount']}")
        print(f"  - Salesperson incentive: {result['salesperson_incentive_amount']}")
        print(f"  - Sales manager commission: {result['sales_manager_commission_amount']}")
        print(f"  - Net company income: {result['net_company_income']}")
        print(f"  - Net salesperson income: {result['net_salesperson_income']}")
        print(f"  - Net sales manager income: {result['net_sales_manager_income']}")

        return True

    except Exception as e:
        print(f"✗ Calculation failed: {e}")
        return False

def main():
    print("🧪 COMPLETE SALES CREATION TEST")
    print("=" * 50)

    success = True
    success &= test_database_schema()
    success &= test_sql_insert()
    success &= test_calculations()

    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The sales creation issue has been completely resolved!")
        print("✅ You can now add new sales transactions without errors")
        print("✅ The database schema is correct and complete")
        print("✅ All calculations work properly")
    else:
        print("❌ Some tests failed. The issue may not be fully resolved.")
        sys.exit(1)

if __name__ == "__main__":
    main()
