# Customer Classification System Implementation Plan

This plan implements customer categorization and tier management to segment customers for better service and risk management in the transport business.

## Business Value

Customer classification enables:
- **Risk Management**: Identify high-risk vs low-risk customers
- **Service Differentiation**: Provide premium service to VIP customers
- **Credit Management**: Set appropriate credit limits by category
- **Marketing Targeting**: Focus on profitable customer segments
- **Performance Analysis**: Compare performance across customer tiers

## Implementation Overview

### Database Schema Changes

#### 1. Extend Vendor Model
Add classification fields to existing Vendor model:

```python
# Add to Vendor model (in models.py)
customer_type = db.Column(db.String(50), default='regular')  # regular, premium, vip, one_time
customer_tier = db.Column(db.String(20), default='bronze')   # bronze, silver, gold, platinum
customer_segment = db.Column(db.String(100))  # manufacturing, logistics, retail, etc.
customer_lifecycle_status = db.Column(db.String(20), default='active')  # active, inactive, blacklisted, dormant
classification_notes = db.Column(db.Text)
classification_date = db.Column(db.Date, default=date.today)
classified_by = db.Column(db.Integer, db.ForeignKey("users.id"))
```

#### 2. Create CustomerCategory Model
```python
class CustomerCategory(db.Model):
    """Customer category definitions for classification"""
    __tablename__ = "customer_categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "category_code", name="uq_customer_category_tenant"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    
    # Credit Settings
    min_credit_limit = db.Column(db.Numeric(12, 2), default=0)
    max_credit_limit = db.Column(db.Numeric(12, 2), default=0)
    default_payment_terms = db.Column(db.String(50), default='Net 30')
    
    # Service Level Settings
    service_priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    sla_hours = db.Column(db.Integer, default=48)  # Service Level Agreement hours
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship("Tenant")
```

### Backend Implementation

#### 1. Classification Management Routes
```python
@app.route("/customers/classification")
@permission_required("vendors", "view")
def customer_classification():
    """Customer classification management interface"""
    categories = CustomerCategory.query.filter_by(
        tenant_id=get_current_tenant_id(),
        is_active=True
    ).order_by(CustomerCategory.sort_order).all()
    
    return render_template(
        "customers/classification.html",
        categories=categories
    )

@app.route("/customers/classification/create", methods=["POST"])
@permission_required("vendors", "edit")
def create_customer_category():
    """Create new customer category"""
    category = CustomerCategory(
        tenant_id=get_current_tenant_id(),
        category_name=request.form.get('category_name'),
        category_code=request.form.get('category_code'),
        description=request.form.get('description'),
        min_credit_limit=float(request.form.get('min_credit_limit', 0)),
        max_credit_limit=float(request.form.get('max_credit_limit', 0)),
        default_payment_terms=request.form.get('default_payment_terms', 'Net 30'),
        service_priority=request.form.get('service_priority', 'medium'),
        sla_hours=int(request.form.get('sla_hours', 48)),
        sort_order=int(request.form.get('sort_order', 0))
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash('Customer category created successfully!', 'success')
    return redirect(url_for('customer_classification'))

@app.route("/customers/<int:id>/classify", methods=["POST"])
@permission_required("vendors", "edit")
def classify_customer(id):
    """Classify individual customer"""
    customer = get_scoped_record(Vendor, id)
    
    # Update classification
    customer.customer_type = request.form.get('customer_type', 'regular')
    customer.customer_tier = request.form.get('customer_tier', 'bronze')
    customer.customer_segment = request.form.get('customer_segment')
    customer.customer_lifecycle_status = request.form.get('lifecycle_status', 'active')
    customer.classification_notes = request.form.get('classification_notes')
    customer.classification_date = date.today()
    customer.classified_by = session['user_id']
    
    # Auto-adjust credit limit based on category
    category = CustomerCategory.query.filter_by(
        category_code=customer.customer_tier
    ).first()
    
    if category and not customer.credit_info:
        customer.credit_info.credit_limit = category.max_credit_limit
        db.session.add(customer.credit_info)
    
    db.session.commit()
    
    flash('Customer classified successfully!', 'success')
    return redirect(url_for('edit_vendor', id=id))
```

