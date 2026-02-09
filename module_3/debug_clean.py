#!/usr/bin/env python3
"""
Debug script to check what's happening with clean.py
"""

import json
import os
import sys

# Check if files exist
print("="*60)
print("Checking file paths...")
print("="*60)

# Check raw data
raw_data_path = "module_3/module_2.1/raw_applicant_data.json"
if os.path.exists(raw_data_path):
    try:
        with open(raw_data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        print(f"✓ Found raw data: {len(raw_data)} records")
    except Exception as e:
        print(f"✗ Error reading raw data: {e}")
        raw_data = []
else:
    print(f"✗ Raw data not found: {raw_data_path}")

# Check if llm_hosting/app.py exists
llm_paths_to_check = [
    "llm_hosting/app.py",
    "module_3/module_2.1/llm_hosting/app.py",
    "module_2/llm_hosting/app.py",
]

print("\nChecking for llm_hosting/app.py:")
for path in llm_paths_to_check:
    if os.path.exists(path):
        print(f"  ✓ Found: {path}")
    else:
        print(f"  ✗ Not found: {path}")

# Check if model exists
model_paths_to_check = [
    "llm_hosting/models/tinyllama-1.1b-chat-v1.0.Q3_K_M.gguf",
    "module_3/module_2.1/llm_hosting/models/tinyllama-1.1b-chat-v1.0.Q3_K_M.gguf",
    "models/tinyllama-1.1b-chat-v1.0.Q3_K_M.gguf",
]

print("\nChecking for model file:")
for path in model_paths_to_check:
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024*1024)
        print(f"  ✓ Found: {path} ({size_mb:.1f} MB)")
    else:
        print(f"  ✗ Not found: {path}")

# Check output files
print("\nChecking output files:")
output_files = [
    "module_3/module_2.1/cleaned_data.json",
    "module_3/module_2.1/llm_extend_applicant_data.json",
]

for path in output_files:
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if LLM fields exist
            has_llm = any('llm-generated-program' in r for r in data)
            
            print(f"  ✓ {path}")
            print(f"    Records: {len(data)}")
            print(f"    Has LLM fields: {has_llm}")
            
            if has_llm:
                sample = next((r for r in data if r.get('llm-generated-program')), None)
                if sample:
                    print(f"    Sample: {sample.get('program_name')} -> {sample.get('llm-generated-program')}")
        except Exception as e:
            print(f"  ✗ Error reading {path}: {e}")
    else:
        print(f"  ✗ Not found: {path}")

print("\n" + "="*60)
print("Current working directory:", os.getcwd())
print("="*60)
