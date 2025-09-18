"""
Initialization script for default data
This script creates default roles, permissions, and property type rates
"""

from src.models.database import db
from src.models.user import User, Role, Permission
from src.models.sale import PropertyTypeRates
from src.models.treasury import Treasury

def init_roles_and_permissions():
    """Initialize default roles and permissions"""
    
    # Create roles
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='مدير النظام - صلاحيات كاملة')
        db.session.add(admin_role)
    
    accountant_role = Role.query.filter_by(name='Accountant').first()
    if not accountant_role:
        accountant_role = Role(name='Accountant', description='محاسب - صلاحيات محدودة')
        db.session.add(accountant_role)
    
    # Create permissions
    permissions_data = [
        ('view_dashboard', 'عرض لوحة التحكم'),
        ('manage_users', 'إدارة المستخدمين'),
        ('manage_roles', 'إدارة الأدوار والصلاحيات'),
        ('view_sales', 'عرض معاملات البيع'),
        ('create_sales', 'إنشاء معاملات بيع جديدة'),
        ('edit_sales', 'تعديل معاملات البيع'),
        ('delete_sales', 'حذف معاملات البيع'),
        ('view_treasury', 'عرض الخزنة والرصيد'),
        ('manage_treasury', 'إدارة الخزنة والرصيد'),
        ('view_transactions', 'عرض المعاملات المالية'),
        ('manage_transactions', 'إدارة المعاملات المالية'),
        ('view_reports', 'عرض التقارير'),
        ('export_data', 'تصدير البيانات'),
        ('manage_property_rates', 'إدارة أسعار أنواع العقارات')
    ]
    
    permissions = []
    for perm_name, perm_desc in permissions_data:
        permission = Permission.query.filter_by(name=perm_name).first()
        if not permission:
            permission = Permission(name=perm_name, description=perm_desc)
            db.session.add(permission)
        permissions.append(permission)
    
    db.session.commit()
    
    # Assign all permissions to admin role
    admin_role.permissions = permissions
    
    # Assign limited permissions to accountant role
    accountant_permissions = [
        'view_dashboard',
        'view_sales',
        'create_sales',
        'edit_sales',
        'view_treasury',
        'view_transactions',
        'view_reports'
    ]
    
    accountant_role.permissions = [p for p in permissions if p.name in accountant_permissions]
    
    db.session.commit()
    
    return admin_role, accountant_role

def init_property_type_rates():
    """Initialize default property type rates based on Excel analysis"""
    
    # Default rates based on the Excel file analysis
    property_types_data = [
        {
            'property_type': 'شقة',
            'company_commission_rate': 0.0000,  # Will be set based on actual Excel data
            'salesperson_commission_rate': 0.0000,
            'salesperson_incentive_rate': 0.0000,
            'additional_incentive_tax_rate': 0.0000,
            'vat_rate': 0.14,  # 14% VAT
            'sales_tax_rate': 0.05,  # 5% sales tax
            'annual_tax_rate': 0.225,  # 22.5% annual tax
            'sales_manager_commission_rate': 0.003  # 0.3% sales manager commission
        },
        {
            'property_type': 'تجاري',
            'company_commission_rate': 0.0000,
            'salesperson_commission_rate': 0.0000,
            'salesperson_incentive_rate': 0.0000,
            'additional_incentive_tax_rate': 0.0000,
            'vat_rate': 0.14,
            'sales_tax_rate': 0.05,
            'annual_tax_rate': 0.225,
            'sales_manager_commission_rate': 0.003
        },
        {
            'property_type': 'اداري',
            'company_commission_rate': 0.0000,
            'salesperson_commission_rate': 0.0000,
            'salesperson_incentive_rate': 0.0000,
            'additional_incentive_tax_rate': 0.0000,
            'vat_rate': 0.14,
            'sales_tax_rate': 0.05,
            'annual_tax_rate': 0.225,
            'sales_manager_commission_rate': 0.003
        },
        {
            'property_type': 'طبي',
            'company_commission_rate': 0.0000,
            'salesperson_commission_rate': 0.0000,
            'salesperson_incentive_rate': 0.0000,
            'additional_incentive_tax_rate': 0.0000,
            'vat_rate': 0.14,
            'sales_tax_rate': 0.05,
            'annual_tax_rate': 0.225,
            'sales_manager_commission_rate': 0.003
        }
    ]
    
    for data in property_types_data:
        existing = PropertyTypeRates.query.filter_by(property_type=data['property_type']).first()
        if not existing:
            rates = PropertyTypeRates(**data)
            db.session.add(rates)
    
    db.session.commit()

def init_treasury():
    """Initialize treasury with zero balance"""
    treasury = Treasury.query.first()
    if not treasury:
        treasury = Treasury(current_balance=0.00)
        db.session.add(treasury)
        db.session.commit()

def create_default_admin():
    """Create default admin user"""
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        raise ValueError("Admin role not found. Please run init_roles_and_permissions first.")
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@broman.com',
            role_id=admin_role.id,
            is_active=True
        )
        admin_user.set_password('admin123')  # Default password - should be changed
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")
    
    return admin_user

def initialize_all_data():
    """Initialize all default data"""
    print("Initializing roles and permissions...")
    init_roles_and_permissions()
    
    print("Initializing property type rates...")
    init_property_type_rates()
    
    print("Initializing treasury...")
    init_treasury()
    
    print("Creating default admin user...")
    create_default_admin()
    
    print("All default data initialized successfully!")

if __name__ == '__main__':
    # This can be run as a standalone script
    from src.main import app
    with app.app_context():
        initialize_all_data()

