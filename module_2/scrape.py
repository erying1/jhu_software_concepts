# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 2 Assignment: Web Scraper
#
# scrape.py
#
# Brief Overview:
#
# scrape.py is the first stage of the Module 2 pipeline. Its job is to collect raw applicant data from TheGradCafe’s public results pages 
# in a way that is respectful of the site’s rules and compatible with the assignment’s constraints.

# The script begins by checking the site’s robots.txt file to confirm that scraping the /survey/ pages is permitted. Once allowed, it uses 
# Python’s standard urllib library to fetch each results page and BeautifulSoup/regular expressions to extract the fields required for the 
# assignment: program name, university, status, status date, degree level, comments, and the entry URL. Because the list‑view pages do not 
# include GRE scores or GPA, those fields are recorded as None to maintain a consistent schema.

# The scraper loops through all available result pages, normalizes missing values, and stores each record as a Python dictionary. When the 
# crawl completes, the script writes the full dataset to raw_applicant_data.json, which becomes the input to the cleaning and 
# LLM‑standardization stages that follow.

# Import necessary libraries
import json
import time
import re
from urllib import request, parse, error
from urllib.parse import urljoin
import urllib.robotparser 
from urllib.parse import urljoin

from bs4 import BeautifulSoup

USER_AGENT = "jhu-module2-scraper"

# Reuse a single HTTP connection for all requests
OPENER = request.build_opener()
OPENER.addheaders = [("User-Agent", USER_AGENT)]

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

import shelve 
DETAIL_CACHE = shelve.open("detail_cache.db")

import sys 
IS_FLASK = not sys.stdin.isatty()

# Define a function to check robots.txt
def check_robots(): 
    robots_url = urljoin(BASE_URL, "robots.txt") 
    rp = urllib.robotparser.RobotFileParser() 
    rp.set_url(robots_url) 
    rp.read() 
    # Use a reasonable user-agent string 
    user_agent = "jhu-module2-scraper" 
    allowed = rp.can_fetch(user_agent, urljoin(BASE_URL, "survey/")) 
    return allowed

# Private helper to fetch HTML content
def _get_html(url: str) -> str: 
    """_get_html(): private helper to fetch HTML using a persistent opener.""" 
    with OPENER.open(url) as resp: 
        return resp.read().decode("utf-8", errors="ignore")

# Private helper to parse a table row into a dict
def _parse_row(tr, base_entry_url: str):
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
    m = re.match(r"(Accepted|Rejected|Interview|Wait listed)\s+on\s+(.+)", status_block, re.I)
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

    # To address module 2 feedback
    detail = _parse_detail_page(entry_url) 
    record.update(detail)

    return record

def _parse_detail_page(entry_url): 
    if not entry_url: 
        return { 
            "comments": None, 
            "term": None, 
            "citizenship": None, 
            "gpa": None, 
            "gre_total": None, 
            "gre_v": None, 
            "gre_aw": None, 
        } 
    # Extract numeric ID from URL 
    m = re.search(r"/result/(\d+)", entry_url) 
    if not m: 
        return {} 
    
    result_id = m.group(1) 
    api_url = f"https://www.thegradcafe.com/api/result/{result_id}" 
    
    try: 
        with OPENER.open(api_url) as resp: 
            data = json.loads(resp.read().decode("utf-8")) 
    except Exception: 
        return {} 
    
    return { 
        "comments": data.get("comments"), 
        "term": data.get("term"), 
        "citizenship": data.get("citizenship"), 
        "gpa": data.get("gpa"), 
        "gre_total": data.get("gre_total"), 
        "gre_v": data.get("gre_v"), 
        "gre_aw": data.get("gre_aw"), 
    }

# Main scraping function
# Running this script will scrape and save data to raw_applicant_data.json

def scrape_data(max_entries: int = 30000, start_page: int = 1):
    """
    scrape_data(): pulls data from Grad Cafe.
    Returns a list of raw applicant dicts.
    Includes error checking for HTTP and URL errors.
    """
    all_entries = []
    page = start_page

    while len(all_entries) < max_entries:
        params = {"page": page}
        url = SEARCH_URL + "?" + parse.urlencode(params)
        try:
            html = _get_html(url)
        except error.HTTPError as e:
            print(f"HTTP error on page {page}: {e}")
            break
        except error.URLError as e:
            print(f"URL error on page {page}: {e}")
            break
        
        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(html, "html.parser")

        # Refer to GradCafe’s HTML to find the correct table selector.
        rows = soup.select("table tr")
        rows = [tr for tr in rows if tr.find("td")]

        new_count = 0
        for tr in rows:
            entry = _parse_row(tr, url)
            if entry:
                all_entries.append(entry)
                new_count += 1

        if new_count == 0:
            print(f"No new entries on page {page}, stopping.")
            break

        print(f"Page {page}: collected {new_count} entries (total {len(all_entries)})")
        print(f"Estimated progress: {len(all_entries)}/{max_entries}")
        page += 1
        time.sleep(0.1)  # be polite
        if page % 10 == 0: 
            with open("checkpoint.json", "w") as f: 
                json.dump(all_entries, f)

    print("Scrape complete.") 
    print(f"Total entries collected: {len(all_entries)}") 
    print(f"Detail pages cached: {len(DETAIL_CACHE)}")

    return all_entries[:max_entries]

# Main function to call scrape_data and save to JSON
if __name__ == "__main__":
    #from scrape import check_robots  # or move check_robots above

    #Exit the program if robots.txt disallows scraping
    if not check_robots():
        raise SystemExit("robots.txt does not allow scraping the target paths.")

    # update later to 30000 once verified to save time.  Initially use 500 to increase cycles of learning 
    # to validate
    data = scrape_data(max_entries=2000)  # Updated to 40000 per Liv's instruction in the class video, i.e., > 30K for upcoming weeks' assignments for proper stats
    
    # Raw data can be saved or passed to clean_data() in clean.py
    with open("module_2/llm_extend_applicant_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
