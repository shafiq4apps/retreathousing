from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.property import Property
from app.models.lease import Lease
from app.models.document import Document
from app.models.message import Message
from app.models.maintenance_request import MaintenanceRequest
from app.forms import MessageForm, MaintenanceRequestForm

tenant_bp = Blueprint('tenant', __name__)

def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_tenant():
            flash('Access denied. Tenant access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@tenant_bp.route('/dashboard')
@login_required
@tenant_required
def dashboard():
    # Get tenant's active lease
    active_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    
    # Get tenant's maintenance requests
    maintenance_requests = MaintenanceRequest.query.filter_by(tenant_id=current_user.id).order_by(MaintenanceRequest.created_at.desc()).limit(5).all()
    
    # Get unread messages
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    
    # Get recent messages
    recent_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.sent_at.desc()).limit(5).all()
    
    # Get lease documents
    lease_documents = []
    if active_lease:
        lease_documents = Document.query.filter_by(lease_id=active_lease.id).all()
    
    stats = {
        'active_lease': active_lease,
        'maintenance_requests_count': len(maintenance_requests),
        'unread_messages': unread_messages,
        'documents_count': len(lease_documents)
    }
    
    return render_template('tenant/dashboard.html', 
                         stats=stats,
                         active_lease=active_lease,
                         maintenance_requests=maintenance_requests,
                         recent_messages=recent_messages,
                         lease_documents=lease_documents)

@tenant_bp.route('/documents')
@login_required
@tenant_required
def documents():
    # Get tenant's lease
    lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    
    documents = []
    if lease:
        documents = Document.query.filter_by(lease_id=lease.id).all()
    
    return render_template('tenant/documents.html', documents=documents, lease=lease)

@tenant_bp.route('/messages')
@login_required
@tenant_required
def messages():
    # Get all messages involving the tenant
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.sent_at.desc()).all()
    
    # Mark messages as read when tenant views them
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).all()
    for message in unread_messages:
        message.mark_as_read()
    
    return render_template('tenant/messages.html', messages=messages)

@tenant_bp.route('/messages/send', methods=['GET', 'POST'])
@login_required
@tenant_required
def send_message():
    form = MessageForm()
    
    # Get tenant's lease to determine property and admin
    active_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    
    if active_lease:
        # Set admin as recipient and property
        admin = User.query.filter_by(role='admin').first()
        if admin:
            form.recipient_id.choices = [(admin.id, 'Property Manager')]
            form.property_id.choices = [(0, 'General')] + [(active_lease.property.id, active_lease.property.address)]
        else:
            flash('No property manager available to send message to.', 'error')
            return redirect(url_for('tenant.messages'))
    else:
        flash('You must have an active lease to send messages.', 'error')
        return redirect(url_for('tenant.messages'))
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=form.recipient_id.data,
            property_id=form.property_id.data if form.property_id.data != 0 else None,
            message_text=form.message_text.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('tenant.messages'))
    
    return render_template('tenant/send_message.html', form=form, active_lease=active_lease)

@tenant_bp.route('/maintenance')
@login_required
@tenant_required
def maintenance():
    requests = MaintenanceRequest.query.filter_by(tenant_id=current_user.id).order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template('tenant/maintenance.html', requests=requests)

@tenant_bp.route('/maintenance/request', methods=['GET', 'POST'])
@login_required
@tenant_required
def request_maintenance():
    form = MaintenanceRequestForm()
    
    # Get tenant's properties (through active leases)
    active_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    
    if not active_lease:
        flash('You must have an active lease to request maintenance.', 'error')
        return redirect(url_for('tenant.maintenance'))
    
    form.property_id.choices = [(active_lease.property.id, active_lease.property.address)]
    
    if form.validate_on_submit():
        maintenance_request = MaintenanceRequest(
            tenant_id=current_user.id,
            property_id=form.property_id.data,
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data
        )
        db.session.add(maintenance_request)
        db.session.commit()
        flash('Maintenance request submitted successfully!', 'success')
        return redirect(url_for('tenant.maintenance'))
    
    return render_template('tenant/request_maintenance.html', form=form, active_lease=active_lease)

@tenant_bp.route('/documents/<int:document_id>/download')
@login_required
@tenant_required
def download_document(document_id):
    from flask import send_file
    document = Document.query.get_or_404(document_id)
    
    # Ensure tenant can only access their own lease documents
    tenant_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    if not tenant_lease or document.lease_id != tenant_lease.id:
        flash('Access denied. You can only access your own documents.', 'error')
        return redirect(url_for('tenant.documents'))
    
    try:
        return send_file(document.file_path, as_attachment=True, download_name=document.file_name)
    except FileNotFoundError:
        flash('File not found on server.', 'error')
        return redirect(url_for('tenant.documents'))

@tenant_bp.route('/documents/<int:document_id>/view')
@login_required
@tenant_required
def view_document(document_id):
    from flask import send_file
    document = Document.query.get_or_404(document_id)
    
    # Ensure tenant can only access their own lease documents
    tenant_lease = Lease.query.filter_by(tenant_id=current_user.id, status='active').first()
    if not tenant_lease or document.lease_id != tenant_lease.id:
        flash('Access denied. You can only access your own documents.', 'error')
        return redirect(url_for('tenant.documents'))
    
    try:
        return send_file(document.file_path, as_attachment=False)
    except FileNotFoundError:
        flash('File not found on server.', 'error')
        return redirect(url_for('tenant.documents'))