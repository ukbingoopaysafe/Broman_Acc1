import sqlite3
import os

db_path = os.path.join('src', 'database', 'broman_accounting.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('Current sales table columns:')
columns = cur.execute("PRAGMA table_info(sales);").fetchall()
for row in columns:
    print(f"  {row[1]} ({row[2]})")

print(f"\nTotal columns: {len(columns)}")

# Check if we have the problematic columns
problematic_columns = [
    'salesperson_tax_rate',
    'sales_manager_tax_rate',
    'salesperson_tax_amount',
    'sales_manager_tax_amount',
    'net_company_income',
    'net_salesperson_income',
    'net_sales_manager_income'
]

print('\nChecking problematic columns:')
for col in problematic_columns:
    found = False
    for column in columns:
        if column[1] == col:
            found = True
            print(f"✓ {col}: NOT NULL={column[3]}, DEFAULT={column[4]}")
            break
    if not found:
        print(f"✗ {col}: MISSING")

conn.close()
