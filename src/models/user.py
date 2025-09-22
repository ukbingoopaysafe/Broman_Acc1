from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .database import db

class Role(db.Model):
    """Role model for user roles (Admin, Accountant)"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationship with users
    users = db.relationship('User', backref='role', lazy=True)
    
    # Many-to-many relationship with permissions
    permissions = db.relationship('Permission', secondary='role_permission', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Permission(db.Model):
    """Permission model for user permissions"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Many-to-many relationship with roles
    roles = db.relationship('Role', secondary='role_permission', back_populates='permissions')
    
    def __repr__(self):
        return f'<Permission {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

# Association table for many-to-many relationship between roles and permissions
role_permission = db.Table('role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with transactions
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission"""
        # If user has no role -> no permission
        if not self.role:
            return False

        # Admin role should always have all permissions regardless of role->permissions mapping
        # Use case-insensitive check to be robust to name variations
        try:
            if self.role.name and self.role.name.lower() == 'admin':
                return True
        except Exception:
            # In unexpected cases just fall back to explicit permission check
            pass

        return any(perm.name == permission_name for perm in self.role.permissions)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role and self.role.name == 'Admin'
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.to_dict() if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

