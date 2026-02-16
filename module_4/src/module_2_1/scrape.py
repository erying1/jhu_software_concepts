#!/usr/bin/env python3
"""
GradCafe scraper - FAST VERSION with parallel processing
Uses threading to fetch multiple detail pages simultaneously
"""

import json
import time
import re
from urllib import request, parse, error
from urllib.parse import urljoin
import urllib.robotparser
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from bs4 import BeautifulSoup

USER_AGENT = "jhu-module2-scraper"

# Thread-safe opener
_lock = threading.Lock()

def get_opener():
    """Get a thread-safe opener."""
    opener = request.build_opener()
    opener.addheaders = [("User-Agent", USER_AGENT)]
    return opener

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"


def check_robots(url=None):
    """Verify that robots.txt allows scraping of the survey pages.

    Args:
        url: Optional URL to check (defaults to survey page).

    Returns:
        bool: True if scraping is allowed, True on error (permissive default).
    """
    robots_url = urljoin(BASE_URL, "robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(USER_AGENT, urljoin(BASE_URL, "survey/"))
    except Exception:
        return True  # allow scraping 

def get_html(url, opener=None, delay=0.1): 
    """Fetch HTML content from a URL.

    Args:
        url (str): Target URL to fetch.
        opener: Optional urllib opener (used for testing).
        delay (float): Rate-limiting delay in seconds.

    Returns:
        str | None: HTML content, or None on failure.
    """ 
    if opener is not None: 
        try: 
            resp = opener.open(url, timeout=10) 
            data = resp.read() 
            if isinstance(data, bytes): 
                return data.decode("utf-8", errors="ignore") 
            return str(data) 
        except Exception: 
            return None 
    return _get_html(url, delay)



def _get_html(url: str, delay: float = 0.1) -> str:
    """Fetch HTML with minimal rate limiting (parallel calls will be rate-limited naturally)."""
    time.sleep(delay)
    try:
        opener = get_opener()
        with opener.open(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return ""

def parse_detail_gre_total_calculation(detail): 
    """Return GRE total from detail dict; used only for tests.""" 
    if not detail: 
        return None 
    v = detail.get("gre_v") 
    q = detail.get("gre_q") 
    if isinstance(v, int) and isinstance(q, int): 
        return v + q 
    return None

def parse_detail_page_html(html, base_url=None):
    """Parse GPA, GRE, citizenship, and term from a detail page.

    Args:
        html (str): Raw HTML content of the detail page.
        base_url (str | None): If provided, sets ``entry_url`` in the result.

    Returns:
        dict: Parsed fields including gpa, gre_v, gre_q, gre_aw, citizenship, term.
    """
    result = _parse_detail_page_html(html)

    # Tests expect entry_url to exist
    if base_url is not None:
        result["entry_url"] = base_url

    return result



def _parse_detail_page_html(entry_url: str):
    """Parse detail data from HTML - optimized version."""
    default = {
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
        return default

    try:
        html = _get_html(entry_url, delay=0.1)  # Reduced delay for parallel
        if not html:
            return default
            
        soup = BeautifulSoup(html, "html.parser")
        result = default.copy()
        
        page_text = soup.get_text()
        
        # Fast extraction - iterate through elements once
        for div in soup.find_all(['div', 'p', 'li', 'dd']):
            text = div.get_text(strip=True)
            
            # GPA
            if 'gpa' in text.lower() and not result['gpa']:
                gpa_match = re.search(r'GPA[:\s]+(\d+\.?\d*)', text, re.I)
                if gpa_match:
                    gpa_val = float(gpa_match.group(1))
                    if 0 < gpa_val <= 4.5:
                        result['gpa'] = gpa_val
            
            # Citizenship
            if not result['citizenship']:
                if re.search(r'\b(International|Domestic|American|U\.?S\.?)\b', text, re.I):
                    if 'international' in text.lower():
                        result['citizenship'] = "International"
                    elif any(word in text.lower() for word in ['american', 'domestic', 'u.s', 'us']):
                        result['citizenship'] = "American"
            
            # Term
            if not result['term']:
                term_match = re.search(r'(?:Term|Season|Semester)[:\s]+(Fall|Spring|Summer|Winter)\s+(\d{4})', text, re.I)
                if term_match:
                    result['term'] = f"{term_match.group(1).capitalize()} {term_match.group(2)}"
                else:
                    term_match = re.search(r'\b(Fall|Spring|Summer|Winter)\s+(\d{4})\b', text, re.I)
                    if term_match:
                        result['term'] = f"{term_match.group(1).capitalize()} {term_match.group(2)}"
            
            # GRE Verbal
            if not result['gre_v']:
                gre_v_match = re.search(r'(?:GRE\s+)?V(?:erbal)?[:\s]+(\d{3})', text, re.I)
                if gre_v_match:
                    val = int(gre_v_match.group(1))
                    if 130 <= val <= 170:
                        result['gre_v'] = val
            
            # GRE Quant
            if not result['gre_q']:
                gre_q_match = re.search(r'(?:GRE\s+)?Q(?:uant)?[:\s]+(\d{3})', text, re.I)
                if gre_q_match:
                    val = int(gre_q_match.group(1))
                    if 130 <= val <= 170:
                        result['gre_q'] = val
            
            # GRE AW
            if not result['gre_aw']:
                gre_aw_match = re.search(r'(?:GRE\s+)?(?:AW|Writing)[:\s]+(\d+\.?\d*)', text, re.I)
                if gre_aw_match:
                    val = float(gre_aw_match.group(1))
                    if 0 <= val <= 6:
                        result['gre_aw'] = val
        
        # Calculate GRE total
        if result['gre_v'] and result['gre_q']:
            result['gre_total'] = result['gre_v'] + result['gre_q']
        
        return result
        
    except Exception as e:
        return default

def parse_row(tr, base_url): 
    """Parse a single table row from the GradCafe listing page.

    Args:
        tr: BeautifulSoup ``<tr>`` element.
        base_url (str): Base URL for resolving relative links.

    Returns:
        dict | None: Parsed entry with program, university, status, etc., or None if invalid.
    """ 
    return _parse_row(tr, base_url)

def _parse_row(tr, base_url: str) -> dict:
    """Parse table row - returns basic info WITHOUT fetching detail page."""
    link = tr.find("a", href=re.compile(r"^/result/"))
    if not link:
        return None
    
    tds = tr.find_all("td", recursive=False)
    if len(tds) < 4:
        return None

    entry_url = urljoin(base_url, link["href"])

    def extract_university(td):
        uni_div = (
            td.find("div", class_="tw-font-medium") or
            td.find("div", class_="font-medium") or
            td.find("span", class_="font-medium")
        )
        if uni_div:
            text = uni_div.get_text(strip=True)
        else:
            raw = td.get_text("\n", strip=True)
            text = raw.split("\n")[0] if raw else None
        
        if text:
            text = re.sub(r"\s+", " ", text).strip()
        return text or None

    university = extract_university(tds[0]) if len(tds) > 0 else None

    program = degree_level = None
    if len(tds) > 1:
        prog_div = tds[1].find("div")
        if prog_div:
            spans = prog_div.find_all("span")
            if spans:
                program = spans[0].get_text(strip=True)
            if len(spans) > 1:
                degree_level = spans[1].get_text(strip=True)
        else:
            text = tds[1].get_text(strip=True)
            if text:
                program = text

    date_added = tds[2].get_text(strip=True) if len(tds) > 2 else None

    status = status_date = None
    if len(tds) > 3:
        status_block = tds[3].get_text(" ", strip=True)
        m = re.match(r"(Accepted|Rejected|Interview|Wait listed|Waitlisted|Other)\s+on\s+(.+)", 
                     status_block, re.I)
        if m:
            status = m.group(1).title()
            if status.lower() == "wait listed":
                status = "Waitlisted"
            status_date = m.group(2)
        else:
            status_match = re.search(r"(Accepted|Rejected|Interview|Wait listed|Waitlisted|Other)", 
                                    status_block, re.I)
            if status_match:
                status = status_match.group(1).title()

    return {
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


def fetch_detail_batch(records, max_workers=10):
    """
    Fetch detail pages in parallel using threading.
    max_workers: number of concurrent threads (default 10)
    """
    if not records: 
        return []

    if isinstance(records[0], str):
        records = [{"entry_url": url} for url in records]

    print(f"\nFetching detail data with {max_workers} parallel threads...")
    
    completed = 0
    total = len(records)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all detail page fetches
        future_to_record = {
            executor.submit(_parse_detail_page_html, rec['entry_url']): rec 
            for rec in records
        }
        
        # Process as they complete
        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                detail = future.result()
                # Only overwrite fields if detail parser actually found real data 
                for key, value in detail.items(): 
                    if value is not None: 
                        record[key] = value
                completed += 1
                
                if completed % 50 == 0:
                    print(f"  {completed}/{total} detail pages fetched...")
                    
            except Exception as e:
                # If detail fetch fails, keep basic record
                pass
    
    print(f"  ✓ Completed {completed}/{total} detail pages")
    return records


def scrape_data(max_entries: int = 1000, start_page: int = 1, parallel_threads: int = 10):
    """
    Main scraping function with parallel processing.
    
    Args:
        max_entries: Total number of entries to collect
        start_page: Starting page number
        parallel_threads: Number of concurrent threads for detail pages (default 10)
    """
    all_entries = []
    page = start_page

    print(f"Starting FAST GradCafe scraper")
    print(f"Target: {max_entries} entries")
    print(f"Parallel threads: {parallel_threads}")
    print("-" * 60)

    # Phase 1: Collect basic info from listing pages (fast)
    print("\nPhase 1: Collecting basic information...")
    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        
        try:
            html = _get_html(url, delay=0.5)
            if not html:
                break
        except Exception as e:
            print(f"  Error on page {page}: {e}")
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
                if len(all_entries) >= max_entries:
                    break

        print(f"  Page {page}: {len(all_entries)} total entries collected")
        page += 1

    print(f"\n✓ Phase 1 complete: {len(all_entries)} entries")

    # Phase 2: Fetch detail pages in parallel (FAST!)
    print("\nPhase 2: Fetching detail data in parallel...")
    all_entries = fetch_detail_batch(all_entries, max_workers=parallel_threads)

    # Final stats
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    print("=" * 60)
    n = len(all_entries)
    fields = ["comments", "gpa", "gre_v", "gre_q", "gre_aw", "gre_total", "term", "citizenship"]
    
    for field in fields:
        if field == "gpa":
            count = sum(1 for e in all_entries if e.get(field) and e.get(field) > 0)
        elif field in ["gre_v", "gre_q", "gre_aw", "gre_total"]:
            count = sum(1 for e in all_entries if e.get(field) and e.get(field) > 0)
        else:
            count = sum(1 for e in all_entries if e.get(field))
        pct = count * 100 // n if n > 0 else 0
        print(f"  {field:15s}: {count:4d} / {n:4d} ({pct:3d}%)")
    
    # Show samples
    print("\nSample entries with details:")
    count = 0
    for entry in all_entries:
        if entry.get("term") or (entry.get("gpa") and entry.get("gpa") > 0):
            print(f"\n  {entry.get('university')} - {entry.get('program_name')}")
            if entry.get('term'):
                print(f"    Term: {entry.get('term')}")
            print(f"    GPA={entry.get('gpa')}, Cit={entry.get('citizenship')}")
            count += 1
            if count >= 3:
                break

    return all_entries[:max_entries]


def main():
    """Run the full scraping pipeline.

    Checks robots.txt, scrapes GradCafe listing and detail pages in parallel,
    and saves results to ``module_3/module_2.1/raw_applicant_data.json``.

    Raises:
        SystemExit: If robots.txt check fails.
    """
    if not check_robots():
        raise SystemExit("❌ robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    # FAST scrape with parallel processing
    # Adjust parallel_threads: higher = faster but more aggressive
    # Recommended: 10-20 threads
    data = scrape_data(
        max_entries=35000, 
        start_page=1, 
        parallel_threads=15  # Increase for more speed!
    )

    # Save to file
    import os

    output_dir = os.path.join("module_3", "module_2.1") 
    os.makedirs(output_dir, exist_ok=True) 
    output_file = os.path.join(output_dir, "raw_applicant_data.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved {len(data)} entries to {output_file}")


def cli_main():
    """CLI entry point with timing and error handling.

    Runs the full scraping pipeline, prints elapsed time on success,
    and handles KeyboardInterrupt and unexpected errors gracefully.
    """
    try:
        start_time = datetime.now()
        main()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\nTotal time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":  # pragma: no cover
    cli_main()

__all__ = [ 
    "cli_main", 
    "get_html", 
    "check_robots", 
    "parse_detail_page_html", 
    "parse_detail_gre_total_calculation", 
    "parse_row", 
    "fetch_detail_batch", 
    "scrape_data",
    "main",
]
