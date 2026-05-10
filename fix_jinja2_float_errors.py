"""
Fix Jinja2 float filter errors in credit management template.
This script will replace all float() function calls with proper Jinja2 float filter.
"""
import sys
import re
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Fixing Jinja2 Float Filter Errors ===")
    
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\customers\\credit_management.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all float() function calls with float filter
    replacements = [
        # Replace float(credit_info.credit_limit) with (credit_info.credit_limit | float)
        (r'float\(credit_info\.credit_limit\)', '(credit_info.credit_limit | float)'),
        
        # Replace float(credit_info.current_outstanding) with (credit_info.current_outstanding | float)
        (r'float\(credit_info\.current_outstanding\)', '(credit_info.current_outstanding | float)'),
        
        # Replace float(credit_info.available_credit) with (credit_info.available_credit | float)
        (r'float\(credit_info\.available_credit\)', '(credit_info.available_credit | float)'),
        
        # Replace float(credit_info.credit_utilization_pct) with (credit_info.credit_utilization_pct | float)
        (r'float\(credit_info\.credit_utilization_pct\)', '(credit_info.credit_utilization_pct | float)'),
    ]
    
    for old_pattern, new_pattern in replacements:
        content = re.sub(old_pattern, new_pattern, content)
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed all Jinja2 float filter errors")
    print("✓ Template should now work correctly with decimal values")

if __name__ == "__main__":
    main()
