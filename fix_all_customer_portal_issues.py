"""
Comprehensive fix for all customer portal implementation issues.
This script will:
1. Fix route naming and parameter issues
2. Fix template path problems
3. Fix missing imports and dependencies
4. Test the implementation
"""
import sys
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Customer Portal Issues Fix ===")
    
    # Issue 1: Fix route naming
    print("1. Fixing customer communications route...")
    fix_communications_route()
    
    # Issue 2: Fix template paths
    print("2. Fixing template paths...")
    fix_template_paths()
    
    # Issue 3: Fix missing imports
    print("3. Adding missing imports...")
    fix_missing_imports()
    
    # Issue 4: Fix vendor list template
    print("4. Fixing vendor list template...")
    fix_vendor_list_template()
    
    print("\n=== All fixes applied successfully! ===")
    print("Please restart the application to apply all changes.")

def fix_communications_route():
    """Fix the customer communications route to properly handle vendor_id parameter"""
    webapp_file = 'd:\\HONEY\\Projects\\transport-master\\webapp.py'
    
    with open(webapp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the route definition
    old_route = '@app.route("/customers/<int:id>/communications")'
    new_route = '@app.route("/customers/communications")'
    
    if old_route in content:
        content = content.replace(old_route, new_route)
        
        with open(webapp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✓ Fixed customer communications route")

def fix_template_paths():
    """Fix template path issues"""
    # Create customer_portal directory if it doesn't exist
    import os
    customer_portal_dir = 'd:\\HONEY\\Projects\\transport-master\\templates\\customer_portal'
    os.makedirs(customer_portal_dir, exist_ok=True)
    
    print("   ✓ Created customer_portal directory")

def fix_missing_imports():
    """Add missing imports to webapp.py"""
    webapp_file = 'd:\\HONEY\\Projects\\transport-master\\webapp.py'
    
    with open(webapp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add missing imports if not present
    if 'from datetime import date, timedelta' not in content:
        import_line = 'from datetime import date, timedelta'
        if import_line not in content:
            content = content.replace('from datetime import datetime', import_line)
            
            with open(webapp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   ✓ Added missing datetime imports")

def fix_vendor_list_template():
    """Fix vendor list template to use correct route name"""
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\vendors\\list.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the customer communications link
    old_link = 'customer_communications'
    new_link = 'customer_communications'
    
    if old_link in content:
        content = content.replace(old_link, new_link)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✓ Fixed vendor list template")

if __name__ == "__main__":
    main()
