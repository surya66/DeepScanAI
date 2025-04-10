# DeepScan: AI-Mediated Human Pentest Coordination Platform

A chat-only interface where clients request pentests via natural language, human analysts manually perform tests, and findings are delivered conversationally—no automation, no tool integrations, pure human expertise.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/surya66/DeepScanAI.git
cd DeepScanAI

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Run the application
# For full application:
python src/run.py

# OR for minimal demo:
cd minimal_app
python -m http.server 3000
```

Default credentials:
- **Client**: client@example.com / password123
- **Analyst**: analyst@example.com / password123
- **Admin**: admin@growthguard.com / password123

Note: Any user with a growthguard.com email domain will automatically be assigned admin privileges.

## Table of Contents
- [Core Architecture](#core-architecture)
- [Key Features](#key-features)
- [Detailed Installation and Setup](#detailed-installation-and-setup)
- [Running the Application](#running-the-application)
- [Browser Testing Results](#browser-testing-results)
- [Project Structure](#project-structure)
- [Development Roadmap](#development-roadmap)

## Core Architecture

### Client ↔ AI Interaction
- **Input**: Clients describe pentest requests in plain English
- **AI Actions**:
  - **Intent Recognition**: Classify request type (web/mobile/API)
  - **Data Extraction**: Parse URLs, credentials, scope
  - **Clarification**: Ask follow-ups for missing information

### AI ↔ Analyst Coordination
- **Task Routing**: Assign requests to analysts based on expertise
- **Analyst Interface**: Secure chat inbox with client requests and deadlines

### Analyst Workflow
- **Manual Pentest Execution**: Use preferred tools outside the platform
- **Report Submission**: Upload findings via chat

### Client Delivery
- **AI-Formatted Results**: Vulnerabilities presented in clear, actionable format
- **Proactive Follow-ups**: Verification of fixes and remediation steps

## Key Features

### No Tool Integrations
Analysts work offline with their preferred tools, focusing on finding real vulnerabilities rather than configuring software.

### Human-Centric
Zero false positives with all findings validated by experts. Complex flaws and business logic exploits reported with clarity.

### Compliance Ready
Auto-generated audit logs (Who requested? Who tested?). SOC 2/GDPR-compliant data handling.

## Detailed Installation and Setup

### Prerequisites
- Python 3.10+
- SQLite (for development) or PostgreSQL (for production)
- Git

### Manual Setup Steps (Alternative to setup.sh)

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements-light.txt
   ```

3. **Initialize the database**
   ```bash
   cd src
   python manage.py create_db
   python manage.py seed_db
   ```

## Running the Application

### Development Server

1. **Start the Flask application**
   ```bash
   cd src
   python run.py
   ```
   This will start the application on http://localhost:5000

2. **Alternative: Run the minimal demo**
   ```bash
   cd minimal_app
   python -m http.server 3000
   ```
   This will start a lightweight demo on http://localhost:3000

### User Roles

- **Client**: Request pentests, view reports, communicate with analysts
- **Analyst**: Claim pentest requests, submit findings, communicate with clients
- **Admin**: Manage users, view all pentests, assign requests manually

## Browser Testing Results

### Application Loading and Navigation

The application loads correctly with proper styling and layout. Navigation menu (Home, About, Demo, Login, Register) functions properly, and the core architecture section displays with the three main components.

### Interactive Demo Chat Functionality

#### Initial Chat Interface
The chat interface loads correctly with an initial AI greeting and functional input field and Send button.

#### Pentest Request Flow
1. **Initial Request**: User submits a request to test a checkout API
2. **AI Response**: AI asks for more details about target URL and focus areas
3. **Additional Details**: User provides specific endpoint and focus on payment processing
4. **Environment Clarification**: AI asks if this is production or staging
5. **Request Confirmation**: After user confirms staging environment, AI creates request #45, assigns to analyst @alice, and provides 8-hour ETA

### UI and Responsiveness
- Clean, modern interface with appropriate spacing and typography
- Clear distinction between user messages (blue) and AI responses (light gray)
- Responsive design that adapts to different screen sizes

## Project Structure

```
DeepScan/
├── docs/                    # Documentation files
│   ├── database_schema.md   # Database design documentation
│   ├── implementation.md    # Implementation details
│   └── presentation.md      # Presentation materials
├── minimal_app/             # Lightweight demo application
│   ├── app.py               # Flask application for demo
│   └── index.html           # Main HTML file for static demo
├── src/                     # Main application source code
│   ├── app/                 # Flask application
│   │   ├── models/          # Database models
│   │   ├── routes/          # Route blueprints
│   │   ├── static/          # Static assets (CSS, JS)
│   │   └── templates/       # HTML templates
│   ├── config.py            # Application configuration
│   ├── manage.py            # Database management script
│   └── run.py               # Application entry point
├── tests/                   # Test files
│   └── test_scenarios.py    # Test scenarios
├── .gitignore               # Git ignore file
├── requirements-light.txt   # Lightweight dependencies
├── setup.sh                 # Setup script for easy installation
└── README.md                # This file
```

## Development Roadmap

### Phase 1: MVP (Current)
- Basic chat interface for pentest requests
- Simplified NLP for intent recognition
- Analyst workflow for claiming requests
- Basic reporting functionality

### Phase 2: Enhanced Features
- Advanced NLP for better context understanding
- Real-time notifications
- File attachment support
- Enhanced reporting templates

### Phase 3: Enterprise Features
- Team management
- Custom workflows
- Integration with ticketing systems
- Advanced analytics and reporting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

GrowthGuard Team - contact@growthguard.com

Project Link: [https://github.com/surya66/DeepScanAI](https://github.com/surya66/DeepScanAI)
