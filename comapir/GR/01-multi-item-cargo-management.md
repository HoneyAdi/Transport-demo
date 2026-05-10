# Multi-Item Cargo Management Implementation

## Overview
Implement multi-item cargo management for GR (Goods Receipt) system to support complex shipments with multiple items per GR.

## Current State
- ✅ Basic TransportBill model exists
- ✅ Single item GR support
- ❌ Multiple items per GR
- ❌ Individual item tracking
- ❌ Cargo classification support

## Implementation Plan

### Database Schema Changes

#### 1. Create GRItem Model
```python
class GRItem(db.Model):
    """Individual items within a GR"""
    __tablename__ = "gr_items"
    
    id = db.Column(db.Integer, primary_key=True)
    gr_id = db.Column(db.Integer, db.ForeignKey('transport_bills.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    item_description = db.Column(db.Text)
    item_code = db.Column(db.String(50))
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_of_measure = db.Column(db.String(20), default='pcs')
    unit_rate = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    weight = db.Column(db.Numeric(8, 2))
    volume = db.Column(db.Numeric(8, 2))
    cargo_type = db.Column(db.String(50))  # hazardous, perishable, fragile
    packaging_type = db.Column(db.String(50))
    dimensions = db.Column(db.String(100))  # LxWxH
    serial_numbers = db.Column(db.Text)
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    gr = db.relationship("TransportBill", backref="items")
```

#### 2. Create CargoClassification Model
```python
class CargoClassification(db.Model):
    """Cargo classification system"""
    __tablename__ = "cargo_classifications"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    is_hazardous = db.Column(db.Boolean, default=False)
    is_perishable = db.Column(db.Boolean, default=False)
    is_fragile = db.Column(db.Boolean, default=False)
    requires_special_handling = db.Column(db.Boolean, default=False)
    max_weight = db.Column(db.Numeric(8, 2))
    temperature_control = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Backend Implementation

#### 1. Multi-Item GR Routes
```python
@app.route("/gr/create-multi-item", methods=["GET", "POST"])
@permission_required("transport_bills", "create")
def create_multi_item_gr():
    """Create GR with multiple items"""
    if request.method == "GET":
        return render_template("gr/multi_item_form.html")
    
    # Handle form submission
    items_data = request.form.getlist("items")
    gr_data = {
        'gr_number': request.form.get('gr_number'),
        'gr_date': request.form.get('gr_date'),
        'party_id': request.form.get('party_id'),
        'vehicle_id': request.form.get('vehicle_id'),
        'from_location_id': request.form.get('from_location_id'),
        'to_location_id': request.form.get('to_location_id'),
        'delivery_type_id': request.form.get('delivery_type_id'),
        'items': items_data
    }
    
    # Create GR and items
    gr = create_gr_with_items(gr_data)
    
    flash('Multi-item GR created successfully', 'success')
    return redirect(url_for('gr_details', id=gr.id))

@app.route("/gr/<int:gr_id>/items")
@permission_required("transport_bills", "view")
def gr_items_list(gr_id):
    """View items within a GR"""
    gr = db.session.get(TransportBill, gr_id)
    if not gr:
        flash('GR not found', 'error')
        return redirect(url_for('gr_list'))
    
    return render_template("gr/items_list.html", gr=gr, items=gr.items)
```

#### 2. Cargo Classification Routes
```python
@app.route("/cargo-classifications")
@permission_required("cargo_classifications", "view")
def cargo_classifications():
    """Manage cargo classifications"""
    classifications = CargoClassification.query.all()
    return render_template("gr/cargo_classifications.html", classifications=classifications)

@app.route("/cargo-classifications/create", methods=["GET", "POST"])
@permission_required("cargo_classifications", "create")
def create_cargo_classification():
    """Create new cargo classification"""
    if request.method == "POST":
        classification = CargoClassification(
            name=request.form.get('name'),
            description=request.form.get('description'),
            is_hazardous=bool(request.form.get('is_hazardous')),
            is_perishable=bool(request.form.get('is_perishable')),
            is_fragile=bool(request.form.get('is_fragile')),
            requires_special_handling=bool(request.form.get('requires_special_handling'))
        )
        
        db.session.add(classification)
        db.session.commit()
        
        flash('Cargo classification created successfully', 'success')
        return redirect(url_for('cargo_classifications'))
    
    return render_template("gr/cargo_classification_form.html")
```

### Frontend Implementation

#### 1. Multi-Item GR Form Template
```html
<!-- templates/gr/multi_item_form.html -->
{% extends 'base.html' %}

