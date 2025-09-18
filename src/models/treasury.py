from datetime import datetime
from .database import db

class Treasury(db.Model):
    """Treasury model for company balance management"""
    __tablename__ = 'treasury'
    
    id = db.Column(db.Integer, primary_key=True)
    current_balance = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Treasury Balance: {self.current_balance}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'current_balance': float(self.current_balance),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def get_current_balance(cls):
        """Get current treasury balance"""
        treasury = cls.query.first()
        if not treasury:
            # Create initial treasury record if it doesn't exist
            treasury = cls(current_balance=0.00)
            db.session.add(treasury)
            db.session.commit()
        return treasury.current_balance
    
    @classmethod
    def update_balance(cls, amount, description=None):
        """Update treasury balance by adding/subtracting amount"""
        treasury = cls.query.first()
        if not treasury:
            treasury = cls(current_balance=0.00)
            db.session.add(treasury)
        
        treasury.current_balance += amount
        treasury.last_updated = datetime.utcnow()
        db.session.commit()
        
        # Create a transaction record
        from .transaction import Transaction
        transaction = Transaction(
            type='Treasury Update',
            amount=amount,
            description=description or f'Treasury balance updated by {amount}',
            transaction_date=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
        
        return treasury.current_balance

