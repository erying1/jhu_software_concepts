#!/usr/bin/env python3
"""
GradCafe scraper that actually fetches detail pages.
The API endpoint doesn't exist - we need to scrape the detail page HTML instead.
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

# Cache for detail pages
DETAIL_CACHE = shelve.open("detail_cache.db", writeback=True)

# Error tracking
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
    print(f"  ⚠ {error_type}: {message}")


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


def _parse_detail_page_html(entry_url: str, use_cache: bool = True) -> dict:
    """
    Fetch and parse the actual detail page HTML.
    This is where comments, GPA, GRE scores, term, citizenship are located.
    """
    default_detail = {
        "comments": None,
        "term": None,
        "citizenship": None,
        "gpa": None,
        "gre_total": None,
        "gre_v": None,
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
        print(f"    Cache hit: {result_id}")
        return DETAIL_CACHE[result_id]
    
    # Fetch the detail page
    try:
        time.sleep(0.75)  # Be polite - more delay for detail pages
        html = _get_html(entry_url, delay=0)  # Already delayed above
        soup = BeautifulSoup(html, "html.parser")
        
        detail = default_detail.copy()
        
        # Parse the detail page
        # Look for the details section - structure may vary
        
        # Method 1: Look for definition list (dl/dt/dd structure)
        dl_elements = soup.find_all("dl")
        for dl in dl_elements:
            dt_elements = dl.find_all("dt")
            dd_elements = dl.find_all("dd")
            
            for dt, dd in zip(dt_elements, dd_elements):
                label = dt.get_text(strip=True).lower()
                value = dd.get_text(strip=True)
                
                if "season" in label or "term" in label:
                    detail["term"] = value
                elif "status" in label and "date" not in label:
                    # Already have status from list view
                    pass
                elif "gpa" in label:
                    # Extract numeric GPA
                    gpa_match = re.search(r"(\d+\.?\d*)", value)
                    if gpa_match:
                        detail["gpa"] = float(gpa_match.group(1))
                elif "gre" in label:
                    if "verbal" in label or "v" == label.replace("gre", "").strip():
                        gre_match = re.search(r"(\d+)", value)
                        if gre_match:
                            detail["gre_v"] = int(gre_match.group(1))
                    elif "analytical" in label or "writing" in label or "aw" in label:
                        gre_match = re.search(r"(\d+\.?\d*)", value)
                        if gre_match:
                            detail["gre_aw"] = float(gre_match.group(1))
                    elif "total" in label or label == "gre":
                        gre_match = re.search(r"(\d+)", value)
                        if gre_match:
                            detail["gre_total"] = int(gre_match.group(1))
                elif "citizenship" in label or "status" in label:
                    detail["citizenship"] = value
        
        # Method 2: Look for table rows
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if "season" in label or "term" in label:
                        detail["term"] = value
                    elif "gpa" in label:
                        gpa_match = re.search(r"(\d+\.?\d*)", value)
                        if gpa_match:
                            detail["gpa"] = float(gpa_match.group(1))
                    elif "gre" in label:
                        if "verbal" in label:
                            gre_match = re.search(r"(\d+)", value)
                            if gre_match:
                                detail["gre_v"] = int(gre_match.group(1))
                        elif "analytical" in label or "writing" in label:
                            gre_match = re.search(r"(\d+\.?\d*)", value)
                            if gre_match:
                                detail["gre_aw"] = float(gre_match.group(1))
                        else:
                            gre_match = re.search(r"(\d+)", value)
                            if gre_match:
                                detail["gre_total"] = int(gre_match.group(1))
                    elif "citizenship" in label or "international" in label:
                        detail["citizenship"] = value
        
        # Method 3: Look for comments section
        # Comments might be in a div, p, or textarea
        comments_section = soup.find(["div", "p", "blockquote"], 
                                     class_=re.compile(r"comment", re.I))
        if not comments_section:
            # Try finding by text content
            for elem in soup.find_all(["div", "p", "blockquote"]):
                if len(elem.get_text(strip=True)) > 50:  # Likely a comment if long
                    # Check if it's not part of navigation/header
                    if not elem.find_parent(["nav", "header", "footer"]):
                        comments_section = elem
                        break
        
        if comments_section:
            detail["comments"] = comments_section.get_text(strip=True)
        
        # Method 4: Look for specific patterns in text
        page_text = soup.get_text()
        
        # Find term/season
        term_match = re.search(r"(?:Term|Season):\s*([^\n,]+)", page_text, re.I)
        if term_match and not detail["term"]:
            detail["term"] = term_match.group(1).strip()
        
        # Find GPA
        gpa_match = re.search(r"GPA:\s*(\d+\.?\d*)", page_text, re.I)
        if gpa_match and not detail["gpa"]:
            detail["gpa"] = float(gpa_match.group(1))
        
        # Find GRE scores
        gre_v_match = re.search(r"GRE\s*(?:Verbal|V):\s*(\d+)", page_text, re.I)
        if gre_v_match and not detail["gre_v"]:
            detail["gre_v"] = int(gre_v_match.group(1))
        
        gre_aw_match = re.search(r"GRE\s*(?:AW|Analytical|Writing):\s*(\d+\.?\d*)", page_text, re.I)
        if gre_aw_match and not detail["gre_aw"]:
            detail["gre_aw"] = float(gre_aw_match.group(1))
        
        # Cache the result
        if result_id:
            DETAIL_CACHE[result_id] = detail
            print(f"    Cached: {result_id}")
        
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
        "gre_aw": None,
    }

    # Fetch detail page HTML
    if entry_url:
        print(f"  Fetching detail: {entry_url}")
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
                
                # Show what we got
                has_detail = any([
                    entry.get("comments"),
                    entry.get("gpa"),
                    entry.get("term"),
                    entry.get("gre_v")
                ])
                print(f"    Entry {len(all_entries)}: "
                      f"{entry.get('university', 'N/A')[:30]} - "
                      f"Detail fields: {'✓' if has_detail else '✗'}")
                
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
            print(f"  Total: {len(all_entries)}/{max_entries}")
            
            # Show detail statistics
            with_comments = sum(1 for e in all_entries if e.get("comments"))
            with_gpa = sum(1 for e in all_entries if e.get("gpa"))
            with_term = sum(1 for e in all_entries if e.get("term"))
            print(f"  Detail stats: Comments={with_comments}, GPA={with_gpa}, Term={with_term}")

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

    # Final stats
    print("\n" + "=" * 60)
    print("Scrape complete!")
    print(f"Total entries: {len(all_entries)}")
    print(f"Detail pages cached: {len(DETAIL_CACHE)}")
    
    # Detail field statistics
    with_comments = sum(1 for e in all_entries if e.get("comments"))
    with_gpa = sum(1 for e in all_entries if e.get("gpa"))
    with_gre_v = sum(1 for e in all_entries if e.get("gre_v"))
    with_gre_aw = sum(1 for e in all_entries if e.get("gre_aw"))
    with_term = sum(1 for e in all_entries if e.get("term"))
    with_citizenship = sum(1 for e in all_entries if e.get("citizenship"))
    
    print(f"\nDetail field coverage:")
    print(f"  Comments: {with_comments} ({with_comments*100//len(all_entries)}%)")
    print(f"  GPA: {with_gpa} ({with_gpa*100//len(all_entries)}%)")
    print(f"  GRE Verbal: {with_gre_v} ({with_gre_v*100//len(all_entries)}%)")
    print(f"  GRE AW: {with_gre_aw} ({with_gre_aw*100//len(all_entries)}%)")
    print(f"  Term: {with_term} ({with_term*100//len(all_entries)}%)")
    print(f"  Citizenship: {with_citizenship} ({with_citizenship*100//len(all_entries)}%)")
    
    if ERROR_LOG:
        print(f"\nTotal errors: {len(ERROR_LOG)}")
    
    print("=" * 60)

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("robots.txt does not allow scraping.")
    
    print("robots.txt check passed ✓\n")

    # Start with small number to test
    data = scrape_data(max_entries=50, start_page=1, checkpoint_interval=2)

    # Save data
    import os
    os.makedirs("module_2", exist_ok=True)
    
    output_file = "module_2/llm_extend_applicant_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Data saved to {output_file}")
    
    # Save error log
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
