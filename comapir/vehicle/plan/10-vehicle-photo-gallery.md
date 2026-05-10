# Vehicle Photo Gallery

A multi-photo gallery system for vehicles allowing upload and management of multiple images including vehicle photos, damage photos, and document scans.

## Overview

The current system supports single document attachments (insurance, fitness). This feature adds a proper photo gallery for each vehicle supporting multiple images with categories, captions, and thumbnail previews.

## Business Value

- Visual identification of vehicles
- Condition documentation at purchase/sale
- Damage/incident evidence
- Insurance claim documentation
- Resale value support
- Fleet inventory visualization

## Key Features

### 1. Photo Categories

**Predefined Categories:**
- **Front View** - Vehicle front photo
- **Rear View** - Vehicle back photo
- **Left Side** - Driver side photo
- **Right Side** - Passenger side photo
- **Interior** - Cabin/interior photos
- **Engine Bay** - Engine compartment
- **Chassis/Underbody** - For heavy vehicles
- **Documents** - RC, Insurance, Permits
- **Damage** - Accident/incident damage photos
- **Other** - Miscellaneous

### 2. Photo Upload

**Features:**
- Multiple file upload (drag & drop)
- Image preview before upload
- Category selection per photo
- Caption/description per photo
- Auto-thumbnail generation
- File size limit (5MB per image)
- Allowed formats: JPG, PNG, WEBP

### 3. Gallery View

**Layout Options:**
- Grid view (thumbnails)
- Carousel/slider view
- Lightbox for full-size view

**Features:**
- Click to enlarge
- Download original
- Delete photo
- Edit caption/category
- Set as primary photo

### 4. Photo Management

**Actions:**
- Edit caption/description
- Change category
- Reorder photos (drag & drop)
- Delete photo
- Download HD version
- Set as cover photo (shows in list view)

### 5. Vehicle List Integration

- Show primary/cover photo in vehicle list
- Photo count badge
- Quick gallery preview on hover

### 6. Document Scanning Integration

- Camera capture for documents
- Auto-crop and perspective correction (optional)
- OCR for document numbers (optional)

## Technical Implementation

### New Model Required
```python
class VehiclePhoto(db.Model):
    __tablename__ = "vehicle_photos"
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # Photo Details
    category = db.Column(db.String(50), default='other')  # front, rear, left, right, interior, document, damage, other
    caption = db.Column(db.String(255))
    description = db.Column(db.Text)
    
    # File Paths
    original_path = db.Column(db.String(500), nullable=False)  # Full resolution
    thumbnail_path = db.Column(db.String(500))  # Small preview
    medium_path = db.Column(db.String(500))  # Medium size for gallery
    
    # Metadata
    file_size = db.Column(db.Integer)  # bytes
    dimensions = db.Column(db.String(20))  # e.g., "1920x1080"
    file_type = db.Column(db.String(10))  # jpg, png, webp
    
    # Status
    is_primary = db.Column(db.Boolean, default=False)  # Cover photo
    is_document = db.Column(db.Boolean, default=False)  # Is a document scan
    
    # Upload Info
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicle = db.relationship("Vehicle", backref="photos")
    uploader = db.relationship("User")

# Update Vehicle model to reference primary photo
# (Optional - can be determined by query)
def get_primary_photo(self):
    return VehiclePhoto.query.filter_by(vehicle_id=self.id, is_primary=True).first()
```

### Image Processing
```python
from PIL import Image
import os

def process_uploaded_image(file, vehicle_id):
    # Save original
    filename = secure_filename(file.filename)
    unique_name = f"vehicle_{vehicle_id}_{int(time.time())}_{filename}"
    
    original_path = os.path.join(UPLOAD_FOLDER, 'original', unique_name)
    file.save(original_path)
    
    # Generate thumbnails
    img = Image.open(original_path)
    
    # Thumbnail (150x150)
    thumb = img.copy()
    thumb.thumbnail((150, 150))
    thumb_path = os.path.join(UPLOAD_FOLDER, 'thumbs', unique_name)
    thumb.save(thumb_path, quality=85)
    
    # Medium (800x600 max)
    medium = img.copy()
    medium.thumbnail((800, 600))
    medium_path = os.path.join(UPLOAD_FOLDER, 'medium', unique_name)
    medium.save(medium_path, quality=90)
    
    return {
        'original': original_path,
        'thumbnail': thumb_path,
        'medium': medium_path,
        'dimensions': f"{img.width}x{img.height}",
        'file_size': os.path.getsize(original_path)
    }
```

### New Routes
```
GET /vehicles/<id>/photos
POST /vehicles/<id>/photos/upload
POST /vehicles/<id>/photos/<photo_id>/delete
POST /vehicles/<id>/photos/<photo_id>/update
POST /vehicles/<id>/photos/<photo_id>/set-primary
GET /vehicles/<id>/photos/<photo_id>/download
```

### UI Components
- Photo grid gallery (masonry or uniform)
- Upload zone (drag & drop)
- Category filter buttons
- Lightbox modal for viewing
- Edit metadata modal
- Photo count badge

## Folder Structure
```
uploads/
└── vehicles/
    ├── original/   # Full resolution
    ├── medium/     # 800px max
    └── thumbs/     # 150px thumbnails
```

## Acceptance Criteria

- [ ] Can upload multiple photos at once
- [ ] Photos categorized (front, rear, side, etc.)
- [ ] Thumbnails auto-generated
- [ ] Gallery displays in grid view
- [ ] Click to enlarge in lightbox
- [ ] Can edit caption and category
- [ ] Can delete photos
- [ ] Can set primary/cover photo
- [ ] Vehicle list shows primary photo
- [ ] Mobile-responsive gallery

## Integration Points

- Vehicle list (show primary photo)
- Vehicle dashboard (photo gallery section)
- Vehicle edit form (upload interface)

## Dependencies

- Pillow (PIL) for image processing
- JavaScript gallery library (e.g., Lightbox2, Fancybox)

## Estimated Effort

- Database model: 2 hours
- Image processing: 4 hours
- Upload functionality: 4 hours
- Gallery UI: 5 hours
- Lightbox integration: 3 hours
- Testing: 2 hours
