import unittest
from app import create_app, db
from app.models import User, PentestRequest, Report, Vulnerability, Message, Analyst, File
from config import Config
import os
import tempfile
import json
from datetime import datetime

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-key'

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

class AuthTestCase(BaseTestCase):
    def test_register_and_login(self):
        # Test user registration
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'client'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was created
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'client')
        
        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_growthguard_admin_privilege(self):
        # Test that users with growthguard.com email are assigned admin role
        response = self.client.post('/auth/register', data={
            'username': 'adminuser',
            'email': 'admin@growthguard.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'client'  # This should be overridden to admin
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify user was created with admin role
        user = User.query.filter_by(username='adminuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'admin')

class ClientTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a test client user
        self.client_user = User(
            username='clientuser',
            email='client@example.com',
            role='client'
        )
        self.client_user.set_password('password123')
        db.session.add(self.client_user)
        db.session.commit()
        
        # Login as client
        self.client.post('/auth/login', data={
            'username': 'clientuser',
            'password': 'password123'
        })
    
    def test_create_pentest_request(self):
        # Test creating a new pentest request
        response = self.client.post('/client/request/new', data={
            'target_url': 'https://test-target.com',
            'request_type': 'web',
            'scope': 'Test the login and checkout functionality',
            'credentials': 'user:password123',
            'priority': 'medium'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify request was created
        request = PentestRequest.query.filter_by(target_url='https://test-target.com').first()
        self.assertIsNotNone(request)
        self.assertEqual(request.request_type, 'web')
        self.assertEqual(request.status, 'pending')
        
        # Verify initial message was created
        message = Message.query.filter_by(request_id=request.id).first()
        self.assertIsNotNone(message)
        self.assertTrue(message.is_ai)
    
    def test_view_request(self):
        # Create a test request
        request = PentestRequest(
            client_id=self.client_user.id,
            target_url='https://view-test.com',
            request_type='api',
            scope='Test API endpoints',
            status='pending',
            priority='high'
        )
        db.session.add(request)
        db.session.commit()
        
        # Test viewing the request
        response = self.client.get(f'/client/request/{request.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test sending a message
        response = self.client.post(f'/client/send_message/{request.id}', data={
            'content': 'This is a test message'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify message was created
        messages = Message.query.filter_by(request_id=request.id).all()
        self.assertEqual(len(messages), 2)  # Initial AI message + user message + AI response
        self.assertEqual(messages[1].content, 'This is a test message')
        self.assertFalse(messages[1].is_ai)

class AnalystTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a test analyst user
        self.analyst_user = User(
            username='analystuser',
            email='analyst@example.com',
            role='analyst'
        )
        self.analyst_user.set_password('password123')
        db.session.add(self.analyst_user)
        db.session.commit()
        
        # Create analyst profile
        self.analyst = Analyst(
            user_id=self.analyst_user.id,
            expertise='web,api',
            availability=True,
            rating=4.5
        )
        db.session.add(self.analyst)
        
        # Create a test client user
        self.client_user = User(
            username='clientuser',
            email='client@example.com',
            role='client'
        )
        self.client_user.set_password('password123')
        db.session.add(self.client_user)
        
        # Create a test request
        self.request = PentestRequest(
            client_id=self.client_user.id,
            target_url='https://analyst-test.com',
            request_type='web',
            scope='Test login functionality',
            status='pending',
            priority='medium'
        )
        db.session.add(self.request)
        db.session.commit()
        
        # Login as analyst
        self.client.post('/auth/login', data={
            'username': 'analystuser',
            'password': 'password123'
        })
    
    def test_claim_request(self):
        # Test claiming a request
        response = self.client.post(f'/analyst/claim_request/{self.request.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify request was assigned to analyst
        request = PentestRequest.query.get(self.request.id)
        self.assertEqual(request.status, 'assigned')
        self.assertEqual(request.analyst_id, self.analyst.id)
    
    def test_submit_report(self):
        # Assign request to analyst
        self.request.analyst_id = self.analyst.id
        self.request.status = 'assigned'
        db.session.commit()
        
        # Test submitting a report
        response = self.client.post(f'/analyst/submit_report/{self.request.id}', data={
            'content': 'This is a test report',
            'severity': 'medium'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify report was created
        report = Report.query.filter_by(request_id=self.request.id).first()
        self.assertIsNotNone(report)
        self.assertEqual(report.content, 'This is a test report')
        self.assertEqual(report.severity, 'medium')
        
        # Verify request status was updated
        request = PentestRequest.query.get(self.request.id)
        self.assertEqual(request.status, 'completed')
    
    def test_add_vulnerability(self):
        # Assign request to analyst
        self.request.analyst_id = self.analyst.id
        self.request.status = 'assigned'
        db.session.commit()
        
        # Test adding a vulnerability
        response = self.client.post(f'/analyst/add_vulnerability/{self.request.id}', data={
            'title': 'SQL Injection',
            'severity': 'high',
            'description': 'Found SQL injection in login form',
            'proof_of_concept': "' OR 1=1 --",
            'remediation': 'Use prepared statements'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify vulnerability was created
        vuln = Vulnerability.query.filter_by(request_id=self.request.id).first()
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln.title, 'SQL Injection')
        self.assertEqual(vuln.severity, 'high')

class FileManagementTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a test client user
        self.client_user = User(
            username='clientuser',
            email='client@example.com',
            role='client'
        )
        self.client_user.set_password('password123')
        db.session.add(self.client_user)
        
        # Create a test request
        self.request = PentestRequest(
            client_id=self.client_user.id,
            target_url='https://file-test.com',
            request_type='web',
            scope='Test file uploads',
            status='pending',
            priority='medium'
        )
        db.session.add(self.request)
        db.session.commit()
        
        # Login as client
        self.client.post('/auth/login', data={
            'username': 'clientuser',
            'password': 'password123'
        })
        
        # Create a temporary test file
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.write(b'Test file content')
        self.test_file.close()
    
    def tearDown(self):
        super().tearDown()
        os.unlink(self.test_file.name)
    
    def test_upload_file(self):
        # Test uploading a file
        with open(self.test_file.name, 'rb') as f:
            response = self.client.post(f'/files/upload/{self.request.id}', data={
                'file': (f, 'test_file.txt')
            }, follow_redirects=True, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        # Verify file was uploaded
        file = File.query.filter_by(request_id=self.request.id).first()
        self.assertIsNotNone(file)
        self.assertEqual(file.filename, 'test_file.txt')
        
        # Test downloading the file
        response = self.client.get(f'/files/download/{file.id}')
        self.assertEqual(response.status_code, 200)
        
        # Test deleting the file
        response = self.client.post(f'/files/delete/{file.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify file was deleted
        file = File.query.filter_by(id=file.id).first()
        self.assertIsNone(file)

class NLPEngineTestCase(BaseTestCase):
    def test_parse_request(self):
        from app.nlp_engine import parse_request
        
        # Test parsing a simple request
        request_text = "I need to test our checkout API at api.staging.shop.com. Credentials: admin@shop.com/Pass123. Focus on payment flows."
        result = parse_request(request_text)
        
        self.assertEqual(result['target_url'], 'api.staging.shop.com')
        self.assertEqual(result['request_type'], 'api')
        self.assertIn('payment flows', result['scope'])
        self.assertIn('admin@shop.com/Pass123', result['credentials'])
        
        # Test parsing a web application request
        request_text = "Please scan our website at https://example.com for vulnerabilities. Focus on the login page and admin dashboard."
        result = parse_request(request_text)
        
        self.assertEqual(result['target_url'], 'https://example.com')
        self.assertEqual(result['request_type'], 'web')
        self.assertIn('login page', result['scope'])
        self.assertIn('admin dashboard', result['scope'])

if __name__ == '__main__':
    unittest.main()