#### 2. Classification Helper Functions
```python
def get_customer_classification_badge(customer_type, customer_tier):
    """Generate appropriate badge for customer classification"""
    type_colors = {
        'regular': 'primary',
        'premium': 'info',
        'vip': 'warning',
        'one_time': 'secondary'
    }
    
    tier_colors = {
        'bronze': 'secondary',
        'silver': 'light',
        'gold': 'warning',
        'platinum': 'success'
    }
    
    return {
        'type_badge': f'<span class="badge bg-{type_colors.get(customer_type, "secondary")}">{customer_type.title()}</span>',
        'tier_badge': f'<span class="badge bg-{tier_colors.get(customer_tier, "secondary")}">{customer_tier.title()}</span>'
    }

def auto_classify_customer(customer):
    """Automatically classify customer based on transaction history"""
    if not customer.transactions:
        return 'one_time'
    
    # Count transactions in last 12 months
    recent_transactions = len([t for t in customer.transactions 
                             if t.transaction_date >= (date.today() - timedelta(days=365))])
    
    if recent_transactions > 50:
        return 'vip'
    elif recent_transactions > 20:
        return 'premium'
    elif recent_transactions > 5:
        return 'regular'
    else:
        return 'one_time'
```

### Frontend Implementation

#### 1. Classification Management Interface
**File**: `templates/customers/classification.html`

Key components:
- Category list with CRUD operations
- Tier/Type management
- Service level settings
- Drag-and-drop sorting
- Bulk classification tools

#### 2. Customer Classification Widget
**Add to**: `templates/vendors/form.html`

Features:
- Classification dropdowns with auto-suggestions
- Tier-based credit limit recommendations
- Lifecycle status management
- Classification history tracking

#### 3. Customer List Enhancements
**Update**: `templates/vendors/list.html`

Add classification columns:
- Customer type badges
- Tier indicators
- Segment information
- Classification-based filtering

### Integration Points

#### 1. Credit Management Integration
- Auto-set credit limits based on tier
- Enforce tier-specific payment terms
- Risk-based credit holds

#### 2. Reporting Integration
- Classification-based performance reports
- Tier-wise revenue analysis
- Segment profitability comparison

#### 3. Workflow Integration
- Classification triggers on customer creation
- Auto-classification based on transaction patterns
- Tier upgrade/downgrade workflows

### Data Migration

#### 1. Initial Classification
```python
def migrate_existing_customers():
    """Classify existing customers based on transaction history"""
    customers = Vendor.query.filter_by(tenant_id=get_current_tenant_id()).all()
    
    for customer in customers:
        customer.customer_type = auto_classify_customer(customer)
        customer.customer_tier = 'bronze'  # Default tier
        customer.customer_lifecycle_status = 'active' if customer.status == 'active' else 'inactive'
        customer.classification_date = date.today()
        customer.classified_by = 1  # System user ID
    
    db.session.commit()
```

#### 2. Category Setup
```python
def setup_default_categories():
    """Create default customer categories"""
    default_categories = [
        {
            'category_name': 'Regular Customers',
            'category_code': 'regular',
            'description': 'Standard transport customers with regular service requirements',
            'min_credit_limit': 50000,
            'max_credit_limit': 200000,
            'default_payment_terms': 'Net 30',
            'service_priority': 'medium',
            'sort_order': 1
        },
        {
            'category_name': 'Premium Customers',
            'category_code': 'premium',
            'description': 'High-value customers requiring priority service',
            'min_credit_limit': 100000,
            'max_credit_limit': 1000000,
            'default_payment_terms': 'Net 15',
            'service_priority': 'high',
            'sort_order': 2
        },
        {
            'category_name': 'VIP Customers',
            'category_code': 'vip',
            'description': 'Top-tier customers with white-glove service',
            'min_credit_limit': 500000,
            'max_credit_limit': 5000000,
            'default_payment_terms': 'Net 15',
            'service_priority': 'urgent',
            'sort_order': 3
        }
    ]
    
    for cat_data in default_categories:
        category = CustomerCategory(
            tenant_id=get_current_tenant_id(),
            **cat_data
        )
        db.session.add(category)
    
    db.session.commit()
```

### Success Metrics

#### Classification Coverage
- 100% of customers classified
- All categories properly configured
- Tier distribution documented

#### Business Impact
- Improved customer service targeting
- Better risk management
- Enhanced credit control
- Performance insights by segment

#### Technical Metrics
- Classification query performance < 100ms
- Bulk classification operations < 5 seconds
- Zero classification errors

### Testing Strategy

#### 1. Unit Tests
- Model validation tests
- Classification logic tests
- Credit limit assignment tests

#### 2. Integration Tests
- Credit system integration
- Reporting compatibility
- Permission system integration

#### 3. User Acceptance Tests
- Classification workflow testing
- Bulk operations testing
- Performance validation

### Security Considerations

#### 1. Access Control
- Classification requires 'vendors' edit permission
- Tier-based credit limit restrictions
- Audit trail for all classification changes

#### 2. Data Validation
- Valid category/tier combinations
- Credit limit range validation
- Required field validation

#### 3. Compliance
- Classification reason logging
- Change history tracking
- User attribution for changes

This implementation provides a robust customer classification system that integrates seamlessly with existing credit management and enables data-driven customer relationship management.
