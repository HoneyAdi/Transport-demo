# POD Advanced Features Implementation

## Overview
Implement advanced POD features including templates, multi-language support, and barcode/QR code integration.

## Database Schema
```sql
-- POD Templates
CREATE TABLE pod_templates (
    id INT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(100) NOT NULL,
    customer_id INT,
    template_config JSON NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tenant_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES vendors(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Multi-language Support
CREATE TABLE pod_translations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    language_code VARCHAR(10) NOT NULL,
    element_key VARCHAR(100) NOT NULL,
    translated_text TEXT NOT NULL,
    tenant_id INT NOT NULL,
    UNIQUE KEY unique_translation (language_code, element_key)
);

-- Barcode/QR Codes
CREATE TABLE pod_barcodes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pod_id INT NOT NULL,
    barcode_type ENUM('barcode', 'qr_code') NOT NULL,
    barcode_data VARCHAR(500) NOT NULL,
    barcode_image_path VARCHAR(500),
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    tenant_id INT NOT NULL,
    FOREIGN KEY (pod_id) REFERENCES mobile_pods(id)
);

-- Offline Sync
CREATE TABLE offline_sync_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    data_json LONGTEXT NOT NULL,
    sync_status ENUM('pending', 'synced', 'failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    last_sync_attempt DATETIME,
    tenant_id INT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES mobile_devices(device_id)
);
```

## Backend Implementation
```python
class PODTemplate:
    def generate_template(self, customer_id, template_id=None):
        """Generate customer-specific POD template"""
        if template_id:
            template = PODTemplate.query.get(template_id)
        else:
            template = PODTemplate.query.filter_by(
                customer_id=customer_id,
                is_default=True
            ).first()
        
        if not template:
            # Use default template
            template = PODTemplate.query.filter_by(
                customer_id=None,
                is_default=True
            ).first()
        
        return template.template_config if template else self.get_default_template()
    
    def apply_template(self, pod_data, template_config):
        """Apply template to POD data"""
        # Apply field mappings, validations, and formatting
        formatted_data = {}
        for field, config in template_config.get('fields', {}).items():
            if config.get('required') and not pod_data.get(field):
                raise ValueError(f"Required field {field} is missing")
            
            formatted_data[field] = self.format_field(
                pod_data.get(field), 
                config.get('format', 'text')
            )
        
        return formatted_data

class PODTranslation:
    def get_translation(self, language_code, element_key):
        """Get translated text"""
        translation = PODTranslation.query.filter_by(
            language_code=language_code,
            element_key=element_key
        ).first()
        
        return translation.translated_text if translation else element_key
    
    def translate_pod_data(self, pod_data, language_code):
        """Translate POD data to specified language"""
        translated_data = {}
        for key, value in pod_data.items():
            if isinstance(value, str):
                translated_data[key] = self.get_translation(language_code, value)
            else:
                translated_data[key] = value
        
        return translated_data

class PODBarcode:
    def generate_barcode(self, pod_id, barcode_type='qr_code'):
        """Generate barcode/QR code for POD"""
        pod = MobilePOD.query.get(pod_id)
        
        barcode_data = {
            'pod_id': pod.id,
            'pod_number': pod.pod_number,
            'bill_id': pod.transport_bill_id,
            'timestamp': pod.captured_at.isoformat()
        }
        
        if barcode_type == 'qr_code':
            barcode_image = self.generate_qr_code(barcode_data)
        else:
            barcode_image = self.generate_barcode(barcode_data)
        
        # Save barcode image
        filename = f"barcode_{pod_id}_{int(time.time())}.png"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'barcodes', filename)
        barcode_image.save(file_path)
        
        # Save to database
        barcode = PODBarcode(
            pod_id=pod_id,
            barcode_type=barcode_type,
            barcode_data=json.dumps(barcode_data),
            barcode_image_path=file_path
        )
        db.session.add(barcode)
        db.session.commit()
        
        return barcode.id

@app.route('/pod/templates/<int:customer_id>')
def get_pod_template(customer_id):
    """Get POD template for customer"""
    template_service = PODTemplate()
    template = template_service.generate_template(customer_id)
    
    return jsonify({'template': template})

@app.route('/pod/translate', methods=['POST'])
def translate_pod():
    """Translate POD data"""
    data = request.get_json()
    language_code = data.get('language_code')
    pod_data = data.get('pod_data')
    
    translation_service = PODTranslation()
    translated_data = translation_service.translate_pod_data(pod_data, language_code)
    
    return jsonify({'translated_data': translated_data})

@app.route('/pod/barcode/generate/<int:pod_id>')
def generate_barcode(pod_id):
    """Generate barcode for POD"""
    barcode_service = PODBarcode()
    barcode_id = barcode_service.generate_barcode(pod_id)
    
    return jsonify({'success': True, 'barcode_id': barcode_id})
```

## Key Features
- **POD Templates**: Customizable templates by customer
- **Multi-language Support**: POD in multiple languages
- **Barcode/QR Codes**: Automated POD identification
- **Offline Sync**: Work offline, sync when online
- **Template Builder**: Visual template creation
- **Language Detection**: Auto-detect customer language

## Implementation Steps
1. Create template management system
2. Implement multi-language support
3. Add barcode/QR code generation
4. Create offline sync functionality
5. Build template builder UI
6. Add language management
7. Test barcode scanning
8. Implement offline data handling

## Benefits
- Customer-specific POD formats
- Multi-language accessibility
- Automated POD identification
- Offline capability
- Improved user experience
- Reduced manual data entry