{% block title %}Create Multi-Item GR{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="bi bi-plus-circle"></i> Create Multi-Item GR</h5>
                </div>
                <div class="card-body">
                    <form method="POST" id="multiItemForm">
                        <!-- Basic GR Information -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">GR Number</label>
                                <input type="text" class="form-control" name="gr_number" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">GR Date</label>
                                <input type="date" class="form-control" name="gr_date" required>
                            </div>
                        </div>
                        
                        <!-- Party Information -->
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Party</label>
                                <select class="form-select" name="party_id" required>
                                    <option value="">Select Party</option>
                                    {% for party in parties %}
                                    <option value="{{ party.id }}">{{ party.vendor_name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Vehicle</label>
                                <select class="form-select" name="vehicle_id" required>
                                    <option value="">Select Vehicle</option>
                                    {% for vehicle in vehicles %}
                                    <option value="{{ vehicle.id }}">{{ vehicle.vehicle_number }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <!-- Items Section -->
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">Items</h6>
                                <button type="button" class="btn btn-sm btn-primary" onclick="addItemRow()">
                                    <i class="bi bi-plus"></i> Add Item
                                </button>
                            </div>
                            <div class="card-body">
                                <div id="itemsContainer">
                                    <!-- Dynamic item rows will be added here -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-3">
                            <div class="col-12">
                                <button type="submit" class="btn btn-primary">
                                    <i class="bi bi-check-circle"></i> Create GR
                                </button>
                                <a href="{{ url_for('gr_list') }}" class="btn btn-secondary">
                                    <i class="bi bi-x-circle"></i> Cancel
                                </a>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function addItemRow() {
    const container = document.getElementById('itemsContainer');
    const itemCount = container.children.length;
    const newRow = document.createElement('div');
    newRow.className = 'row mb-2 item-row border p-2';
    newRow.innerHTML = `
        <div class="col-md-2">
            <input type="text" class="form-control" name="items[${itemCount}][item_name]" placeholder="Item Name" required>
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control" name="items[${itemCount}][item_code]" placeholder="Item Code">
        </div>
        <div class="col-md-1">
            <input type="number" class="form-control" name="items[${itemCount}][quantity]" placeholder="Qty" required>
        </div>
        <div class="col-md-1">
            <input type="text" class="form-control" name="items[${itemCount}][uom]" placeholder="UOM" value="pcs">
        </div>
        <div class="col-md-2">
            <input type="number" class="form-control" name="items[${itemCount}][unit_rate]" placeholder="Rate" required>
        </div>
        <div class="col-md-2">
            <input type="number" class="form-control" name="items[${itemCount}][weight]" placeholder="Weight">
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-danger btn-sm" onclick="removeItemRow(this)">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    container.appendChild(newRow);
}

function removeItemRow(button) {
    button.closest('.item-row').remove();
}
</script>
{% endblock %}
```

#### 2. Cargo Classification Template
```html
<!-- templates/gr/cargo_classifications.html -->
{% extends 'base.html' %}

{% block title %}Cargo Classifications{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0"><i class="bi bi-tags"></i> Cargo Classifications</h5>
                    <a href="{{ url_for('create_cargo_classification') }}" class="btn btn-primary">
                        <i class="bi bi-plus"></i> Add Classification
                    </a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Hazardous</th>
                                    <th>Perishable</th>
                                    <th>Fragile</th>
                                    <th>Special Handling</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for classification in classifications %}
                                <tr>
                                    <td>{{ classification.name }}</td>
                                    <td>{{ classification.description or '-' }}</td>
                                    <td>
                                        {% if classification.is_hazardous %}
                                        <span class="badge bg-danger">Yes</span>
                                        {% else %}
                                        <span class="badge bg-success">No</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if classification.is_perishable %}
                                        <span class="badge bg-warning">Yes</span>
                                        {% else %}
                                        <span class="badge bg-success">No</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if classification.is_fragile %}
                                        <span class="badge bg-warning">Yes</span>
                                        {% else %}
                                        <span class="badge bg-success">No</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if classification.requires_special_handling %}
                                        <span class="badge bg-info">Yes</span>
                                        {% else %}
                                        <span class="badge bg-secondary">No</span>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <a href="{{ url_for('edit_cargo_classification', id=classification.id) }}" class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-pencil"></i>
                                            </a>
                                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteClassification({{ classification.id }})">
                                                <i class="bi bi-trash"></i>
                                            </button>
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
{% endblock %}
```

### Database Migration Script
```python
# create_multi_item_gr_tables.py
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

from models import db, GRItem, CargoClassification
from webapp import app

def create_tables():
    """Create multi-item GR tables"""
    with app.app_context():
        try:
            db.create_all()
            print("SUCCESS: Multi-item GR tables created!")
            print("   - gr_items")
            print("   - cargo_classifications")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
```

### Integration Points
- Extend existing TransportBill model with items relationship
- Add cargo classification dropdown to GR forms
- Integrate with existing vendor/vehicle systems
- Connect with delivery and dispatch modules
- Link with payment and accounting systems

### Business Benefits
- **Complex Shipment Support**: Handle multiple items per GR
- **Cargo Classification**: Automated handling rules based on cargo type
- **Weight/Volume Calculations**: Automatic calculations
- **Special Handling**: Hazardous, perishable, fragile item management
- **Item Tracking**: Individual item tracking within GRs
- **Compliance**: Proper cargo classification and documentation

### Success Metrics
- Multi-item GR creation time
- Item accuracy rate
- Cargo classification coverage
- Special handling compliance
- User adoption metrics

This implementation will transform the GR system from single-item support to a comprehensive multi-item cargo management system that can handle complex business scenarios effectively.
