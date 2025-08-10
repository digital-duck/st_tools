#!/usr/bin/env python3
"""
JavaScript Syntax Checker for AI HTML Apps

This script checks for common JavaScript syntax issues that can cause 
code to be displayed as HTML instead of being executed, specifically:
- Template literals (backticks) that may break string concatenation
- Dollar brace expressions that should be avoided in single-file HTML apps

Usage: python check_syntax.py [filename]
If no filename provided, defaults to ai_audio.html
"""

import re
import sys
import os

def check_js_syntax(file_path):
    """Check JavaScript syntax issues in HTML file"""
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    print(f"🔍 Checking JavaScript syntax in: {file_path}")
    print("-" * 50)
    
    # Check for template literals (backticks)
    template_literals = re.findall(r'`[^`]*`', content)
    
    # Check for dollar brace expressions
    dollar_braces = re.findall(r'\$\{[^}]*\}', content)
    
    # Check for common problematic patterns
    problematic_patterns = []
    
    # ES6 template strings in single-file HTML
    if template_literals:
        problematic_patterns.append(f"Template literals: {len(template_literals)} found")
    
    if dollar_braces:
        problematic_patterns.append(f"Dollar brace expressions: {len(dollar_braces)} found")
    
    # Check for unescaped quotes in HTML attributes
    unescaped_quotes = re.findall(r'onclick="[^"]*"[^"]*"[^"]*"', content)
    if unescaped_quotes:
        problematic_patterns.append(f"Potentially unescaped quotes: {len(unescaped_quotes)} found")
    
    # Results
    if not problematic_patterns:
        print("✅ No JavaScript syntax issues found!")
        print("   - No template literals detected")
        print("   - No dollar brace expressions found")
        print("   - String concatenation should work properly")
    else:
        print("⚠️  Potential issues found:")
        for pattern in problematic_patterns:
            print(f"   - {pattern}")
        
        if template_literals:
            print("\n📝 Template literals found (showing first 3):")
            for i, literal in enumerate(template_literals[:3], 1):
                preview = literal[:50] + "..." if len(literal) > 50 else literal
                print(f"   {i}. {preview}")
        
        if dollar_braces:
            print("\n📝 Dollar brace expressions found (showing first 3):")
            for i, expr in enumerate(dollar_braces[:3], 1):
                print(f"   {i}. {expr}")
    
    # File statistics
    js_lines = len([line for line in content.split('\n') if '<script>' in line or '</script>' in line or (line.strip().startswith('//') or 'function' in line)])
    total_lines = len(content.split('\n'))
    
    print(f"\n📊 File Statistics:")
    print(f"   - Total lines: {total_lines}")
    print(f"   - File size: {len(content):,} characters")
    print(f"   - JavaScript sections detected")
    
    print(f"\n✅ Syntax check completed for {os.path.basename(file_path)}")
    
    return len(problematic_patterns) == 0

def main():
    # Get filename from command line argument or use default
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "ai_audio.html"
    
    # Check if it's a relative path, make it relative to current directory
    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)
    
    success = check_js_syntax(filename)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()