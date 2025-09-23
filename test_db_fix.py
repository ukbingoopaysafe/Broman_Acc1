from src.models.database import db
from src.models.sale import Sale

print('Testing database connection...')
print('Sale model columns:')
for col in Sale.__table__.columns:
    print(f'  {col.name}: {col.type} (nullable: {col.nullable})')
print('Database connection successful!')
