import sqlite3, os
db = os.path.join('src','database','broman_accounting.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
existing = [c[1] for c in cur.execute("PRAGMA table_info(sales);").fetchall()]
adds = []

# Existing columns that were already added
if 'project_name' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN project_name VARCHAR(255);")
if 'salesperson_name' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN salesperson_name VARCHAR(255);")
if 'sales_manager_name' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN sales_manager_name VARCHAR(255);")
if 'notes' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN notes TEXT;")
if 'created_by' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN created_by INTEGER;")

# Missing columns that are causing the error
if 'salesperson_tax_rate' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN salesperson_tax_rate NUMERIC(5, 4) DEFAULT 0;")
if 'sales_manager_tax_rate' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN sales_manager_tax_rate NUMERIC(5, 4) DEFAULT 0;")
if 'salesperson_tax_amount' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN salesperson_tax_amount NUMERIC(15, 2) DEFAULT 0;")
if 'sales_manager_tax_amount' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN sales_manager_tax_amount NUMERIC(15, 2) DEFAULT 0;")
if 'net_company_income' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN net_company_income NUMERIC(15, 2);")
if 'net_salesperson_income' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN net_salesperson_income NUMERIC(15, 2) DEFAULT 0;")
if 'net_sales_manager_income' not in existing:
    adds.append("ALTER TABLE sales ADD COLUMN net_sales_manager_income NUMERIC(15, 2) DEFAULT 0;")

for a in adds:
    print('Executing:', a)
    cur.execute(a)
conn.commit()
print('Done. Current columns:')
for row in cur.execute("PRAGMA table_info(sales);").fetchall():
    print(row)
conn.close()
