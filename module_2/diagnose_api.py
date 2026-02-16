#!/usr/bin/env python3
"""
Diagnostic script to check what GradCafe's API is actually returning.
"""

import json
from urllib import request

USER_AGENT = "jhu-module2-scraper"
OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

# Test a few different result IDs
test_ids = [997749, 997748, 997700, 990000, 980000, 970000]

print("Testing GradCafe API endpoints...")
print("=" * 60)

for result_id in test_ids:
    api_url = f"https://www.thegradcafe.com/api/result/{result_id}"
    print(f"\nTesting ID {result_id}:")
    print(f"URL: {api_url}")
    
    try:
        with OPENER.open(api_url, timeout=10) as resp:
            # Get the raw content
            raw_content = resp.read().decode("utf-8", errors="ignore")
            
            print(f"Status: {resp.status}")
            print(f"Content-Type: {resp.headers.get('Content-Type')}")
            print(f"Length: {len(raw_content)} bytes")
            print(f"First 200 chars: {raw_content[:200]}")
            
            # Try to parse as JSON
            try:
                data = json.loads(raw_content)
                print(f"✓ Valid JSON")
                print(f"Keys: {list(data.keys())}")
                if 'gpa' in data:
                    print(f"  GPA: {data.get('gpa')}")
                if 'term' in data:
                    print(f"  Term: {data.get('term')}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON Parse Error: {e}")
                
    except Exception as e:
        print(f"✗ Request failed: {e}")

print("\n" + "=" * 60)
print("\nDiagnosis:")
print("If all IDs return HTML or errors, the API may not exist.")
print("If some work and some don't, older entries may not have API data.")
print("If the format is different, we need to adapt the scraper.")
