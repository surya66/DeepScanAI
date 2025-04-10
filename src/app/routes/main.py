from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import PentestRequest, Message
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page route"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route based on user role"""
    if current_user.role == 'client':
        return redirect(url_for('client.dashboard'))
    elif current_user.role == 'analyst':
        return redirect(url_for('analyst.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid user role', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page route"""
    return render_template('contact.html')
