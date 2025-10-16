#!/usr/bin/env python3
"""
Script to replace old snackbar patterns with the new show_snack() method from BaseView.
"""

import re
import os

def replace_snackbar_pattern(content):
    """Replace old snackbar patterns with show_snack() calls."""
    
    # Pattern 1: Multi-line snackbar with RED color (error)
    pattern1 = r'self\.page\.snack_bar = ft\.SnackBar\(\s*content=ft\.Text\("([^"]+)"\),\s*bgcolor=ft\.Colors\.RED_\d+\s*\)\s*self\.page\.snack_bar\.open = True\s*self\.page\.update\(\)'
    content = re.sub(pattern1, r'self.show_snack("\1", is_error=True)', content, flags=re.MULTILINE)
    
    # Pattern 2: Multi-line snackbar with GREEN color (success)
    pattern2 = r'self\.page\.snack_bar = ft\.SnackBar\(\s*content=ft\.Text\(([^)]+)\),\s*bgcolor=ft\.Colors\.GREEN_\d+\s*\)\s*self\.page\.snack_bar\.open = True\s*self\.page\.update\(\)'
    content = re.sub(pattern2, r'self.show_snack(\1)', content, flags=re.MULTILINE)
    
    # Pattern 3: Compact format with .open and .update on same lines
    pattern3 = r'self\.page\.snack_bar = ft\.SnackBar\(content=ft\.Text\("([^"]+)"\), bgcolor=ft\.Colors\.RED_\d+\)\s*self\.page\.snack_bar\.open = True'
    content = re.sub(pattern3, r'self.show_snack("\1", is_error=True)', content)
    
    pattern4 = r'self\.page\.snack_bar = ft\.SnackBar\(content=ft\.Text\(([^)]+)\), bgcolor=ft\.Colors\.GREEN_\d+\)\s*self\.page\.snack_bar\.open = True'
    content = re.sub(pattern4, r'self.show_snack(\1)', content)
    
    return content

def process_file(filepath):
    """Process a single file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    content = replace_snackbar_pattern(content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
        return True
    else:
        print(f"  - No changes needed in {filepath}")
        return False

def main():
    """Main function."""
    views_dir = "views"
    files_to_process = [
        os.path.join(views_dir, "file_selector_view.py"),
        os.path.join(views_dir, "update_csv_view.py"),
    ]
    
    updated_count = 0
    for filepath in files_to_process:
        if os.path.exists(filepath):
            if process_file(filepath):
                updated_count += 1
        else:
            print(f"File not found: {filepath}")
    
    print(f"\n✓ Done! Updated {updated_count} file(s)")

if __name__ == "__main__":
    main()
