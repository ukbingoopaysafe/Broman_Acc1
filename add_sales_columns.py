import sqlite3, os
db = os.path.join('src','database','broman_accounting.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
existing = [c[1] for c in cur.execute("PRAGMA table_info(sales);").fetchall()]
adds = []
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

for a in adds:
    print('Executing:', a)
    cur.execute(a)
conn.commit()
print('Done. Current columns:')
for row in cur.execute("PRAGMA table_info(sales);").fetchall():
    print(row)
conn.close()