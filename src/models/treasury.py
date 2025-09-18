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
    
    # ------------------------------------------------------------------
    # Compatibility helpers for route usage
    # Routes refer to attributes/methods: balance, get_current, set_balance,
    # add_to_balance, subtract_from_balance. Provide them here mapping to
    # the canonical current_balance field used by the model.
    # ------------------------------------------------------------------
    @property
    def balance(self):
        return self.current_balance

    @classmethod
    def get_current(cls):
        """Return the singleton treasury row; create if missing."""
        treasury = cls.query.first()
        if not treasury:
            treasury = cls(current_balance=0.00)
            db.session.add(treasury)
            db.session.commit()
        return treasury

    @classmethod
    def set_balance(cls, new_balance: float):
        """Set absolute balance value and update timestamp."""
        treasury = cls.get_current()
        treasury.current_balance = float(new_balance)
        treasury.last_updated = datetime.utcnow()
        db.session.commit()
        return treasury.current_balance

    @classmethod
    def add_to_balance(cls, amount: float):
        treasury = cls.get_current()
        treasury.current_balance = float(treasury.current_balance) + float(amount)
        treasury.last_updated = datetime.utcnow()
        db.session.commit()
        return treasury.current_balance

    @classmethod
    def subtract_from_balance(cls, amount: float):
        treasury = cls.get_current()
        treasury.current_balance = float(treasury.current_balance) - float(amount)
        treasury.last_updated = datetime.utcnow()
        db.session.commit()
        return treasury.current_balance

    @classmethod
    def get_current_balance(cls):
        """Get current treasury balance (kept for backward compatibility)."""
        return cls.get_current().current_balance

    @classmethod
    def update_balance(cls, amount, description=None):
        """Update treasury balance by adding/subtracting amount and log txn."""
        new_balance = cls.add_to_balance(amount)
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
        return new_balance

