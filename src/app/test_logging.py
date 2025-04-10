import logging
import os
from datetime import datetime

class TestLogger:
    """
    Test logger for DeepScan application to verify logging functionality
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = app.logger
        self.security_logger = logging.getLogger('security')
        self.audit_logger = logging.getLogger('audit')
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
    
    def run_tests(self):
        """Run a series of tests to verify logging functionality"""
        results = []
        
        # Test application logging
        try:
            self.logger.info("Test application log message")
            results.append(("Application logging", "Success"))
        except Exception as e:
            results.append(("Application logging", f"Failed: {str(e)}"))
        
        # Test error logging
        try:
            self.logger.error("Test error log message")
            results.append(("Error logging", "Success"))
        except Exception as e:
            results.append(("Error logging", f"Failed: {str(e)}"))
        
        # Test security logging
        try:
            self.security_logger.info("LOGIN_ATTEMPT: Test security log message", 
                                     extra={'request_id': 'test-request-id'})
            results.append(("Security logging", "Success"))
        except Exception as e:
            results.append(("Security logging", f"Failed: {str(e)}"))
        
        # Test audit logging
        try:
            self.audit_logger.info("USER_ACTION: Test audit log message", 
                                  extra={'request_id': 'test-request-id', 'user_id': 'test-user'})
            results.append(("Audit logging", "Success"))
        except Exception as e:
            results.append(("Audit logging", f"Failed: {str(e)}"))
        
        # Verify log files were created
        log_files = ['deepscan.log', 'error.log', 'security.log', 'audit.log']
        for log_file in log_files:
            file_path = os.path.join('logs', log_file)
            if os.path.exists(file_path):
                results.append((f"{log_file} creation", "Success"))
            else:
                results.append((f"{log_file} creation", "Failed: File not found"))
        
        return results
    
    def generate_test_report(self):
        """Generate a report of the logging test results"""
        results = self.run_tests()
        
        report = f"DeepScan Logging Test Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 50 + "\n\n"
        
        for test, result in results:
            status = "✅" if "Success" in result else "❌"
            report += f"{status} {test}: {result}\n"
        
        # Write report to file
        with open('logs/test_report.txt', 'w') as f:
            f.write(report)
        
        return report
