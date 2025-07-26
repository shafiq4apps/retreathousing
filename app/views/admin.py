from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.property import Property
from app.models.lease import Lease
from app.models.document import Document
from app.models.message import Message
from app.models.maintenance_request import MaintenanceRequest
from app.forms import TenantRegistrationForm, PropertyForm, LeaseForm, MessageForm, DocumentUploadForm
import secrets
import string

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get dashboard statistics
    total_properties = Property.query.filter_by(owner_id=current_user.id).count()
    total_tenants = User.query.filter_by(role='tenant', is_active=True).count()
    active_leases = Lease.query.filter_by(status='active').count()
    pending_maintenance = MaintenanceRequest.query.filter_by(status='pending').count()
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    
    # Recent activity
    recent_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.sent_at.desc()).limit(5).all()
    recent_maintenance = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).limit(5).all()
    
    stats = {
        'total_properties': total_properties,
        'total_tenants': total_tenants,
        'active_leases': active_leases,
        'pending_maintenance': pending_maintenance,
        'unread_messages': unread_messages
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_messages=recent_messages,
                         recent_maintenance=recent_maintenance)

@admin_bp.route('/properties')
@login_required
@admin_required
def properties():
    properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('admin/properties.html', properties=properties)

@admin_bp.route('/properties/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(
            owner_id=current_user.id,
            address=form.address.data,
            property_type=form.property_type.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            square_footage=form.square_footage.data,
            rent_amount=form.rent_amount.data,
            description=form.description.data
        )
        db.session.add(property)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('admin.properties'))
    return render_template('admin/add_property.html', form=form)

@admin_bp.route('/tenants')
@login_required
@admin_required
def tenants():
    tenants = User.query.filter_by(role='tenant').all()
    return render_template('admin/tenants.html', tenants=tenants)

@admin_bp.route('/tenants/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_tenant():
    form = TenantRegistrationForm()
    if form.validate_on_submit():
        # Generate secure password
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        tenant = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role='tenant'
        )
        tenant.set_password(password)
        
        db.session.add(tenant)
        db.session.commit()
        
        flash(f'Tenant added successfully! Generated password: {password}', 'success')
        return redirect(url_for('admin.tenants'))
    return render_template('admin/add_tenant.html', form=form)

@admin_bp.route('/leases')
@login_required
@admin_required
def leases():
    leases = Lease.query.all()
    return render_template('admin/leases.html', leases=leases)

