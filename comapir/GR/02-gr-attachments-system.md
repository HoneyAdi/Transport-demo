# GR Attachments System Implementation

## Overview
Implement document attachment system for GR (Goods Receipt) to support compliance, documentation, and digital workflows.

## Current State
- ✅ Basic TransportBill model exists
- ✅ GR number generation
- ✅ Basic party information tracking
- ❌ Document attachment support
- ❌ Document validation and approval
- ❌ Digital signature capture

## Implementation Plan

### Database Schema Changes

#### 1. Create GRAttachment Model
```python
class GRAttachment(db.Model):
    """Attachments for GR documents"""
    __tablename__ = "gr_attachments"
    
    id = db.Column(db.Integer, primary_key=True)
    gr_id = db.Column(db.Integer, db.ForeignKey('transport_bills.id'), nullable=False)
    attachment_type = db.Column(db.String(50))  # PO, invoice, photo, document
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    expiry_date = db.Column(db.Date)
    
    # Relationships
    gr = db.relationship("TransportBill", backref="attachments")
    uploader = db.relationship("User", foreign_keys=[uploaded_by])
    approver = db.relationship("User", foreign_keys=[approved_by])
```

#### 2. Create DocumentType Model
```python
class DocumentType(db.Model):
    """Document type definitions"""
    __tablename__ = "document_types"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_required = db.Column(db.Boolean, default=False)
    max_file_size = db.Column(db.Integer)  # in KB
    allowed_extensions = db.Column(db.Text)  # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Backend Implementation

#### 1. GR Attachment Routes
```python
@app.route("/gr/<int:gr_id>/attachments")
@permission_required("transport_bills", "view")
def gr_attachments(gr_id):
    """View attachments for a GR"""
    gr = db.session.get(TransportBill, gr_id)
    if not gr:
        flash('GR not found', 'error')
        return redirect(url_for('gr_list'))
    
    return render_template("gr/attachments.html", gr=gr, attachments=gr.attachments)

@app.route("/gr/<int:gr_id>/upload-attachment", methods=["GET", "POST"])
@permission_required("transport_bills", "edit")
def upload_gr_attachment(gr_id):
    """Upload attachment to GR"""
    gr = db.session.get(TransportBill, gr_id)
    if not gr:
        flash('GR not found', 'error')
        return redirect(url_for('gr_list'))
    
    if request.method == "GET":
        return render_template("gr/upload_attachment.html", gr=gr)
    
    # Handle file upload
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('gr_attachments', gr_id=gr_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('gr_attachments', gr_id=gr_id))
    
    # Validate file
    if not allowed_file(file.filename):
        flash('File type not allowed', 'error')
        return redirect(url_for('gr_attachments', gr_id=gr_id))
    
    # Save file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'gr_attachments', filename)
    file.save(file_path)
    
    # Create attachment record
    attachment = GRAttachment(
        gr_id=gr_id,
        attachment_type=request.form.get('attachment_type', 'document'),
        file_name=filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.mimetype,
        description=request.form.get('description', ''),
        uploaded_by=session['user_id']
    )
    
    db.session.add(attachment)
    db.session.commit()
    
    flash('Attachment uploaded successfully', 'success')
    return redirect(url_for('gr_attachments', gr_id=gr_id))

@app.route("/gr/attachment/<int:attachment_id>/approve", methods=["POST"])
@permission_required("gr_attachments", "approve")
def approve_gr_attachment(attachment_id):
    """Approve GR attachment"""
    attachment = db.session.get(GRAttachment, attachment_id)
    if not attachment:
        flash('Attachment not found', 'error')
        return redirect(url_for('gr_list'))
    
    attachment.is_approved = True
    attachment.approved_by = session['user_id']
    attachment.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Attachment approved successfully', 'success')
    return redirect(url_for('gr_attachments', gr_id=attachment.gr_id))

@app.route("/gr/attachment/<int:attachment_id>/reject", methods=["POST"])
@permission_required("gr_attachments", "approve")
def reject_gr_attachment(attachment_id):
    """Reject GR attachment"""
    attachment = db.session.get(GRAttachment, attachment_id)
    if not attachment:
        flash('Attachment not found', 'error')
        return redirect(url_for('gr_list'))
    
    attachment.is_approved = False
    attachment.rejection_reason = request.form.get('rejection_reason', '')
    attachment.approved_by = session['user_id']
    attachment.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('Attachment rejected successfully', 'success')
    return redirect(url_for('gr_attachments', gr_id=attachment.gr_id))
```

### Frontend Implementation

#### 1. GR Attachments List Template
```html
<!-- templates/gr/attachments.html -->
{% extends 'base.html' %}

