=========================================================
Modern Concepts in Python: Spring 2026
Module 2 Assignment: Web Scraping
Due Date: 2/1/2026 @ 11:59 PM EST
Author: Eric Rying
JHED ID: 15C95A
=========================================================

######################################
## Overview
######################################
This project implements a complete GradCafe web‑scraping and data‑cleaning pipeline using 
Python 3.10+, urllib, BeautifulSoup, regex, and a locally hosted LLM as required by the 
Module 2 assignment. The final dataset contains 30,000+ applicant entries stored in 
`applicant_data.json`.

---
######################################
## Approach
######################################

### 1. robots.txt Verification (SHALL)
Before scraping, I implemented a `check_robots()` function using `urllib.robotparser` to 
verify that the `/survey/` path is allowed for my custom user‑agent 
`jhu-module2-scraper`. A screenshot of `robots.txt` is included in the module_2 directory.

### 2. Scraping with urllib (SHALL)
All HTTP requests were performed using `urllib.request.Request` with a custom user‑agent. 
URL management uses `urllib.parse.urljoin` and `urllib.parse.urlencode`.

### 3. Parsing HTML with BeautifulSoup + Regex (SHOULD)
The HTML table on each GradCafe survey page was parsed using BeautifulSoup. For each row:
- University name extracted from `<div class="tw-font-medium">`
- Program name and degree level extracted from `<span>` elements
- Status and status date parsed using regex (e.g., “Rejected on 26 Jan”)
- Entry URL extracted from the `<a>` tag
- Missing fields (comments, GRE, GPA, citizenship, term) are set to `None` because they 
  are not available in the list view.

The scraper loops through pages until 30,000 entries are collected. Initially used 500 to increase cycles of learning 
to validate the overall code pipeline: scrape (load/save) -> clean -> llm_clean

## 4. Clean.py Basic Cleaning (+ later LLM cleaning as noted in 5)

clean.py performs the second stage of the Module 2 workflow: transforming the raw scraped records into a consistent, analysis‑ready dataset. 
The script begins with a basic cleaning pass that normalizes status labels, removes leftover HTML, and converts missing or empty fields into 
None so the data has a uniform structure.

## 5. Data Cleaning with Local LLM (SHALL)
After this initial cleanup, the script prepares the dataset for first‑pass standardization using the local TinyLlama model provided in the 
assignment bundle. Clean.py batches all program and university fields into a temporary file and invokes the LLM once through the llm_hosting/app.py pipeline. 
The model returns two new fields for every record: llm_generated_program and llm_generated_university, which represent the model’s best guess at a standardized 
version of each label. The script then merges these LLM‑generated values back into the cleaned dataset, preserving the original fields while adding the standardized 
ones as additional columns. Finally, clean.py writes the fully processed dataset to applicant_data.json.

### 6. Final JSON Output (SHALL)
The cleaned dataset is stored in `applicant_data.json` with:
- consistent `None` values for missing fields
- normalized status labels
- no HTML remnants
- standardized program and university names

# LLM Install and ENV variables
As required, I installed the provided `llm_hosting` package and ran the local TinyLlama model to standardize program names and university names. 
Environment variables were set  in PowerShell:

# pip install llama-cpp-python-cu121    #Install the CUDA wheel to help speed things up

$env:MODEL_REPO="TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
$env:MODEL_FILE="tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
$env:N_THREADS="8"
$env:N_CTX="2048"
$env:N_GPU_LAYERS="0"    # I have an RTX3090 on my desktop,  still debugging. Maybe try next week

######################################
# Dev + Test Comments:
######################################
I tested the LLM using the sample_data.json to start.
Then, after generating a starting file with 500 entries, I executed the cleaning pipeline using the following to further test:  
> python app.py --file ../raw_applicant_data.json > llm_extend_applicant_data.json

The output includes two new fields from the llm:
- llm_generated_program
- llm_generated_university

######################################
## How to Run
######################################

1. Scrape data:
   python scrape.py            # Output: raw_applicant_data.json

2. Clean + LLM standardize:
   python clean.py             # Input: raw_applicant_data.json, Output: llm_extend_applicant_data.json

   # Note for ref: CLI version is python llm_hosting/app.py --file raw_applicant_data.json > applicant_data.json
  
3. Final cleaned version output:
   llm_extend_applicant_data.json

######################################
## Project Structure
######################################
module_2/
│── scrape.py
│── clean.py
│── raw_applicant_data.json (output from scape.py)
│── applicant_data.json (output from basic cleaning)
│── llm_extend_applicant_data.json (output from LLM cleaning)
│── requirements.txt
│── robots.txt (screenshot included)
│── README.txt
│── llm_hosting/  (local LLM for cleaning)
│     ├── app.py
│     ├── canon_programs.txt  (used by the LLM)
│     ├── canon_universities.txt  (used by the LLM)
│     ├── requirements.txt
│     └── (other provided files)

---
######################################
## Known Bugs and Next Step issues:
######################################

No known SW bugs so far noticed in testing and debug.  

However, the following is a summary of next step issues to consider and address.

Known Output Issues to Review in Next Steps:
1) Minor misspellings (e.g., “Stoony Brook University”)
2) Abbreviations not fully expanded (e.g., “Cuny”)
3) Unicode/encoding artifacts (e.g., “UniversitΣt”, “WisconsinûMadison”)
4) Program drift or typos (e.g., “Sociocultuural Anthropology”)
5) Troll or invalid institutions preserved verbatim (e.g., “Janitor”, “Sarah Stamp”)

#######################
## Module 2 Checklist
#######################

✔ robots.txt verified  
✔ urllib used for all requests  
✔ BeautifulSoup used for parsing  
✔ 30,000+ entries scraped  
✔ Basic cleaning implemented  
✔ Local LLM used for standardization  
✔ llm-generated-program added  
✔ llm-generated-university added  
✔ Output saved to llm_extend_applicant_data.json 