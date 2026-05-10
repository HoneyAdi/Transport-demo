# Advanced Customer Analytics Implementation Plan

This plan implements comprehensive customer analytics and business intelligence for data-driven decision making and customer relationship optimization.

## Business Value

Advanced customer analytics enables:
- **Performance Insights**: Track customer profitability, revenue contribution, and growth trends
- **Risk Assessment**: Identify at-risk customers and churn indicators
- **Lifetime Value Analysis**: Calculate CLV and segment customers by value
- **Satisfaction Monitoring**: Track NPS scores and customer satisfaction trends
- **Business Intelligence**: Provide actionable insights for strategic decisions

## Implementation Overview

### Database Schema Changes

#### 1. Extend Existing Models
Add analytics fields to existing models:

```python
# Add to Vendor model
customer_lifetime_value = db.Column(db.Numeric(15, 2), default=0)
customer_satisfaction_score = db.Column(db.Numeric(5, 2), default=0)
customer_churn_risk = db.Column(db.String(20), default='low')  # low, medium, high
last_analytics_calculated = db.Column(db.DateTime)
```

#### 2. Create CustomerAnalytics Model
```python
class CustomerAnalytics(db.Model):
    """Customer performance analytics cache and calculation results"""
    __tablename__ = "customer_analytics"
    __table_args__ = (
        UniqueConstraint("vendor_id", "period_start", "period_end", name="uq_customer_analytics_period"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False, index=True)
    
    # Period Definition
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), default='monthly')  # daily, weekly, monthly, quarterly, yearly
    
    # Performance Metrics
    total_revenue = db.Column(db.Numeric(15, 2), default=0)
    total_bills = db.Column(db.Integer, default=0)
    total_deliveries = db.Column(db.Integer, default=0)
    on_time_deliveries = db.Column(db.Integer, default=0)
    delayed_deliveries = db.Column(db.Integer, default=0)
    
    # Financial Metrics
    avg_order_value = db.Column(db.Numeric(12, 2), default=0)
    total_payments = db.Column(db.Numeric(15, 2), default=0)
    outstanding_balance = db.Column(db.Numeric(15, 2), default=0)
    
    # Satisfaction Metrics
    customer_satisfaction_score = db.Column(db.Numeric(5, 2), default=0)
    total_feedback_entries = db.Column(db.Integer, default=0)
    positive_feedback_percentage = db.Column(db.Numeric(5, 2), default=0)
    
    # Calculated Fields
    on_time_delivery_rate = db.Column(db.Numeric(5, 2), default=0)  # percentage
    customer_lifetime_value = db.Column(db.Numeric(15, 2), default=0)
    churn_probability = db.Column(db.Numeric(5, 2), default=0)  # percentage
    growth_rate = db.Column(db.Numeric(5, 2), default=0)  # percentage
    
    # Timestamps
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = db.relationship("Vendor", backref="analytics")
    tenant = db.relationship("Tenant")
```

### Backend Implementation

