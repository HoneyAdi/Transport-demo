# POD Dashboard & Status Tracking Implementation

## Overview
Implement comprehensive POD dashboard with real-time status tracking, aging reports, and performance metrics.

## Database Schema
```sql
-- POD Status Master
CREATE TABLE pod_status (
    id INT PRIMARY KEY AUTO_INCREMENT,
    status_code VARCHAR(20) UNIQUE NOT NULL,
    status_name VARCHAR(50) NOT NULL,
    description TEXT,
    color_code VARCHAR(10),
    is_default BOOLEAN DEFAULT FALSE,
    tenant_id INT NOT NULL
);

-- POD Tracking
CREATE TABLE pod_tracking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transport_bill_id INT NOT NULL,
    status_code VARCHAR(20) NOT NULL,
    timestamp DATETIME NOT NULL,
    updated_by INT,
    remarks TEXT,
    location VARCHAR(200),
    tenant_id INT NOT NULL,
    FOREIGN KEY (transport_bill_id) REFERENCES transport_bills(id),
    FOREIGN KEY (status_code) REFERENCES pod_status(status_code)
);
```

## Backend Implementation
```python
# Models
class PodStatus(db.Model):
    __tablename__ = "pod_status"
    id = db.Column(db.Integer, primary_key=True)
    status_code = db.Column(db.String(20), unique=True, nullable=False)
    status_name = db.Column(db.String(50), nullable=False)
    color_code = db.Column(db.String(10))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))

class PodTracking(db.Model):
    __tablename__ = "pod_tracking"
    id = db.Column(db.Integer, primary_key=True)
    transport_bill_id = db.Column(db.Integer, db.ForeignKey('transport_bills.id'))
    status_code = db.Column(db.String(20), db.ForeignKey('pod_status.status_code'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    remarks = db.Column(db.Text)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))

# Key Routes
@app.route('/pod/dashboard')
def pod_dashboard():
    # KPI cards, status counts, aging analysis
    status_counts = db.session.query(PodStatus, func.count(PodTracking.id))\
        .join(PodTracking).group_by(PodStatus.id).all()
    return render_template('pod/dashboard.html', status_counts=status_counts)

@app.route('/pod/update_status/<int:bill_id>', methods=['POST'])
def update_pod_status(bill_id):
    # Update POD status with tracking
    tracking = PodTracking(
        transport_bill_id=bill_id,
        status_code=request.form.get('status'),
        updated_by=current_user.id,
        remarks=request.form.get('remarks')
    )
    db.session.add(tracking)
    db.session.commit()
    return redirect(url_for('pod_list'))
```

## Frontend Features
- Dashboard with KPI cards and charts
- POD aging bucket analysis (0-2, 3-7, 8-15, 15+ days)
- Status-wise POD listing with filters
- Real-time status updates
- Performance metrics dashboard

## Implementation Steps
1. Create database tables via migration
2. Add POD models to models.py
3. Implement dashboard and list routes
4. Create responsive dashboard templates
5. Add Chart.js for visualizations
6. Test status tracking functionality

## Benefits
- Real-time POD visibility
- Aging analysis for overdue PODs
- Performance metrics and KPIs
- Streamlined POD workflow
- Better operational insights
