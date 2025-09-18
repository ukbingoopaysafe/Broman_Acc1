from datetime import datetime
from .database import db

class Transaction(db.Model):
    """Transaction model for all financial transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'Sale', 'Expense', 'Deposit', etc.
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Positive for income, negative for expense
    description = db.Column(db.Text, nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    related_entity_id = db.Column(db.Integer, nullable=True)  # ID of related entity (e.g., Sale.id)
    related_entity_type = db.Column(db.String(50), nullable=True)  # Type of related entity (e.g., 'Sale')
    
    # Relationship with sales (one-to-one)
    sale = db.relationship('Sale', backref='transaction', uselist=False)
    
    def __repr__(self):
        return f'<Transaction {self.type}: {self.amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': float(self.amount),
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'user_id': self.user_id,
            'related_entity_id': self.related_entity_id,
            'related_entity_type': self.related_entity_type
        }
    
    @classmethod
    def create_sale_transaction(cls, sale_data, user_id=None):
        """Create a transaction for a sale"""
        # Calculate net amount for the company (total commission minus taxes and expenses)
        net_amount = (
            sale_data.get('total_company_commission_before_tax', 0) -
            sale_data.get('vat_amount', 0) -
            sale_data.get('sales_tax_amount', 0) -
            sale_data.get('annual_tax_amount', 0) -
            sale_data.get('salesperson_incentive_amount', 0) -
            sale_data.get('sales_manager_commission_amount', 0)
        )
        
        transaction = cls(
            type='Sale',
            amount=net_amount,
            description=f"بيع عقار - {sale_data.get('client_name', 'غير محدد')} - كود الوحدة: {sale_data.get('unit_code', 'غير محدد')}",
            transaction_date=datetime.utcnow(),
            user_id=user_id,
            related_entity_type='Sale'
        )
        
        return transaction

