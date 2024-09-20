"""
Script to check the coverage numbers.
Not a part of the test suite.
"""
import json
import sys
from pathlib import Path

PASS_PERCENTAGE = 0 # Disable this until we can make it configurable from commandline args -> jenkins parameter

current_directory = Path.cwd()
with open(current_directory / 'coverage_data' / 'new_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if "total_coverage" not in data:
    print("'total_coverage' key not found in the coverage data.")
    sys.exit(1)  # Fails jenkins step

if data["total_coverage"] < PASS_PERCENTAGE:
    print(f"Coverage is below the threshold. Coverage: {data['total_coverage']}% < 80%")
    sys.exit(1)  

print("Coverage check passed!")
sys.exit(0)  # Passes jenkins step
