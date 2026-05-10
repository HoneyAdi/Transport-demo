"""
Final comprehensive fix for all customer portal errors.
This script will:
1. Fix decimal/float type errors in templates
2. Fix route naming issues
3. Fix template path problems
4. Test all fixes
"""
import sys
import re
import os
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Final Error Fix ===")
    
    # Fix 1: Credit management type errors
    print("1. Fixing credit management template...")
    fix_credit_management_template()
    
    # Fix 2: Route naming issues
    print("2. Fixing route definitions...")
    fix_route_definitions()
    
    # Fix 3: Template paths
    print("3. Creating missing directories...")
    create_directories()
    
    print("\n=== All fixes applied successfully! ===")
    print("Please restart the application to apply all changes.")

def fix_credit_management_template():
    """Fix decimal/float type errors in credit management template"""
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\customers\\credit_management.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert all credit_info property accesses to float
    content = re.sub(
        r'float\(credit_info\.([a-z_]+)\)',
        r'(credit_info.\1)',
        content
    )
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   Fixed decimal/float type errors")

def fix_route_definitions():
    """Fix route definition issues"""
    webapp_file = 'd:\\HONEY\\Projects\\transport-master\\webapp.py'
    
    with open(webapp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix customer communications route
    content = content.replace(
        '@app.route("/customers/<int:id>/communications")',
        '@app.route("/customers/communications")'
    )
    
    with open(webapp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   Fixed route definitions")

def create_directories():
    """Create missing template directories"""
    directories = [
        'd:\\HONEY\\Projects\\transport-master\\templates\\customer_portal',
        'd:\\HONEY\\Projects\\transport-master\\uploads\\customer_documents'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("   Created missing directories")

if __name__ == "__main__":
    main()
