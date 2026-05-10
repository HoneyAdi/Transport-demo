"""
Fix decimal/float type errors in credit management template.
This script will convert all decimal operations to compatible types.
"""
import sys
import re
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Fixing Credit Management Type Errors ===")
    
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\customers\\credit_management.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Convert decimal multiplication to float
    content = re.sub(
        r'credit_info\.credit_limit \* 0\.8',
        'float(credit_info.credit_limit) * 0.8',
        content
    )
    
    # Fix 2: Convert decimal comparison to float
    content = re.sub(
        r'credit_info\.current_outstanding > credit_info\.credit_limit \* 0\.8',
        'float(credit_info.current_outstanding) > float(credit_info.credit_limit) * 0.8',
        content
    )
    
    # Fix 3: Convert available credit comparison
    content = re.sub(
        r'\(credit_info\.available_credit or 0\) < 0',
        '(float(credit_info.available_credit or 0) < 0',
        content
    )
    
    # Fix 4: Convert credit utilization access
    content = re.sub(
        r'credit_info\.credit_utilization_pct >= 90',
        'float(credit_info.credit_utilization_pct or 0) >= 90',
        content
    )
    
    content = re.sub(
        r'credit_info\.credit_utilization_pct >= 70',
        'float(credit_info.credit_utilization_pct or 0) >= 70',
        content
    )
    
    # Fix 5: Convert all credit_info property accesses to float
    content = re.sub(
        r'credit_info\.(current_outstanding|credit_limit|available_credit|credit_utilization_pct)',
        r'float(credit_info.\1)',
        content
    )
    
    # Write the fixed content back
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed all decimal/float type errors in credit_management.html")
    print("✓ Template should now work correctly with decimal values")

if __name__ == "__main__":
    main()
