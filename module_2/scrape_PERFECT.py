#!/usr/bin/env python3
"""
GradCafe scraper - FINAL VERSION based on actual HTML structure
Extracts from <dl> definition lists and filters out fake zeros
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
    """Fetch HTML with minimal rate limiting."""
    time.sleep(delay)
    try:
        opener = get_opener()
        with opener.open(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return ""


def _parse_detail_page_html(entry_url: str):
    """
    Parse detail data from HTML - FINAL VERSION based on actual structure.
    GradCafe uses <dl><dt>Label</dt><dd>Value</dd></dl> structure.
    """
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
        html = _get_html(entry_url, delay=0.1)
        if not html:
            return default
            
        soup = BeautifulSoup(html, "html.parser")
        result = default.copy()
        
        # METHOD 1: Extract from definition list (<dl>)
        # This is the main data structure GradCafe uses
        for dt in soup.find_all('dt'):
            label = dt.get_text(strip=True).lower()
            dd = dt.find_next_sibling('dd')
            if not dd:
                continue
            
            value = dd.get_text(strip=True)
            
            # GPA (label: "Undergrad GPA")
            if 'gpa' in label and not result['gpa']:
                try:
                    gpa_val = float(value)
                    if 0 < gpa_val <= 4.5:  # Valid GPA range
                        result['gpa'] = gpa_val
                except:
                    pass
            
            # Citizenship (label: "Degree's Country of Origin")
            if 'country' in label or 'citizenship' in label:
                if 'international' in value.lower():
                    result['citizenship'] = "International"
                elif any(word in value.lower() for word in ['american', 'domestic', 'u.s', 'usa']):
                    result['citizenship'] = "American"
        
        # METHOD 2: Extract GRE from <ul> lists
        # GradCafe shows GRE in unordered lists
        for ul in soup.find_all('ul'):
            text = ul.get_text()
            
            # GRE Verbal
            if 'gre verbal' in text.lower() and not result['gre_v']:
                match = re.search(r'GRE Verbal[:\s]+(\d+)', text, re.I)
                if match:
                    try:
                        val = int(match.group(1))
                        # CRITICAL: Filter out zeros (fake data)
                        if 130 <= val <= 170:  # Valid GRE range only
                            result['gre_v'] = val
                    except:
                        pass
            
            # GRE Quant (also called "GRE General" sometimes)
            if not result['gre_q']:
                # Try "GRE General"
                match = re.search(r'GRE General[:\s]+(\d+)', text, re.I)
                if match:
                    try:
                        val = int(match.group(1))
                        if 130 <= val <= 170:
                            result['gre_q'] = val
                    except:
                        pass
                
                # Try "GRE Quant"
                if not result['gre_q']:
                    match = re.search(r'GRE Quant[:\s]+(\d+)', text, re.I)
                    if match:
                        try:
                            val = int(match.group(1))
                            if 130 <= val <= 170:
                                result['gre_q'] = val
                        except:
                            pass
            
            # GRE AW
            if 'analytical writing' in text.lower() and not result['gre_aw']:
                match = re.search(r'Analytical Writing[:\s]+(\d+\.?\d*)', text, re.I)
                if match:
                    try:
                        val = float(match.group(1))
                        # CRITICAL: Filter out zeros
                        if 0.5 <= val <= 6.0:  # Valid AW range (0 is fake)
                            result['gre_aw'] = val
                    except:
                        pass
        
        # Calculate GRE total if we have both V and Q
        if result['gre_v'] and result['gre_q']:
            result['gre_total'] = result['gre_v'] + result['gre_q']
        
        # METHOD 3: Term extraction
        # NOTE: Based on diagnostic, term is NOT displayed on GradCafe pages
        # Leaving this in case some entries have it, but expect 0% coverage
        page_text = soup.get_text()
        term_match = re.search(r'\b(Fall|Spring|Summer|Winter)\s+(\d{4})\b', page_text, re.I)
        if term_match:
            # Exclude "Terms of Service"
            if 'service' not in term_match.group(0).lower():
                result['term'] = f"{term_match.group(1).capitalize()} {term_match.group(2)}"
        
        # Comments - look for user commentary (usually below data fields)
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            # Skip boilerplate
            if any(phrase in text.lower() for phrase in ['estimated', 'gradcafe', 'terms of service']):
                continue
            # Must be substantial
            if len(text) >= 30:
                result['comments'] = text[:500]
                break
        
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


def fetch_detail_batch(records, max_workers=15):
    """Fetch detail pages in parallel using threading."""
    print(f"\nFetching detail data with {max_workers} parallel threads...")
    
    completed = 0
    total = len(records)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_record = {
            executor.submit(_parse_detail_page_html, rec['entry_url']): rec 
            for rec in records
        }
        
        for future in as_completed(future_to_record):
            record = future_to_record[future]
            try:
                detail = future.result()
                record.update(detail)
                completed += 1
                
                if completed % 100 == 0:
                    print(f"  {completed}/{total} detail pages fetched...")
                    
            except Exception as e:
                pass
    
    print(f"  ✓ Completed {completed}/{total} detail pages")
    return records


def scrape_data(max_entries: int = 1000, start_page: int = 1, parallel_threads: int = 15):
    """Main scraping function with parallel processing."""
    all_entries = []
    page = start_page

    print(f"Starting GradCafe scraper - FINAL PERFECT VERSION")
    print(f"Target: {max_entries} entries")
    print(f"Parallel threads: {parallel_threads}")
    print("-" * 60)

    # Phase 1: Collect basic info
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

        print(f"  Page {page}: {len(all_entries)} total entries")
        page += 1

    print(f"\n✓ Phase 1 complete: {len(all_entries)} entries")

    # Phase 2: Fetch details in parallel
    print("\nPhase 2: Fetching detail data in parallel...")
    all_entries = fetch_detail_batch(all_entries, max_workers=parallel_threads)

    # Final stats
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    print("=" * 60)
    n = len(all_entries)
    
    # Count real values only (exclude nulls and zeros)
    stats = {
        "GPA": sum(1 for e in all_entries if e.get("gpa") and e.get("gpa") > 0),
        "GRE V": sum(1 for e in all_entries if e.get("gre_v") and e.get("gre_v") >= 130),
        "GRE Q": sum(1 for e in all_entries if e.get("gre_q") and e.get("gre_q") >= 130),
        "GRE AW": sum(1 for e in all_entries if e.get("gre_aw") and e.get("gre_aw") >= 0.5),
        "GRE Total": sum(1 for e in all_entries if e.get("gre_total") and e.get("gre_total") > 260),
        "Term": sum(1 for e in all_entries if e.get("term")),
        "Citizenship": sum(1 for e in all_entries if e.get("citizenship")),
        "Comments": sum(1 for e in all_entries if e.get("comments")),
    }
    
    for field, count in stats.items():
        pct = count * 100 // n if n > 0 else 0
        print(f"  {field:15s}: {count:4d} / {n:4d} ({pct:3d}%)")
    
    # Show samples
    print("\nSample entries with data:")
    shown = 0
    for entry in all_entries:
        if (entry.get("gpa") and entry.get("gpa") > 0) or entry.get("term"):
            print(f"\n  {entry.get('university')} - {entry.get('program_name')}")
            if entry.get('gpa'):
                print(f"    GPA: {entry.get('gpa')}")
            if entry.get('term'):
                print(f"    Term: {entry.get('term')}")
            if entry.get('citizenship'):
                print(f"    Citizenship: {entry.get('citizenship')}")
            if entry.get('gre_v') and entry.get('gre_v') >= 130:
                print(f"    GRE: V={entry.get('gre_v')}, Q={entry.get('gre_q')}, AW={entry.get('gre_aw')}")
            shown += 1
            if shown >= 5:
                break

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("❌ robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    data = scrape_data(
        max_entries=1000, 
        start_page=1, 
        parallel_threads=15
    )

    import os
    os.makedirs("module_3", exist_ok=True)
    
    output_file = "module_3/module_2.1/raw_applicant_data.json"
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
