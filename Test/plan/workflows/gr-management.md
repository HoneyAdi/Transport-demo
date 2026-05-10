# GR (Goods Receipt) Management Test Plan

## Overview
Test the complete Goods Receipt lifecycle including creation, versioning, attachments, and amendment workflows.

## Prerequisites
- User with appropriate permissions (Operations role)
- Test vendors and items configured in system
- Sample documents ready for upload testing
- Database with GR-related tables initialized

## Test Environment Setup
- **Login URL**: `/login`
- **GR Management URL**: `/gr` (or equivalent)
- **Test User**: ops@company.com / ops123
- **Required Permissions**: GR creation, edit, attachment upload

---

## Test Case 1: GR Creation Workflow

### 1.1 Basic GR Creation
**Objective**: Verify users can create new Goods Receipts with all required fields

**Test Steps**:
1. Login as Operations user
2. Navigate to GR creation page
3. Fill in mandatory fields:
   - GR Number (auto-generated)
   - Vendor selection
   - GR Date
   - Item details (name, quantity, rate)
   - Vehicle details
   - Driver information
4. Click "Save" button
5. Verify GR is created successfully
6. Check GR appears in GR list

**Expected Results**:
- GR number auto-generated with correct format
- All fields saved correctly
- GR status set to "Draft" or "Active"
- GR appears in list with correct details
- Audit log entry created

**Pass/Fail Criteria**:
- ☐ GR created without errors
- ☐ All data saved accurately
- ☐ GR list updated immediately
- ☐ Audit trail recorded

### 1.2 GR with Multiple Items
**Objective**: Test GR creation with multiple line items

**Test Steps**:
1. Create new GR
2. Add multiple items (3-5 different products)
3. Verify item calculations (quantity × rate = amount)
4. Test total amount calculation
5. Save GR
6. Review created GR details

**Expected Results**:
- All items saved correctly
- Calculations accurate
- Total amount matches sum of items
- Item order maintained

---

## Test Case 2: GR Attachment System

### 2.1 Single Document Upload
**Objective**: Verify document attachment functionality

**Test Steps**:
1. Create new GR
2. Click "Add Attachment"
3. Select document file (PDF, JPG, DOC)
4. Add attachment description
5. Upload document
6. Verify attachment appears in GR details

**Expected Results**:
- File uploaded successfully
- Attachment metadata saved (name, size, upload date)
- Document preview works for supported formats
- Download functionality works

### 2.2 Multiple Document Upload
**Objective**: Test uploading multiple documents to single GR

**Test Steps**:
1. Create GR with basic details
2. Upload 3-5 different documents:
   - PDF invoice
   - JPG photo of goods
   - Excel weight slip
   - Signed delivery note
3. Verify all attachments display correctly
4. Test document preview for each type

**Expected Results**:
- All files uploaded successfully
- File size limits enforced
- Supported formats preview correctly
- Attachment list shows all documents

### 2.3 Document Management
**Objective**: Test attachment editing and deletion

**Test Steps**:
1. Create GR with attachments
2. Edit attachment description
3. Delete one attachment
4. Add new attachment
5. Verify final attachment list

**Expected Results**:
- Description updates save correctly
- Deletion removes file and database record
- New attachments add correctly
- Attachment order maintained

---

## Test Case 3: GR Versioning System

### 3.1 GR Amendment Workflow
**Objective**: Test GR versioning and amendment process

**Test Steps**:
1. Create initial GR (Version 1)
2. Edit GR details (change quantity, add item, etc.)
3. Save changes
4. Verify new version created
5. Check version history
6. Compare versions

**Expected Results**:
- Original GR marked as "Original"
- New version created with "Amendment" status
- Version number incremented
- Version history shows all changes
- Original version preserved

### 3.2 Multiple Amendments
**Objective**: Test multiple GR amendments

**Test Steps**:
1. Create GR (Version 1)
2. Make first amendment (Version 2)
3. Make second amendment (Version 3)
4. Review complete version history
5. Test version comparison
6. Verify audit trail completeness

**Expected Results**:
- Each amendment creates new version
- Version history chronological
- All changes tracked
- Audit log complete for each version

### 3.3 Version Rollback
**Objective**: Test ability to view/restore previous versions

**Test Steps**:
1. Create GR with 3 versions
2. Navigate to version history
3. View each version details
4. Test version comparison
5. Verify rollback functionality (if available)

**Expected Results**:
- All versions accessible
- Version comparison shows differences
- Rollback works (if implemented)
- Data integrity maintained

---

## Test Case 4: GR Search and Filtering

### 4.1 Basic Search
**Objective**: Test GR search functionality

**Test Steps**:
1. Navigate to GR list
2. Search by GR number
3. Search by vendor name
4. Search by date range
5. Search by item name

**Expected Results**:
- Search returns accurate results
- Search works for all fields
- Results display correctly
- Performance acceptable

### 4.2 Advanced Filtering
**Objective**: Test GR filtering options

