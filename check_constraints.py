import sqlite3

db_path = 'src/database/broman_accounting.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print('Checking all column constraints:')
columns = cur.execute('PRAGMA table_info(sales);').fetchall()

not_null_columns = []
for row in columns:
    col_name = row[1]
    col_type = row[2]
    nullable = row[3]
    if nullable == 0:
        not_null_columns.append(col_name)
        print(f'  {col_name}: {col_type} (NOT NULL)')

print(f'\nFound {len(not_null_columns)} NOT NULL columns')

print('\nChecking for NULL values in NOT NULL columns:')
for col_name in not_null_columns:
    try:
        result = cur.execute(f'SELECT COUNT(*) FROM sales WHERE {col_name} IS NULL;').fetchone()
        if result[0] > 0:
            print(f'  {col_name}: {result[0]} NULL values')
        else:
            print(f'  {col_name}: OK (no NULL values)')
    except Exception as e:
        print(f'  {col_name}: Error checking - {e}')

conn.close()
