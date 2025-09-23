import sqlite3
import os

db_path = os.path.join('src', 'database', 'broman_accounting.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('Current sales table constraints:')
columns = cur.execute("PRAGMA table_info(sales);").fetchall()
for row in columns:
    print(f"  {row[1]}: NOT NULL={row[3]}, DEFAULT={row[4]}")

print('\nRecreating sales table with compatible NULL/defaults...')
try:
        # Always create temporary table with correct schema to normalize constraints
        cur.execute('''
            CREATE TABLE sales_temp (
                id INTEGER PRIMARY KEY,
                client_name VARCHAR(255) NOT NULL,
                sale_date DATE NOT NULL,
                unit_code VARCHAR(100) NOT NULL UNIQUE,
                unit_price NUMERIC(15, 2) NOT NULL,
                property_type VARCHAR(50) NOT NULL,
                project_name VARCHAR(255),
                salesperson_name VARCHAR(255),
                sales_manager_name VARCHAR(255),
                notes TEXT,
                created_by INTEGER,
                company_commission_rate NUMERIC(5, 4) NOT NULL,
                salesperson_commission_rate NUMERIC(5, 4) DEFAULT 0,
                salesperson_incentive_rate NUMERIC(5, 4) DEFAULT 0,
                additional_incentive_tax_rate NUMERIC(5, 4) DEFAULT 0,
                vat_rate NUMERIC(5, 4) DEFAULT 0.14,
                sales_tax_rate NUMERIC(5, 4) DEFAULT 0.05,
                annual_tax_rate NUMERIC(5, 4) DEFAULT 0.225,
                salesperson_tax_rate NUMERIC(5, 4) DEFAULT 0,
                sales_manager_tax_rate NUMERIC(5, 4) DEFAULT 0,
                sales_manager_commission_rate NUMERIC(5, 4) DEFAULT 0.003,
                company_commission_amount NUMERIC(15, 2) NOT NULL,
                salesperson_commission_amount NUMERIC(15, 2) DEFAULT 0,
                salesperson_incentive_amount NUMERIC(15, 2) DEFAULT 0,
                total_company_commission_before_tax NUMERIC(15, 2) DEFAULT 0,
                total_salesperson_incentive_paid NUMERIC(15, 2) DEFAULT 0,
                vat_amount NUMERIC(15, 2) DEFAULT 0,
                sales_tax_amount NUMERIC(15, 2) DEFAULT 0,
                annual_tax_amount NUMERIC(15, 2) DEFAULT 0,
                sales_manager_commission_amount NUMERIC(15, 2) DEFAULT 0,
                transaction_id INTEGER,
                created_at DATETIME,
                updated_at DATETIME,
                salesperson_tax_amount NUMERIC(15, 2) DEFAULT 0,
                sales_manager_tax_amount NUMERIC(15, 2) DEFAULT 0,
                net_company_income NUMERIC(15, 2),
                net_salesperson_income NUMERIC(15, 2) DEFAULT 0,
                net_sales_manager_income NUMERIC(15, 2) DEFAULT 0
            )
        ''')

        # Copy data from old table (use COALESCE and defaults to satisfy new nullable columns)
        cur.execute('''
            INSERT INTO sales_temp (
                id, client_name, sale_date, unit_code, unit_price, property_type,
                project_name, salesperson_name, sales_manager_name, notes, created_by,
                company_commission_rate, salesperson_commission_rate, salesperson_incentive_rate,
                additional_incentive_tax_rate, vat_rate, sales_tax_rate, annual_tax_rate,
                salesperson_tax_rate, sales_manager_tax_rate, sales_manager_commission_rate,
                company_commission_amount, salesperson_commission_amount, salesperson_incentive_amount,
                total_company_commission_before_tax, total_salesperson_incentive_paid,
                vat_amount, sales_tax_amount, annual_tax_amount, sales_manager_commission_amount,
                transaction_id, created_at, updated_at, salesperson_tax_amount,
                sales_manager_tax_amount, net_company_income, net_salesperson_income, net_sales_manager_income
            )
            SELECT
                id, client_name, sale_date, unit_code, unit_price, property_type,
                project_name, salesperson_name, sales_manager_name, notes, created_by,
                company_commission_rate, salesperson_commission_rate, salesperson_incentive_rate,
                additional_incentive_tax_rate, vat_rate, sales_tax_rate, annual_tax_rate,
                salesperson_tax_rate, sales_manager_tax_rate, COALESCE(sales_manager_commission_rate, 0.003),
                company_commission_amount, salesperson_commission_amount, salesperson_incentive_amount,
                COALESCE(total_company_commission_before_tax, 0), COALESCE(total_salesperson_incentive_paid, 0),
                COALESCE(vat_amount, 0), COALESCE(sales_tax_amount, 0), COALESCE(annual_tax_amount, 0), COALESCE(sales_manager_commission_amount, 0),
                transaction_id, created_at, updated_at, salesperson_tax_amount,
                sales_manager_tax_amount, net_company_income, net_salesperson_income, net_sales_manager_income
            FROM sales
        ''')

        # Drop old table and rename new one
        cur.execute('DROP TABLE sales')
        cur.execute('ALTER TABLE sales_temp RENAME TO sales')
        print('✓ Successfully recreated sales table with correct constraints')

except Exception as e2:
        print(f'Recreation failed: {e2}')
        conn.rollback()

conn.commit()

print('\nUpdated sales table constraints:')
columns = cur.execute("PRAGMA table_info(sales);").fetchall()
for row in columns:
    print(f"  {row[1]}: NOT NULL={row[3]}, DEFAULT={row[4]}")

conn.close()
