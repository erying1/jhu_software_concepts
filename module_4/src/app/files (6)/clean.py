# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 2 Assignment: Web Scraper
#
# clean.py

"""
clean.py -- Module 2 Data Cleaning Pipeline
--------------------------------------------
Transforms raw scraped records into a consistent, analysis-ready dataset.

The pipeline has three stages:

1. **Basic cleaning** -- normalize status labels, strip HTML from comments,
   convert numeric fields, and standardize citizenship values.
2. **LLM standardization** -- batch-process program and university names
   through a local LLM to produce canonical labels.
3. **Merge** -- attach the LLM-generated fields back to each record.

Input:
    ``raw_applicant_data.json`` (from ``scrape.py``)

Output:
    ``cleaned_data.json`` (after basic cleaning),
    ``llm_extend_applicant_data.json`` (after LLM standardization)
"""

# Need for basic cleaning
import json
import re
from typing import List, Dict

# Need for LLM cleaning
import subprocess
import tempfile
import os

import sys 
PYTHON = sys.executable

from anthropic import Anthropic
import anthropic

def _normalize_status(status: str | None) -> str | None:
    """Normalize an application status string to a canonical value.

    Args:
        status: Raw status string (e.g. 'accepted', 'Rejected', 'Wait listed').

    Returns:
        str | None: One of 'Accepted', 'Rejected', 'Waitlisted', the stripped
        original, or None if input is empty/None.
    """
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

def normalize_status(status): 
    """Public wrapper for ``_normalize_status``.

    Args:
        status: Raw status string.

    Returns:
        str | None: Normalized status value.
    """ 
    return _normalize_status(status)

def _clean_single_record(rec: Dict) -> Dict:
    """Normalize a single applicant record.

    Performs status normalization, text stripping, HTML removal from comments,
    numeric conversion for GPA/GRE fields, and citizenship standardization.

    Args:
        rec (dict): Raw scraped record.

    Returns:
        dict: Cleaned record with normalized fields.
    """
    rec = dict(rec)  # shallow copy

    # --- Normalize status ---
    rec["status"] = _normalize_status(rec.get("status"))

    # --- Normalize text fields ---
    text_fields = [
        "program_name", "university", "comments", "date_added",
        "entry_url", "status_date", "term", "citizenship",
        "degree_level"
    ]

    for key in text_fields:
        val = rec.get(key)
        if val is None: 
            rec[key] = None 
        else: 
            rec[key] = str(val).strip()

    # --- Strip HTML from comments ---
    if rec["comments"]:
        rec["comments"] = re.sub(r"<[^>]+>", "", rec["comments"]).strip()

    # --- Normalize numeric fields ---
    def to_float(x):
        try:
            return float(x)
        except:
            return None

    def to_int(x):
        try:
            return int(x)
        except:
            return None

    rec["gpa"] = to_float(rec.get("gpa"))
    rec["gre_total"] = to_int(rec.get("gre_total"))
    rec["gre_v"] = to_int(rec.get("gre_v"))
    rec["gre_aw"] = to_float(rec.get("gre_aw"))

    # --- Normalize citizenship ---
    if rec["citizenship"]:
        c = rec["citizenship"].lower()
        if "american" in c:
            rec["citizenship"] = "American"
        elif "international" in c:
            rec["citizenship"] = "International"
        else:
            rec["citizenship"] = "Other"

    return rec



