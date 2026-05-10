# POD Integration Features Implementation

## Overview
Integrate POD system with accounting, customer portal, and third-party systems for seamless operations.

## Accounting Integration
```python
class AccountingIntegration:
    def generate_invoice_on_pod(self, pod_id):
        """Auto-generate invoice on POD completion"""
        pod = MobilePOD.query.get(pod_id)
        bill = TransportBill.query.get(pod.transport_bill_id)
        
        invoice = AccountingInvoice(
            customer_id=bill.vendor_id,
            invoice_number=self.generate_invoice_number(),
            amount=bill.total_amount,
            due_date=datetime.utcnow() + timedelta(days=30),
            pod_reference=pod_id,
            status='generated'
        )
        db.session.add(invoice)
        db.session.commit()
        return invoice.id
    
    def process_deductions(self, damage_report):
        """Handle damage/shortage deductions"""
        deduction = AccountingDeduction(
            pod_id=damage_report.pod_id,
            deduction_type='damage',
            amount=damage_report.estimated_loss,
            description=damage_report.description
        )
        db.session.add(deduction)
        db.session.commit()
        return deduction.id
```

## Customer Portal Integration
```python
@app.route('/api/customer/pod/<string:pod_number>')
@customer_auth_required
def customer_get_pod(pod_number):
    """Customer POD access"""
    pod = MobilePOD.query.filter_by(pod_number=pod_number).first()
    if not pod or pod.transport_bill.vendor_id != current_customer.id:
        return jsonify({'error': 'POD not found'}), 404
    
    return jsonify({
        'pod_number': pod.pod_number,
        'status': pod.status,
        'delivery_date': pod.captured_at,
        'documents': [{'name': doc.file_name, 'url': url_for('download_pod_document', doc_id=doc.id)} 
                      for doc in pod.documents]
    })

@app.route('/customer/portal/pods')
@customer_auth_required
def customer_pod_list():
    """Customer POD history"""
    pods = db.session.query(MobilePOD, TransportBill)\
        .join(TransportBill, MobilePOD.transport_bill_id == TransportBill.id)\
        .filter(TransportBill.vendor_id == current_customer.id)\
        .order_by(MobilePOD.captured_at.desc()).all()
    
    return render_template('customer_portal/pods.html', pods=pods)
```

## Third-party API Integration
```python
@app.route('/api/external/pod/sync', methods=['POST'])
def external_pod_sync():
    """Third-party POD synchronization"""
    data = request.get_json()
    api_key = request.headers.get('X-API-Key')
    
    # Validate API key
    if not validate_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Process POD data
    for pod_data in data.get('pods', []):
        pod = MobilePOD(
            transport_bill_id=pod_data['bill_id'],
            external_system_id=pod_data.get('external_id'),
            sync_status='synced'
        )
        db.session.add(pod)
    
    db.session.commit()
    return jsonify({'synced': len(data.get('pods', []))})

@app.route('/api/external/pod/status-update', methods=['POST'])
def external_status_update():
    """Update POD status from external system"""
    data = request.get_json()
    pod_id = data.get('pod_id')
    new_status = data.get('status')
    
    pod = MobilePOD.query.filter_by(external_system_id=pod_id).first()
    if pod:
        pod.status = new_status
        pod.sync_status = 'updated'
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'POD not found'}), 404
```

## Notification System
```python
class NotificationService:
    def send_pod_notification(self, pod_id, notification_type):
        """Send POD notifications"""
        pod = MobilePOD.query.get(pod_id)
        bill = TransportBill.query.get(pod.transport_bill_id)
        
        if notification_type == 'completed':
            # Email to customer
            self.send_email(
                recipient=bill.vendor.email,
                subject=f'POD Completed - {pod.pod_number}',
                template='pod_completed_email.html',
                data={'pod': pod, 'bill': bill}
            )
            
            # SMS notification
            self.send_sms(
                recipient=bill.vendor.phone,
                message=f'POD {pod.pod_number} has been completed successfully'
            )
        
        elif notification_type == 'overdue':
            # Internal notification for overdue PODs
            self.send_internal_notification(
                users=[pod.captured_by],
                message=f'POD {pod.pod_number} is overdue for submission'
            )
```

## Key Features
- **Accounting Integration**: Auto-invoice generation on POD completion
- **Customer Portal**: Customer POD access and download
- **Email/SMS Notifications**: Real-time status notifications
- **Third-party APIs**: External system synchronization
- **Webhook Support**: Event-driven integrations
- **Data Sync**: Bidirectional data synchronization

## Integration Points
- Accounting system (invoices, payments)
- Customer portal (self-service access)
- Email/SMS gateway (notifications)
- Third-party logistics systems
- ERP systems
- Document management systems

## Implementation Steps
1. Design integration architecture
2. Implement accounting integration
3. Create customer portal APIs
4. Set up notification system
5. Implement third-party APIs
6. Add webhook support
7. Create integration monitoring
8. Test all integrations

## Benefits
- Automated invoice generation
- Improved customer satisfaction
- Real-time notifications
- Seamless system integration
- Reduced manual data entry
- Better data synchronization
