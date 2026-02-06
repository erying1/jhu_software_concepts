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

BASE_URL = "https://www.thegradcafe.com/"
SEARCH_URL = "https://www.thegradcafe.com/survey/"

USER_AGENT = "jhu-module2-scraper"

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
    """_get_html(): private helper to fetch HTML using urllib."""
    req = request.Request(url, headers={"User-Agent": USER_AGENT})
    with request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="ignore")

# Private helper to parse a table row into a dict
def _parse_row(tr, base_entry_url: str):
    tds = tr.find_all("td")
    if len(tds) < 5:
        return None

    # --- University ---
    uni_div = tds[0].find("div", class_="tw-font-medium")
    university = uni_div.get_text(strip=True) if uni_div else None

    # --- Program + Degree ---
    program = None
    degree_level = None
    prog_div = tds[1].find("div")
    if prog_div:
        spans = prog_div.find_all("span")
        if len(spans) >= 1:
            program = spans[0].get_text(strip=True)
        if len(spans) >= 2:
            degree_level = spans[1].get_text(strip=True)

    # --- Date Added ---
    date_added = tds[2].get_text(strip=True)

    # --- Status + Status Date ---
    status_block = tds[3].get_text(" ", strip=True)
    # Example: "Rejected on 26 Jan"
    status = None
    status_date = None
    m = re.match(r"(Accepted|Rejected|Interview|Wait listed)\s+on\s+(.+)", status_block, re.I)
    if m:
        status = m.group(1).title()
        status_date = m.group(2)

    # --- Entry URL ---
    link = tds[4].find("a", href=True)
    entry_url = urljoin(base_entry_url, link["href"]) if link else None

    # Sets the nominal value to None if not available, as per requirements
    # Defined as per requirements in the assignment page for module 2
    return {
        "program_name": program,
        "university": university,
        "comments": None,          # not available on list page
        "date_added": date_added,
        "entry_url": entry_url,
        "status": status,
        "status_date": status_date,
        "term": None,              # not available on list page
        "citizenship": None,       # not available on list page
        "gre_total": None,         # not available on list page
        "gre_v": None,
        "degree_level": degree_level,
        "gpa": None,
        "gre_aw": None,
    }

# Main scraping function
# Running this script will scrape and save data to raw_applicant_data.json

def scrape_data(max_entries: int = 30000):
    """
    scrape_data(): pulls data from Grad Cafe.
    Returns a list of raw applicant dicts.
    Includes error checking for HTTP and URL errors.
    """
    all_entries = []
    page = 1

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
        table = soup.find("table")
        if not table:
            print(f"No table found on page {page}, stopping.")
            break

        rows = table.find_all("tr")
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
        page += 1
        time.sleep(1)  # be polite

    return all_entries[:max_entries]

# Main function to call scrape_data and save to JSON
if __name__ == "__main__":
    #from scrape import check_robots  # or move check_robots above

    #Exit the program if robots.txt disallows scraping
    if not check_robots():
        raise SystemExit("robots.txt does not allow scraping the target paths.")

    # update later to 30000 once verified to save time.  Initially use 500 to increase cycles of learning 
    # to validate
    data = scrape_data(max_entries=1000)  # Updated to 40000 per Liv's instruction in the class video, i.e., > 30K for upcoming weeks' assignments for proper stats
    
    # Raw data can be saved or passed to clean_data() in clean.py
    with open("raw_applicant_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
