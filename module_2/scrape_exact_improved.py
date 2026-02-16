#!/usr/bin/env python3
"""
GradCafe scraper - improved version with robust detail page fetching.
Handles the actual HTML structure and API endpoints used by GradCafe.
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


def _parse_detail_page(entry_url: str):
    """
    Fetch additional details from the API endpoint.
    GradCafe has an API endpoint at /api/result/<id> that returns JSON.
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

    # Extract numeric ID from /result/<id>
    m = re.search(r"/result/(\d+)", entry_url)
    if not m:
        return default

    result_id = m.group(1)
    api_url = f"https://www.thegradcafe.com/api/result/{result_id}"

    try:
        time.sleep(0.3)  # Rate limiting for API calls
        with OPENER.open(api_url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
        # Parse the API response
        details = {
            "comments": data.get("comments"),
            "term": data.get("term"),
            "citizenship": data.get("citizenship"),
            "gpa": data.get("gpa"),
            "gre_total": data.get("gre_total") or data.get("gre"),
            "gre_v": data.get("gre_v") or data.get("gre_verbal"),
            "gre_q": data.get("gre_q") or data.get("gre_quant"),
            "gre_aw": data.get("gre_aw") or data.get("gre_writing"),
        }
        
        # Clean up the values
        for key in details:
            if details[key] in ("", "null", "NULL", "N/A", "n/a"):
                details[key] = None
        
        return details
        
    except error.HTTPError as e:
        if e.code == 404:
            # API endpoint doesn't exist for this result
            pass
        else:
            print(f"  HTTP {e.code} for {api_url}")
        return default
    except Exception as e:
        print(f"  API error for {result_id}: {e}")
        return default


def _parse_row(tr, base_url: str) -> dict:
    """
    Parse a single table row from the search results page.
    """
    # Must contain a detail link
    link = tr.find("a", href=re.compile(r"^/result/"))
    if not link:
        return None
    
    # Must be a main row with 5+ <td> cells
    tds = tr.find_all("td", recursive=False)
    if len(tds) < 4:
        return None

    # Extract entry URL
    entry_url = urljoin(base_url, link["href"])

    # University (robust extractor)
    def extract_university(td):
        # Try multiple known class names used by GradCafe
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
            # Fallback: first line of text in the cell
            raw = td.get_text("\n", strip=True)
            text = raw.split("\n")[0] if raw else None
            
            # Regex fallback for messy HTML
            if not text and raw:
                m = re.search(r"([A-Za-z].+)", raw)
                if m:
                    text = m.group(1).strip()

        # Normalize whitespace
        if text:
            text = re.sub(r"\s+", " ", text).strip()
            
        return text or None

    # Extract fields
    university = extract_university(tds[0]) if len(tds) > 0 else None

    # Program + Degree
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
            # Fallback: try to extract from text
            text = tds[1].get_text(strip=True)
            if text:
                program = text

    # Date Added
    date_added = tds[2].get_text(strip=True) if len(tds) > 2 else None

    # Status + Status Date
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
            # Sometimes status is just the word without "on date"
            status_match = re.search(r"(Accepted|Rejected|Interview|Wait listed|Waitlisted|Other)", 
                                    status_block, re.I)
            if status_match:
                status = status_match.group(1).title()
                if status.lower() == "wait listed":
                    status = "Waitlisted"

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

    # Fetch detail page data from API
    detail = _parse_detail_page(entry_url)
    record.update(detail)

    return record


def scrape_data(max_entries: int = 100, start_page: int = 1):
    """Main scraping function."""
    all_entries = []
    page = start_page

    print(f"Starting GradCafe scraper")
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

        # Progress stats
        n = len(all_entries)
        if n > 0:
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
            
            print(f"  Coverage: ", end="")
            for field, count in stats.items():
                pct = count * 100 // n if n > 0 else 0
                print(f"{field}={pct}% ", end="")
            print()

        # Checkpoint every 5 pages
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
        count = sum(1 for e in all_entries if e.get(field))
        pct = count * 100 // n if n > 0 else 0
        print(f"  {field:15s}: {count:4d} / {n:4d} ({pct:3d}%)")
    
    # Show sample entries with data
    print("\nSample entries with details:")
    count = 0
    for entry in all_entries:
        if entry.get("gpa") or entry.get("citizenship") or entry.get("comments"):
            print(f"  {entry.get('university')} - {entry.get('program_name')}")
            print(f"    GPA={entry.get('gpa')}, Cit={entry.get('citizenship')}, "
                  f"GRE V={entry.get('gre_v')}, Q={entry.get('gre_q')}, AW={entry.get('gre_aw')}")
            if entry.get('comments'):
                comment_preview = entry.get('comments')[:60] + "..." if len(entry.get('comments', '')) > 60 else entry.get('comments')
                print(f"    Comments: {comment_preview}")
            count += 1
            if count >= 5:
                break

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("❌ robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    # Scrape data
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
