#!/usr/bin/env python3
import unittest
import sys
import os
import time
from flask import Flask
from app import create_app, db
from app.models import User, PentestRequest, Report, Vulnerability, Message, Analyst, File
from app.test_logging import TestLogger
from config import Config

class IntegrationTestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'integration-test-key'

def run_integration_tests():
    """Run integration tests for the DeepScan application"""
    print("Starting DeepScan Integration Tests")
    print("=" * 50)
    
    # Create test directory if it doesn't exist
    if not os.path.exists('test_results'):
        os.makedirs('test_results')
    
    # Setup test application
    app = create_app(IntegrationTestConfig)
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Test logging system
        print("\nTesting Logging System...")
        test_logger = TestLogger(app)
        logging_results = test_logger.run_tests()
        for test, result in logging_results:
            status = "✅" if "Success" in result else "❌"
            print(f"{status} {test}: {result}")
        
        # Run unit tests
        print("\nRunning Unit Tests...")
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('tests', pattern='test_*.py')
        test_runner = unittest.TextTestRunner(verbosity=2)
        test_result = test_runner.run(test_suite)
        
        # Create test data for end-to-end testing
        print("\nSetting up test data for end-to-end testing...")
        setup_test_data()
        
        # Run end-to-end tests
        print("\nRunning End-to-End Tests...")
        run_e2e_tests(app)
        
        # Clean up test data
        print("\nCleaning up test data...")
        db.drop_all()
    
    print("\nIntegration Testing Complete")
    print("=" * 50)

def setup_test_data():
    """Setup test data for end-to-end testing"""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@growthguard.com',
        role='admin'
    )
    admin.set_password('adminpass')
    
    # Create client user
    client = User(
        username='client',
        email='client@example.com',
        role='client'
    )
    client.set_password('clientpass')
    
    # Create analyst user
    analyst_user = User(
        username='analyst',
        email='analyst@example.com',
        role='analyst'
    )
    analyst_user.set_password('analystpass')
    
    db.session.add_all([admin, client, analyst_user])
    db.session.commit()
    
    # Create analyst profile
    analyst = Analyst(
        user_id=analyst_user.id,
        expertise='web,api,mobile',
        availability=True,
        rating=4.8
    )
    db.session.add(analyst)
    
    # Create pentest requests
    request1 = PentestRequest(
        client_id=client.id,
        target_url='https://example.com',
        request_type='web',
        scope='Test the login and checkout functionality',
        credentials='user:password123',
        priority='high',
        status='pending'
    )
    
    request2 = PentestRequest(
        client_id=client.id,
        target_url='api.example.com',
        request_type='api',
        scope='Test the payment API endpoints',
        credentials='apikey:abc123',
        priority='medium',
        status='assigned',
        analyst_id=analyst.id
    )
    
    request3 = PentestRequest(
        client_id=client.id,
        target_url='https://mobile.example.com',
        request_type='mobile',
        scope='Test the mobile app authentication',
        priority='low',
        status='completed',
        analyst_id=analyst.id
    )
    
    db.session.add_all([request1, request2, request3])
    db.session.commit()
    
    # Create messages
    message1 = Message(
        request_id=request1.id,
        user_id=None,
        is_ai=True,
        content='Thank you for your pentest request. Our team will review it shortly.'
    )
    
    message2 = Message(
        request_id=request1.id,
        user_id=client.id,
        is_ai=False,
        content='When can I expect this to be assigned?'
    )
    
    message3 = Message(
        request_id=request1.id,
        user_id=None,
        is_ai=True,
        content='Your request is currently pending. We typically assign requests within 24 hours.'
    )
    
    db.session.add_all([message1, message2, message3])
    
    # Create report for completed request
    report = Report(
        request_id=request3.id,
        analyst_id=analyst.id,
        content='This is a test report for the mobile app authentication.',
        severity='medium'
    )
    db.session.add(report)
    
    # Create vulnerabilities
    vuln1 = Vulnerability(
        request_id=request3.id,
        title='Weak Password Policy',
        severity='medium',
        description='The application allows weak passwords with less than 8 characters.',
        proof_of_concept='Created account with password "123"',
        remediation='Implement a stronger password policy requiring at least 8 characters, including uppercase, lowercase, numbers, and special characters.'
    )
    
    vuln2 = Vulnerability(
        request_id=request3.id,
        title='Session Timeout Not Implemented',
        severity='low',
        description='The application does not timeout inactive sessions.',
        proof_of_concept='Left session idle for 2 hours and was still authenticated.',
        remediation='Implement session timeout after a period of inactivity (e.g., 30 minutes).'
    )
    
    db.session.add_all([vuln1, vuln2])
    db.session.commit()
    
    print("✅ Test data created successfully")

