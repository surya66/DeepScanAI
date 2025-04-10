# DeepScan Database Schema Design

## Overview
This document outlines the database schema for the DeepScan AI-Mediated Human Pentest Coordination Platform. The schema is designed to support the core functionality of the platform, including user management, pentest request handling, analyst assignment, and report management.

## Entity Relationship Diagram

```
+----------------+       +-------------------+       +----------------+
|     Users      |       |  PentestRequests  |       |    Analysts    |
+----------------+       +-------------------+       +----------------+
| id (PK)        |       | id (PK)           |       | id (PK)        |
| username       |       | client_id (FK)    |<----->| user_id (FK)   |
| email          |       | analyst_id (FK)   |       | expertise      |
| password_hash  |       | target_url        |       | availability   |
| role           |       | credentials       |       | rating         |
| created_at     |       | scope             |       | created_at     |
| last_login     |       | status            |       +----------------+
+----------------+       | priority          |
        ^                | created_at        |
        |                | updated_at        |
        |                +-------------------+
        |                        |
        |                        v
+----------------+       +-------------------+
|   Messages     |       |     Reports       |
+----------------+       +-------------------+
| id (PK)        |       | id (PK)           |
| request_id (FK)|<----->| request_id (FK)   |
| user_id (FK)   |       | analyst_id (FK)   |
| content        |       | content           |
| is_ai          |       | severity          |
| created_at     |       | file_path         |
+----------------+       | created_at        |
                         +-------------------+
                                 |
                                 v
                         +-------------------+
                         |  Vulnerabilities  |
                         +-------------------+
                         | id (PK)           |
                         | report_id (FK)    |
                         | title             |
                         | description       |
                         | severity          |
                         | poc               |
                         | remediation       |
                         | status            |
                         | created_at        |
                         | updated_at        |
                         +-------------------+
```

## Tables Description

### Users
Stores information about all users of the platform, including clients and administrators.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| username      | String       | Unique username                                  |
| email         | String       | Unique email address                             |
| password_hash | String       | Hashed password                                  |
| role          | String       | User role (client, admin)                        |
| created_at    | DateTime     | Account creation timestamp                       |
| last_login    | DateTime     | Last login timestamp                             |

### Analysts
Stores information about security analysts who perform pentests.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| user_id       | Integer      | Foreign key to Users table                       |
| expertise     | String       | Areas of expertise (web, mobile, API)            |
| availability  | Boolean      | Current availability status                      |
| rating        | Float        | Performance rating                               |
| created_at    | DateTime     | Record creation timestamp                        |

### PentestRequests
Stores information about pentest requests submitted by clients.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| client_id     | Integer      | Foreign key to Users table (client)              |
| analyst_id    | Integer      | Foreign key to Analysts table                    |
| target_url    | String       | Target URL or application                        |
| credentials   | String       | Encrypted credentials for testing                |
| scope         | Text         | Detailed scope of the pentest                    |
| status        | String       | Request status (pending, assigned, completed)    |
| priority      | String       | Priority level (low, medium, high, critical)     |
| created_at    | DateTime     | Request submission timestamp                     |
| updated_at    | DateTime     | Last update timestamp                            |

### Messages
Stores all messages exchanged in the chat interface.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| request_id    | Integer      | Foreign key to PentestRequests table             |
| user_id       | Integer      | Foreign key to Users table (sender)              |
| content       | Text         | Message content                                  |
| is_ai         | Boolean      | Whether message is from AI or human              |
| created_at    | DateTime     | Message timestamp                                |

### Reports
Stores pentest reports submitted by analysts.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| request_id    | Integer      | Foreign key to PentestRequests table             |
| analyst_id    | Integer      | Foreign key to Analysts table                    |
| content       | Text         | Report summary content                           |
| severity      | String       | Overall severity (low, medium, high, critical)   |
| file_path     | String       | Path to uploaded report file                     |
| created_at    | DateTime     | Report submission timestamp                      |

### Vulnerabilities
Stores individual vulnerabilities identified in reports.

| Field         | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | Integer      | Primary key                                      |
| report_id     | Integer      | Foreign key to Reports table                     |
| title         | String       | Vulnerability title                              |
| description   | Text         | Detailed description                             |
| severity      | String       | Severity level (low, medium, high, critical)     |
| poc           | Text         | Proof of concept                                 |
| remediation   | Text         | Remediation steps                                |
| status        | String       | Status (open, fixed, verified)                   |
| created_at    | DateTime     | Record creation timestamp                        |
| updated_at    | DateTime     | Last update timestamp                            |

## Relationships

1. **Users to PentestRequests**: One-to-many (A client can have multiple pentest requests)
2. **Analysts to PentestRequests**: One-to-many (An analyst can handle multiple pentest requests)
3. **Users to Analysts**: One-to-one (An analyst is associated with one user account)
4. **PentestRequests to Messages**: One-to-many (A pentest request can have multiple messages)
5. **PentestRequests to Reports**: One-to-one (A pentest request has one final report)
6. **Reports to Vulnerabilities**: One-to-many (A report can document multiple vulnerabilities)

## Notes for Implementation

- Use SQLAlchemy ORM for database interactions
- Implement proper indexing for frequently queried fields
- Ensure proper encryption for sensitive data like credentials
- Use foreign key constraints to maintain data integrity
- Implement soft delete where appropriate to preserve data history
