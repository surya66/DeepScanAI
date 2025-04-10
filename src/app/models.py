from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # client, analyst, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    analyst = db.relationship('Analyst', backref='user', uselist=False)
    client_requests = db.relationship('PentestRequest', backref='client', lazy='dynamic', 
                                     foreign_keys='PentestRequest.client_id')
    messages = db.relationship('Message', backref='user', lazy='dynamic',
                              foreign_keys='Message.user_id')
    files = db.relationship('File', backref='uploader', lazy='dynamic',
                           foreign_keys='File.uploaded_by')
    
    def __init__(self, username, email, password, role='client'):
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        
        # Auto-assign admin role for growthguard.com email domains
        if email.endswith('@growthguard.com'):
            self.role = 'admin'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Analyst(db.Model):
    """Analyst model for storing analyst-specific information"""
    __tablename__ = 'analysts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expertise = db.Column(db.String(255), nullable=False)  # Comma-separated list: web,api,mobile
    availability = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    
    # Relationships
    assigned_requests = db.relationship('PentestRequest', backref='analyst', lazy='dynamic',
                                       foreign_keys='PentestRequest.analyst_id')
    
    def __repr__(self):
        return f'<Analyst {self.user.username}>'

class PentestRequest(db.Model):
    """Pentest request model for storing request information"""
    __tablename__ = 'pentest_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analyst_id = db.Column(db.Integer, db.ForeignKey('analysts.id'), nullable=True)
    target_url = db.Column(db.String(255), nullable=False)
    request_type = db.Column(db.String(20), nullable=False)  # web, api, mobile
    scope = db.Column(db.Text, nullable=False)
    credentials = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, assigned, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='request', lazy='dynamic')
    reports = db.relationship('Report', backref='request', lazy='dynamic')
    vulnerabilities = db.relationship('Vulnerability', backref='request', lazy='dynamic')
    files = db.relationship('File', backref='request', lazy='dynamic')
    
    def __repr__(self):
        return f'<PentestRequest {self.id}>'

class Message(db.Model):
    """Message model for storing conversation messages"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('pentest_requests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for system/AI messages
    is_ai = db.Column(db.Boolean, default=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'

class Report(db.Model):
    """Report model for storing pentest reports"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('pentest_requests.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.id}>'

class Vulnerability(db.Model):
    """Vulnerability model for storing individual vulnerabilities"""
    __tablename__ = 'vulnerabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('pentest_requests.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    proof_of_concept = db.Column(db.Text, nullable=False)
    remediation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vulnerability {self.id}>'

class File(db.Model):
    """File model for storing file information"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('pentest_requests.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<File {self.id}>'
