"""
Final fix for Jinja2 float filter errors.
Simple direct replacement without Unicode issues.
"""
import sys
import os
sys.path.insert(0, 'D:\\HONEY\\Projects\\transport-master')

def main():
    print("=== Final Type Error Fix ===")
    
    template_file = 'd:\\HONEY\\Projects\\transport-master\\templates\\customers\\credit_management.html'
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all float() calls with float filter
    content = content.replace('float(credit_info.credit_limit)', '(credit_info.credit_limit | float)')
    content = content.replace('float(credit_info.current_outstanding)', '(credit_info.current_outstanding | float)')
    content = content.replace('float(credit_info.available_credit)', '(credit_info.available_credit | float)')
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed Jinja2 float filter errors")

if __name__ == "__main__":
    main()
