#!/usr/bin/env python3
"""
Test if the LLM subprocess actually works
"""

import json
import subprocess
import sys
import os
import tempfile

print("="*60)
print("Testing LLM subprocess")
print("="*60)

# Create a tiny test input
test_data = [
    {"program_name": "Computer Science", "university": "Stanford University"},
    {"program_name": "Info Studies", "university": "McG"},
]

# Write to temp file
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding='utf-8') as tmp_in:
    json.dump(test_data, tmp_in)
    tmp_in_path = tmp_in.name

tmp_out_path = tmp_in_path + ".out"

print(f"\nTest input file: {tmp_in_path}")
print(f"Test output file: {tmp_out_path}")

# Try different possible paths for app.py
possible_paths = [
    "llm_hosting/app.py",
    "module_3/module_2.1/llm_hosting/app.py",
    "module_2/llm_hosting/app.py",
]

app_path = None
for path in possible_paths:
    if os.path.exists(path):
        app_path = path
        print(f"\n✓ Found app.py at: {path}")
        break

if not app_path:
    print("\n✗ Could not find llm_hosting/app.py in any expected location!")
    print("\nChecked:")
    for path in possible_paths:
        print(f"  - {path}")
    sys.exit(1)

# Build command
cmd = [sys.executable, app_path, "--file", tmp_in_path, "--out", tmp_out_path]

print(f"\nCommand: {' '.join(cmd)}")
print("\n" + "="*60)
print("Running subprocess...")
print("="*60)

try:
    result = subprocess.run(
        cmd, 
        check=True,
        capture_output=True,
        text=True
    )
    
    print("\n✓ Subprocess completed successfully!")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    # Check output
    if os.path.exists(tmp_out_path):
        print(f"\n✓ Output file created!")
        
        with open(tmp_out_path, 'r', encoding='utf-8') as f:
            output = []
            for line in f:
                if line.strip():
                    output.append(json.loads(line))
        
        print(f"  Records in output: {len(output)}")
        
        if output:
            print("\nSample output:")
            for i, record in enumerate(output[:2], 1):
                print(f"\n  Record {i}:")
                print(f"    Input:  {record.get('program_name')} @ {record.get('university')}")
                print(f"    Output: {record.get('llm-generated-program')} @ {record.get('llm-generated-university')}")
    else:
        print(f"\n✗ Output file not created!")
        
except subprocess.CalledProcessError as e:
    print(f"\n✗ Subprocess failed with return code {e.returncode}")
    print(f"\nSTDOUT:\n{e.stdout}")
    print(f"\nSTDERR:\n{e.stderr}")
    
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

print("\n" + "="*60)
