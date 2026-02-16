#!/usr/bin/env python3
"""
Diagnostic tool: Fetch one GradCafe detail page and show what's actually there.
This will help us understand why term extraction isn't working.
"""

from urllib import request
from bs4 import BeautifulSoup
import re

USER_AGENT = "jhu-module2-scraper"
OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

# Test a specific result ID
test_url = "https://www.thegradcafe.com/result/997749"

print("Fetching detail page...")
print(f"URL: {test_url}")
print("=" * 80)

try:
    with OPENER.open(test_url, timeout=10) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Get all text
    page_text = soup.get_text()
    
    # Print first 2000 characters to see structure
    print("\nFirst 2000 characters of page text:")
    print("-" * 80)
    print(page_text[:2000])
    print("-" * 80)
    
    # Look for specific fields
    print("\n\nSearching for key fields:")
    print("-" * 80)
    
    # GPA
    gpa_match = re.search(r'GPA:?\s*(\d+\.\d+)', page_text, re.I)
    if gpa_match:
        print(f"✓ GPA found: {gpa_match.group(1)}")
    else:
        print("✗ GPA not found")
    
    # Term
    term_patterns = [
        (r'(Fall|Spring|Summer|Winter)\s+(\d{4})', "Full format (Fall 2026)"),
        (r'([FS])\s*\'?(\d{2})', "Abbreviated (F26, S26)"),
        (r'Season:?\s*(Fall|Spring|Summer|Winter)', "Season field"),
        (r'Term:?\s*(\w+)', "Term field"),
    ]
    
    term_found = False
    for pattern, desc in term_patterns:
        match = re.search(pattern, page_text, re.I)
        if match:
            print(f"✓ Term found ({desc}): {match.group(0)}")
            term_found = True
    
    if not term_found:
        print("✗ Term not found with any pattern")
    
    # Citizenship
    if re.search(r'\bInternational\b', page_text, re.I):
        print("✓ Citizenship found: International")
    elif re.search(r'\bAmerican\b|\bU\.?S\.?\b|\bDomestic\b', page_text, re.I):
        print("✓ Citizenship found: American")
    else:
        print("✗ Citizenship not found")
    
    # GRE
    gre_v = re.search(r'(?:GRE\s*)?V(?:erbal)?:?\s*(\d+)', page_text, re.I)
    gre_q = re.search(r'(?:GRE\s*)?Q(?:uant)?:?\s*(\d+)', page_text, re.I)
    
    if gre_v:
        print(f"✓ GRE Verbal found: {gre_v.group(1)}")
    else:
        print("✗ GRE Verbal not found")
    
    if gre_q:
        print(f"✓ GRE Quant found: {gre_q.group(1)}")
    else:
        print("✗ GRE Quant not found")
    
    # Look for all lines containing specific keywords
    print("\n\nLines containing 'GPA':")
    for line in page_text.split('\n'):
        if 'gpa' in line.lower() and line.strip():
            print(f"  {line.strip()[:100]}")
    
    print("\n\nLines containing 'Fall' or 'Spring':")
    for line in page_text.split('\n'):
        if ('fall' in line.lower() or 'spring' in line.lower()) and line.strip():
            print(f"  {line.strip()[:100]}")
    
    print("\n\nLines containing 'International' or 'American':")
    for line in page_text.split('\n'):
        if ('international' in line.lower() or 'american' in line.lower()) and line.strip():
            print(f"  {line.strip()[:100]}")
    
    # Save full HTML for inspection
    with open("detail_page_sample.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n\n✓ Full HTML saved to: detail_page_sample.html")
    print("  Open this file in a text editor to see the exact structure")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
