# DeepScan: AI-Mediated Human Pentest Coordination Platform

## Overview

DeepScan is an AI-mediated human pentest coordination platform that provides a chat-only interface where clients can request pentests via natural language, human analysts manually perform tests, and findings are delivered conversationally. The platform combines AI efficiency with human expertise, positioning DeepScan as a premium pentesting concierge service.

This document provides comprehensive documentation for the DeepScan Proof of Concept (POC) implementation.

## Core Architecture

### 1. Client ↔ AI Interaction
- Clients describe pentest requests in plain English
- AI recognizes intent, extracts data, and asks for clarification when needed
- Natural language interface eliminates the need for complex dashboards

### 2. AI ↔ Analyst Coordination
- Tasks are routed to analysts based on expertise and priority
- Analysts receive structured information extracted from client requests
- Pre-formatted response templates ensure consistency

### 3. Analyst Workflow
- Analysts perform manual pentests using their preferred tools
- Document findings including vulnerabilities, proofs of concept, and remediation steps
- Submit reports through the platform

### 4. Client Delivery
- AI formats analyst findings into conversational responses
- Clients receive expert-validated results with zero false positives
- Compliance-ready audit logs track all interactions

## Technical Implementation

### Technology Stack
- **Backend**: Python with Flask framework
- **Database**: SQLAlchemy ORM with SQLite (can be upgraded to PostgreSQL)
- **Authentication**: Flask-Login with role-based access control
- **Frontend**: Bootstrap 5 for responsive design
- **NLP Processing**: Custom NLP engine for request parsing
- **Logging**: Comprehensive logging system with rotating file handlers

### Database Schema

The database consists of the following main models:

1. **User**: Stores user information and authentication details
   - Attributes: id, username, email, password_hash, role, created_at
   - Relationships: client_requests, analyst_profile, messages

2. **Analyst**: Stores analyst-specific information
   - Attributes: id, user_id, expertise, availability, rating
   - Relationships: user, assigned_requests

3. **PentestRequest**: Stores pentest request details
   - Attributes: id, client_id, analyst_id, target_url, request_type, scope, credentials, priority, status, created_at
   - Relationships: client, analyst, messages, report, vulnerabilities, files

4. **Message**: Stores conversation messages
   - Attributes: id, request_id, user_id, is_ai, content, created_at
   - Relationships: request, user

5. **Report**: Stores pentest reports
   - Attributes: id, request_id, analyst_id, content, severity, created_at
   - Relationships: request, analyst

6. **Vulnerability**: Stores vulnerability findings
   - Attributes: id, request_id, title, severity, description, proof_of_concept, remediation
   - Relationships: request

7. **File**: Stores uploaded files
   - Attributes: id, request_id, user_id, filename, filepath, file_type, uploaded_at
   - Relationships: request, user

### Authentication System

The authentication system provides:

- User registration with role selection (client, analyst)
- Special handling for growthguard.com email domains (automatically assigned admin privileges)
- Secure password hashing
- Role-based access control
- User profile management

### Client Interface

The client interface includes:

- Dashboard showing all pentest requests
- Form for creating new pentest requests
- Detailed view of individual requests
- Chat interface for communicating with AI and analysts
- Report viewing with vulnerability details

### Analyst Interface

The analyst interface includes:

- Dashboard showing available and assigned requests
- Ability to claim pending requests
- Interface for adding vulnerabilities
- Report submission form
- Chat interface for communicating with clients

### NLP Engine

The NLP engine provides:

- Parsing of natural language pentest requests
- Extraction of key information (target URL, credentials, scope)
- Classification of request types (web, API, mobile)
- Generation of appropriate AI responses

### Logging System

The logging system includes:

- Application logs for general events
- Access logs for HTTP requests
- Security logs for authentication events
- Error logs for exceptions
- Audit logs for user actions

## Deployment

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/surya66/DeepScanAI.git
   cd DeepScanAI
   ```

2. Install dependencies:
   ```
   pip install -r requirements-light.txt
   ```

3. Initialize the database:
   ```
   cd src
   python manage.py create_db
   python manage.py seed_db
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Access the application at http://localhost:5000

### Testing

The application includes comprehensive testing:

1. Unit tests for individual components:
   ```
   cd src
   python -m unittest discover tests
   ```

2. Integration tests for end-to-end workflows:
   ```
   cd src
   python integration_tests.py
   ```

## User Workflows

### Client Workflow

1. Register/login to the platform
2. Create a new pentest request using natural language
3. Provide additional details if requested by the AI
4. Receive updates as the pentest progresses
5. View the final report with vulnerabilities and remediation steps

### Analyst Workflow

1. Register/login to the platform
2. View available pentest requests
3. Claim a request based on expertise
4. Perform the pentest using preferred tools
5. Document findings and add vulnerabilities
6. Submit the final report

### Admin Workflow

1. Login with a growthguard.com email (automatic admin privileges)
2. Manage users (clients and analysts)
3. Monitor all pentest requests
4. View system logs and audit trails

## Future Enhancements

The current POC implementation focuses on core functionality. Future enhancements could include:

1. End-to-end encryption for chat communications
2. Integration with popular pentest tools (Burp Suite, Nessus)
3. Automated vulnerability verification
4. Advanced analytics and reporting
5. Client-specific compliance reporting
6. Mobile application support

## Conclusion

The DeepScan POC demonstrates the feasibility of an AI-mediated human pentest coordination platform. By combining AI efficiency with human expertise, DeepScan provides a unique value proposition in the cybersecurity market. The platform's natural language interface simplifies the pentest request process for clients, while the structured workflow ensures high-quality results from human analysts.
