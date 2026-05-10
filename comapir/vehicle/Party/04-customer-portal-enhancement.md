# Customer Portal Enhancement Implementation Plan

This plan implements a modern, mobile-friendly customer portal with self-service capabilities and enhanced user experience.

## Business Value

Enhanced customer portal enables:
- **Self-Service**: Customers manage their own information and requests
- **Real-Time Tracking**: Live order and delivery status updates
- **Mobile Accessibility**: Responsive design for all devices
- **Reduced Support Load**: Automated workflows reduce manual interventions
- **Customer Empowerment**: Direct access to account management and data

## Implementation Overview

### Database Schema Changes

#### 1. Extend CustomerPortalAccount Model
Add portal enhancement fields:

```python
# Add to CustomerPortalAccount model
last_login_ip = db.Column(db.String(45))
login_count = db.Column(db.Integer, default=0)
failed_login_attempts = db.Column(db.Integer, default=0)
account_locked_until = db.Column(db.DateTime)
password_changed_at = db.Column(db.DateTime)
two_factor_enabled = db.Column(db.Boolean, default=False)
two_factor_secret = db.Column(db.String(32))
notification_preferences = db.Column(db.Text)  # JSON for notification settings
language_preference = db.Column(db.String(10), default='en')
timezone_preference = db.Column(db.String(50), default='UTC')
portal_theme = db.Column(db.String(20), default='light')
```

#### 2. Create CustomerNotification Model
```python
class CustomerNotification(db.Model):
    """Customer notifications and preferences"""
    __tablename__ = "customer_notifications"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Notification Details
    notification_type = db.Column(db.String(50))  # payment_reminder, delivery_update, document_upload, general
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_email_sent = db.Column(db.Boolean, default=False)
    is_sms_sent = db.Column(db.Boolean, default=False)
    is_push_sent = db.Column(db.Boolean, default=True)
    
    # Preferences
    email_enabled = db.Column(db.Boolean, default=True)
    sms_enabled = db.Column(db.Boolean, default=False)
    push_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="notifications")
    tenant = db.relationship("Tenant")
```

#### 3. Create CustomerDocument Model
```python
class CustomerDocument(db.Model):
    """Customer uploaded documents"""
    __tablename__ = "customer_documents"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Document Details
    document_type = db.Column(db.String(50))  # invoice, receipt, contract, identity_proof, other
    document_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="documents")
    uploader = db.relationship("User", foreign_keys=[uploaded_by])
    approver = db.relationship("User", foreign_keys=[approved_by])
    tenant = db.relationship("Tenant")
```

### Backend Implementation

