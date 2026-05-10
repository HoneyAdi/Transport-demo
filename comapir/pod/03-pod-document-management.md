# POD Document Management Implementation

## Overview
Implement comprehensive document management system for PODs with version control, expiry management, and secure storage.

## Database Schema
```sql
-- POD Documents
CREATE TABLE pod_documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pod_tracking_id INT NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT,
    version_number INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at DATETIME,
    tenant_id INT NOT NULL,
    FOREIGN KEY (pod_tracking_id) REFERENCES pod_tracking(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Document Types
INSERT INTO document_types (type_code, type_name) VALUES
('signed_pod', 'Signed POD'),
('delivery_challan', 'Delivery Challan'),
('unloading_report', 'Unloading Report'),
('damage_photos', 'Damage Photos'),
('identity_proof', 'Identity Proof'),
('other', 'Other Documents');
```

## Backend Implementation
```python
class PODDocument(db.Model):
    __tablename__ = "pod_documents"
    id = db.Column(db.Integer, primary_key=True)
    pod_tracking_id = db.Column(db.Integer, db.ForeignKey('pod_tracking.id'))
    document_type = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    version_number = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))

@app.route('/pod/documents/upload/<int:tracking_id>', methods=['POST'])
def upload_pod_document(tracking_id):
    file = request.files['document']
    document_type = request.form.get('document_type')
    
    # Save file with secure naming
    filename = secure_filename(f"pod_{tracking_id}_{int(time.time())}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pod_docs', filename)
    file.save(file_path)
    
    # Create document record
    doc = PODDocument(
        pod_tracking_id=tracking_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        uploaded_by=current_user.id
    )
    db.session.add(doc)
    db.session.commit()
    
    return jsonify({'success': True, 'document_id': doc.id})

@app.route('/pod/documents/<int:doc_id>/download')
def download_pod_document(doc_id):
    doc = PODDocument.query.get_or_404(doc_id)
    return send_file(doc.file_path, as_attachment=True, download_name=doc.file_name)
```

## Key Features
- **Multi-document Support**: Multiple document types per POD
- **Version Control**: Track document versions and amendments
- **Document Expiry**: Automatic expiry management
- **Secure Storage**: Encrypted file storage with access control
- **Document Preview**: In-app document viewing
- **Bulk Operations**: Mass upload and download
- **Search & Filter**: Advanced document search capabilities

## Document Types
- Signed POD copies
- Delivery challans
- Unloading reports
- Damage photos
- Identity proofs
- Other supporting documents

## Implementation Steps
1. Create document management tables
2. Implement file upload/download APIs
3. Add document preview functionality
4. Create version control system
5. Implement expiry management
6. Add document search and filters
7. Create document management UI
8. Test file security and access control

## Benefits
- Centralized document storage
- Version tracking for amendments
- Secure document access
- Automated expiry management
- Easy document retrieval
- Compliance with document retention policies
