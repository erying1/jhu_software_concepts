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


def check_robots():
    """Check robots.txt."""
    robots_url = urljoin(BASE_URL, "robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(USER_AGENT, urljoin(BASE_URL, "survey/"))


def _get_html(url: str, delay: float = 0.1) -> str:
    """Fetch HTML with minimal rate limiting (parallel calls will be rate-limited naturally)."""
    time.sleep(delay)
    try:
        opener = get_opener()
        with opener.open(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return ""


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
                    try:
                        gpa_val = float(gpa_match.group(1))
                        if 0 < gpa_val <= 4.5:
                            result['gpa'] = gpa_val
                    except:
                        pass
            
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
                    try:
                        val = int(gre_v_match.group(1))
                        if 130 <= val <= 170:
                            result['gre_v'] = val
                    except:
                        pass
            
            # GRE Quant
            if not result['gre_q']:
                gre_q_match = re.search(r'(?:GRE\s+)?Q(?:uant)?[:\s]+(\d{3})', text, re.I)
                if gre_q_match:
                    try:
                        val = int(gre_q_match.group(1))
                        if 130 <= val <= 170:
                            result['gre_q'] = val
                    except:
                        pass
            
            # GRE AW
            if not result['gre_aw']:
                gre_aw_match = re.search(r'(?:GRE\s+)?(?:AW|Writing)[:\s]+(\d+\.?\d*)', text, re.I)
                if gre_aw_match:
                    try:
                        val = float(gre_aw_match.group(1))
                        if 0 <= val <= 6:
                            result['gre_aw'] = val
                    except:
                        pass
        
        # Calculate GRE total
        if result['gre_v'] and result['gre_q']:
            result['gre_total'] = result['gre_v'] + result['gre_q']
        
        return result
        
    except Exception as e:
        return default


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
                record.update(detail)
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
    """Main function."""
    if not check_robots():
        raise SystemExit("❌ robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    # FAST scrape with parallel processing
    # Adjust parallel_threads: higher = faster but more aggressive
    # Recommended: 10-20 threads
    data = scrape_data(
        max_entries=1000, 
        start_page=1, 
        parallel_threads=15  # Increase for more speed!
    )

    # Save to file
    import os
    os.makedirs("module_2", exist_ok=True)
    
    output_file = "module_2/raw_applicant_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved {len(data)} entries to {output_file}")


if __name__ == "__main__":
    try:
        start_time = datetime.now()
        main()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n⏱ Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
