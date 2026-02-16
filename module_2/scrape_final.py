#!/usr/bin/env python3
"""
Improved GradCafe scraper with comprehensive field extraction.
Handles multiple HTML structures and field name variations.
"""

import json
import time
import re
from urllib import request, parse, error
from urllib.parse import urljoin
import urllib.robotparser
from datetime import datetime
import shelve
import sys

from bs4 import BeautifulSoup

USER_AGENT = "jhu-module2-scraper"

OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

DETAIL_CACHE = shelve.open("detail_cache.db", writeback=True)
ERROR_LOG = []


def log_error(error_type, message, details=None):
    """Log errors for debugging."""
    error_entry = {
        "type": error_type,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    ERROR_LOG.append(error_entry)


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
    try:
        with OPENER.open(url, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        log_error("HTTP_ERROR", f"Failed to fetch {url}", str(e))
        raise


def _extract_numeric(text, is_float=False):
    """Extract numeric value from text."""
    if not text:
        return None
    
    # Remove common text
    text = str(text).replace("n/a", "").replace("N/A", "").strip()
    
    if is_float:
        match = re.search(r"(\d+\.?\d*)", text)
        return float(match.group(1)) if match else None
    else:
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else None


def _parse_detail_page_html(entry_url: str, use_cache: bool = True) -> dict:
    """
    Comprehensive parsing of GradCafe detail pages.
    Tries multiple methods to extract all fields.
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
    
    # Fetch the detail page
    try:
        time.sleep(0.75)
        html = _get_html(entry_url, delay=0)
        soup = BeautifulSoup(html, "html.parser")
        
        detail = default_detail.copy()
        
        # Create a field map for flexible matching
        field_data = {}
        
        # Method 1: Parse all table rows
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    field_data[label] = value
        
        # Method 2: Parse definition lists
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True).lower()
                value = dd.get_text(strip=True)
                field_data[label] = value
        
        # Method 3: Parse labeled divs/spans
        for elem in soup.find_all(["div", "span", "p"]):
            text = elem.get_text(strip=True)
            # Look for "Label: Value" pattern
            if ":" in text and len(text) < 200:
                parts = text.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip().lower()
                    value = parts[1].strip()
                    if label and value:
                        field_data[label] = value
        
        # Now extract fields from the collected data
        
        # TERM / SEASON
        for key in field_data:
            if any(term in key for term in ["season", "term", "semester", "applying season"]):
                value = field_data[key]
                # Extract just the term (e.g., "F25" or "Fall 2025")
                if value and value.lower() not in ["n/a", "none", ""]:
                    detail["term"] = value
                    break
        
        # CITIZENSHIP
        for key in field_data:
            if any(term in key for term in ["citizenship", "international", "student type", "residency"]):
                value = field_data[key]
                if value and value.lower() not in ["n/a", "none", ""]:
                    # Skip if it looks like a decision status
                    if value not in ["Accepted", "Rejected", "Interview", "Wait listed", "Other"]:
                        detail["citizenship"] = value
                        break
        
        # GPA
        for key in field_data:
            if "gpa" in key or "grade point" in key:
                value = field_data[key]
                gpa = _extract_numeric(value, is_float=True)
                if gpa:
                    detail["gpa"] = gpa
                    break
        
        # GRE VERBAL
        for key in field_data:
            if any(term in key for term in ["gre v", "gre verbal", "verbal reasoning", "gre general (v)"]):
                value = field_data[key]
                gre_v = _extract_numeric(value)
                if gre_v:
                    detail["gre_v"] = gre_v
                    break
        
        # GRE QUANTITATIVE
        for key in field_data:
            if any(term in key for term in ["gre q", "gre quant", "quantitative reasoning", "gre general (q)"]):
                value = field_data[key]
                gre_q = _extract_numeric(value)
                if gre_q:
                    detail["gre_q"] = gre_q
                    break
        
        # GRE ANALYTICAL WRITING
        for key in field_data:
            if any(term in key for term in ["gre aw", "gre w", "gre writing", "analytical writing", "gre general (aw)"]):
                value = field_data[key]
                gre_aw = _extract_numeric(value, is_float=True)
                if gre_aw:
                    detail["gre_aw"] = gre_aw
                    break
        
        # GRE TOTAL (if available)
        for key in field_data:
            if "gre" in key and ("total" in key or key == "gre"):
                value = field_data[key]
                # Total is usually V + Q
                gre_total = _extract_numeric(value)
                if gre_total and gre_total > 200:  # Sanity check (new GRE is 260-340)
                    detail["gre_total"] = gre_total
                    break
        
        # Calculate GRE total if we have V and Q
        if not detail["gre_total"] and detail.get("gre_v") and detail.get("gre_q"):
            detail["gre_total"] = detail["gre_v"] + detail["gre_q"]
        
        # COMMENTS
        # Look for comments in multiple places
        comment_text = None
        
        # Try finding by field name
        for key in field_data:
            if any(term in key for term in ["comment", "note", "undergrad gpa"]):
                if "gpa" not in key:  # Skip GPA fields
                    value = field_data[key]
                    if value and len(value) > 10:  # Comments are usually longer
                        comment_text = value
                        break
        
        # Try finding longer text blocks
        if not comment_text:
            for elem in soup.find_all(["div", "p", "blockquote", "td"]):
                text = elem.get_text(strip=True)
                # Comments are usually 50+ characters and not in navigation
                if len(text) >= 50 and len(text) < 5000:
                    # Make sure it's not part of header/footer/nav
                    if not elem.find_parent(["nav", "header", "footer", "script"]):
                        # Check if it looks like actual comment content
                        if not any(skip in text.lower() for skip in ["copyright", "privacy policy", "terms of use", "search results"]):
                            comment_text = text
                            break
        
        if comment_text:
            detail["comments"] = comment_text
        
        # Cache the result
        if result_id:
            DETAIL_CACHE[result_id] = detail
        
        return detail
        
    except error.HTTPError as e:
        log_error("HTTP_ERROR", f"HTTP {e.code} for {entry_url}", str(e))
        return default_detail
    except Exception as e:
        log_error("PARSE_ERROR", f"Failed to parse {entry_url}", 
                 f"{type(e).__name__}: {str(e)}")
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


def scrape_data(max_entries: int = 30000, start_page: int = 1, 
                checkpoint_interval: int = 5):
    """Main scraping function."""
    all_entries = []
    page = start_page
    pages_with_no_data = 0
    max_empty_pages = 3

    print(f"Starting scrape from page {start_page}")
    print(f"Target: {max_entries} entries")
    print(f"Cached detail pages: {len(DETAIL_CACHE)}")
    print("-" * 60)

    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        
        try:
            print(f"\nPage {page}:")
            html = _get_html(url, delay=1.0)
        except Exception as e:
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                break
            page += 1
            continue

        # Parse list view
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        rows = [tr for tr in rows if tr.find("td")]

        new_count = 0
        for tr in rows:
            entry = _parse_row(tr, url)
            if entry:
                all_entries.append(entry)
                new_count += 1
                
                # Progress indicator
                if len(all_entries) % 5 == 0:
                    fields = []
                    if entry.get("comments"): fields.append("Comm")
                    if entry.get("gpa"): fields.append("GPA")
                    if entry.get("gre_v"): fields.append("GRE-V")
                    if entry.get("gre_aw"): fields.append("GRE-AW")
                    if entry.get("term"): fields.append("Term")
                    if entry.get("citizenship"): fields.append("Cit")
                    
                    print(f"  Entry {len(all_entries)}: [{', '.join(fields) if fields else 'No details'}]")
                
                if len(all_entries) >= max_entries:
                    break

        if new_count == 0:
            print(f"  No new entries on page {page}")
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                break
        else:
            pages_with_no_data = 0
            print(f"  Collected {new_count} entries from page")
            
            # Detailed statistics
            stats = {
                "comments": sum(1 for e in all_entries if e.get("comments")),
                "gpa": sum(1 for e in all_entries if e.get("gpa")),
                "gre_v": sum(1 for e in all_entries if e.get("gre_v")),
                "gre_q": sum(1 for e in all_entries if e.get("gre_q")),
                "gre_aw": sum(1 for e in all_entries if e.get("gre_aw")),
                "gre_total": sum(1 for e in all_entries if e.get("gre_total")),
                "term": sum(1 for e in all_entries if e.get("term")),
                "citizenship": sum(1 for e in all_entries if e.get("citizenship")),
            }
            
            total = len(all_entries)
            print(f"  Total: {total}/{max_entries} ({total*100//max_entries if max_entries > 0 else 0}%)")
            print(f"  Fields: Comm={stats['comments']}, GPA={stats['gpa']}, "
                  f"GRE-V={stats['gre_v']}, GRE-AW={stats['gre_aw']}, "
                  f"Term={stats['term']}, Cit={stats['citizenship']}")

        # Checkpoint
        if page % checkpoint_interval == 0:
            checkpoint_file = "checkpoint.json"
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({
                    "entries": all_entries,
                    "last_page": page,
                    "timestamp": datetime.now().isoformat(),
                }, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Checkpoint saved")

        page += 1

    # Final statistics
    print("\n" + "=" * 60)
    print("SCRAPE COMPLETE!")
    print("=" * 60)
    print(f"Total entries: {len(all_entries)}")
    print(f"Detail pages cached: {len(DETAIL_CACHE)}")
    
    # Comprehensive field coverage
    total = len(all_entries)
    if total > 0:
        stats = {
            "Comments": sum(1 for e in all_entries if e.get("comments")),
            "GPA": sum(1 for e in all_entries if e.get("gpa")),
            "GRE Verbal": sum(1 for e in all_entries if e.get("gre_v")),
            "GRE Quant": sum(1 for e in all_entries if e.get("gre_q")),
            "GRE AW": sum(1 for e in all_entries if e.get("gre_aw")),
            "GRE Total": sum(1 for e in all_entries if e.get("gre_total")),
            "Term": sum(1 for e in all_entries if e.get("term")),
            "Citizenship": sum(1 for e in all_entries if e.get("citizenship")),
        }
        
        print("\nField Coverage:")
        for field, count in stats.items():
            pct = count * 100 // total
            print(f"  {field:15s}: {count:4d} / {total} ({pct:3d}%)")
    
    if ERROR_LOG:
        print(f"\nTotal errors logged: {len(ERROR_LOG)}")
    
    print("=" * 60)

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("robots.txt does not allow scraping.")
    
    print("✓ robots.txt check passed\n")

    # Test with 100 entries first
    data = scrape_data(max_entries=100, start_page=1, checkpoint_interval=3)

    # Save data
    import os
    os.makedirs("module_2", exist_ok=True)
    
    output_file = "module_2/llm_extend_applicant_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Data saved to {output_file}")
    
    # Save error log if any
    if ERROR_LOG:
        error_file = "error_log.json"
        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(ERROR_LOG, f, indent=2)
        print(f"✓ Error log saved to {error_file}")
    
    DETAIL_CACHE.close()
    print("✓ Cache closed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        DETAIL_CACHE.close()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        DETAIL_CACHE.close()
        raise
