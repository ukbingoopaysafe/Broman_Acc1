
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
    additional_incentive_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
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
    additional_incentive_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    vat_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.14)  # Default 14%
    sales_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.05)  # Default 5%
    annual_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0.225)  # Default 22.5%
    salesperson_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    sales_manager_tax_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)
    sales_manager_commission_rate = db.Column(db.Numeric(5, 4), nullable=True, default=0)

    # Calculated amounts (based on Excel logic)
    company_commission_amount = db.Column(db.Numeric(15, 2), nullable=False)
    total_company_commission_before_tax = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    total_salesperson_incentive_paid = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    total_company_income_after_5_percent = db.Column(db.Numeric(15, 2), nullable=True, default=0)

    vat_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    sales_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    total_vat_and_sales_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    net_company_income_after_sales_tax = db.Column(db.Numeric(15, 2), nullable=True, default=0)

    salesperson_commission_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    salesperson_incentive_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    total_salesperson_income_before_tax = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    salesperson_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    net_salesperson_income = db.Column(db.Numeric(15, 2), nullable=True, default=0)

    sales_manager_commission_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    total_sales_manager_income_before_tax = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    sales_manager_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    net_sales_manager_income = db.Column(db.Numeric(15, 2), nullable=True, default=0)

    annual_tax_amount = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    net_company_income_after_all_taxes_and_commissions = db.Column(db.Numeric(15, 2), nullable=True, default=0)
    final_company_income = db.Column(db.Numeric(15, 2), nullable=False)

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
            'unit_price': float(self.unit_price or 0),
            'property_type': self.property_type,
            'project_name': self.project_name,
            'salesperson_name': self.salesperson_name,
            'sales_manager_name': self.sales_manager_name,
            'notes': self.notes,
            'company_commission_rate': float(self.company_commission_rate or 0),
            'salesperson_commission_rate': float(self.salesperson_commission_rate or 0),
            'salesperson_incentive_rate': float(self.salesperson_incentive_rate or 0),
            'additional_incentive_tax_rate': float(self.additional_incentive_tax_rate or 0),
            'vat_rate': float(self.vat_rate or 0),
            'sales_tax_rate': float(self.sales_tax_rate or 0),
            'annual_tax_rate': float(self.annual_tax_rate or 0),
            'salesperson_tax_rate': float(self.salesperson_tax_rate or 0),
            'sales_manager_tax_rate': float(self.sales_manager_tax_rate or 0),
            'sales_manager_commission_rate': float(self.sales_manager_commission_rate or 0),

            'company_commission_amount': float(self.company_commission_amount or 0),
            'total_company_commission_before_tax': float(self.total_company_commission_before_tax or 0),
            'total_salesperson_incentive_paid': float(self.total_salesperson_incentive_paid or 0),
            'total_company_income_after_5_percent': float(self.total_company_income_after_5_percent or 0),

            'vat_amount': float(self.vat_amount or 0),
            'sales_tax_amount': float(self.sales_tax_amount or 0),
            'total_vat_and_sales_tax_amount': float(self.total_vat_and_sales_tax_amount or 0),
            'net_company_income_after_sales_tax': float(self.net_company_income_after_sales_tax or 0),

            'salesperson_commission_amount': float(self.salesperson_commission_amount or 0),
            'salesperson_incentive_amount': float(self.salesperson_incentive_amount or 0),
            'total_salesperson_income_before_tax': float(self.total_salesperson_income_before_tax or 0),
            'salesperson_tax_amount': float(self.salesperson_tax_amount or 0),
            'net_salesperson_income': float(self.net_salesperson_income or 0),

            'sales_manager_commission_amount': float(self.sales_manager_commission_amount or 0),
            'total_sales_manager_income_before_tax': float(self.total_sales_manager_income_before_tax or 0),
            'sales_manager_tax_amount': float(self.sales_manager_tax_amount or 0),
            'net_sales_manager_income': float(self.net_sales_manager_income or 0),

            'annual_tax_amount': float(self.annual_tax_amount or 0),
            'net_company_income_after_all_taxes_and_commissions': float(self.net_company_income_after_all_taxes_and_commissions or 0),
            'final_company_income': float(self.final_company_income or 0),

            'created_by': self.created_by,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    # The calculate_sale_amounts method will be moved to src/services/calculation_service.py
    # and will be called from the API endpoints.

