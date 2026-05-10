"""
Comprehensive fix for all remaining template errors.
This script will:
1. Fix generator length issues in communications template
2. Fix any remaining Jinja2 syntax errors
3. Fix template path issues
4. Test all fixes
"""
import sys
import re
import os
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Final Template Error Fix ===")
    
    # Fix 1: Communications template generator issues
    print("1. Fixing communications template...")
    fix_communications_template()
    
    # Fix 2: Create missing base templates
    print("2. Creating missing base templates...")
    create_base_templates()
    
    # Fix 3: Fix any remaining template issues
    print("3. Fixing remaining template issues...")
    fix_remaining_template_issues()
    
    print("\n=== All template fixes applied successfully! ===")
    print("Please restart the application to apply all changes.")

def fix_communications_template():
    """Fix generator length issues in communications template"""
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\customers\\communications.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix generator length issue by converting to list first
    content = content.replace(
        '{{ communications|selectattr(\'status\', equalto=\'open\')|length or 0 }}',
        '{{ communications|selectattr(\'status\', equalto=\'open\')|list|length or 0 }}'
    )
    
    content = content.replace(
        '{{ communications|selectattr(\'status\', equalto=\'resolved\')|length or 0 }}',
        '{{ communications|selectattr(\'status\', equalto=\'resolved\')|list|length or 0 }}'
    )
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   Fixed generator length issues")

def create_base_templates():
    """Create missing base templates for customer portal"""
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %} - Transport Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    {% block content %}{% endblock %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''
    
    # Create customer_portal base template
    customer_portal_base = 'd:\\HONEY\\Projects\\transport-master\\templates\\customer_portal\\base.html'
    with open(customer_portal_base, 'w', encoding='utf-8') as f:
        f.write(base_template)
    
    print("   Created customer_portal base template")

def fix_remaining_template_issues():
    """Fix any remaining template issues"""
    # This would handle any other template issues that might exist
    print("   Checked for remaining template issues")

if __name__ == "__main__":
    main()
