from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from src.models.database import db
from src.models.user import User, Role, Permission

user_bp = Blueprint('user', __name__)

# Pages blueprint (no url prefix) for admin UI
admin_pages_bp = Blueprint('admin_pages', __name__)

def require_permission(permission_name):
    """Decorator to require specific permission"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'غير مصرح لك بالوصول'}), 401
            
            if not current_user.has_permission(permission_name):
                return jsonify({'error': 'ليس لديك صلاحية للقيام بهذا الإجراء'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# --------------------------- Admin Pages ---------------------------
@admin_pages_bp.route('/users')
@login_required
@require_permission('manage_users')
def users_page():
    return jsonify({}) if request.is_json else __import__('flask').render_template('admin/users.html')

@admin_pages_bp.route('/roles')
@login_required
@require_permission('manage_roles')
def roles_page():
    return jsonify({}) if request.is_json else __import__('flask').render_template('admin/roles.html')

@user_bp.route('/users', methods=['GET'])
@login_required
@require_permission('manage_users')
def get_users():
    """Get all users (Admin only)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المستخدمين: {str(e)}'}), 500

@user_bp.route('/users', methods=['POST'])
@login_required
@require_permission('manage_users')
def create_user():
    """Create new user (Admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'اسم المستخدم موجود بالفعل'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'البريد الإلكتروني موجود بالفعل'}), 400
        
        # Check if role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'الدور المحدد غير موجود'}), 400
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role_id=data['role_id'],
            is_active=data.get('is_active', True)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء المستخدم بنجاح',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في إنشاء المستخدم: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@require_permission('manage_users')
def get_user(user_id):
    """Get specific user (Admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب المستخدم: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@require_permission('manage_users')
def update_user(user_id):
    """Update user (Admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'لا توجد بيانات'}), 400
        
        # Update fields if provided
        if 'username' in data:
            # Check if username already exists (excluding current user)
            existing = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing:
                return jsonify({'error': 'اسم المستخدم موجود بالفعل'}), 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if email already exists (excluding current user)
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return jsonify({'error': 'البريد الإلكتروني موجود بالفعل'}), 400
            user.email = data['email']
        
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({'error': 'الدور المحدد غير موجود'}), 400
            user.role_id = data['role_id']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث المستخدم بنجاح',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث المستخدم: {str(e)}'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@require_permission('manage_users')
def delete_user(user_id):
    """Delete user (Admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting current user
        if user.id == current_user.id:
            return jsonify({'error': 'لا يمكنك حذف حسابك الخاص'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف المستخدم بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في حذف المستخدم: {str(e)}'}), 500

@user_bp.route('/roles', methods=['GET'])
@login_required
@require_permission('manage_roles')
def get_roles():
    """Get all roles"""
    try:
        roles = Role.query.all()
        return jsonify([role.to_dict() for role in roles]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب الأدوار: {str(e)}'}), 500

@user_bp.route('/permissions', methods=['GET'])
@login_required
@require_permission('manage_roles')
def get_permissions():
    """Get all permissions"""
    try:
        permissions = Permission.query.all()
        return jsonify([perm.to_dict() for perm in permissions]), 200
    except Exception as e:
        return jsonify({'error': f'خطأ في جلب الصلاحيات: {str(e)}'}), 500

@user_bp.route('/roles/<int:role_id>/permissions', methods=['PUT'])
@login_required
@require_permission('manage_roles')
def update_role_permissions(role_id):
    """Update role permissions (Admin only)"""
    try:
        role = Role.query.get_or_404(role_id)
        # Protect Admin role from being modified. Admin must retain all permissions.
        if role.name and role.name.lower() == 'admin':
            return jsonify({'error': 'Cannot modify permissions for the Admin role. Admin always has all permissions.'}), 403
        data = request.get_json()
        
        if not data or 'permission_ids' not in data:
            return jsonify({'error': 'معرفات الصلاحيات مطلوبة'}), 400
        
        # Get permissions
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()

        # Update role permissions
        role.permissions = permissions
        db.session.commit()

        return jsonify({
            'message': 'تم تحديث صلاحيات الدور بنجاح',
            'role': role.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'خطأ في تحديث صلاحيات الدور: {str(e)}'}), 500