#### 1. Analytics Calculation Functions
```python
def calculate_customer_analytics(vendor_id, period_start, period_end):
    """Calculate comprehensive analytics for a customer"""
    from sqlalchemy import func
    
    # Get transport bills for the period
    bills = TransportBill.query.filter(
        TransportBill.vendor_id == vendor_id,
        TransportBill.date.between(period_start, period_end)
    ).all()
    
    # Get payments for the period
    payments = CustomerTransaction.query.filter(
        CustomerTransaction.vendor_id == vendor_id,
        CustomerTransaction.transaction_type == 'payment',
        CustomerTransaction.transaction_date.between(period_start, period_end)
    ).all()
    
    # Get deliveries from dispatch trips
    deliveries = DispatchTrip.query.filter(
        DispatchTrip.vendor_id == vendor_id,
        DispatchTrip.trip_date.between(period_start, period_end)
    ).all()
    
    # Get feedback for the period
    feedback = CustomerFeedback.query.filter(
        CustomerFeedback.vendor_id == vendor_id,
        CustomerFeedback.feedback_date.between(period_start, period_end)
    ).all()
    
    # Calculate metrics
    total_revenue = sum(float(b.rate) for b in bills)
    total_bills = len(bills)
    total_deliveries = len(deliveries)
    on_time_deliveries = len([d for d in deliveries if d.status == 'completed'])
    total_payments = sum(float(t.amount) for t in payments)
    outstanding_balance = total_revenue - total_payments
    
    # Calculate satisfaction metrics
    total_feedback = len(feedback)
    positive_feedback = len([f for f in feedback if f.rating and f.rating >= 4])
    satisfaction_score = (sum(f.rating or 0 for f in feedback) / total_feedback) if total_feedback > 0 else 0
    positive_feedback_pct = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
    
    # Calculate delivery performance
    on_time_rate = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    avg_order_value = total_revenue / total_bills if total_bills > 0 else 0
    
    # Calculate lifetime value (simplified)
    lifetime_value = total_revenue * 0.2  # 20% of revenue as estimated lifetime value
    
    # Calculate churn risk (simplified)
    churn_probability = 5.0  # Default low risk
    if on_time_rate < 80:
        churn_probability = 20.0  # High risk
    elif on_time_rate < 90:
        churn_probability = 10.0  # Medium risk
    
    # Calculate growth rate (month-over-month)
    previous_period_revenue = get_previous_period_revenue(vendor_id, period_start)
    growth_rate = ((total_revenue - previous_period_revenue) / previous_period_revenue * 100) if previous_period_revenue > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_bills': total_bills,
        'total_deliveries': total_deliveries,
        'on_time_deliveries': on_time_deliveries,
        'on_time_delivery_rate': on_time_rate,
        'avg_order_value': avg_order_value,
        'total_payments': total_payments,
        'outstanding_balance': outstanding_balance,
        'satisfaction_score': satisfaction_score,
        'total_feedback': total_feedback,
        'positive_feedback_percentage': positive_feedback_pct,
        'customer_lifetime_value': lifetime_value,
        'churn_probability': churn_probability,
        'growth_rate': growth_rate
    }

def get_previous_period_revenue(vendor_id, current_period_start):
    """Get revenue from previous period for growth calculation"""
    previous_period_end = current_period_start - timedelta(days=30)
    revenue = db.session.query(func.sum(TransportBill.rate)).filter(
        TransportBill.vendor_id == vendor_id,
        TransportBill.date.between(previous_period_end, current_period_start)
    ).scalar() or 0
    return revenue
```

#### 2. Analytics Routes
```python
@app.route("/customers/analytics/dashboard")
@permission_required("vendors", "view")
def customer_analytics_dashboard():
    """Customer analytics dashboard with KPIs and insights"""
    customers = scoped_query(Vendor).all()
    
    # Calculate overall metrics
    total_customers = len(customers)
    total_revenue = sum(c.credit_info.current_outstanding or 0 for c in customers)
    high_value_customers = len([c for c in customers if c.customer_tier in ['gold', 'platinum']])
    
    return render_template(
        "customers/analytics_dashboard.html",
        customers=customers,
        total_customers=total_customers,
        total_revenue=total_revenue,
        high_value_customers=high_value_customers
    )

@app.route("/customers/<int:id>/analytics")
@permission_required("vendors", "view")
def customer_analytics_detail():
    """Detailed analytics for individual customer"""
    customer = get_scoped_record(Vendor, id)
    
    # Get period filters
    period_type = request.args.get('period', 'monthly')
    period_end = date.today()
    
    if period_type == 'monthly':
        period_start = period_end - timedelta(days=30)
    elif period_type == 'quarterly':
        period_start = period_end - timedelta(days=90)
    elif period_type == 'yearly':
        period_start = period_end - timedelta(days=365)
    else:
        period_start = period_end - timedelta(days=30)
    
    # Calculate analytics
    analytics = calculate_customer_analytics(id, period_start, period_end)
    
    # Get historical data for trends
    historical_data = CustomerAnalytics.query.filter_by(vendor_id=id).order_by(
        CustomerAnalytics.period_start.desc()
    ).limit(12).all()  # Last 12 periods
    
    return render_template(
        "customers/analytics_detail.html",
        customer=customer,
        analytics=analytics,
        historical_data=historical_data,
        period_type=period_type
    )

@app.route("/customers/analytics/performance")
@permission_required("vendors", "view")
def customer_performance_report():
    """Customer performance comparison report"""
    customers = scoped_query(Vendor).all()
    customer_data = []
    
    for customer in customers:
        # Get latest analytics
        latest_analytics = CustomerAnalytics.query.filter_by(vendor_id=customer.id).order_by(
            CustomerAnalytics.period_start.desc()
        ).first()
        
        if latest_analytics:
            customer_data.append({
                'customer': customer,
                'analytics': latest_analytics,
                'rank': 0  # Will be calculated
            })
    
    # Sort by revenue
    customer_data.sort(key=lambda x: x['analytics'].total_revenue, reverse=True)
    
    # Assign ranks
    for i, data in enumerate(customer_data, 1):
        data['rank'] = i
    
    return render_template(
        "customers/performance_report.html",
        customer_data=customer_data
    )
```

