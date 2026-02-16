#!/usr/bin/env python3
"""
Fetch a real GradCafe detail page to see its actual structure.
Run this to get a sample HTML file we can inspect.
"""

from urllib import request, parse
from bs4 import BeautifulSoup
import json

USER_AGENT = "jhu-module2-scraper"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

def get_first_detail_url():
    """Get the detail URL from the first entry on page 1."""
    opener = request.build_opener()
    opener.addheaders = [("User-Agent", USER_AGENT)]
    
    # Fetch page 1 of search results
    url = SEARCH_URL + "?" + parse.urlencode({"page": 1})
    print(f"Fetching list page: {url}")
    
    with opener.open(url, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find first detail link
    rows = soup.select("table tr")
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) >= 5:
            link = tds[4].find("a", href=True)
            if link:
                from urllib.parse import urljoin
                detail_url = urljoin(url, link["href"])
                print(f"Found detail URL: {detail_url}")
                return detail_url, opener
    
    return None, None


def fetch_and_save_detail_page(url, opener):
    """Fetch the detail page and save HTML."""
    print(f"\nFetching detail page: {url}")
    
    with opener.open(url, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    # Save raw HTML
    with open("sample_detail.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✓ Saved to: sample_detail.html")
    
    # Parse and show structure
    soup = BeautifulSoup(html, "html.parser")
    
    print("\n" + "="*80)
    print("HTML STRUCTURE ANALYSIS")
    print("="*80)
    
    # Find all tables
    tables = soup.find_all("table")
    print(f"\nFound {len(tables)} table(s)")
    
    for i, table in enumerate(tables, 1):
        print(f"\n--- TABLE {i} ---")
        rows = table.find_all("tr")[:15]  # First 15 rows
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) == 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)[:100]  # Truncate long values
                print(f"  {label:30s} | {value}")
            elif len(cells) == 1:
                print(f"  {cells[0].get_text(strip=True)[:80]}")
    
    # Find all definition lists
    dls = soup.find_all("dl")
    if dls:
        print(f"\nFound {len(dls)} definition list(s)")
        for i, dl in enumerate(dls, 1):
            print(f"\n--- DEFINITION LIST {i} ---")
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True)
                value = dd.get_text(strip=True)[:100]
                print(f"  {label:30s} | {value}")
    
    # Look for key text patterns
    print("\n" + "="*80)
    print("SEARCHING FOR KEY FIELDS IN PAGE TEXT")
    print("="*80)
    
    page_text = soup.get_text()
    
    # Search for specific patterns
    patterns = {
        "Season/Term": [r"Season[:\s]+([^\n]+)", r"Term[:\s]+([^\n]+)", r"Semester[:\s]+([^\n]+)"],
        "GPA": [r"GPA[:\s]+(\d+\.?\d*)", r"Grade Point Average[:\s]+(\d+\.?\d*)"],
        "GRE Verbal": [r"GRE\s+V[:\s]+(\d+)", r"GRE\s+Verbal[:\s]+(\d+)", r"Verbal[:\s]+(\d+)"],
        "GRE Quant": [r"GRE\s+Q[:\s]+(\d+)", r"GRE\s+Quant[:\s]+(\d+)", r"Quantitative[:\s]+(\d+)"],
        "GRE AW": [r"GRE\s+AW[:\s]+(\d+\.?\d*)", r"GRE\s+Writing[:\s]+(\d+\.?\d*)", r"Analytical\s+Writing[:\s]+(\d+\.?\d*)"],
        "Citizenship": [r"Citizenship[:\s]+([^\n]+)", r"International[:\s]+([^\n]+)", r"Student Type[:\s]+([^\n]+)"],
    }
    
    import re
    found_any = False
    for field, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                print(f"\n✓ {field}: {match.group(1).strip()}")
                print(f"  Pattern: {pattern}")
                found_any = True
                break
    
    if not found_any:
        print("\n⚠ No standard field patterns found in text!")
        print("\nShowing first 2000 characters of page text:")
        print("-"*80)
        print(page_text[:2000])
    
    # Show page structure
    print("\n" + "="*80)
    print("PAGE STRUCTURE (Main content divs)")
    print("="*80)
    
    # Look for main content
    for div in soup.find_all("div", class_=True):
        classes = " ".join(div.get("class", []))
        if any(word in classes.lower() for word in ["content", "main", "result", "detail", "entry", "data"]):
            print(f"\nDiv class: {classes}")
            text_preview = div.get_text(strip=True)[:300]
            print(f"Content: {text_preview}...")
    
    # Try to extract specific fields based on common patterns
    print("\n" + "="*80)
    print("EXTRACTION ATTEMPT")
    print("="*80)
    
    extracted = {}
    
    # Try to find in table rows
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                if any(x in label for x in ["season", "term", "semester", "applying"]):
                    extracted["term"] = value
                elif "gpa" in label and "undergrad" not in label:
                    extracted["gpa"] = value
                elif "gre" in label:
                    if "v" in label or "verbal" in label:
                        extracted["gre_v"] = value
                    elif "q" in label or "quant" in label:
                        extracted["gre_q"] = value
                    elif "aw" in label or "writing" in label or "analytical" in label:
                        extracted["gre_aw"] = value
                elif any(x in label for x in ["citizenship", "international", "student type"]):
                    extracted["citizenship"] = value
    
    print("\nExtracted fields:")
    print(json.dumps(extracted, indent=2))
    
    if not extracted:
        print("\n⚠ WARNING: Could not extract any fields!")
        print("The HTML structure might be different than expected.")
        print("\nPlease inspect sample_detail.html manually to see the actual structure.")


if __name__ == "__main__":
    print("GradCafe Detail Page Fetcher & Analyzer")
    print("="*80)
    
    try:
        detail_url, opener = get_first_detail_url()
        
        if detail_url:
            fetch_and_save_detail_page(detail_url, opener)
            print("\n" + "="*80)
            print("NEXT STEPS:")
            print("="*80)
            print("1. Open 'sample_detail.html' in a browser")
            print("2. Look for where Term, Citizenship, GRE scores appear")
            print("3. View page source to see exact HTML structure")
            print("4. Share findings so we can fix the parser")
        else:
            print("Could not find a detail URL")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
