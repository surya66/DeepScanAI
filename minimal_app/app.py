from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DeepScan - AI-Mediated Human Pentest Coordination Platform</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .navbar {
                background-color: #ffffff !important;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .navbar-brand {
                font-weight: bold;
                color: #0d6efd !important;
            }
            .chat-container {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #dee2e6;
                border-radius: 0.25rem;
                padding: 1rem;
                background-color: #fff;
            }
            .chat-message {
                margin-bottom: 1rem;
                max-width: 80%;
            }
            .chat-message-ai {
                align-self: flex-start;
                margin-right: auto;
            }
            .chat-message-user {
                align-self: flex-end;
                margin-left: auto;
            }
            .chat-message-content {
                padding: 0.75rem;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            .footer {
                margin-top: 3rem;
                padding: 1.5rem 0;
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
            .card {
                box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
                margin-bottom: 1.5rem;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light">
            <div class="container">
                <a class="navbar-brand" href="#">DeepScan</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav me-auto">
                        <li class="nav-item">
                            <a class="nav-link active" href="#">Home</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#about">About</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#demo">Demo</a>
                        </li>
                    </ul>
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link" href="#login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#register">Register</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <div class="row">
                <div class="col-md-8 offset-md-2 text-center">
                    <h1 class="display-4 mb-4">DeepScan</h1>
                    <h2 class="mb-4">AI-Mediated Human Pentest Coordination Platform</h2>
                    <p class="lead">
                        A chat-only interface where clients request pentests via natural language, human analysts manually perform tests, 
                        and findings are delivered conversationally—no automation, no tool integrations, pure human expertise.
                    </p>
                </div>
            </div>

            <div class="row mt-5" id="about">
                <div class="col-md-12">
                    <h2 class="text-center mb-4">Core Architecture</h2>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">Client ↔ AI Interaction</h5>
                            <p class="card-text">
                                <strong>Input:</strong> Clients describe pentest requests in plain English.<br>
                                <strong>AI Actions:</strong> Intent recognition, data extraction, and clarification.
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">AI ↔ Analyst Coordination</h5>
                            <p class="card-text">
                                <strong>Task Routing:</strong> Assign requests to analysts based on expertise.<br>
                                <strong>Analyst Interface:</strong> Secure chat inbox with client requests and deadlines.
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">Client Delivery</h5>
                            <p class="card-text">
                                <strong>AI-Formatted Results:</strong> Vulnerabilities presented in clear, actionable format.<br>
                                <strong>Proactive Follow-ups:</strong> Verification of fixes and remediation steps.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-5" id="demo">
                <div class="col-md-12">
                    <h2 class="text-center mb-4">Interactive Demo</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex flex-column chat-container" id="chatContainer">
                                <div class="chat-message chat-message-ai">
                                    <div class="chat-message-content bg-light">
                                        <strong>AI Copilot</strong>
                                        <div class="mt-1">Hello! I'm your DeepScan AI assistant. How can I help you with your security testing needs today?</div>
                                    </div>
                                </div>
                            </div>
                            <form id="chatForm" class="mt-3">
                                <div class="input-group">
                                    <input type="text" id="messageInput" class="form-control" placeholder="Type your message here..." required>
                                    <button type="submit" class="btn btn-primary">Send</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-5">
                <div class="col-md-12">
                    <h2 class="text-center mb-4">Key Features</h2>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">No Tool Integrations</h5>
                                    <p class="card-text">Analysts work offline with their preferred tools, focusing on finding real vulnerabilities rather than configuring software.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h5 class="card-title">Human-Centric</h5>
                                    <p class="card-text">Zero false positives with all findings validated by experts. Complex flaws and business logic exploits reported with clarity.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="footer mt-5">
            <div class="container text-center">
                <span class="text-muted">© 2025 DeepScan. All rights reserved.</span>
            </div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const chatForm = document.getElementById('chatForm');
                const messageInput = document.getElementById('messageInput');
                const chatContainer = document.getElementById('chatContainer');
                
                // Sample responses for the demo
                const responses = [
                    "I understand you want to test your application. Could you provide the target URL and any specific areas you'd like us to focus on?",
                    "Thanks for the details. Is this a production environment or a staging/test environment?",
                    "Great! I've created request #45 for you. It's been assigned to analyst @alice who will begin testing shortly. Estimated completion time: 8 hours.",
                    "I've notified the analyst about your request. They'll be in touch if they need any additional information.",
                    "The analyst has completed their testing and found 2 vulnerabilities: 1 Critical (SQL Injection) and 1 High (XSS). Would you like to see the details?",
                    "Here's the critical vulnerability details:\\n\\n🚨 SQL Injection in login form\\nPoC: ' OR 1=1 --\\nImpact: Unauthorized access to all user accounts\\nFix: Use parameterized queries instead of string concatenation."
                ];
                
                let responseIndex = 0;
                
                chatForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Add user message
                    const userMessageDiv = document.createElement('div');
                    userMessageDiv.className = 'chat-message chat-message-user';
                    userMessageDiv.innerHTML = `
                        <div class="chat-message-content bg-primary text-white">
                            <strong>You</strong>
                            <div class="mt-1">${message}</div>
                        </div>
                    `;
                    chatContainer.appendChild(userMessageDiv);
                    
                    // Clear input
                    messageInput.value = '';
                    
                    // Scroll to bottom
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                    
                    // Simulate AI response after a short delay
                    setTimeout(function() {
                        const aiMessageDiv = document.createElement('div');
                        aiMessageDiv.className = 'chat-message chat-message-ai';
                        aiMessageDiv.innerHTML = `
                            <div class="chat-message-content bg-light">
                                <strong>AI Copilot</strong>
                                <div class="mt-1">${responses[responseIndex]}</div>
                            </div>
                        `;
                        chatContainer.appendChild(aiMessageDiv);
                        
                        // Increment response index or reset if at end
                        responseIndex = (responseIndex + 1) % responses.length;
                        
                        // Scroll to bottom again
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }, 1000);
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/chat', methods=['POST'])
def chat():
    # Sample responses for the demo
    responses = [
        "I understand you want to test your application. Could you provide the target URL and any specific areas you'd like us to focus on?",
        "Thanks for the details. Is this a production environment or a staging/test environment?",
        "Great! I've created request #45 for you. It's been assigned to analyst @alice who will begin testing shortly. Estimated completion time: 8 hours.",
        "I've notified the analyst about your request. They'll be in touch if they need any additional information.",
        "The analyst has completed their testing and found 2 vulnerabilities: 1 Critical (SQL Injection) and 1 High (XSS). Would you like to see the details?",
        "Here's the critical vulnerability details:\n\n🚨 SQL Injection in login form\nPoC: ' OR 1=1 --\nImpact: Unauthorized access to all user accounts\nFix: Use parameterized queries instead of string concatenation."
    ]
    
    # Get message from request
    data = request.json
    message = data.get('message', '')
    
    # Simple response logic
    if 'scan' in message.lower() or 'test' in message.lower():
        response = responses[0]
    elif 'url' in message.lower() or 'http' in message.lower():
        response = responses[1]
    elif 'staging' in message.lower() or 'test' in message.lower():
        response = responses[2]
    elif 'thank' in message.lower() or 'great' in message.lower():
        response = responses[3]
    elif 'status' in message.lower() or 'update' in message.lower():
        response = responses[4]
    elif 'detail' in message.lower() or 'show' in message.lower():
        response = responses[5]
    else:
        response = "I'm not sure I understand. Could you provide more details about what you'd like to test?"
    
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
