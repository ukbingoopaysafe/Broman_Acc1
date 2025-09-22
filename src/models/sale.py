from datetime import datetime, date
from .database import db
from decimal import Decimal

class PropertyTypeRates(db.Model):
    """Property type rates for commissions and taxes"""
    __tablename__ = 'property_type_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    property_type = db.Column(db.String(50), unique=True, nullable=False)
    company_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    salesperson_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    salesperson_incentive_rate = db.Column(db.Numeric(5, 4), nullable=False)
    additional_incentive_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 4), nullable=False)
    sales_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    annual_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    sales_manager_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    
    def __repr__(self):
        return f'<PropertyTypeRates {self.property_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_type': self.property_type,
            'company_commission_rate': float(self.company_commission_rate),
            'salesperson_commission_rate': float(self.salesperson_commission_rate),
            'salesperson_incentive_rate': float(self.salesperson_incentive_rate),
            'additional_incentive_tax_rate': float(self.additional_incentive_tax_rate),
            'vat_rate': float(self.vat_rate),
            'sales_tax_rate': float(self.sales_tax_rate),
            'annual_tax_rate': float(self.annual_tax_rate),
            'sales_manager_commission_rate': float(self.sales_manager_commission_rate)
        }
    
    @classmethod
    def get_rates_for_property_type(cls, property_type):
        """Get rates for a specific property type"""
        return cls.query.filter_by(property_type=property_type).first()

class Sale(db.Model):
    """Sale model for real estate transactions with enhanced calculation support"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    unit_code = db.Column(db.String(100), unique=True, nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    project_name = db.Column(db.String(255), nullable=True)
    salesperson_name = db.Column(db.String(255), nullable=True)
    sales_manager_name = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, nullable=True)
    
    # Commission and tax rates (user-defined for each transaction)
    company_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    salesperson_commission_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    salesperson_incentive_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    vat_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.14)  # Default 14%
    sales_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.05)  # Default 5%
    annual_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.225)  # Default 22.5%
    salesperson_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    sales_manager_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    
    # Calculated amounts (based on Excel logic)
    company_commission_amount = db.Column(db.Numeric(15, 2), nullable=False)
    salesperson_commission_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    salesperson_incentive_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    sales_manager_commission_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    
    # Tax amounts
    vat_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    sales_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    annual_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    salesperson_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    sales_manager_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    
    # Net amounts
    net_company_income = db.Column(db.Numeric(15, 2), nullable=False)
    net_salesperson_income = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    net_sales_manager_income = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    
    # Foreign key to transaction
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), unique=True, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Sale {self.unit_code} - {self.client_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_name': self.client_name,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'unit_code': self.unit_code,
            'unit_price': float(self.unit_price),
            'property_type': self.property_type,
            'project_name': self.project_name,
            'salesperson_name': self.salesperson_name,
            'sales_manager_name': self.sales_manager_name,
            'notes': self.notes,
            'company_commission_rate': float(self.company_commission_rate),
            'salesperson_commission_rate': float(self.salesperson_commission_rate or 0),
            'salesperson_incentive_rate': float(self.salesperson_incentive_rate or 0),
            'vat_rate': float(self.vat_rate or 0),
            'sales_tax_rate': float(self.sales_tax_rate or 0),
            'annual_tax_rate': float(self.annual_tax_rate or 0),
            'salesperson_tax_rate': float(self.salesperson_tax_rate or 0),
            'sales_manager_tax_rate': float(self.sales_manager_tax_rate or 0),
            'company_commission_amount': float(self.company_commission_amount),
            'salesperson_commission_amount': float(self.salesperson_commission_amount or 0),
            'salesperson_incentive_amount': float(self.salesperson_incentive_amount or 0),
            'sales_manager_commission_amount': float(self.sales_manager_commission_amount or 0),
            'vat_amount': float(self.vat_amount or 0),
            'sales_tax_amount': float(self.sales_tax_amount or 0),
            'annual_tax_amount': float(self.annual_tax_amount or 0),
            'salesperson_tax_amount': float(self.salesperson_tax_amount or 0),
            'sales_manager_tax_amount': float(self.sales_manager_tax_amount or 0),
            'net_company_income': float(self.net_company_income),
            'net_salesperson_income': float(self.net_salesperson_income or 0),
            'net_sales_manager_income': float(self.net_sales_manager_income or 0),
            'created_by': self.created_by,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def calculate_sale_amounts(cls, unit_price, company_commission_rate, 
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