def clean_data(raw_records: List[Dict]) -> List[Dict]:
    """Run the full cleaning pipeline on a list of raw records.

    Steps:
        1. Basic cleaning (normalize fields, strip HTML, convert types).
        2. Batch LLM standardization of program and university names.
        3. Merge LLM-generated fields back into each record.

    Args:
        raw_records (list[dict]): Raw scraped records from ``scrape.py``.

    Returns:
        list[dict]: Cleaned records with LLM-generated fields attached.
    """

 
    # 1. Basic cleaning 
 
    total = len(raw_records) 
    print(f"Starting basic cleaning on {total} records...") 
    
    if not raw_records:
        return []  # <-- prevents file write

    cleaned_basic = [] 
    for i, r in enumerate(raw_records, start=1): 
        cleaned_basic.append(_clean_single_record(r)) 
        if i % 1000 == 0 or i == total: 
            print(f" Basic cleaning: {i}/{total} ({i/total:.1%})")

    # 2. Save pre‑LLM cleaned snapshot 
    # Only save if directory exists (prevents test failures)
    try:
        save_data(cleaned_basic, "module_3/module_2.1/cleaned_data.json")
    except FileNotFoundError:
        #Swallow during tests
        pass
        
    # 3. Prepare batch data for LLM 
    print("Preparing LLM batch input...") 
    print(f" Creating LLM batch for {len(cleaned_basic)} records...")

    batch_input = [ 
        { "program_name": r["program_name"], 
          "university": r["university"] 
        }          
        for r in cleaned_basic 
    ] 
    
    # 4. Run batch LLM cleaning 
    print("Running LLM batch...")
    cleaned_LLM_output = llm_clean_batch(batch_input) 
    
    # 5. Merge LLM results back into cleaned_basic 
    print("Merging LLM results back into records...") 
    total = len(cleaned_basic)

    for i, (rec, llm) in enumerate(zip(cleaned_basic, cleaned_LLM_output), start=1): 
        rec["llm-generated-program"] = llm.get("llm-generated-program", rec["program_name"]) 
        rec["llm-generated-university"] = llm.get("llm-generated-university", rec["university"])
       
        if i % 1000 == 0 or i == total: 
            print(f" LLM merge: {i}/{total} ({i/total:.1%})")

    print("Cleaning complete.") 
    print(f" Total records processed: {len(cleaned_basic)}")
    
    return cleaned_basic
      

     
def save_data(cleaned_records: List[Dict], filename: str = "applicant_data.json"):
    """Save cleaned records to a JSON file.

    Args:
        cleaned_records (list[dict]): Records to save.
        filename (str): Output file path.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)


def load_data(filename: str = "applicant_data.json") -> List[Dict]:
    """Load records from a JSON file.

    Args:
        filename (str): Path to the JSON file.

    Returns:
        list[dict]: Parsed records.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)



# LLM cleaning step (required by assignment) 
# Calls the local TinyLlama standardizer in llm_hosting/app.py in a batch mode for the whole file

def llm_clean_batch(records: list[dict]) -> list[dict]:
    """Standardize program and university names using a local LLM.

    Writes records to a temp file, invokes ``llm_hosting/app.py``, and reads
    back JSONL output with ``llm-generated-program`` and
    ``llm-generated-university`` fields.

    Args:
        records (list[dict]): Batch of records with ``program_name``
            and ``university`` fields.

    Returns:
        list[dict]: Records with LLM-generated fields, or the original
        records unchanged if the LLM step fails.
    """

    if not records:
        return []

    # Write batch to a temporary input file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp_in:
        json.dump(records, tmp_in)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path + ".out"

    cmd = [ 
        PYTHON, 
        os.path.join(os.path.dirname(__file__), "llm_hosting", "app.py"), 
        "--file", tmp_in_path, "--out", tmp_out_path 
    ]

    print("Running LLM with command:", cmd)
    
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"LLM batch failed: {e}")
        # Return original records unchanged
        return records

    # Read JSONL output
    cleaned = []
    try:
        with open(tmp_out_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cleaned.append(json.loads(line))
    except Exception as e:
        print(f"Failed to read LLM batch output: {e}")
        return records

    # Cleanup
    try:
        os.remove(tmp_in_path)
        os.remove(tmp_out_path)
    except:
        pass

    return cleaned


def main():
    """Run the full cleaning pipeline from the command line.

    Loads raw data, runs basic + LLM cleaning, and saves the result.
    """
    raw = load_data("module_3/module_2.1/raw_applicant_data.json")
    print(f"Loaded {len(raw)} rows from module_3/module_2.1/raw_applicant_data.json")

    cleaned = clean_data(raw)

    save_data(cleaned, "module_3/module_2.1/llm_extend_applicant_data.json")
    print(f"Saved {len(cleaned)} rows after clean+LLM to module_3/module_2.1/llm_extend_applicant_data.json")


if __name__ == "__main__":  # pragma: no cover
    main()

__all__ = [ 
    "clean_single_record", 
    "normalize_status", 
    "clean_data", 
    "save_data", 
    "load_data", 
    "llm_clean_batch", 
    "main",
]