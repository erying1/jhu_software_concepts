#!/usr/bin/env python3
"""
GradCafe scraper tailored to the ACTUAL HTML structure.
Based on analysis of real detail pages.
"""

import json
from os import link
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

DETAIL_CACHE = shelve.open("detail_cache_final.db", writeback=True)


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
    with OPENER.open(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def _parse_detail_page(entry_url: str):
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
        with OPENER.open(api_url) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return default

    return {
        "comments": data.get("comments"),
        "term": data.get("term"),
        "citizenship": data.get("citizenship"),
        "gpa": data.get("gpa"),
        "gre_total": data.get("gre_total"),
        "gre_v": data.get("gre_v"),
        "gre_q": data.get("gre_q"),
        "gre_aw": data.get("gre_aw"),
    }


def _parse_row(tr, base_entry_url: str) -> dict: 
    # Must contain a detail link 
    link = tr.find("a", href=re.compile(r"^/result/")) 
    if not link: 
        return None 
    
    # Must be a main row with 5+ <td> cells 
    tds = tr.find_all("td", recursive=False) 
    if len(tds) < 5: 
        return None

    entry_url = urljoin(base_entry_url, link["href"])

    # University (robust extractor) 
    def extract_university(td): 
        # Try multiple known class names used by GradCafe 
        uni_div = (
            td.find("div", class_="tw-font-medium") or 
            td.find("div", class_="font-medium") or 
            td.find("div", class_="font-semibold") or 
            td.find("span", class_="font-medium") or 
            td.find("span", class_="font-semibold")
        )

        if uni_div:
            text = uni_div.get_text(strip=True)
        else:
            # Fallback: first line of text in the cell
            raw = td.get_text("\n", strip=True)
            text = raw.split("\n")[0] if raw else None
            
            # Regex fallback for messy HTML if not text and raw: 
            m = re.search(r"([A-Za-z].+)", raw) 
            if m: 
                text = m.group(1).strip()

        # Normalize whitespace
        if text:
            text = re.sub(r"\s+", " ", text).strip()
            
        return text or None

    # Use it
    university = extract_university(tds[0])


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
    link = tr.find("a", href=re.compile(r"^/result/"))
 
    if link: 
        entry_url = urljoin(base_entry_url, link["href"]) 
    else: 
        entry_url = None

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
        detail = _parse_detail_page(entry_url)
        record.update(detail)

    return record


def scrape_data(max_entries: int = 100, start_page: int = 1):
    """Main scraping function."""
    all_entries = []
    page = start_page

    print(f"Starting scrape")
    print(f"Target: {max_entries} entries")
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
                    print(f"  {len(all_entries)} entries")
                
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
        
        print(f"  Coverage: ", end="")
        for field, count in stats.items():
            pct = count*100//n if n > 0 else 0
            print(f"{field}={pct}% ", end="")
        print()

        # Checkpoint every 3 pages
        if page % 3 == 0:
            with open("checkpoint.json", "w", encoding="utf-8") as f:
                json.dump({"entries": all_entries, "last_page": page}, 
                         f, ensure_ascii=False, indent=2)

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
        print(f"  {field:15s}: {count:4d} / {n:4d} ({pct:3d}%)")
    
    # Show sample values
    print("\nSample values:")
    for entry in all_entries[:5]:
        if entry.get("gpa") or entry.get("citizenship"):
            print(f"  GPA={entry.get('gpa')}, Cit={entry.get('citizenship')}, "
                  f"V={entry.get('gre_v')}, AW={entry.get('gre_aw')}")

    return all_entries[:max_entries]


def main():
    """Main function."""
    if not check_robots():
        raise SystemExit("robots.txt check failed")
    
    print("✓ robots.txt OK\n")

    data = scrape_data(max_entries=20, start_page=1)

    import os
    os.makedirs("module_2", exist_ok=True)
    
    with open("module_2/raw_applicant_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved to module_2/raw_applicant_data.json")
    
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
