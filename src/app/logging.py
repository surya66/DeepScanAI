import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, g
import time
import uuid

def setup_logging(app):
    """Setup logging configuration for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler for application logs
    file_handler = RotatingFileHandler('logs/deepscan.log', maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Set up file handler for access logs
    access_log = logging.getLogger('werkzeug')
    access_file_handler = RotatingFileHandler('logs/access.log', maxBytes=10485760, backupCount=10)
    access_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(message)s'
    ))
    access_log.addHandler(access_file_handler)
    
    # Set up file handler for security logs
    security_log = logging.getLogger('security')
    security_file_handler = RotatingFileHandler('logs/security.log', maxBytes=10485760, backupCount=10)
    security_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(request_id)s] %(message)s'
    ))
    security_file_handler.setLevel(logging.INFO)
    security_log.addHandler(security_file_handler)
    security_log.setLevel(logging.INFO)
    
    # Set up file handler for error logs
    error_file_handler = RotatingFileHandler('logs/error.log', maxBytes=10485760, backupCount=10)
    error_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    error_file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(error_file_handler)
    
    # Set up file handler for audit logs
    audit_log = logging.getLogger('audit')
    audit_file_handler = RotatingFileHandler('logs/audit.log', maxBytes=10485760, backupCount=10)
    audit_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(request_id)s] [%(user_id)s] %(message)s'
    ))
    audit_log.addHandler(audit_file_handler)
    audit_log.setLevel(logging.INFO)
    
    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('DeepScan startup')
    
    return app

def log_request_info():
    """Log information about the current request"""
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    g.request_id = request_id
    
    # Log request details
    app.logger.info(f'Request: {request.method} {request.path} [ID: {request_id}]')
    
    # Set the start time for request duration calculation
    g.start_time = time.time()

def log_response_info(response):
    """Log information about the response"""
    # Calculate request duration
    duration = time.time() - g.get('start_time', time.time())
    
    # Log response details
    app.logger.info(f'Response: {response.status_code} [Duration: {duration:.4f}s] [ID: {g.get("request_id", "unknown")}]')
    
    return response

def log_security_event(event_type, message, level='INFO'):
    """Log a security event"""
    security_log = logging.getLogger('security')
    
    # Create a log record with extra fields
    extra = {
        'request_id': getattr(g, 'request_id', 'unknown')
    }
    
    # Log the security event with the appropriate level
    if level == 'INFO':
        security_log.info(f'{event_type}: {message}', extra=extra)
    elif level == 'WARNING':
        security_log.warning(f'{event_type}: {message}', extra=extra)
    elif level == 'ERROR':
        security_log.error(f'{event_type}: {message}', extra=extra)
    elif level == 'CRITICAL':
        security_log.critical(f'{event_type}: {message}', extra=extra)

def log_audit_event(event_type, message, user_id=None):
    """Log an audit event"""
    audit_log = logging.getLogger('audit')
    
    # If user_id is not provided, try to get it from the current user
    if user_id is None and hasattr(g, 'user'):
        user_id = g.user.id
    
    # Create a log record with extra fields
    extra = {
        'request_id': getattr(g, 'request_id', 'unknown'),
        'user_id': user_id or 'anonymous'
    }
    
    # Log the audit event
    audit_log.info(f'{event_type}: {message}', extra=extra)

def register_logging_handlers(app):
    """Register before_request and after_request handlers for logging"""
    @app.before_request
    def before_request():
        log_request_info()
    
    @app.after_request
    def after_request(response):
        return log_response_info(response)
    
    return app
