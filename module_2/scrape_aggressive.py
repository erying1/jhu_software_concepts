#!/usr/bin/env python3
"""
Alternative GradCafe parser with aggressive field extraction.
This version tries EVERY possible method to find fields.
"""

import json
import time
import re
from urllib import request, parse, error
from urllib.parse import urljoin
import urllib.robotparser
from datetime import datetime
import shelve

from bs4 import BeautifulSoup

USER_AGENT = "jhu-module2-scraper"

OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

DETAIL_CACHE = shelve.open("detail_cache_v2.db", writeback=True)
ERROR_LOG = []


def check_robots():
    """Check robots.txt."""
    robots_url = urljoin(BASE_URL, "robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    allowed = rp.can_fetch(USER_AGENT, urljoin(BASE_URL, "survey/"))
    return allowed


def _get_html(url: str, delay: float = 1.0) -> str:
    """Fetch HTML with rate limiting."""
    time.sleep(delay)
    with OPENER.open(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _aggressive_extract(soup, page_text):
    """
    Aggressively extract all possible fields from page.
    Returns a dict of all found label:value pairs.
    """
    fields = {}
    
    # Method 1: Table rows with ANY structure
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            
            # Two-column layout
            if len(cells) == 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                if label and value:
                    fields[label] = value
            
            # Sometimes labels are in <strong> or <b>
            for cell in cells:
                strong = cell.find(["strong", "b"])
                if strong:
                    label = strong.get_text(strip=True).lower()
                    # Get text after the strong tag
                    remaining = cell.get_text(strip=True)[len(strong.get_text(strip=True)):]
                    value = remaining.strip(": \n\t")
                    if label and value:
                        fields[label] = value
    
    # Method 2: Definition lists
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            label = dt.get_text(strip=True).lower()
            value = dd.get_text(strip=True)
            if label and value:
                fields[label] = value
    
    # Method 3: Divs/Spans/P with "Label: Value" pattern
    for elem in soup.find_all(["div", "span", "p", "li"]):
        text = elem.get_text(strip=True)
        if ":" in text and len(text) < 300:
            parts = text.split(":", 1)
            if len(parts) == 2:
                label = parts[0].strip().lower()
                value = parts[1].strip()
                # Only if it looks like a field (not too long)
                if label and value and len(label) < 50:
                    fields[label] = value
    
    # Method 4: Text patterns (regex on full text)
    # Season/Term patterns
    for pattern in [r"Season:\s*([^\n,;]+)", r"Term:\s*([^\n,;]+)", 
                    r"Semester:\s*([^\n,;]+)", r"Applying Season:\s*([^\n,;]+"]:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            fields["_season_regex"] = match.group(1).strip()
    
    # GPA patterns
    for pattern in [r"GPA:\s*(\d+\.?\d*)", r"Grade Point Average:\s*(\d+\.?\d*)",
                    r"Undergrad GPA:\s*(\d+\.?\d*)?"]:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            fields["_gpa_regex"] = match.group(1).strip()
    
    # GRE patterns
    gre_patterns = {
        "_gre_v_regex": [r"GRE\s+V(?:erbal)?:\s*(\d+)", r"Verbal(?:\s+Reasoning)?:\s*(\d+)"],
        "_gre_q_regex": [r"GRE\s+Q(?:uant)?:\s*(\d+)", r"Quantitative(?:\s+Reasoning)?:\s*(\d+)"],
        "_gre_aw_regex": [r"GRE\s+(?:AW|Writing):\s*(\d+\.?\d*)", r"Analytical\s+Writing:\s*(\d+\.?\d*)"],
    }
    
    for field_key, pattern_list in gre_patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                fields[field_key] = match.group(1).strip()
                break
    
    # Citizenship patterns
    for pattern in [r"(?:Status|Citizenship):\s*([AI])", r"International:\s*(Yes|No)",
                    r"(?:U\.?S\.?\s+)?(?:Citizen|Student):\s*(Yes|No)"]:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            fields["_citizenship_regex"] = match.group(1).strip()
    
    return fields


def _smart_field_lookup(fields, search_terms, default=None):
    """
    Look up a field in the extracted fields dict using multiple search terms.
    Returns the first matching value found.
    """
    # First try exact matches
    for term in search_terms:
        if term in fields:
            val = fields[term]
            if val and val.lower() not in ["n/a", "none", "", "-"]:
                return val
    
    # Then try partial matches
    for term in search_terms:
        for key in fields:
            if term in key:
                val = fields[key]
                if val and val.lower() not in ["n/a", "none", "", "-"]:
                    return val
    
    return default


def _parse_detail_page_html(entry_url: str, use_cache: bool = True) -> dict:
    """
    Ultra-aggressive detail page parser.
    """
    default_detail = {
        "comments": None,
        "term": None,
        "citizenship": None,
        "gpa": None,
        "gre_total": None,
        "gre_v": None,
        "gre_q": None,
        "gre_aw": None,
    }
    
    if not entry_url:
        return default_detail
    
    # Extract ID for caching
    result_id = None
    m = re.search(r"[?&]id=(\d+)", entry_url)
    if m:
        result_id = m.group(1)
    
    # Check cache
    if use_cache and result_id and result_id in DETAIL_CACHE:
        return DETAIL_CACHE[result_id]
    
    try:
        time.sleep(0.75)
        html = _get_html(entry_url, delay=0)
        soup = BeautifulSoup(html, "html.parser")
        page_text = soup.get_text()
        
        # Get all possible fields
        all_fields = _aggressive_extract(soup, page_text)
        
        detail = default_detail.copy()
        
        # TERM / SEASON
        term = _smart_field_lookup(all_fields, 
            ["season", "term", "semester", "applying season", "applying for", "_season_regex"])
        if term:
            detail["term"] = term
        
        # CITIZENSHIP
        citizenship = _smart_field_lookup(all_fields,
            ["status", "citizenship", "international", "student type", 
             "student status", "residency", "_citizenship_regex"])
        if citizenship:
            # Map common values
            cit_lower = citizenship.lower()
            if cit_lower in ["a", "american", "u.s.", "us", "usa", "domestic", "yes"] or "american" in cit_lower:
                detail["citizenship"] = "American"
            elif cit_lower in ["i", "international", "no"] or "international" in cit_lower:
                detail["citizenship"] = "International"
            else:
                detail["citizenship"] = citizenship
        
        # GPA
        gpa_str = _smart_field_lookup(all_fields,
            ["gpa", "grade point average", "undergraduate gpa", "_gpa_regex"])
        if gpa_str:
            gpa_match = re.search(r"(\d+\.?\d*)", gpa_str)
            if gpa_match:
                gpa_val = float(gpa_match.group(1))
                # Sanity check (GPA should be 0-4 or 0-10 scale)
                if 0 <= gpa_val <= 10:
                    detail["gpa"] = gpa_val
        
        # GRE VERBAL
        gre_v_str = _smart_field_lookup(all_fields,
            ["gre v", "gre verbal", "verbal", "verbal reasoning", 
             "gre general (v)", "gre general: v", "_gre_v_regex"])
        if gre_v_str:
            gre_v_match = re.search(r"(\d+)", gre_v_str)
            if gre_v_match:
                gre_v = int(gre_v_match.group(1))
                # New GRE verbal is 130-170
                if 130 <= gre_v <= 170:
                    detail["gre_v"] = gre_v
        
        # GRE QUANTITATIVE
        gre_q_str = _smart_field_lookup(all_fields,
            ["gre q", "gre quant", "quantitative", "quantitative reasoning",
             "gre general (q)", "gre general: q", "_gre_q_regex"])
        if gre_q_str:
            gre_q_match = re.search(r"(\d+)", gre_q_str)
            if gre_q_match:
                gre_q = int(gre_q_match.group(1))
                if 130 <= gre_q <= 170:
                    detail["gre_q"] = gre_q
        
        # GRE ANALYTICAL WRITING
        gre_aw_str = _smart_field_lookup(all_fields,
            ["gre aw", "gre w", "gre writing", "analytical writing",
             "writing", "gre general (aw)", "gre general: aw", "_gre_aw_regex"])
        if gre_aw_str:
            gre_aw_match = re.search(r"(\d+\.?\d*)", gre_aw_str)
            if gre_aw_match:
                gre_aw = float(gre_aw_match.group(1))
                # AW is 0-6
                if 0 <= gre_aw <= 6:
                    detail["gre_aw"] = gre_aw
        
        # GRE TOTAL (usually V + Q)
        if detail.get("gre_v") and detail.get("gre_q"):
            detail["gre_total"] = detail["gre_v"] + detail["gre_q"]
        
        # COMMENTS
        # Look for longer text blocks (comments are usually 50+ chars)
        comments = None
        
        # Try to find a field labeled as comments
        comments = _smart_field_lookup(all_fields,
            ["comments", "notes", "user notes", "additional info"])
        
        # If not found, look for longer text in specific elements
        if not comments or len(comments) < 20:
            for elem in soup.find_all(["div", "p", "blockquote", "td"]):
                text = elem.get_text(strip=True)
                # Comments are usually substantial text
                if 50 <= len(text) <= 5000:
                    # Skip navigation/header/footer
                    if elem.find_parent(["nav", "header", "footer", "script"]):
                        continue
                    # Skip common page elements
                    if any(skip in text.lower() for skip in 
                          ["copyright", "privacy", "terms", "search", "filter", 
                           "sort by", "results per page", "navigation"]):
                        continue
                    # This might be comments
                    if not comments or len(text) > len(comments):
                        comments = text
        
        if comments and len(comments) >= 20:
            detail["comments"] = comments
        
        # Cache the result
        if result_id:
            DETAIL_CACHE[result_id] = detail
        
        return detail
        
    except Exception as e:
        ERROR_LOG.append({
            "type": "PARSE_ERROR",
            "url": entry_url,
            "error": f"{type(e).__name__}: {str(e)}"
        })
        return default_detail


def _parse_row(tr, base_entry_url: str) -> dict:
    """Parse table row from list view."""
    tds = tr.find_all("td", recursive=False)
    if len(tds) < 5:
        return None

    # University
    uni_div = tds[0].find("div", class_="tw-font-medium")
    university = uni_div.get_text(strip=True) if uni_div else None

    # Program + Degree
    program = degree_level = None
    prog_div = tds[1].find("div")
    if prog_div:
        spans = prog_div.find_all("span")
        if spans:
            program = spans[0].get_text(strip=True)
        if len(spans) > 1:
            degree_level = spans[1].get_text(strip=True)

    # Date Added
    date_added = tds[2].get_text(strip=True)

    # Status + Status Date
    status_block = tds[3].get_text(" ", strip=True)
    status = status_date = None
    m = re.match(r"(Accepted|Rejected|Interview|Wait listed|Other)\s+on\s+(.+)", 
                 status_block, re.I)
    if m:
        status = m.group(1).title()
        status_date = m.group(2)

    # Entry URL
    link = tds[4].find("a", href=True)
    entry_url = urljoin(base_entry_url, link["href"]) if link else None

    # Base record
    record = {
        "program_name": program,
        "university": university,
        "date_added": date_added,
        "entry_url": entry_url,
        "status": status,
        "status_date": status_date,
        "degree_level": degree_level,
        "comments": None,
        "term": None,
        "citizenship": None,
        "gpa": None,
        "gre_total": None,
        "gre_v": None,
        "gre_q": None,
        "gre_aw": None,
    }

    # Fetch detail page
    if entry_url:
        detail = _parse_detail_page_html(entry_url)
        record.update(detail)

    return record


def scrape_data(max_entries: int = 100, start_page: int = 1, 
                checkpoint_interval: int = 3):
    """Main scraping function."""
    all_entries = []
    page = start_page

    print(f"Starting scrape")
    print(f"Target: {max_entries} entries")
    print(f"Cached: {len(DETAIL_CACHE)}")
    print("-" * 60)

    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        
        try:
            print(f"\nPage {page}:")
            html = _get_html(url, delay=1.0)
        except Exception as e:
            print(f"  Error: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        rows = [tr for tr in rows if tr.find("td")]

        if not rows:
            break

        for tr in rows:
            entry = _parse_row(tr, url)
            if entry:
                all_entries.append(entry)
                
                if len(all_entries) % 10 == 0:
                    print(f"  {len(all_entries)} entries scraped")
                
                if len(all_entries) >= max_entries:
                    break

        # Stats
        n = len(all_entries)
        stats = {
            "Comm": sum(1 for e in all_entries if e.get("comments")),
            "GPA": sum(1 for e in all_entries if e.get("gpa")),
            "V": sum(1 for e in all_entries if e.get("gre_v")),
            "Q": sum(1 for e in all_entries if e.get("gre_q")),
            "AW": sum(1 for e in all_entries if e.get("gre_aw")),
            "Tot": sum(1 for e in all_entries if e.get("gre_total")),
            "Term": sum(1 for e in all_entries if e.get("term")),
            "Cit": sum(1 for e in all_entries if e.get("citizenship")),
        }
        
        print(f"  Total: {n}/{max_entries}")
        print(f"  Coverage: ", end="")
        for field, count in stats.items():
            pct = count*100//n if n > 0 else 0
            print(f"{field}={pct}% ", end="")
        print()

        # Checkpoint
        if page % checkpoint_interval == 0:
            with open("checkpoint.json", "w", encoding="utf-8") as f:
                json.dump({"entries": all_entries, "last_page": page}, 
                         f, ensure_ascii=False, indent=2)
            print(f"  ✓ Checkpoint saved")

        page += 1

    # Final stats
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    n = len(all_entries)
    fields = ["comments", "gpa", "gre_v", "gre_q", "gre_aw", "gre_total", "term", "citizenship"]
    for field in fields:
        count = sum(1 for e in all_entries if e.get(field))
        pct = count*100//n if n > 0 else 0
        print(f"  {field:15s}: {count:4d} / {n} ({pct:3d}%)")

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    data = scrape_data(max_entries=100, start_page=1)

    import os
    os.makedirs("module_2", exist_ok=True)
    
    with open("module_2/llm_extend_applicant_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to module_2/llm_extend_applicant_data.json")
    
    DETAIL_CACHE.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
        DETAIL_CACHE.close()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        DETAIL_CACHE.close()
