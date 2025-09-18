from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from src.models.database import db
from src.models.user import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'GET':
        # Return login page
        return render_template('login.html')
    
    # Handle POST request (login form submission)
    data = request.get_json() if request.is_json else request.form
    
    if not data:
        return jsonify({'error': 'لا توجد بيانات'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400
    
    # Find user
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'الحساب غير مفعل'}), 401
    
    # Login user
    login_user(user, remember=True)
    
    return jsonify({
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user.to_dict(),
        'redirect': url_for('dashboard.index')
    }), 200

@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    """Logout route"""
    logout_user()
    if request.is_json:
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200
    else:
        flash('تم تسجيل الخروج بنجاح', 'success')
        return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get current user profile"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'لا توجد بيانات'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'error': 'جميع الحقول مطلوبة'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'كلمة المرور الحالية غير صحيحة'}), 400
    
    if new_password != confirm_password:
        return jsonify({'error': 'كلمة المرور الجديدة وتأكيدها غير متطابقتان'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'}), 400
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

