#!/usr/bin/env python3
"""
Quick test script for the improved GradCafe scraper.
Tests with just 10 entries to verify data collection works.
"""

import json
import sys

# Add the current directory to path to import the scraper
sys.path.insert(0, '.')

from scrape_exact_improved import scrape_data, check_robots


def test_scraper():
    """Test the scraper with a small sample."""
    
    print("=" * 60)
    print("GRADCAFE SCRAPER TEST")
    print("=" * 60)
    
    # Check robots.txt
    print("\n1. Checking robots.txt...")
    if not check_robots():
        print("   ❌ FAILED: robots.txt disallows scraping")
        return False
    print("   ✓ PASSED: robots.txt allows scraping")
    
    # Scrape 10 entries
    print("\n2. Scraping 10 test entries...")
    try:
        data = scrape_data(max_entries=100, start_page=1)
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    if len(data) == 0:
        print("   ❌ FAILED: No data collected")
        return False
    
    print(f"   ✓ PASSED: Collected {len(data)} entries")
    
    # Check data structure
    print("\n3. Validating data structure...")
    required_fields = [
        "program_name", "university", "date_added", "entry_url",
        "status", "degree_level"
    ]
    
    detail_fields = [
        "comments", "term", "citizenship", "gpa",
        "gre_total", "gre_v", "gre_q", "gre_aw"
    ]
    
    for field in required_fields:
        if field not in data[0]:
            print(f"   ❌ FAILED: Missing field '{field}'")
            return False
    print("   ✓ PASSED: All required fields present")
    
    # Check detail field coverage
    print("\n4. Checking detail field coverage...")
    total = len(data)
    coverage = {}
    
    for field in detail_fields:
        count = sum(1 for entry in data if entry.get(field) not in (None, "", "null"))
        coverage[field] = (count, count * 100 // total if total > 0 else 0)
    
    print("\n   Field Coverage:")
    for field, (count, pct) in coverage.items():
        print(f"   - {field:15s}: {count}/{total} ({pct}%)")
    
    # At least some entries should have detail data
    total_detail_entries = sum(1 for entry in data 
                               if any(entry.get(f) not in (None, "", "null") 
                                     for f in detail_fields))
    
    if total_detail_entries == 0:
        print("\n   ⚠ WARNING: No entries have detail data")
        print("   This may indicate the API endpoint isn't working.")
    else:
        print(f"\n   ✓ PASSED: {total_detail_entries}/{total} entries have detail data")
    
    # Display sample entries
    print("\n5. Sample entries with data:")
    samples_shown = 0
    for entry in data:
        if any(entry.get(f) not in (None, "", "null") for f in detail_fields):
            print(f"\n   Entry: {entry.get('university')} - {entry.get('program_name')}")
            print(f"   Status: {entry.get('status')} ({entry.get('degree_level')})")
            
            if entry.get('gpa'):
                print(f"   GPA: {entry.get('gpa')}")
            
            if entry.get('gre_v') or entry.get('gre_q'):
                print(f"   GRE: V={entry.get('gre_v')}, Q={entry.get('gre_q')}, AW={entry.get('gre_aw')}")
            
            if entry.get('citizenship'):
                print(f"   Citizenship: {entry.get('citizenship')}")
            
            if entry.get('term'):
                print(f"   Term: {entry.get('term')}")
            
            if entry.get('comments'):
                comment = entry.get('comments')[:80] + "..." if len(entry.get('comments', '')) > 80 else entry.get('comments')
                print(f"   Comments: {comment}")
            
            samples_shown += 1
            if samples_shown >= 3:
                break
    
    # Save test data
    print("\n6. Saving test data...")
    try:
        with open("test_scraper_output.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("   ✓ PASSED: Test data saved to test_scraper_output.json")
    except Exception as e:
        print(f"   ❌ FAILED: Could not save test data: {e}")
        return False
    
    # Final verdict
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if total_detail_entries > 0:
        print("✓ SUCCESS: Scraper is working correctly!")
        print(f"  - Collected {len(data)} entries")
        print(f"  - {total_detail_entries} entries have detail data")
        print(f"  - Ready for full scrape")
    else:
        print("⚠ PARTIAL SUCCESS: Basic scraping works, but no detail data")
        print("  - This may be normal if recent entries lack detail")
        print("  - Try increasing to 50-100 entries for better coverage")
    
    return True


if __name__ == "__main__":
    try:
        success = test_scraper()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