#### 1. Enhanced Portal Routes
```python
@app.route("/customer-portal/dashboard")
def enhanced_customer_dashboard():
    """Enhanced customer dashboard with modern UI"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        flash('Please login to access your dashboard', 'error')
        return redirect(url_for('customer_login'))
    
    # Get customer data
    customer = account.vendor
    recent_bills = TransportBill.query.filter_by(
        party_information=str(customer.id)
    ).order_by(TransportBill.date.desc()).limit(10).all()
    
    # Get notifications
    notifications = CustomerNotification.query.filter_by(
        vendor_id=customer.id,
        is_read=False
    ).order_by(CustomerNotification.created_at.desc()).limit(5).all()
    
    # Get unread count
    unread_count = CustomerNotification.query.filter_by(
        vendor_id=customer.id,
        is_read=False
    ).count()
    
    return render_template(
        "customer_portal/enhanced_dashboard.html",
        account=account,
        customer=customer,
        recent_bills=recent_bills,
        notifications=notifications,
        unread_count=unread_count
    )

@app.route("/customer-portal/orders")
def customer_orders():
    """Customer order tracking interface"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return redirect(url_for('customer_login'))
    
    customer = account.vendor
    
    # Get filters
    status_filter = request.args.get('status', 'all')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    # Build query
    query = TransportBill.query.filter_by(party_information=str(customer.id))
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if date_from:
        try:
            query = query.filter(TransportBill.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except:
            pass
    
    if date_to:
        try:
            query = query.filter(TransportBill.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except:
            pass
    
    orders = query.order_by(TransportBill.date.desc()).all()
    
    return render_template(
        "customer_portal/orders.html",
        account=account,
        customer=customer,
        orders=orders,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to
    )

@app.route("/customer-portal/documents")
def customer_documents():
    """Customer document management interface"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return redirect(url_for('customer_login'))
    
    customer = account.vendor
    
    # Get documents
    documents = CustomerDocument.query.filter_by(vendor_id=customer.id).order_by(
        CustomerDocument.uploaded_at.desc()
    ).all()
    
    return render_template(
        "customer_portal/documents.html",
        account=account,
        customer=customer,
        documents=documents
    )

@app.route("/customer-portal/upload-document", methods=["POST"])
def upload_customer_document():
    """Handle customer document uploads"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'customer_documents', str(account.vendor_id))
        os.makedirs(file_path, exist_ok=True)
        
        # Save file
        full_path = os.path.join(file_path, filename)
        file.save(full_path)
        
        # Create document record
        document = CustomerDocument(
            tenant_id=account.tenant_id,
            vendor_id=account.vendor_id,
            document_type=request.form.get('document_type'),
            document_name=request.form.get('document_name', filename),
            file_path=os.path.join('customer_documents', str(account.vendor_id), filename),
            file_size=os.path.getsize(full_path),
            mime_type=file.mimetype,
            uploaded_by=account.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({'success': True, 'document_id': document.id})
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route("/customer-portal/profile")
def customer_profile():
    """Customer profile management interface"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return redirect(url_for('customer_login'))
    
    customer = account.vendor
    
    if request.method == 'POST':
        # Update profile information
        customer.primary_contact_name = request.form.get('primary_contact_name')
        customer.primary_contact_phone = request.form.get('primary_contact_phone')
        customer.primary_contact_email = request.form.get('primary_contact_email')
        
        # Update account preferences
        account.language_preference = request.form.get('language_preference', 'en')
        account.timezone_preference = request.form.get('timezone_preference', 'UTC')
        account.portal_theme = request.form.get('portal_theme', 'light')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer_profile'))
    
    return render_template(
        "customer_portal/profile.html",
        account=account,
        customer=customer
    )

@app.route("/customer-portal/notifications")
def customer_notifications():
    """Customer notification center"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return redirect(url_for('customer_login'))
    
    customer = account.vendor
    
    # Get notifications with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = CustomerNotification.query.filter_by(vendor_id=customer.id).order_by(
        CustomerNotification.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template(
        "customer_portal/notifications.html",
        account=account,
        customer=customer,
        notifications=notifications
    )

@app.route("/customer-portal/mark-notification-read/<int:notification_id>", methods=["POST"])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    account = db.session.get(CustomerPortalAccount, session.get("customer_id"))
    if not account or not account.is_active:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notification = CustomerNotification.query.filter_by(
        id=notification_id,
        vendor_id=account.vendor_id
    ).first()
    
    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
    
    return jsonify({'error': 'Notification not found'}), 404
```

