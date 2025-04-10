import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import PentestRequest, Report, Vulnerability
from app import db
from datetime import datetime

file_bp = Blueprint('file', __name__, url_prefix='/files')

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'zip'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_folder():
    """Get the upload folder path, create if it doesn't exist"""
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

@file_bp.route('/upload/<int:request_id>', methods=['POST'])
@login_required
def upload_file(request_id):
    """Upload a file for a specific pentest request"""
    # Get the pentest request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if user has permission to upload files for this request
    if current_user.role == 'client' and pentest_request.client_id != current_user.id:
        flash('You do not have permission to upload files for this request.', 'danger')
        return redirect(url_for('client.view_request', request_id=request_id))
    
    if current_user.role == 'analyst' and (not hasattr(current_user, 'analyst') or 
                                          pentest_request.analyst_id != current_user.analyst.id):
        flash('You do not have permission to upload files for this request.', 'danger')
        return redirect(url_for('analyst.view_request', request_id=request_id))
    
    # Check if file was included in the request
    if 'file' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(request.referrer)
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(request.referrer)
    
    # Check if the file type is allowed
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Create request-specific folder
        request_folder = os.path.join(get_upload_folder(), f'request_{request_id}')
        if not os.path.exists(request_folder):
            os.makedirs(request_folder)
        
        # Save the file
        file_path = os.path.join(request_folder, filename)
        file.save(file_path)
        
        # Create a file record in the database
        file_record = File(
            request_id=request_id,
            filename=filename,
            file_path=os.path.join(f'request_{request_id}', filename),
            uploaded_by=current_user.id,
            uploaded_at=datetime.utcnow()
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        flash('File successfully uploaded.', 'success')
        
        # Redirect based on user role
        if current_user.role == 'client':
            return redirect(url_for('client.view_request', request_id=request_id))
        else:
            return redirect(url_for('analyst.view_request', request_id=request_id))
    
    flash('File type not allowed.', 'danger')
    return redirect(request.referrer)

@file_bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """Download a file"""
    # Get the file record
    file_record = File.query.get_or_404(file_id)
    
    # Get the pentest request
    pentest_request = PentestRequest.query.get_or_404(file_record.request_id)
    
    # Check if user has permission to download this file
    if current_user.role == 'client' and pentest_request.client_id != current_user.id:
        flash('You do not have permission to download this file.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    if current_user.role == 'analyst' and (not hasattr(current_user, 'analyst') or 
                                          pentest_request.analyst_id != current_user.analyst.id):
        flash('You do not have permission to download this file.', 'danger')
        return redirect(url_for('analyst.dashboard'))
    
    # Get the directory and filename
    directory = os.path.join(get_upload_folder(), os.path.dirname(file_record.file_path))
    filename = os.path.basename(file_record.file_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@file_bp.route('/list/<int:request_id>')
@login_required
def list_files(request_id):
    """List all files for a specific pentest request"""
    # Get the pentest request
    pentest_request = PentestRequest.query.get_or_404(request_id)
    
    # Check if user has permission to view files for this request
    if current_user.role == 'client' and pentest_request.client_id != current_user.id:
        flash('You do not have permission to view files for this request.', 'danger')
        return redirect(url_for('client.dashboard'))
    
    if current_user.role == 'analyst' and (not hasattr(current_user, 'analyst') or 
                                          pentest_request.analyst_id != current_user.analyst.id):
        flash('You do not have permission to view files for this request.', 'danger')
        return redirect(url_for('analyst.dashboard'))
    
    # Get all files for this request
    files = File.query.filter_by(request_id=request_id).order_by(File.uploaded_at.desc()).all()
    
    # Get user information for each file
    file_data = []
    for file in files:
        uploader = User.query.get(file.uploaded_by)
        file_data.append({
            'id': file.id,
            'filename': file.filename,
            'uploaded_by': uploader.username,
            'uploaded_at': file.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            'role': uploader.role
        })
    
    return jsonify({'files': file_data})

@file_bp.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """Delete a file"""
    # Get the file record
    file_record = File.query.get_or_404(file_id)
    
    # Get the pentest request
    pentest_request = PentestRequest.query.get_or_404(file_record.request_id)
    
    # Check if user has permission to delete this file
    if current_user.role != 'admin' and file_record.uploaded_by != current_user.id:
        flash('You do not have permission to delete this file.', 'danger')
        return redirect(request.referrer)
    
    # Delete the file from the filesystem
    file_path = os.path.join(get_upload_folder(), file_record.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete the file record from the database
    db.session.delete(file_record)
    db.session.commit()
    
    flash('File successfully deleted.', 'success')
    
    # Redirect based on user role
    if current_user.role == 'client':
        return redirect(url_for('client.view_request', request_id=pentest_request.id))
    else:
        return redirect(url_for('analyst.view_request', request_id=pentest_request.id))

# Add File model to models.py
class File:
    """File model for storing file information"""
    id = None
    request_id = None
    filename = None
    file_path = None
    uploaded_by = None
    uploaded_at = None
    
    def __init__(self, request_id, filename, file_path, uploaded_by, uploaded_at):
        self.request_id = request_id
        self.filename = filename
        self.file_path = file_path
        self.uploaded_by = uploaded_by
        self.uploaded_at = uploaded_at