@admin_bp.route('/leases/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lease():
    form = LeaseForm()
    
    # Populate choices
    form.tenant_id.choices = [(u.id, u.full_name) for u in User.query.filter_by(role='tenant', is_active=True).all()]
    form.property_id.choices = [(p.id, p.address) for p in Property.query.filter_by(owner_id=current_user.id).all()]
    
    if form.validate_on_submit():
        lease = Lease(
            tenant_id=form.tenant_id.data,
            property_id=form.property_id.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            monthly_rent=form.monthly_rent.data,
            security_deposit=form.security_deposit.data
        )
        db.session.add(lease)
        db.session.commit()
        flash('Lease created successfully!', 'success')
        return redirect(url_for('admin.leases'))
    return render_template('admin/add_lease.html', form=form)

@admin_bp.route('/messages')
@login_required
@admin_required
def messages():
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.sent_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/messages/send', methods=['GET', 'POST'])
@login_required
@admin_required
def send_message():
    form = MessageForm()
    
    # Populate tenant choices
    form.recipient_id.choices = [(u.id, u.full_name) for u in User.query.filter_by(role='tenant', is_active=True).all()]
    form.property_id.choices = [(0, 'None')] + [(p.id, p.address) for p in Property.query.filter_by(owner_id=current_user.id).all()]
    
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
        return redirect(url_for('admin.messages'))
    return render_template('admin/send_message.html', form=form)

@admin_bp.route('/messages/<int:message_id>/read')
@login_required
@admin_required
def mark_message_read(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Only allow recipient to mark as read
    if message.recipient_id == current_user.id:
        message.is_read = True
        db.session.commit()
        flash('Message marked as read.', 'success')
    else:
        flash('You can only mark your own messages as read.', 'error')
    
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:message_id>/delete')
@login_required
@admin_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Only allow sender or recipient to delete
    if message.sender_id == current_user.id or message.recipient_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted successfully.', 'success')
    else:
        flash('You can only delete your own messages.', 'error')
    
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/mark-all-read')
@login_required
@admin_required
def mark_all_messages_read():
    messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).all()
    
    for message in messages:
        message.is_read = True
    
    db.session.commit()
    flash(f'{len(messages)} messages marked as read.', 'success')
    return redirect(url_for('admin.messages'))

@admin_bp.route('/maintenance')
@login_required
@admin_required
def maintenance():
    requests = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template('admin/maintenance.html', requests=requests)

@admin_bp.route('/maintenance/update', methods=['POST'])
@login_required
@admin_required
def update_maintenance_status():
    request_id = request.form.get('request_id')
    new_status = request.form.get('status')
    
    if not request_id or not new_status:
        flash('Missing request ID or status.', 'error')
        return redirect(url_for('admin.maintenance'))
    
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    maintenance_request.status = new_status
    db.session.commit()
    
    flash(f'Maintenance request status updated to {new_status.replace("_", " ").title()}!', 'success')
    return redirect(url_for('admin.maintenance'))

@admin_bp.route('/maintenance/<int:request_id>/delete')
@login_required
@admin_required
def delete_maintenance_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    
    try:
        db.session.delete(maintenance_request)
        db.session.commit()
        flash('Maintenance request deleted successfully.', 'success')
    except Exception as e:
        flash('Error deleting maintenance request.', 'error')
    
    return redirect(url_for('admin.maintenance'))

@admin_bp.route('/maintenance/<int:request_id>/view')
@login_required
@admin_required
def view_maintenance_request(request_id):
    maintenance_request = MaintenanceRequest.query.get_or_404(request_id)
    return render_template('admin/maintenance_detail.html', request=maintenance_request)

@admin_bp.route('/documents')
@login_required
@admin_required
def documents():
    documents = Document.query.all()
    return render_template('admin/documents.html', documents=documents)

@admin_bp.route('/documents/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_document():
    form = DocumentUploadForm()
    
    # Populate lease choices
    form.lease_id.choices = [(l.id, f"{l.tenant.full_name} - {l.property.address}") for l in Lease.query.all()]
    
    if form.validate_on_submit():
        import os
        from werkzeug.utils import secure_filename
        
        # Get uploaded file
        file = form.file.data
        original_filename = secure_filename(file.filename)
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Create document record
        document = Document(
            lease_id=form.lease_id.data,
            document_type=form.document_type.data,
            file_name=original_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            mime_type=file.mimetype,
            uploaded_by=current_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash('Document uploaded successfully!', 'success')
        return redirect(url_for('admin.documents'))
    
    return render_template('admin/upload_document.html', form=form)

@admin_bp.route('/documents/<int:document_id>/download')
@login_required
@admin_required
def download_document(document_id):
    from flask import send_file
    document = Document.query.get_or_404(document_id)
    
    try:
        return send_file(document.file_path, as_attachment=True, download_name=document.file_name)
    except FileNotFoundError:
        flash('File not found on server.', 'error')
        return redirect(url_for('admin.documents'))

@admin_bp.route('/documents/<int:document_id>/view')
@login_required
@admin_required
def view_document(document_id):
    from flask import send_file
    document = Document.query.get_or_404(document_id)
    
    try:
        return send_file(document.file_path, as_attachment=False)
    except FileNotFoundError:
        flash('File not found on server.', 'error')
        return redirect(url_for('admin.documents'))

@admin_bp.route('/documents/<int:document_id>/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_document(document_id):
    import os
    document = Document.query.get_or_404(document_id)
    
    try:
        # Delete physical file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete database record
        db.session.delete(document)
        db.session.commit()
        
        flash('Document deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting document.', 'error')
    
    return redirect(url_for('admin.documents'))