#### 3. Automated Analytics Updates
```python
def update_customer_analytics():
    """Automated task to update customer analytics"""
    from datetime import date, timedelta
    
    # Get all active customers
    customers = Vendor.query.filter_by(status='active').all()
    
    for customer in customers:
        # Calculate analytics for last month
        period_end = date.today()
        period_start = period_end - timedelta(days=30)
        
        analytics_data = calculate_customer_analytics(customer.id, period_start, period_end)
        
        # Check if analytics already exist for this period
        existing = CustomerAnalytics.query.filter_by(
            vendor_id=customer.id,
            period_start=period_start,
            period_end=period_end
        ).first()
        
        if not existing:
            analytics = CustomerAnalytics(
                tenant_id=customer.tenant_id,
                vendor_id=customer.id,
                period_start=period_start,
                period_end=period_end,
                period_type='monthly',
                **analytics_data
            )
            db.session.add(analytics)
    
    db.session.commit()
    print(f"Updated analytics for {len(customers)} customers")
```

### Frontend Implementation

#### 1. Analytics Dashboard Template
**File**: `templates/customers/analytics_dashboard.html`

Key components:
- Overall KPI cards (total customers, revenue, high-value customers)
- Customer performance table with rankings
- Revenue distribution charts
- Customer segment breakdown
- Export functionality

#### 2. Customer Analytics Detail Template
**File**: `templates/customers/analytics_detail.html`

Key components:
- Customer profile with key metrics
- Period-based analytics with filters
- Historical trend charts
- Performance comparisons
- Satisfaction metrics dashboard

#### 3. Performance Report Template
**File**: `templates/customers/performance_report.html`

Key components:
- Customer ranking table
- Revenue contribution analysis
- Performance metrics comparison
- Growth rate tracking
- Export to Excel functionality

### Integration Points

#### 1. Existing System Integration
- Link with Vendor model for customer data
- Connect with CustomerCredit for financial metrics
- Integrate with CustomerFeedback for satisfaction scores
- Use CustomerCommunication for interaction history

#### 2. Data Sources
- TransportBill for revenue and order data
- CustomerTransaction for payment history
- CustomerFeedback for satisfaction metrics
- DispatchTrip for delivery performance
- CustomerCredit for financial health

#### 3. Workflow Integration
- Trigger analytics updates on new bills/payments
- Automated monthly calculation tasks
- Integration with customer classification system
- Link with communication hub for follow-up actions

### Success Metrics

#### Analytics Coverage
- 100% of customers with analytics data
- Complete performance metrics tracking
- Historical trend analysis (12+ months)
- Real-time KPI calculations

#### Business Intelligence
- Customer lifetime value calculation
- Churn prediction indicators
- Growth rate analysis
- Segment profitability comparison

#### Technical Performance
- Analytics queries < 2 seconds
- Dashboard load time < 3 seconds
- Report generation < 5 seconds
- Data export < 10 seconds

### Testing Strategy

#### 1. Unit Tests
- Analytics calculation accuracy
- Performance metric validation
- Data aggregation tests
- Edge case handling

#### 2. Integration Tests
- Customer data integration
- Payment system connectivity
- Feedback system linkage
- Communication hub integration

#### 3. Performance Tests
- Large dataset handling (1000+ customers)
- Complex query optimization
- Concurrent user access
- Export functionality stress testing

### Security Considerations

#### 1. Access Control
- Analytics requires 'vendors' view permission
- Customer-specific data isolation
- Audit trail for analytics calculations
- Role-based access to sensitive metrics

#### 2. Data Privacy
- Customer data anonymization in reports
- Secure data export functionality
- Compliance with data protection regulations
- Sensitive metric access controls

#### 3. Performance Security
- Query optimization for large datasets
- Cached analytics calculations
- Rate limiting for report generation
- Secure API endpoints for analytics data

This implementation provides comprehensive customer analytics that enables data-driven decision making, customer relationship optimization, and business intelligence capabilities for the transport management system.