{% block title %}GR Attachments{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-paperclip"></i> GR Attachments</h5>
                    <a href="{{ url_for('upload_gr_attachment', gr_id=gr.id) }}" class="btn btn-primary">
                        <i class="bi bi-plus"></i> Upload Attachment
                    </a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Uploaded By</th>
                                    <th>Uploaded At</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for attachment in attachments %}
                                <tr>
                                    <td>
                                        {% if attachment.is_approved %}
                                            <a href="{{ url_for('download_attachment', attachment_id=attachment.id) }}" class="text-primary">
                                                {{ attachment.file_name }}
                                            </a>
                                        {% else %}
                                            <span class="text-muted">{{ attachment.file_name }}</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <span class="badge bg-{% if attachment.attachment_type == 'PO' %}primary{% elif attachment.attachment_type == 'invoice' %}success{% else %}info{% endif %}">
                                            {{ attachment.attachment_type }}
                                        </span>
                                    </td>
                                    <td>{{ "{:,.0f}".format(attachment.file_size / 1024) }} KB</td>
                                    <td>{{ attachment.uploader.name if attachment.uploader else '-' }}</td>
                                    <td>{{ attachment.uploaded_at.strftime('%d %b %Y, %I:%M %p') }}</td>
                                    <td>
                                        {% if attachment.is_approved %}
                                            <span class="badge bg-success">Approved</span>
                                        {% elif attachment.approved_at %}
                                            <span class="badge bg-warning">Pending</span>
                                        {% else %}
                                            <span class="badge bg-secondary">Pending</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <a href="{{ url_for('download_attachment', attachment_id=attachment.id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-download"></i>
                                            </a>
                                            {% if not attachment.is_approved %}
                                                <button type="button" class="btn btn-sm btn-outline-success" onclick="approveAttachment({{ attachment.id }})">
                                                    <i class="bi bi-check-circle"></i>
                                                </button>
                                                <button type="button" class="btn btn-sm btn-outline-danger" onclick="rejectAttachment({{ attachment.id }})">
                                                    <i class="bi bi-x-circle"></i>
                                                </button>
                                            {% endif %}
                                        </div>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function approveAttachment(attachmentId) {
    if (confirm('Are you sure you want to approve this attachment?')) {
        // Submit approval form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/gr/attachment/${attachmentId}/approve`;
        form.innerHTML = '<input type="hidden" name="rejection_reason" value="">';
        document.body.appendChild(form);
        form.submit();
    }
}

function rejectAttachment(attachmentId) {
    const reason = prompt('Please provide rejection reason:');
    if (reason) {
        // Submit rejection form
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/gr/attachment/${attachmentId}/reject`;
        form.innerHTML = `<input type="hidden" name="rejection_reason" value="${reason}">`;
        document.body.appendChild(form);
        form.submit();
    }
}
</script>
{% endblock %}
```

#### 2. Upload Attachment Template
```html
<!-- templates/gr/upload_attachment.html -->
{% extends 'base.html' %}

{% block title %}Upload GR Attachment{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-upload"></i> Upload Attachment</h5>
                </div>
                <div class="card-body">
                    <form method="POST" enctype="multipart/form-data">
                        <input type="hidden" name="attachment_type" value="document">
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Select File</label>
                                <input type="file" class="form-control" name="file" required accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" name="description" rows="3" placeholder="Optional description"></textarea>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-12">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-upload"></i> Upload Attachment
                                </button>
                                <a href="{{ url_for('gr_attachments', gr_id=gr.id) }}" class="btn btn-secondary">
                                    <i class="bi bi-arrow-left"></i> Back to Attachments
                                </a>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Database Migration Script
```python
# create_gr_attachment_tables.py
import sys
import os
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db, GRAttachment, DocumentType
from webapp import app

def create_tables():
    """Create GR attachment tables"""
    with app.app_context():
        try:
            # Create upload directory
            upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'gr_attachments')
            os.makedirs(upload_dir, exist_ok=True)
            
            db.create_all()
            print("SUCCESS: GR attachment tables created!")
            print("   - gr_attachments")
            print("   - document_types")
            print(f"   - Upload directory: {upload_dir}")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False

def setup_default_document_types():
    """Setup default document types"""
    default_types = [
        {'name': 'Purchase Order', 'description': 'Customer purchase order document'},
        {'name': 'Invoice', 'description': 'Supplier invoice document'},
        {'name': 'Delivery Challan', 'description': 'Delivery challan document'},
        {'name': 'Proof of Delivery', 'description': 'Proof of delivery document'},
        {'name': 'Insurance Certificate', 'description': 'Insurance certificate document'},
        {'name': 'Vehicle Registration', 'description': 'Vehicle registration document'},
        {'name': 'Other', 'description': 'Other supporting document'}
    ]
    
    with app.app_context():
        for doc_type in default_types:
            existing = DocumentType.query.filter_by(name=doc_type['name']).first()
            if not existing:
                new_type = DocumentType(
                    name=doc_type['name'],
                    description=doc_type['description'],
                    is_required=doc_type['name'] in ['Purchase Order', 'Invoice']
                )
                db.session.add(new_type)
        
        db.session.commit()
        print("Default document types setup completed")

if __name__ == "__main__":
    success = create_tables()
    if success:
        setup_default_document_types()
    sys.exit(0 if success else 1)
```

### Integration Points
- Extend existing TransportBill model with attachments relationship
- Add attachment management to GR forms
- Integrate with existing user/permission systems
- Connect with document type management
- Link with file storage and security systems

### Business Benefits
- **Document Management**: Complete attachment lifecycle
- **Compliance Support**: Document validation and approval
- **Audit Trail**: Complete attachment history
- **Digital Workflows**: Paperless document processing
- **Security**: File type validation and access control

### Success Metrics
- Attachment upload success rate
- Document approval turnaround time
- Compliance document coverage
- User adoption metrics
- Storage utilization efficiency

This implementation will transform the GR system from basic document handling to a comprehensive attachment management system that supports compliance, audit trails, and digital workflows.
