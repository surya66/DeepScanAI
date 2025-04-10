from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Analyst
from app import db, login_manager
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'client')
        
        # Validate input
        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Invalid email format.', 'danger')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(username=username, email=email, password=password, role=role)
        
        # Special handling for growthguard.com email domains
        if email.endswith('@growthguard.com'):
            new_user.role = 'admin'
        
        db.session.add(new_user)
        
        # If registering as an analyst, create analyst profile
        if role == 'analyst':
            expertise = request.form.get('expertise', 'web')
            db.session.flush()  # Flush to get the user ID
            new_analyst = Analyst(user_id=new_user.id, expertise=expertise, availability=True)
            db.session.add(new_analyst)
        
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in a user"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'
        
        # Validate input
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('auth/login.html')
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')
        
        # Log in user
        login_user(user, remember=remember)
        
        # Redirect based on role
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if user.role == 'client':
            return redirect(url_for('client.dashboard'))
        elif user.role == 'analyst' or user.role == 'admin':
            return redirect(url_for('analyst.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out a user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    return render_template('auth/profile.html')

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email:
            flash('Username and email are required.', 'danger')
            return render_template('auth/edit_profile.html')
        
        # Check if username already exists (if changed)
        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/edit_profile.html')
        
        # Check if email already exists (if changed)
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('auth/edit_profile.html')
        
        # Update username and email
        current_user.username = username
        current_user.email = email
        
        # Special handling for growthguard.com email domains
        if email.endswith('@growthguard.com') and current_user.role != 'admin':
            current_user.role = 'admin'
            flash('Your account has been upgraded to admin based on your email domain.', 'success')
        
        # Update password if provided
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/edit_profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('auth/edit_profile.html')
            
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html')

@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin view for managing users"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    """Admin view for editing a user"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        new_password = request.form.get('new_password')
        
        # Validate input
        if not username or not email or not role:
            flash('Username, email, and role are required.', 'danger')
            return render_template('auth/admin_edit_user.html', user=user)
        
        # Check if username already exists (if changed)
        if username != user.username and User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/admin_edit_user.html', user=user)
        
        # Check if email already exists (if changed)
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('auth/admin_edit_user.html', user=user)
        
        # Update user
        user.username = username
        user.email = email
        user.role = role
        
        # Special handling for growthguard.com email domains
        if email.endswith('@growthguard.com') and role != 'admin':
            user.role = 'admin'
            flash(f'User {username} has been automatically assigned admin role based on email domain.', 'info')
        
        # Update password if provided
        if new_password:
            user.set_password(new_password)
            flash('Password updated successfully.', 'success')
        
        # Handle analyst profile
        if role == 'analyst' and not hasattr(user, 'analyst'):
            expertise = request.form.get('expertise', 'web')
            new_analyst = Analyst(user_id=user.id, expertise=expertise, availability=True)
            db.session.add(new_analyst)
        elif role != 'analyst' and hasattr(user, 'analyst'):
            db.session.delete(user.analyst)
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('auth.admin_users'))
    
    return render_template('auth/admin_edit_user.html', user=user)

@auth_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    """Admin view for deleting a user"""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting self
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('auth.admin_users'))
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.', 'success')
    return redirect(url_for('auth.admin_users'))
