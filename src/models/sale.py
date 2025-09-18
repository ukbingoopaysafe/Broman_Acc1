from datetime import datetime, date
from .database import db

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
    """Sale model for real estate transactions"""
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    unit_code = db.Column(db.String(100), unique=True, nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    
    # Commission and tax rates (stored at time of sale to preserve historical accuracy)
    company_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    salesperson_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    salesperson_incentive_rate = db.Column(db.Numeric(5, 4), nullable=False)
    additional_incentive_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 4), nullable=False)
    sales_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    annual_tax_rate = db.Column(db.Numeric(5, 4), nullable=False)
    sales_manager_commission_rate = db.Column(db.Numeric(5, 4), nullable=False)
    
    # Calculated amounts
    company_commission_amount = db.Column(db.Numeric(15, 2), nullable=False)
    salesperson_commission_amount = db.Column(db.Numeric(15, 2), nullable=False)
    salesperson_incentive_amount = db.Column(db.Numeric(15, 2), nullable=False)
    total_company_commission_before_tax = db.Column(db.Numeric(15, 2), nullable=False)
    total_salesperson_incentive_paid = db.Column(db.Numeric(15, 2), nullable=False)
    vat_amount = db.Column(db.Numeric(15, 2), nullable=False)
    sales_tax_amount = db.Column(db.Numeric(15, 2), nullable=False)
    annual_tax_amount = db.Column(db.Numeric(15, 2), nullable=False)
    sales_manager_commission_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Foreign key to transaction
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), unique=True, nullable=False)
    
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
            'company_commission_rate': float(self.company_commission_rate),
            'salesperson_commission_rate': float(self.salesperson_commission_rate),
            'salesperson_incentive_rate': float(self.salesperson_incentive_rate),
            'additional_incentive_tax_rate': float(self.additional_incentive_tax_rate),
            'vat_rate': float(self.vat_rate),
            'sales_tax_rate': float(self.sales_tax_rate),
            'annual_tax_rate': float(self.annual_tax_rate),
            'sales_manager_commission_rate': float(self.sales_manager_commission_rate),
            'company_commission_amount': float(self.company_commission_amount),
            'salesperson_commission_amount': float(self.salesperson_commission_amount),
            'salesperson_incentive_amount': float(self.salesperson_incentive_amount),
            'total_company_commission_before_tax': float(self.total_company_commission_before_tax),
            'total_salesperson_incentive_paid': float(self.total_salesperson_incentive_paid),
            'vat_amount': float(self.vat_amount),
            'sales_tax_amount': float(self.sales_tax_amount),
            'annual_tax_amount': float(self.annual_tax_amount),
            'sales_manager_commission_amount': float(self.sales_manager_commission_amount),
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def calculate_sale_amounts(cls, unit_price, property_type):
        """Calculate all amounts for a sale based on unit price and property type"""
        # Get rates for property type
        rates = PropertyTypeRates.get_rates_for_property_type(property_type)
        if not rates:
            raise ValueError(f"No rates found for property type: {property_type}")
        
        unit_price = float(unit_price)
        
        # Calculate commission amounts
        company_commission_amount = unit_price * float(rates.company_commission_rate)
        salesperson_commission_amount = unit_price * float(rates.salesperson_commission_rate)
        salesperson_incentive_amount = unit_price * float(rates.salesperson_incentive_rate)
        sales_manager_commission_amount = unit_price * float(rates.sales_manager_commission_rate)
        
        # Calculate total company commission before tax
        total_company_commission_before_tax = company_commission_amount
        
        # Calculate tax amounts
        vat_amount = total_company_commission_before_tax * float(rates.vat_rate)
        sales_tax_amount = total_company_commission_before_tax * float(rates.sales_tax_rate)
        annual_tax_amount = total_company_commission_before_tax * float(rates.annual_tax_rate)
        
        # Calculate total salesperson incentive paid
        total_salesperson_incentive_paid = salesperson_incentive_amount
        
        return {
            'company_commission_rate': rates.company_commission_rate,
            'salesperson_commission_rate': rates.salesperson_commission_rate,
            'salesperson_incentive_rate': rates.salesperson_incentive_rate,
            'additional_incentive_tax_rate': rates.additional_incentive_tax_rate,
            'vat_rate': rates.vat_rate,
            'sales_tax_rate': rates.sales_tax_rate,
            'annual_tax_rate': rates.annual_tax_rate,
            'sales_manager_commission_rate': rates.sales_manager_commission_rate,
            'company_commission_amount': company_commission_amount,
            'salesperson_commission_amount': salesperson_commission_amount,
            'salesperson_incentive_amount': salesperson_incentive_amount,
            'total_company_commission_before_tax': total_company_commission_before_tax,
            'total_salesperson_incentive_paid': total_salesperson_incentive_paid,
            'vat_amount': vat_amount,
            'sales_tax_amount': sales_tax_amount,
            'annual_tax_amount': annual_tax_amount,
            'sales_manager_commission_amount': sales_manager_commission_amount
        }

