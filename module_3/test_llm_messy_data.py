#!/usr/bin/env python3
"""
Test if LLM actually standardizes messy input
"""

import json
import subprocess
import sys
import tempfile
import os

# Create test data with intentionally messy input
test_data = [
    {"program_name": "CS", "university": "MIT"},  # Already clean
    {"program_name": "Info Studies", "university": "McG"},  # Needs expansion
    {"program_name": "comp sci", "university": "Stanford Univ"},  # Needs capitalization
    {"program_name": "Mathematics", "university": "UBC"},  # Abbreviation
    {"program_name": "Machine Learning", "university": "CMU"},  # Abbreviation
    {"program_name": "data science", "university": "berkeley"},  # All lowercase
]

print("="*60)
print("Testing LLM Standardization")
print("="*60)
print("\nTest input (messy data):")
for i, item in enumerate(test_data, 1):
    print(f"  {i}. {item['program_name']} @ {item['university']}")

# Write to temp file
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding='utf-8') as tmp_in:
    json.dump(test_data, tmp_in)
    tmp_in_path = tmp_in.name

tmp_out_path = tmp_in_path + ".out"

# Path to app.py
app_path = "module_3/module_2.1/llm_hosting/app.py"

if not os.path.exists(app_path):
    print(f"\n✗ Can't find {app_path}")
    sys.exit(1)

print(f"\n✓ Found app.py at: {app_path}")

# Run LLM
cmd = [sys.executable, app_path, "--file", tmp_in_path, "--out", tmp_out_path]

print(f"\nRunning LLM...")
print(f"Command: {' '.join(cmd)}")
print("\n" + "="*60)

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    
    # Read output
    if os.path.exists(tmp_out_path):
        with open(tmp_out_path, 'r', encoding='utf-8') as f:
            output = []
            for line in f:
                if line.strip():
                    output.append(json.loads(line))
        
        print("\n" + "="*60)
        print("LLM Output:")
        print("="*60)
        
        for i, item in enumerate(output, 1):
            orig_prog = test_data[i-1]['program_name']
            orig_uni = test_data[i-1]['university']
            llm_prog = item.get('llm-generated-program', '???')
            llm_uni = item.get('llm-generated-university', '???')
            
            prog_changed = orig_prog != llm_prog
            uni_changed = orig_uni != llm_uni
            
            marker_p = "✓" if prog_changed else "✗"
            marker_u = "✓" if uni_changed else "✗"
            
            print(f"\n{i}. Input:  '{orig_prog}' @ '{orig_uni}'")
            print(f"   Output: '{llm_prog}' @ '{llm_uni}'")
            print(f"   Changed: Program {marker_p}  University {marker_u}")
        
        # Summary
        total_changed = sum(1 for i, item in enumerate(output) 
                           if (item.get('llm-generated-program') != test_data[i]['program_name'] or
                               item.get('llm-generated-university') != test_data[i]['university']))
        
        print("\n" + "="*60)
        print(f"Summary: {total_changed}/{len(output)} records were changed")
        print("="*60)
        
        if total_changed == 0:
            print("\n⚠️  WARNING: LLM made NO changes!")
            print("This suggests the LLM is not standardizing properly.")
            print("\nPossible issues:")
            print("  - LLM prompt/few-shot examples too conservative")
            print("  - Temperature = 0 making it too deterministic")
            print("  - Fallback function being used instead of LLM")
        
    else:
        print("✗ Output file not created")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Cleanup
    try:
        os.remove(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)
    except:
        pass
