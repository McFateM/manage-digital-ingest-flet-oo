#!/usr/bin/env python3
"""
Test script for the Object-Oriented structure

This script tests that all imports work correctly and classes can be instantiated.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    try:
        # Test base imports
        print("Testing imports...")
        
        # Test view imports
        from views import (
            BaseView, HomeView, AboutView, SettingsView, 
            ExitView, FileSelectorView, DerivativesView, 
            StorageView, LogView, LogOverlay
        )
        print("✅ Views package imported successfully")
        
        # Test main app import
        from app import MDIApplication
        print("✅ MDIApplication imported successfully")
        
        # Test utility imports
        import utils
        print("✅ Utils module imported successfully")
        
        print("\\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_class_structure():
    """Test that classes can be instantiated (without Flet page)."""
    try:
        print("\\nTesting class structure...")
        
        # Test that we can import the application class
        from app import MDIApplication
        app = MDIApplication()
        print("✅ MDIApplication instantiated successfully")
        
        # Test logging setup
        app.setup_logging()
        print("✅ Logging setup completed")
        
        print("\\n🎉 Class structure test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Class structure error: {e}")
        return False

def test_file_structure():
    """Test that all expected files exist."""
    expected_files = [
        'app.py',
        'views/__init__.py',
        'views/base_view.py',
        'views/home_view.py',
        'views/about_view.py',
        'views/settings_view.py',
        'views/exit_view.py',
        'views/file_selector_view.py',
        'views/derivatives_view.py',
        'views/storage_view.py',
        'views/log_view.py',
        'views/log_overlay.py',
        'OO_MIGRATION.md'
    ]
    
    print("\\nTesting file structure...")
    missing_files = []
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\\n🎉 All expected files exist!")
        return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("OO STRUCTURE TEST")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_class_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\\n" + "=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED! OO structure is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 50)

if __name__ == "__main__":
    main()