def run_e2e_tests(app):
    """Run end-to-end tests for the DeepScan application"""
    with app.test_client() as client:
        # Test 1: User Authentication Flow
        print("\nTest 1: User Authentication Flow")
        
        # Login as client
        response = client.post('/auth/login', data={
            'username': 'client',
            'password': 'clientpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Client login successful")
        
        # Access client dashboard
        response = client.get('/client/dashboard')
        assert response.status_code == 200
        print("✅ Client dashboard accessible")
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        print("✅ Logout successful")
        
        # Login as analyst
        response = client.post('/auth/login', data={
            'username': 'analyst',
            'password': 'analystpass'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Analyst login successful")
        
        # Access analyst dashboard
        response = client.get('/analyst/dashboard')
        assert response.status_code == 200
        print("✅ Analyst dashboard accessible")
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        print("✅ Logout successful")
        
        # Test 2: Client Request Flow
        print("\nTest 2: Client Request Flow")
        
        # Login as client
        client.post('/auth/login', data={
            'username': 'client',
            'password': 'clientpass'
        })
        
        # Create new request
        response = client.post('/client/request/new', data={
            'target_url': 'https://integration-test.com',
            'request_type': 'web',
            'scope': 'Integration test request',
            'credentials': 'test:test123',
            'priority': 'medium'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ New request creation successful")
        
        # Get the new request ID
        request = PentestRequest.query.filter_by(target_url='https://integration-test.com').first()
        assert request is not None
        
        # View request details
        response = client.get(f'/client/request/{request.id}')
        assert response.status_code == 200
        print("✅ Request details view successful")
        
        # Send message
        response = client.post(f'/client/send_message/{request.id}', data={
            'content': 'Integration test message'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Message sending successful")
        
        # Logout
        client.get('/auth/logout')
        
        # Test 3: Analyst Workflow
        print("\nTest 3: Analyst Workflow")
        
        # Login as analyst
        client.post('/auth/login', data={
            'username': 'analyst',
            'password': 'analystpass'
        })
        
        # Claim the request
        response = client.post(f'/analyst/claim_request/{request.id}', follow_redirects=True)
        assert response.status_code == 200
        print("✅ Request claiming successful")
        
        # View request details
        response = client.get(f'/analyst/request/{request.id}')
        assert response.status_code == 200
        print("✅ Analyst request view successful")
        
        # Add vulnerability
        response = client.post(f'/analyst/add_vulnerability/{request.id}', data={
            'title': 'Integration Test Vulnerability',
            'severity': 'high',
            'description': 'This is a test vulnerability',
            'proof_of_concept': 'Test POC',
            'remediation': 'Test remediation'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Vulnerability addition successful")
        
        # Submit report
        response = client.post(f'/analyst/submit_report/{request.id}', data={
            'content': 'Integration test report',
            'severity': 'high'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Report submission successful")
        
        # Logout
        client.get('/auth/logout')
        
        # Test 4: Client Report View
        print("\nTest 4: Client Report View")
        
        # Login as client
        client.post('/auth/login', data={
            'username': 'client',
            'password': 'clientpass'
        })
        
        # View report
        response = client.get(f'/client/request/{request.id}/report')
        assert response.status_code == 200
        print("✅ Report viewing successful")
        
        # Logout
        client.get('/auth/logout')
        
        print("\nAll end-to-end tests passed successfully!")

if __name__ == '__main__':
    run_integration_tests()
