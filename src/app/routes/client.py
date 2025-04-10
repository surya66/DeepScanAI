from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import PentestRequest, Report, Vulnerability, Message
from app import db
from datetime import datetime

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/dashboard')
@login_required
def dashboard():
    """Client dashboard showing all pentest requests."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        flash('Access denied. You are not registered as a client.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all requests for this client
    pentest_requests = PentestRequest.query.filter_by(
        client_id=current_user.id
    ).order_by(PentestRequest.created_at.desc()).all()
    
    return render_template(
        'client/dashboard.html',
        pentest_requests=pentest_requests
    )

@client_bp.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request():
    """Create a new pentest request."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        flash('Access denied. You are not registered as a client.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        request_type = request.form.get('request_type')
        scope = request.form.get('scope')
        credentials = request.form.get('credentials')
        priority = request.form.get('priority', 'medium')
        
        # Validate input
        if not target_url or not request_type or not scope:
            flash('Target URL, request type, and scope are required.', 'danger')
            return render_template('client/new_request.html')
        
        # Create new request
        new_pentest_request = PentestRequest(
            client_id=current_user.id,
            target_url=target_url,
            request_type=request_type,
            scope=scope,
            credentials=credentials,
            priority=priority,
            status='pending'
        )
        
        db.session.add(new_pentest_request)
        db.session.commit()
        
        # Create initial AI message
        ai_message = Message(
            request_id=new_pentest_request.id,
            user_id=None,  # System/AI message
            is_ai=True,
            content=f"Thank you for your pentest request for {target_url}. Our team will review your request and assign an analyst with expertise in {request_type} security."
        )
        
        db.session.add(ai_message)
        db.session.commit()
        
        flash('Pentest request submitted successfully.', 'success')
        return redirect(url_for('client.view_request', request_id=new_pentest_request.id))
    
    return render_template('client/new_request.html')

@client_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    """View details of a specific pentest request."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        flash('Access denied. You are not registered as a client.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if this request belongs to the current user
    if pentest_request.client_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. This request does not belong to you.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Get messages for this request
    messages = Message.query.filter_by(request_id=request_id).order_by(Message.created_at).all()
    
    # Get report if exists
    report = Report.query.filter_by(request_id=request_id).first()
    
    # Get vulnerabilities if report exists
    vulnerabilities = []
    if report:
        vulnerabilities = Vulnerability.query.filter_by(request_id=request_id).order_by(Vulnerability.severity.desc()).all()
    
    # Get files for this request
    files = File.query.filter_by(request_id=request_id).order_by(File.uploaded_at.desc()).all()
    
    return render_template(
        'client/view_request.html',
        pentest_request=pentest_request,
        messages=messages,
        report=report,
        vulnerabilities=vulnerabilities,
        files=files
    )

@client_bp.route('/request/<int:request_id>/report')
@login_required
def view_report(request_id):
    """View the report for a specific pentest request."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        flash('Access denied. You are not registered as a client.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if this request belongs to the current user
    if pentest_request.client_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. This request does not belong to you.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Get report
    report = Report.query.filter_by(request_id=request_id).first()
    
    if not report:
        flash('No report available for this request yet.', 'warning')
        return redirect(url_for('client.view_request', request_id=request_id))
    
    # Get vulnerabilities
    vulnerabilities = Vulnerability.query.filter_by(request_id=request_id).order_by(Vulnerability.severity.desc()).all()
    
    return render_template(
        'client/view_report.html',
        pentest_request=pentest_request,
        report=report,
        vulnerabilities=vulnerabilities
    )

@client_bp.route('/send_message/<int:request_id>', methods=['POST'])
@login_required
def send_message(request_id):
    """Send a message in a pentest request conversation."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        flash('Access denied. You are not registered as a client.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if this request belongs to the current user
    if pentest_request.client_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. This request does not belong to you.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    # Create new message
    content = request.form.get('content')
    if content:
        new_message = Message(
            request_id=request_id,
            user_id=current_user.id,
            is_ai=False,
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_message)
        
        # Create AI response
        ai_response = Message(
            request_id=request_id,
            user_id=None,  # System/AI message
            is_ai=True,
            content=f"Thank you for your message. {generate_ai_response(pentest_request.status)}",
            created_at=datetime.utcnow()
        )
        
        db.session.add(ai_response)
        db.session.commit()
    
    return redirect(url_for('client.view_request', request_id=request_id))

def generate_ai_response(request_status):
    """Generate an appropriate AI response based on request status."""
    if request_status == 'pending':
        return "Your request is still pending assignment to an analyst. We'll notify you once an analyst has been assigned."
    elif request_status == 'assigned':
        return "Your request is currently being worked on by one of our security analysts. They will update you with their findings soon."
    elif request_status == 'completed':
        return "Your pentest has been completed. Please review the report and let us know if you have any questions about the findings."
    else:
        return "Our team is reviewing your request and will respond shortly."

@client_bp.route('/api/requests')
@login_required
def api_get_requests():
    """API endpoint to get all pentest requests for a client."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all requests for this client
    pentest_requests = PentestRequest.query.filter_by(
        client_id=current_user.id
    ).order_by(PentestRequest.created_at.desc()).all()
    
    # Format response
    requests_data = []
    for req in pentest_requests:
        requests_data.append({
            'id': req.id,
            'target_url': req.target_url,
            'request_type': req.request_type,
            'status': req.status,
            'priority': req.priority,
            'created_at': req.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'requests': requests_data})

@client_bp.route('/api/request/<int:request_id>/vulnerabilities')
@login_required
def api_get_vulnerabilities(request_id):
    """API endpoint to get vulnerabilities for a specific pentest request."""
    # Check if user is a client
    if current_user.role != 'client' and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if this request belongs to the current user
    if pentest_request.client_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get vulnerabilities
    vulnerabilities = Vulnerability.query.filter_by(request_id=request_id).order_by(Vulnerability.severity.desc()).all()
    
    # Format response
    vulnerabilities_data = []
    for vuln in vulnerabilities:
        vulnerabilities_data.append({
            'id': vuln.id,
            'title': vuln.title,
            'severity': vuln.severity,
            'description': vuln.description,
            'proof_of_concept': vuln.proof_of_concept,
            'remediation': vuln.remediation
        })
    
    return jsonify({'vulnerabilities': vulnerabilities_data})

# Import File model to avoid undefined reference
from app.models import File
