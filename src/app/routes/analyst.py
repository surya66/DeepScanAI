from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import PentestRequest, User, Analyst, Report, Message, Vulnerability
from app import db
from datetime import datetime

analyst_bp = Blueprint('analyst', __name__, url_prefix='/analyst')

@analyst_bp.route('/dashboard')
@login_required
def dashboard():
    """Analyst dashboard showing pending and assigned requests."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get analyst profile
    analyst = current_user.analyst
    
    # Get pending requests that match analyst expertise
    expertise_list = analyst.expertise.split(',')
    pending_requests = PentestRequest.query.filter(
        PentestRequest.status == 'pending',
        PentestRequest.request_type.in_(expertise_list)
    ).order_by(PentestRequest.created_at.desc()).all()
    
    # Get requests assigned to this analyst
    assigned_requests = PentestRequest.query.filter_by(
        analyst_id=analyst.id,
        status='assigned'
    ).order_by(PentestRequest.updated_at.desc()).all()
    
    # Get completed requests by this analyst
    completed_requests = PentestRequest.query.filter_by(
        analyst_id=analyst.id,
        status='completed'
    ).order_by(PentestRequest.updated_at.desc()).limit(5).all()
    
    return render_template(
        'analyst/dashboard.html',
        pending_requests=pending_requests,
        assigned_requests=assigned_requests,
        completed_requests=completed_requests,
        analyst=analyst
    )

@analyst_bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    """View details of a specific pentest request."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Get client info
    client = User.query.get(pentest_request.client_id)
    
    # Get messages for this request
    messages = Message.query.filter_by(request_id=request_id).order_by(Message.created_at).all()
    
    # Get report if exists
    report = Report.query.filter_by(request_id=request_id).first()
    
    return render_template(
        'analyst/view_request.html',
        pentest_request=pentest_request,
        client=client,
        messages=messages,
        report=report,
        current_user=current_user
    )

@analyst_bp.route('/assign/<int:request_id>', methods=['GET', 'POST'])
@login_required
def assign_request(request_id):
    """Assign a pentest request to the current analyst."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if request is already assigned
    if pentest_request.status != 'pending':
        flash('This request is already assigned or completed.', 'warning')
        return redirect(url_for('analyst.dashboard'))
    
    # Assign to current analyst
    pentest_request.analyst_id = current_user.analyst.id
    pentest_request.status = 'assigned'
    pentest_request.updated_at = datetime.utcnow()
    
    # Create system message
    system_message = Message(
        request_id=request_id,
        user_id=None,  # System message
        is_ai=True,
        content=f"Request assigned to analyst {current_user.username}."
    )
    
    db.session.add(system_message)
    db.session.commit()
    
    flash('Request successfully assigned to you.', 'success')
    return redirect(url_for('analyst.view_request', request_id=request_id))

@analyst_bp.route('/submit_report/<int:request_id>', methods=['GET', 'POST'])
@login_required
def submit_report(request_id):
    """Submit a report for a pentest request."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if request is assigned to this analyst
    if pentest_request.analyst_id != current_user.analyst.id:
        flash('This request is not assigned to you.', 'warning')
        return redirect(url_for('analyst.dashboard'))
    
    # Check if report already exists
    existing_report = Report.query.filter_by(request_id=request_id).first()
    if existing_report:
        flash('A report already exists for this request.', 'warning')
        return redirect(url_for('analyst.view_request', request_id=request_id))
    
    if request.method == 'POST':
        # Create new report
        new_report = Report(
            request_id=request_id,
            content=request.form.get('content'),
            severity=request.form.get('severity'),
            created_at=datetime.utcnow()
        )
        
        # Update request status
        pentest_request.status = 'completed'
        pentest_request.updated_at = datetime.utcnow()
        
        # Create system message
        system_message = Message(
            request_id=request_id,
            user_id=None,  # System message
            is_ai=True,
            content=f"Report submitted by analyst {current_user.username}."
        )
        
        db.session.add(new_report)
        db.session.add(system_message)
        db.session.commit()
        
        flash('Report successfully submitted.', 'success')
        return redirect(url_for('analyst.view_request', request_id=request_id))
    
    return render_template('analyst/submit_report.html', pentest_request=pentest_request)

@analyst_bp.route('/add_vulnerability/<int:request_id>', methods=['GET', 'POST'])
@login_required
def add_vulnerability(request_id):
    """Add a vulnerability to a pentest request."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if request is assigned to this analyst
    if pentest_request.analyst_id != current_user.analyst.id:
        flash('This request is not assigned to you.', 'warning')
        return redirect(url_for('analyst.dashboard'))
    
    if request.method == 'POST':
        # Create new vulnerability
        new_vulnerability = Vulnerability(
            request_id=request_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            severity=request.form.get('severity'),
            proof_of_concept=request.form.get('proof_of_concept'),
            remediation=request.form.get('remediation'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_vulnerability)
        db.session.commit()
        
        flash('Vulnerability successfully added.', 'success')
        return redirect(url_for('analyst.view_request', request_id=request_id))
    
    return render_template('analyst/add_vulnerability.html', pentest_request=pentest_request)

@analyst_bp.route('/send_message/<int:request_id>', methods=['POST'])
@login_required
def send_message(request_id):
    """Send a message in a pentest request conversation."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        flash('Access denied. You are not registered as an analyst.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if request is assigned to this analyst
    if pentest_request.analyst_id != current_user.analyst.id:
        flash('This request is not assigned to you.', 'warning')
        return redirect(url_for('analyst.dashboard'))
    
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
        db.session.commit()
    
    return redirect(url_for('analyst.view_request', request_id=request_id))

@analyst_bp.route('/api/requests', methods=['GET'])
@login_required
def api_get_requests():
    """API endpoint to get pending requests for an analyst."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Get analyst profile
    analyst = current_user.analyst
    
    # Get pending requests that match analyst expertise
    expertise_list = analyst.expertise.split(',')
    pending_requests = PentestRequest.query.filter(
        PentestRequest.status == 'pending',
        PentestRequest.request_type.in_(expertise_list)
    ).order_by(PentestRequest.created_at.desc()).all()
    
    # Format response
    requests_data = []
    for req in pending_requests:
        client = User.query.get(req.client_id)
        requests_data.append({
            'id': req.id,
            'target_url': req.target_url,
            'request_type': req.request_type,
            'priority': req.priority,
            'client': client.username,
            'created_at': req.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'requests': requests_data})

@analyst_bp.route('/api/assign/<int:request_id>', methods=['POST'])
@login_required
def api_assign_request(request_id):
    """API endpoint to assign a request to an analyst."""
    # Check if user is an analyst
    if not hasattr(current_user, 'analyst'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Get the request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if request is already assigned
    if pentest_request.status != 'pending':
        return jsonify({'error': 'Request already assigned'}), 400
    
    # Assign to current analyst
    pentest_request.analyst_id = current_user.analyst.id
    pentest_request.status = 'assigned'
    pentest_request.updated_at = datetime.utcnow()
    
    # Create system message
    system_message = Message(
        request_id=request_id,
        user_id=None,  # System message
        is_ai=True,
        content=f"Request assigned to analyst {current_user.username}."
    )
    
    db.session.add(system_message)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Request assigned successfully'})