#### 2. Enhanced Authentication
```python
@app.route("/customer-portal/login", methods=["GET", "POST"])
def enhanced_customer_login():
    """Enhanced customer login with security features"""
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        two_factor_code = request.form.get('two_factor_code')
        
        account = CustomerPortalAccount.query.filter_by(
            email=email,
            tenant_id=get_current_tenant_id()
        ).first()
        
        if not account:
            flash('Invalid email or password', 'error')
            return redirect(url_for('customer_login'))
        
        # Check if account is locked
        if account.account_locked_until and account.account_locked_until > datetime.utcnow():
            flash('Account temporarily locked. Please try again later.', 'error')
            return redirect(url_for('customer_login'))
        
        # Check failed attempts
        if account.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            account.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
            account.failed_login_attempts = 0
            db.session.commit()
            
            flash('Account locked due to too many failed attempts. Try again in 30 minutes.', 'error')
            return redirect(url_for('customer_login'))
        
        # Verify password
        if check_password_hash(password, account.password_hash):
            # Check two-factor if enabled
            if account.two_factor_enabled and not two_factor_code:
                # Send two-factor code
                send_two_factor_code(account)
                flash('Two-factor authentication code sent to your email.', 'info')
                return render_template('customer_portal/two_factor.html', email=email)
            
            # Successful login
            account.last_login_at = datetime.utcnow()
            account.last_login_ip = request.remote_addr
            account.login_count += 1
            account.failed_login_attempts = 0
            account.account_locked_until = None
            db.session.commit()
            
            session['customer_id'] = account.id
            session['customer_email'] = account.email
            session['customer_name'] = account.full_name
            
            if remember_me:
                session.permanent = True
            
            flash('Login successful!', 'success')
            return redirect(url_for('enhanced_customer_dashboard'))
        else:
            # Failed login
            account.failed_login_attempts += 1
            db.session.commit()
            
            flash('Invalid email or password', 'error')
    
    return render_template('customer_portal/enhanced_login.html')

def send_two_factor_code(account):
    """Send two-factor authentication code"""
    import random
    import string
    
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    account.two_factor_secret = code
    account.two_factor_secret_expires = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    # Send email with code (implementation depends on email service)
    # send_email(account.email, "Two-Factor Authentication Code", f"Your code is: {code}")
```

### Frontend Implementation

#### 1. Enhanced Dashboard Template
**File**: `templates/customer_portal/enhanced_dashboard.html`

Key components:
- Modern responsive design with Bootstrap 5
- Real-time order status updates
- Notification center with unread count
- Quick action buttons
- Mobile-optimized layout
- Dark/light theme support

#### 2. Order Tracking Template
**File**: `templates/customer_portal/orders.html`

Key components:
- Advanced filtering and search
- Real-time status updates
- Order details modal
- Document download links
- Timeline view

#### 3. Document Management Template
**File**: `templates/customer_portal/documents.html`

Key components:
- Drag-and-drop file upload
- Document categorization
- Approval workflow
- Secure file download
- Mobile-friendly interface

#### 4. Profile Management Template
**File**: `templates/customer_portal/profile.html`

Key components:
- Account information editing
- Preference management
- Password change
- Two-factor setup
- Language/timezone selection

#### 5. Notification Center Template
**File**: `templates/customer_portal/notifications.html`

Key components:
- Paginated notification list
- Mark as read functionality
- Notification preferences
- Real-time updates
- Filter by type

### Integration Points

#### 1. Existing System Integration
- Connect with CustomerPortalAccount for authentication
- Link with Vendor model for customer data
- Integrate with TransportBill for order tracking
- Use CustomerNotification for alerts

#### 2. Security Integration
- Two-factor authentication
- Account lockout protection
- Secure file upload handling
- Session management
- CSRF protection

#### 3. Mobile Optimization
- Progressive Web App (PWA) support
- Responsive design for all screen sizes
- Touch-friendly interfaces
- Offline functionality
- Push notifications

### Success Metrics

#### Portal Usage
- Daily active users
- Session duration tracking
- Feature usage analytics
- Mobile vs desktop usage
- Self-service task completion

#### Customer Satisfaction
- Support ticket reduction
- User feedback scores
- Portal usability metrics
- Task completion rates
- Response time improvements

#### Technical Performance
- Page load time < 2 seconds
- Mobile responsiveness score
- Accessibility compliance
- Security audit results
- Uptime and availability

### Security Considerations

#### 1. Authentication Security
- Strong password requirements
- Two-factor authentication
- Account lockout protection
- Session timeout management
- Secure password reset

#### 2. Data Protection
- File upload validation
- Data encryption at rest
- Secure document storage
- Access logging and monitoring
- GDPR compliance

#### 3. API Security
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection
- Secure headers

This implementation provides a modern, secure, and mobile-friendly customer portal that enhances customer experience and reduces support overhead through self-service capabilities.
