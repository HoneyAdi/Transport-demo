# POD Financial Integration Implementation

## Overview
Integrate POD system with financial processes including payment processing, deductions, and credit control.

## Database Schema
```sql
-- Payment Processing
CREATE TABLE pod_payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pod_id INT NOT NULL,
    invoice_id INT,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('pending', 'processed', 'failed') DEFAULT 'pending',
    payment_date DATETIME,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    tenant_id INT NOT NULL,
    FOREIGN KEY (pod_id) REFERENCES mobile_pods(id),
    FOREIGN KEY (invoice_id) REFERENCES accounting_invoices(id)
);

-- Deduction Management
CREATE TABLE pod_deductions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pod_id INT NOT NULL,
    deduction_type ENUM('damage', 'shortage', 'penalty', 'other') NOT NULL,
    deduction_amount DECIMAL(10,2) NOT NULL,
    deduction_reason TEXT,
    approved_by INT,
    approved_at DATETIME,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    tenant_id INT NOT NULL,
    FOREIGN KEY (pod_id) REFERENCES mobile_pods(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);

-- Credit Control
CREATE TABLE pod_credit_control (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pod_id INT NOT NULL,
    customer_id INT NOT NULL,
    credit_limit DECIMAL(10,2),
    current_balance DECIMAL(10,2),
    payment_terms INT, -- days
    last_payment_date DATETIME,
    credit_status ENUM('good', 'warning', 'blocked') DEFAULT 'good',
    tenant_id INT NOT NULL,
    FOREIGN KEY (pod_id) REFERENCES mobile_pods(id),
    FOREIGN KEY (customer_id) REFERENCES vendors(id)
);
```

## Backend Implementation
```python
class PaymentProcessor:
    def trigger_payment_on_pod(self, pod_id):
        """Auto-trigger payment on POD completion"""
        pod = MobilePOD.query.get(pod_id)
        bill = TransportBill.query.get(pod.transport_bill_id)
        
        # Check for deductions
        total_deductions = db.session.query(func.sum(PodDeduction.deduction_amount))\
            .filter_by(pod_id=pod_id, status='approved').scalar() or 0
        
        payment_amount = bill.total_amount - total_deductions
        
        payment = PodPayment(
            pod_id=pod_id,
            payment_amount=payment_amount,
            payment_status='pending',
            payment_date=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()
        
        # Process payment through gateway
        self.process_payment_gateway(payment)
        return payment.id
    
    def calculate_deductions(self, damage_report):
        """Calculate damage/shortage deductions"""
        deduction = PodDeduction(
            pod_id=damage_report.pod_id,
            deduction_type='damage',
            deduction_amount=damage_report.estimated_loss,
            deduction_reason=damage_report.description,
            status='pending'
        )
        db.session.add(deduction)
        db.session.commit()
        return deduction.id
    
    def update_credit_control(self, pod_id):
        """Update customer credit status"""
        pod = MobilePOD.query.get(pod_id)
        bill = TransportBill.query.get(pod.transport_bill_id)
        
        credit_control = PodCreditControl.query.filter_by(
            customer_id=bill.vendor_id
        ).first()
        
        if credit_control:
            # Update balance and check credit limit
            credit_control.current_balance += bill.total_amount
            
            if credit_control.current_balance > credit_control.credit_limit:
                credit_control.credit_status = 'blocked'
            elif credit_control.current_balance > credit_control.credit_limit * 0.8:
                credit_control.credit_status = 'warning'
            else:
                credit_control.credit_status = 'good'
            
            db.session.commit()

@app.route('/pod/payment/trigger/<int:pod_id>', methods=['POST'])
def trigger_pod_payment(pod_id):
    """Trigger payment processing"""
    processor = PaymentProcessor()
    payment_id = processor.trigger_payment_on_pod(pod_id)
    
    return jsonify({'success': True, 'payment_id': payment_id})

@app.route('/pod/deduction/create', methods=['POST'])
def create_deduction():
    """Create POD deduction"""
    data = request.get_json()
    
    deduction = PodDeduction(
        pod_id=data['pod_id'],
        deduction_type=data['deduction_type'],
        deduction_amount=data['amount'],
        deduction_reason=data['reason']
    )
    db.session.add(deduction)
    db.session.commit()
    
    return jsonify({'success': True, 'deduction_id': deduction.id})
```

## Key Features
- **Payment Processing**: Auto-payment trigger on POD completion
- **Deduction Management**: Handle damage/shortage deductions
- **Credit Control**: Monitor customer credit limits
- **Invoice Generation**: Auto-create invoices from PODs
- **Payment Tracking**: Monitor payment status
- **Financial Reporting**: POD-based financial analytics

## Integration Points
- Payment gateways (Stripe, PayPal, etc.)
- Accounting systems
- Credit management systems
- Invoice generation
- Banking APIs
- Financial reporting tools

## Implementation Steps
1. Create financial integration tables
2. Implement payment processing logic
3. Add deduction management system
4. Create credit control module
5. Integrate with payment gateways
6. Build financial reporting
7. Test payment workflows
8. Implement security measures

## Benefits
- Automated payment processing
- Reduced manual accounting
- Better cash flow management
- Improved credit control
- Accurate deduction handling
- Streamlined financial operations
