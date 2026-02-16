#!/usr/bin/env python3
"""
Debug diagnostic: Test detail page fetching to see why all fields are null.
This will fetch ONE detail page and show exactly what's happening.
"""

from urllib import request
from bs4 import BeautifulSoup
import re
import json

USER_AGENT = "jhu-module2-scraper"
OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

# Test with the first entry from your data
test_url = "https://www.thegradcafe.com/result/997783"

print("=" * 80)
print("DETAIL PAGE FETCH DIAGNOSTIC")
print("=" * 80)
print(f"\nTesting URL: {test_url}\n")

try:
    # Fetch the page
    print("1. Fetching page...")
    with OPENER.open(test_url, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    print(f"   ✓ Fetched {len(html)} bytes")
    
    # Parse with BeautifulSoup
    print("\n2. Parsing HTML...")
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text()
    print(f"   ✓ Extracted {len(page_text)} characters of text")
    
    # Show first 1000 characters
    print("\n3. First 1000 characters of page text:")
    print("-" * 80)
    print(page_text[:1000])
    print("-" * 80)
    
    # Test extraction patterns
    print("\n4. Testing extraction patterns:")
    print("-" * 80)
    
    result = {
        "gpa": None,
        "citizenship": None,
        "term": None,
        "gre_v": None,
        "gre_q": None,
        "gre_aw": None,
    }
    
    # GPA
    gpa_match = re.search(r'GPA[:\s]+(\d+\.?\d*)', page_text, re.I)
    if gpa_match:
        result['gpa'] = float(gpa_match.group(1))
        print(f"   ✓ GPA found: {result['gpa']}")
    else:
        print("   ✗ GPA not found")
        # Show lines with 'gpa'
        print("     Lines containing 'GPA':")
        for line in page_text.split('\n'):
            if 'gpa' in line.lower() and line.strip():
                print(f"       {line.strip()[:80]}")
    
    # Citizenship
    if 'international' in page_text.lower():
        result['citizenship'] = "International"
        print(f"   ✓ Citizenship: International")
    elif any(word in page_text.lower() for word in ['american', 'domestic', 'u.s']):
        result['citizenship'] = "American"
        print(f"   ✓ Citizenship: American")
    else:
        print("   ✗ Citizenship not found")
    
    # Term
    term_match = re.search(r'\b(Fall|Spring|Summer|Winter)\s+(\d{4})\b', page_text, re.I)
    if term_match:
        result['term'] = f"{term_match.group(1)} {term_match.group(2)}"
        print(f"   ✓ Term found: {result['term']}")
    else:
        print("   ✗ Term not found")
        print("     Lines containing 'fall', 'spring', 'season', or 'term':")
        for line in page_text.split('\n'):
            if any(word in line.lower() for word in ['fall', 'spring', 'season', 'term']) and line.strip():
                print(f"       {line.strip()[:80]}")
                if len([l for l in page_text.split('\n') if any(w in l.lower() for w in ['fall', 'spring'])]) > 10:
                    print("       (more than 10 lines - showing first few)")
                    break
    
    # GRE Verbal
    gre_v_match = re.search(r'(?:GRE\s+)?V(?:erbal)?[:\s]+(\d{3})', page_text, re.I)
    if gre_v_match:
        val = int(gre_v_match.group(1))
        if 130 <= val <= 170:
            result['gre_v'] = val
            print(f"   ✓ GRE Verbal found: {result['gre_v']}")
        else:
            print(f"   ✗ GRE Verbal found but out of range: {val}")
    else:
        print("   ✗ GRE Verbal not found")
    
    # GRE Quant
    gre_q_match = re.search(r'(?:GRE\s+)?Q(?:uant)?[:\s]+(\d{3})', page_text, re.I)
    if gre_q_match:
        val = int(gre_q_match.group(1))
        if 130 <= val <= 170:
            result['gre_q'] = val
            print(f"   ✓ GRE Quant found: {result['gre_q']}")
        else:
            print(f"   ✗ GRE Quant found but out of range: {val}")
    else:
        print("   ✗ GRE Quant not found")
    
    # GRE AW
    gre_aw_match = re.search(r'(?:GRE\s+)?(?:AW|Writing)[:\s]+(\d+\.?\d*)', page_text, re.I)
    if gre_aw_match:
        val = float(gre_aw_match.group(1))
        if 0 <= val <= 6:
            result['gre_aw'] = val
            print(f"   ✓ GRE AW found: {result['gre_aw']}")
        else:
            print(f"   ✗ GRE AW found but out of range: {val}")
    else:
        print("   ✗ GRE AW not found")
        # Check for the 0.0 false match
        if '0.0' in page_text or '0' in page_text:
            print("     Note: Found '0' or '0.0' in page - may be causing false matches")
    
    # Summary
    print("\n5. Extraction Result:")
    print("-" * 80)
    print(json.dumps(result, indent=2))
    
    # Check HTML structure
    print("\n6. HTML Structure Analysis:")
    print("-" * 80)
    
    # Count elements
    divs = len(soup.find_all('div'))
    ps = len(soup.find_all('p'))
    dts = len(soup.find_all('dt'))
    dds = len(soup.find_all('dd'))
    
    print(f"   Divs: {divs}")
    print(f"   Paragraphs: {ps}")
    print(f"   Definition terms (dt): {dts}")
    print(f"   Definition descriptions (dd): {dds}")
    
    # Look for specific patterns in HTML
    print("\n7. Searching HTML for data fields:")
    print("-" * 80)
    
    # Check if there's a table or definition list with the data
    for element in soup.find_all(['table', 'dl', 'ul']):
        text = element.get_text(strip=True)[:200]
        if any(keyword in text.lower() for keyword in ['gpa', 'gre', 'term', 'season']):
            print(f"   Found potential data in <{element.name}>:")
            print(f"   {text}...")
    
    # Save full HTML for manual inspection
    with open("detail_page_full.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("\n8. Full HTML saved to: detail_page_full.html")
    print("   Open this file to manually inspect the page structure")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
    if result['citizenship'] and not any([result['gpa'], result['term'], result['gre_v']]):
        print("\n💡 FINDING: Citizenship works, but academic fields don't")
        print("   → These fields may not be displayed on GradCafe pages")
        print("   → Or they're in a format we're not detecting")
    
    if all(v is None for v in result.values()):
        print("\n⚠️  WARNING: NO fields extracted successfully")
        print("   → Detail page may be structured very differently")
        print("   → Or data isn't available on these pages")
    
    print("\n📋 Next step: Open detail_page_full.html and search for:")
    print("   - 'GPA' or '3.' (GPA values)")
    print("   - 'Fall' or 'Spring' (terms)")
    print("   - '16' (GRE scores start with 1)")
    print("   If you can't find these, the data isn't there to scrape!")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