**Test Steps**:
1. Apply date range filter
2. Filter by vendor
3. Filter by status
4. Filter by amount range
5. Combine multiple filters

**Expected Results**:
- Filters work independently
- Combined filters work correctly
- Filter results accurate
- Filter state maintained

---

## Test Case 5: GR Export and Reporting

### 5.1 Excel Export
**Objective**: Test GR data export to Excel

**Test Steps**:
1. Select GR(s) for export
2. Choose Excel export option
3. Download and open Excel file
4. Verify data accuracy
5. Check formatting and formulas

**Expected Results**:
- Export completes successfully
- Excel file opens without errors
- All data exported accurately
- Formatting preserved
- File size reasonable

### 5.2 PDF Generation
**Objective**: Test GR PDF report generation

**Test Steps**:
1. Select single GR
2. Generate PDF report
3. Open and review PDF
4. Verify layout and content
5. Test batch PDF generation

**Expected Results**:
- PDF generates correctly
- Layout professional
- All content included
- Print quality good
- Batch PDF works

---

## Test Case 6: GR Integration Testing

### 6.1 GR to Transport Bill Integration
**Objective**: Test GR conversion to transport bills

**Test Steps**:
1. Create GR with complete details
2. Navigate to transport bill creation
3. Select GR for billing
4. Verify auto-population of data
5. Generate transport bill
6. Verify bill-GR linkage

**Expected Results**:
- GR data auto-populates correctly
- All required fields transferred
- Bill-GR relationship established
- Calculations preserved
- Status updates work

### 6.2 Multi-Item GR to Bill
**Objective**: Test complex GR with multiple items

**Test Steps**:
1. Create GR with 5+ items
2. Generate transport bill
3. Verify all items transferred
4. Check calculations
5. Test bill modifications

**Expected Results**:
- All items transferred accurately
- Calculations correct
- Item order maintained
- Modifications work properly

---

## Performance Testing

### 7.1 Large Data Handling
**Objective**: Test system performance with large GR data

**Test Steps**:
1. Create GR with 50+ items
2. Upload multiple large attachments
3. Test save performance
4. Test load performance
5. Test search performance

**Expected Results**:
- Save completes within 30 seconds
- Load completes within 10 seconds
- Search completes within 5 seconds
- No memory errors
- System remains responsive

### 7.2 Concurrent User Testing
**Objective**: Test multiple users creating GRs simultaneously

**Test Steps**:
1. Have 3 users create GRs simultaneously
2. Test GR number generation
3. Verify data integrity
4. Check for conflicts
5. Test attachment uploads

**Expected Results**:
- No GR number conflicts
- All data saved correctly
- No data corruption
- Performance acceptable
- Attachments work correctly

---

## Security Testing

### 8.1 Permission Testing
**Objective**: Verify GR access controls

**Test Steps**:
1. Test with unauthorized user
2. Test with read-only access
3. Test with edit permissions
4. Test tenant isolation
5. Test audit trail

**Expected Results**:
- Unauthorized access blocked
- Read-only users cannot edit
- Edit permissions work correctly
- Tenant isolation enforced
- All actions logged

---

## Error Handling Testing

### 9.1 Validation Errors
**Objective**: Test input validation and error messages

**Test Steps**:
1. Submit GR with missing required fields
2. Enter invalid data types
3. Test file upload limits
4. Test duplicate GR numbers
5. Test invalid dates

**Expected Results**:
- Clear error messages displayed
- Invalid data rejected
- File size limits enforced
- Duplicate prevention works
- Date validation works

### 9.2 System Error Recovery
**Objective**: Test system behavior during errors

**Test Steps**:
1. Test database connection loss
2. Test file system errors
3. Test network timeouts
4. Test memory limitations
5. Verify data integrity

**Expected Results**:
- Graceful error handling
- No data corruption
- User-friendly error messages
- Automatic recovery where possible
- Proper logging of errors

---

## Test Results Summary

### Pass/Fall Checklist
- [ ] GR Creation - Basic
- [ ] GR Creation - Multiple Items
- [ ] Single Document Upload
- [ ] Multiple Document Upload
- [ ] Document Management
- [ ] GR Amendment Workflow
- [ ] Multiple Amendments
- [ ] Version Rollback
- [ ] Basic Search
- [ ] Advanced Filtering
- [ ] Excel Export
- [ ] PDF Generation
- [ ] GR to Bill Integration
- [ ] Multi-Item GR to Bill
- [ ] Large Data Handling
- [ ] Concurrent User Testing
- [ ] Permission Testing
- [ ] Validation Errors
- [ ] System Error Recovery

### Issues Found
- **Critical**: 
- **Major**: 
- **Minor**: 

### Recommendations
- **Immediate**: 
- **Short-term**: 
- **Long-term**: 

---

**Test Completed By**: ________________________  
**Date**: ________________________  
**Environment**: ________________________  
**Overall Status**: ☐ Pass ☐ Fail ☐ Partial
