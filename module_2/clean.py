# Modern Concepts in Python: Spring 2026
# by Eric Rying
#
# Module 2 Assignment: Web Scraper
#
# clean.py

# Overview of clean.py:
#
# clean.py performs the second stage of the Module 2 workflow: transforming the raw scraped records into a consistent, analysis‑ready dataset. 
# The script begins with a basic cleaning pass that normalizes status labels, removes leftover HTML, and converts missing or empty fields into 
# None so the data has a uniform structure.
#
# After this initial cleanup, the script prepares the dataset for first‑pass standardization using the local TinyLlama model provided in the 
# assignment bundle. Clean.py batches all program and university fields into a temporary file and 
# invokes the LLM once through the llm_hosting/app.py pipeline. The model returns two new fields for every record—llm-generated-program and 
# llm-generated-university—which represent the model’s best guess at a standardized version of each label.
# The script then merges these LLM‑generated values back into the cleaned dataset, preserving the original fields while adding the standardized 
# ones as additional columns. Finally, clean.py writes the fully processed dataset to applicant_data.json.

# Input file: raw_applicant_data.json (from scrape.py)
# Output file: cleaned_applicant_data.json (includes basic cleaning)
#              llm_extend_applicant_data.json (after calling the LLM for standardization and merging results)

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
    """Normalize one record."""
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
        if not val or str(val).strip() == "":
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
    """
    Full cleaning pipeline:
    1. Basic cleaning
    2. Batch LLM standardization
    3. Merge LLM results into records
    """

    # 1. Basic cleaning 
    cleaned_basic = [_clean_single_record(r) for r in raw_records] 
    
    # 2. Save pre‑LLM cleaned snapshot 
    save_data(cleaned_basic, "cleaned_data.json") 
    
    # 3. Prepare batch data for LLM 
    batch_input = [ 
        { "program_name": r["program_name"], 
          "university": r["university"] 
        }          
        for r in cleaned_basic ] 
    
    # 4. Run batch LLM cleaning 
    cleaned_LLM_output = llm_clean_batch(batch_input) 
    
    # 5. Merge LLM results back into cleaned_basic 
    for rec, llm in zip(cleaned_basic, cleaned_LLM_output): 
        rec["llm-generated-program"] = llm.get("llm-generated-program", rec["program_name"]) 
        rec["llm-generated-university"] = llm.get("llm-generated-university", rec["university"]) 
    
    return cleaned_basic
      

def save_data(cleaned_records: List[Dict], filename: str = "applicant_data.json"):
    """Save cleaned data to JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)


def load_data(filename: str = "applicant_data.json") -> List[Dict]:
    """Load cleaned data from JSON."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)



# LLM cleaning step (required by assignment) 
# Calls the local TinyLlama standardizer in llm_hosting/app.py in a batch mode for the whole file

def llm_clean_batch(records: list[dict]) -> list[dict]:
    """
    Calls the local LLM standardizer (llm_hosting/app.py) on a batch of records.
    Returns a list of dicts with LLM-generated fields merged in.
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
    "llm_hosting/app.py",
    "--file", tmp_in_path,
    "--out", tmp_out_path
   ]


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


if __name__ == "__main__":
    # Example pipeline: load raw, clean, save file
    raw = load_data("module_2/raw_applicant_data.json")
    print(f"Loaded {len(raw)} rows from module_2/raw_applicant_data.json")

    # Clean the data: basic and LLM
    cleaned = clean_data(raw)

    save_data(cleaned, "module_2/llm_extend_applicant_data.json")
    print(f"Saved {len(cleaned)} rows after clean+LLM to module_2/llm_extend_applicant_data.json")

