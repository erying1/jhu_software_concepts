# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 2 Assignment: Web Scraper
#
# clean.py

# Import necessary libraries
import json
import os
import re
from typing import List, Dict

from urllib import request
import urllib.error

def _normalize_status(status: str | None) -> str | None:
    if not status:
        return None
    s = status.strip().lower()
    if "accept" in s:
        return "Accepted"
    if "reject" in s:
        return "Rejected"
    if "wait" in s:
        return "Waitlisted"
    return status.strip()

def _clean_single_record(rec: Dict) -> Dict:
    """_clean_single_record(): private helper to normalize one record."""
    rec = dict(rec)  # shallow copy

    rec["status"] = _normalize_status(rec.get("status"))

    # Ensure missing values are None
    for key in [
        "program_name", "university", "comments", "date_added", "entry_url",
        "status_date", "term", "citizenship", "degree_level"
    ]:
        if not rec.get(key):
            rec[key] = None

    # Strip HTML remnants if any slipped through
    if rec["comments"]:
        rec["comments"] = re.sub(r"<[^>]+>", "", rec["comments"]).strip()

    return rec

# Main cleaning function
def clean_data(raw_records: List[Dict]) -> List[Dict]:
    """
    clean_data(): converts data into a structured, normalized format.
    """
    cleaned = []
    for rec in raw_records:
        cleaned.append(_clean_single_record(rec))
    return cleaned

# Private helper to call LLM API for batch cleaning
def _call_llm_batch(records: List[Dict]) -> List[Dict]:
    """
    _call_llm_batch(): private helper to clean data using an LLM.
    You can batch comments or full records and ask the LLM to:
      - fix typos
      - standardize term names
      - remove irrelevant noise
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # If you don't have an API key, you can skip or stub this.
        print("No OPENAI_API_KEY set; skipping LLM cleaning.")
        return records

    # Example: send only comments + term to LLM for normalization.
    # In practice, chunk this to avoid large payloads.
    prompt_records = [
        {
            "comments": r.get("comments"),
            "term": r.get("term")
        }
        for r in records
    ]

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a data cleaning assistant. "
                    "For each record, clean the comments (remove noise, fix obvious typos) "
                    "and standardize the term (e.g., 'Fall 2025', 'Spring 2024'). "
                    "Return JSON with the same list structure and keys."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt_records),
            },
        ],
        "temperature": 0.0,
    }

    req = request.Request(
        LLM_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"LLM request failed: {e}")
        return records

    try:
        content = resp_data["choices"][0]["message"]["content"]
        cleaned_partial = json.loads(content)
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return records

    # Merge LLM-cleaned fields back into original records
    for rec, llm_rec in zip(records, cleaned_partial):
        if "comments" in llm_rec:
            rec["comments"] = llm_rec["comments"]
        if "term" in llm_rec:
            rec["term"] = llm_rec["term"]

    return records

# Save cleaned data to JSON
def save_data(cleaned_records: List[Dict], filename: str = "applicant_data.json"):
    """
    save_data(): saves cleaned data into a JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

# Load cleaned data from JSON
def load_data(filename: str = "applicant_data.json") -> List[Dict]:
    """
    load_data(): loads cleaned data from a JSON file.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# Main function to call clean_data and save to JSON file, applicant_data.json
if __name__ == "__main__":
    # Example pipeline: load raw, clean, save file
    with open("raw_applicant_data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    cleaned = clean_data(raw)
    save_data(cleaned, "applicant_data.json")
