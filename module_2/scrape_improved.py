# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 2 Assignment: Web Scraper - IMPROVED VERSION
#
# scrape.py
#
# Key improvements:
# 1. Proper caching to avoid re-fetching detail pages
# 2. Rate limiting to be respectful of the server
# 3. Better error handling
# 4. Progress tracking and resumability

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

# Reuse a single HTTP connection for all requests
OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

# Cache for detail page data to avoid re-fetching
DETAIL_CACHE = shelve.open("detail_cache.db", writeback=True)

IS_FLASK = not sys.stdin.isatty()


def check_robots():
    """Check if robots.txt allows scraping the survey pages."""
    robots_url = urljoin(BASE_URL, "robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    user_agent = USER_AGENT
    allowed = rp.can_fetch(user_agent, urljoin(BASE_URL, "survey/"))
    return allowed


def _get_html(url: str, delay: float = 1.0) -> str:
    """
    Fetch HTML using a persistent opener with rate limiting.
    
    Args:
        url: The URL to fetch
        delay: Seconds to wait before making the request (for rate limiting)
    
    Returns:
        HTML content as a string
    """
    time.sleep(delay)  # Be polite to the server
    try:
        with OPENER.open(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        raise


def _parse_detail_page(entry_url: str, use_cache: bool = True) -> dict:
    """
    Parse detail page data from GradCafe API.
    
    Args:
        entry_url: The URL of the entry detail page
        use_cache: Whether to use cached data if available
    
    Returns:
        Dictionary with detail fields (comments, term, citizenship, GPA, GRE scores)
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
    
    # Extract numeric ID from URL
    m = re.search(r"/result/(\d+)", entry_url)
    if not m:
        return default_detail
    
    result_id = m.group(1)
    
    # Check cache first
    if use_cache and result_id in DETAIL_CACHE:
        print(f"  Cache hit for result {result_id}")
        return DETAIL_CACHE[result_id]
    
    # Fetch from API
    api_url = f"https://www.thegradcafe.com/api/result/{result_id}"
    
    try:
        time.sleep(0.1)  # Rate limit API calls
        with OPENER.open(api_url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        detail = {
            "comments": data.get("comments"),
            "term": data.get("term"),
            "citizenship": data.get("citizenship"),
            "gpa": data.get("gpa"),
            "gre_total": data.get("gre_total"),
            "gre_v": data.get("gre_v"),
            "gre_aw": data.get("gre_aw"),
        }
        
        # Cache the result
        DETAIL_CACHE[result_id] = detail
        print(f"  Fetched and cached result {result_id}")
        
        return detail
        
    except error.HTTPError as e:
        print(f"  HTTP error fetching detail for {result_id}: {e}")
        return default_detail
    except error.URLError as e:
        print(f"  URL error fetching detail for {result_id}: {e}")
        return default_detail
    except json.JSONDecodeError as e:
        print(f"  JSON decode error for {result_id}: {e}")
        return default_detail
    except Exception as e:
        print(f"  Unexpected error fetching detail for {result_id}: {e}")
        return default_detail


def _parse_row(tr, base_entry_url: str) -> dict:
    """
    Parse a table row from the list view into a dictionary.
    
    Args:
        tr: BeautifulSoup table row element
        base_entry_url: Base URL for constructing entry links
    
    Returns:
        Dictionary with applicant data, or None if parsing fails
    """
    tds = tr.find_all("td", recursive=False)
    if len(tds) < 5:
        return None

    # --- University ---
    uni_div = tds[0].find("div", class_="tw-font-medium")
    university = uni_div.get_text(strip=True) if uni_div else None

    # --- Program + Degree ---
    program = degree_level = None
    prog_div = tds[1].find("div")
    if prog_div:
        spans = prog_div.find_all("span")
        if spans:
            program = spans[0].get_text(strip=True)
        if len(spans) > 1:
            degree_level = spans[1].get_text(strip=True)

    # --- Date Added ---
    date_added = tds[2].get_text(strip=True)

    # --- Status + Status Date ---
    status_block = tds[3].get_text(" ", strip=True)
    status = status_date = None
    m = re.match(r"(Accepted|Rejected|Interview|Wait listed)\s+on\s+(.+)", 
                 status_block, re.I)
    if m:
        status = m.group(1).title()
        status_date = m.group(2)

    # --- Entry URL ---
    link = tds[4].find("a", href=True)
    entry_url = urljoin(base_entry_url, link["href"]) if link else None

    # Base record from list view
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

    # Fetch detail page data
    detail = _parse_detail_page(entry_url)
    record.update(detail)

    return record


def scrape_data(max_entries: int = 30000, start_page: int = 1, 
                checkpoint_interval: int = 10):
    """
    Scrape data from GradCafe, combining list and detail views.
    
    Args:
        max_entries: Maximum number of entries to collect
        start_page: Page number to start from (for resuming)
        checkpoint_interval: Save checkpoint every N pages
    
    Returns:
        List of applicant dictionaries with full data
    """
    all_entries = []
    page = start_page
    pages_with_no_data = 0
    max_empty_pages = 3  # Stop after this many consecutive empty pages

    print(f"Starting scrape from page {start_page}")
    print(f"Target: {max_entries} entries")
    print(f"Cache contains {len(DETAIL_CACHE)} detail pages")
    print("-" * 60)

    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        
        try:
            print(f"\nPage {page}:")
            html = _get_html(url, delay=1.0)  # 1 second delay between pages
        except error.HTTPError as e:
            print(f"  HTTP error on page {page}: {e}")
            if e.code == 404:
                print("  Reached end of available pages")
                break
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                break
            page += 1
            continue
        except error.URLError as e:
            print(f"  URL error on page {page}: {e}")
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                break
            page += 1
            continue
        except Exception as e:
            print(f"  Unexpected error on page {page}: {e}")
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                break
            page += 1
            continue

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")
        rows = [tr for tr in rows if tr.find("td")]

        new_count = 0
        for tr in rows:
            entry = _parse_row(tr, url)
            if entry:
                all_entries.append(entry)
                new_count += 1
                
                # Stop if we've reached the max
                if len(all_entries) >= max_entries:
                    break

        if new_count == 0:
            print(f"  No new entries on page {page}")
            pages_with_no_data += 1
            if pages_with_no_data >= max_empty_pages:
                print(f"  Stopping after {max_empty_pages} consecutive empty pages")
                break
        else:
            pages_with_no_data = 0  # Reset counter
            print(f"  Collected {new_count} entries")
            print(f"  Total: {len(all_entries)}/{max_entries} "
                  f"({len(all_entries)*100//max_entries}%)")

        # Save checkpoint periodically
        if page % checkpoint_interval == 0:
            checkpoint_file = "checkpoint.json"
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump({
                    "entries": all_entries,
                    "last_page": page,
                    "timestamp": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            print(f"  Checkpoint saved to {checkpoint_file}")

        page += 1

    # Final statistics
    print("\n" + "=" * 60)
    print("Scrape complete!")
    print(f"Total entries collected: {len(all_entries)}")
    print(f"Detail pages cached: {len(DETAIL_CACHE)}")
    print(f"Final page: {page - 1}")
    print("=" * 60)

    return all_entries[:max_entries]


def main():
    """Main function to run the scraper."""
    # Check robots.txt
    if not check_robots():
        raise SystemExit("robots.txt does not allow scraping the target paths.")
    
    print("robots.txt check passed ✓")
    print()

    # Run scraper
    # Start with 2000 for testing, then increase to 30000+ for full assignment
    data = scrape_data(max_entries=2000, start_page=1, checkpoint_interval=10)

    # Save final data
    output_file = "module_2/llm_extend_applicant_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nData saved to {output_file}")
    
    # Close cache
    DETAIL_CACHE.close()
    print("Cache closed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
        DETAIL_CACHE.close()
        print("Cache closed safely")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        DETAIL_CACHE.close()
        print("Cache closed")
        raise
