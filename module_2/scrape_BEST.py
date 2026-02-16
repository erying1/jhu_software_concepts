#!/usr/bin/env python3
"""
GradCafe scraper - IMPROVED HTML parsing with better field extraction
Based on actual HTML structure analysis
"""

import json
import time
import re
from urllib import request, parse, error
from urllib.parse import urljoin
import urllib.robotparser
from datetime import datetime

from bs4 import BeautifulSoup

USER_AGENT = "jhu-module2-scraper"

OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"


def check_robots():
    """Check robots.txt."""
    robots_url = urljoin(BASE_URL, "robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(USER_AGENT, urljoin(BASE_URL, "survey/"))


def _get_html(url: str, delay: float = 0.5) -> str:
    """Fetch HTML with rate limiting."""
    time.sleep(delay)
    try:
        with OPENER.open(url, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""


def _parse_detail_page_html(entry_url: str):
    """
    Parse detail data from HTML - IMPROVED with actual structure knowledge.
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
        html = _get_html(entry_url, delay=0.5)
        if not html:
            return default
            
        soup = BeautifulSoup(html, "html.parser")
        result = default.copy()
        
        # Get all text content
        page_text = soup.get_text()
        
        # === IMPROVED: Extract from structured HTML elements ===
        
        # Look for definition list (dl/dt/dd) or divs with labels
        # GradCafe often uses label: value format
        
        # Method 1: Find all divs and look for label-value pairs
        for div in soup.find_all(['div', 'p', 'li', 'dd']):
            text = div.get_text(strip=True)
            
            # GPA pattern: "Undergrad GPA: 3.60" or just "GPA: 3.60"
            if 'gpa' in text.lower() and not result['gpa']:
                gpa_match = re.search(r'GPA[:\s]+(\d+\.?\d*)', text, re.I)
                if gpa_match:
                    try:
                        gpa_val = float(gpa_match.group(1))
                        if 0 < gpa_val <= 4.5:  # Valid GPA range
                            result['gpa'] = gpa_val
                    except:
                        pass
            
            # Citizenship pattern: "American" or "International" often appears alone
            if not result['citizenship']:
                if re.search(r'\b(International|Domestic|American|U\.?S\.?)\b', text, re.I):
                    if 'international' in text.lower():
                        result['citizenship'] = "International"
                    elif any(word in text.lower() for word in ['american', 'domestic', 'u.s', 'us']):
                        result['citizenship'] = "American"
            
            # Term pattern: Look for "Fall 2026", "Spring 2025", etc.
            # Try to find it near "Term", "Season", "Semester" labels
            if not result['term']:
                # Pattern 1: "Term: Fall 2026" or "Season: Fall 2026"
                term_match = re.search(r'(?:Term|Season|Semester)[:\s]+(Fall|Spring|Summer|Winter)\s+(\d{4})', text, re.I)
                if term_match:
                    season = term_match.group(1).capitalize()
                    year = term_match.group(2)
                    result['term'] = f"{season} {year}"
                else:
                    # Pattern 2: Just "Fall 2026" or "F26" in the text
                    term_match = re.search(r'\b(Fall|Spring|Summer|Winter)\s+(\d{4})\b', text, re.I)
                    if term_match:
                        season = term_match.group(1).capitalize()
                        year = term_match.group(2)
                        result['term'] = f"{season} {year}"
                    else:
                        # Pattern 3: Abbreviated "F26", "S26"
                        term_match = re.search(r'\b([FS])[\s\']?(\d{2})\b', text)
                        if term_match:
                            season = "Fall" if term_match.group(1).upper() == 'F' else "Spring"
                            year = "20" + term_match.group(2)
                            result['term'] = f"{season} {year}"
            
            # GRE Verbal
            if not result['gre_v']:
                gre_v_match = re.search(r'(?:GRE\s+)?V(?:erbal)?[:\s]+(\d{3})', text, re.I)
                if gre_v_match:
                    try:
                        val = int(gre_v_match.group(1))
                        if 130 <= val <= 170:  # Valid GRE range
                            result['gre_v'] = val
                    except:
                        pass
            
            # GRE Quant
            if not result['gre_q']:
                gre_q_match = re.search(r'(?:GRE\s+)?Q(?:uant)?(?:itative)?[:\s]+(\d{3})', text, re.I)
                if gre_q_match:
                    try:
                        val = int(gre_q_match.group(1))
                        if 130 <= val <= 170:
                            result['gre_q'] = val
                    except:
                        pass
            
            # GRE AW
            if not result['gre_aw']:
                gre_aw_match = re.search(r'(?:GRE\s+)?(?:AW|Writing|Analytical)[:\s]+(\d+\.?\d*)', text, re.I)
                if gre_aw_match:
                    try:
                        val = float(gre_aw_match.group(1))
                        if 0 <= val <= 6:
                            result['gre_aw'] = val
                    except:
                        pass
        
        # Calculate GRE total if we have V and Q
        if result['gre_v'] and result['gre_q']:
            result['gre_total'] = result['gre_v'] + result['gre_q']
        
        # === Extract Comments ===
        # Look for longer text blocks that aren't field labels
        boilerplate = [
            "this data is estimated",
            "gradcafe",
            "all rights reserved",
            "privacy policy",
            "terms of service",
            "undergrad gpa",
            "gre verbal",
            "status:",
        ]
        
        for element in soup.find_all(['p', 'div']):
            text = element.get_text(strip=True)
            
            # Skip boilerplate
            if any(phrase in text.lower() for phrase in boilerplate):
                continue
            
            # Skip if too short or has field labels
            if len(text) < 30 or ':' in text[:20]:
                continue
            
            # This might be a real comment
            if not result['comments']:
                result['comments'] = text[:500]
                break
        
        return result
        
    except Exception as e:
        print(f"  Detail page error for {entry_url}: {e}")
        return default


def _parse_row(tr, base_url: str) -> dict:
    """Parse a single table row from the search results page."""
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
            td.find("div", class_="tw-font-semibold") or
            td.find("div", class_="font-semibold") or
            td.find("span", class_="font-medium") or
            td.find("span", class_="tw-font-semibold") or
            td.find("span", class_="font-semibold")
        )

        if uni_div:
            text = uni_div.get_text(strip=True)
        else:
            raw = td.get_text("\n", strip=True)
            text = raw.split("\n")[0] if raw else None
            
            if not text and raw:
                m = re.search(r"([A-Za-z].+)", raw)
                if m:
                    text = m.group(1).strip()

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
                if status.lower() == "wait listed":
                    status = "Waitlisted"

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

    detail = _parse_detail_page_html(entry_url)
    record.update(detail)

    return record


def scrape_data(max_entries: int = 1000, start_page: int = 1):
    """Main scraping function."""
    all_entries = []
    page = start_page

    print(f"Starting GradCafe scraper (IMPROVED HTML parsing)")
    print(f"Target: {max_entries} entries")
    print("-" * 60)

    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        
        try:
            print(f"\nPage {page}:")
            html = _get_html(url, delay=1.0)
            
            if not html:
                print("  Empty response, stopping.")
                break
                
        except Exception as e:
            print(f"  Error: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        rows = [tr for tr in rows if tr.find("td")]

        if not rows:
            print("  No more rows found, stopping.")
            break

        page_entries = 0
        for tr in rows:
            entry = _parse_row(tr, url)
            if entry:
                all_entries.append(entry)
                page_entries += 1
                
                if len(all_entries) % 25 == 0:
                    print(f"  {len(all_entries)} entries collected...")
                
                if len(all_entries) >= max_entries:
                    break

        print(f"  Collected {page_entries} entries from this page")

        n = len(all_entries)
        if n > 0:
            stats = {
                "Comm": sum(1 for e in all_entries if e.get("comments")),
                "GPA": sum(1 for e in all_entries if e.get("gpa") and e.get("gpa") > 0),
                "V": sum(1 for e in all_entries if e.get("gre_v") and e.get("gre_v") > 0),
                "Q": sum(1 for e in all_entries if e.get("gre_q") and e.get("gre_q") > 0),
                "AW": sum(1 for e in all_entries if e.get("gre_aw") and e.get("gre_aw") > 0),
                "Tot": sum(1 for e in all_entries if e.get("gre_total") and e.get("gre_total") > 0),
                "Term": sum(1 for e in all_entries if e.get("term")),
                "Cit": sum(1 for e in all_entries if e.get("citizenship")),
            }
            
            print(f"  Coverage: ", end="")
            for field, count in stats.items():
                pct = count * 100 // n if n > 0 else 0
                print(f"{field}={pct}% ", end="")
            print()

        if page % 5 == 0:
            checkpoint_data = {
                "entries": all_entries,
                "last_page": page,
                "timestamp": datetime.now().isoformat()
            }
            with open("checkpoint.json", "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            print(f"  Checkpoint saved at page {page}")

        page += 1

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
    
    # Show sample entries with data
    print("\nSample entries with details:")
    count = 0
    for entry in all_entries:
        if entry.get("term") or (entry.get("gpa") and entry.get("gpa") > 0):
            print(f"\n  {entry.get('university')} - {entry.get('program_name')}")
            if entry.get('term'):
                print(f"    Term: {entry.get('term')}")
            print(f"    GPA={entry.get('gpa')}, Cit={entry.get('citizenship')}")
            if entry.get('gre_v') or entry.get('gre_q'):
                print(f"    GRE: V={entry.get('gre_v')}, Q={entry.get('gre_q')}, AW={entry.get('gre_aw')}")
            count += 1
            if count >= 5:
                break

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("❌ robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    # Scrape data - change max_entries as needed
    data = scrape_data(max_entries=1000, start_page=1)

    # Save to file
    import os
    os.makedirs("module_2", exist_ok=True)
    
    output_file = "module_2/raw_applicant_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved {len(data)} entries to {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
