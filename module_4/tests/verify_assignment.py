"""
Verification script to check if all required assignment tests exist
and have proper markers.

Required by assignment:
1. test_flask_page.py with @pytest.mark.web
2. test_buttons.py with @pytest.mark.buttons
3. test_analysis_format.py with @pytest.mark.analysis
4. test_db_insert.py with @pytest.mark.db
5. test_integration_end_to_end.py with @pytest.mark.integration

Run this to verify: python verify_assignment.py
"""

import os
import re

def check_test_file(filepath, required_marker):
    """Check if a test file exists and has the required marker."""
    if not os.path.exists(filepath):
        return False, f"❌ File missing: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for marker
    marker_pattern = f'@pytest\\.mark\\.{required_marker}'
    if not re.search(marker_pattern, content):
        return False, f"⚠️  Missing marker @pytest.mark.{required_marker} in {filepath}"
    
    return True, f"✅ {filepath} has @pytest.mark.{required_marker}"


def main():
    """Verify all required assignment tests."""
    print("=" * 70)
    print("ASSIGNMENT TEST VERIFICATION")
    print("=" * 70)
    
    required_tests = [
        ("tests/test_flask_page.py", "web"),
        ("tests/test_buttons.py", "buttons"),
        ("tests/test_analysis_format.py", "analysis"),
        ("tests/test_db_insert.py", "db"),
        ("tests/test_integration_end_to_end.py", "integration"),
    ]
    
    all_good = True
    
    for filepath, marker in required_tests:
        success, message = check_test_file(filepath, marker)
        print(message)
        if not success:
            all_good = False
    
    print("=" * 70)
    
    # Check pytest.ini
    if os.path.exists("pytest.ini"):
        with open("pytest.ini", 'r') as f:
            content = f.read()
        
        markers_defined = all(marker in content for marker in ["web", "buttons", "analysis", "db", "integration"])
        if markers_defined:
            print("✅ pytest.ini has all required markers defined")
        else:
            print("⚠️  pytest.ini missing some marker definitions")
            all_good = False
    else:
        print("❌ pytest.ini not found")
        all_good = False
    
    print("=" * 70)
    
    if all_good:
        print("🎉 ALL ASSIGNMENT REQUIREMENTS MET!")
    else:
        print("⚠️  SOME REQUIREMENTS MISSING - See above")
    
    print("=" * 70)
    
    # Additional checks
    print("\nADDITIONAL CHECKS:")
    print("-" * 70)
    
    # Check for unmarked tests
    test_files = []
    for root, dirs, files in os.walk("tests"):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    
    print(f"Total test files found: {len(test_files)}")
    
    # Count files without markers
    unmarked = []
    for filepath in test_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if '@pytest.mark.' not in content:
            unmarked.append(filepath)
    
    if unmarked:
        print(f"\n⚠️  {len(unmarked)} test files without any markers:")
        for f in unmarked:
            print(f"   - {f}")
        print("\nAssignment requires: ALL tests must be marked")
    else:
        print("✅ All test files have markers")


if __name__ == "__main__":
    main()
