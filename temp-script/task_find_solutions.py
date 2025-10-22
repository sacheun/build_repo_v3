"""
Task: Find all solution (.sln) files in repository
Input: repo_directory, repo_name (command-line arguments)
Output: JSON file with solutions array
"""

import sys
import os
import json
from datetime import datetime

if len(sys.argv) < 3:
    print("Usage: task_find_solutions.py <repo_directory> <repo_name>")
    sys.exit(1)

repo_dir = sys.argv[1]
repo_name = sys.argv[2]

print(f"Task: task-find-solutions")
print(f"Repository: {repo_name}")
print(f"Directory: {repo_dir}")

result_status = "SUCCESS"
solutions = []

# Recursively search for .sln files
try:
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.sln'):
                solution_path = os.path.join(root, file)
                solutions.append({
                    'name': file,
                    'path': solution_path
                })
                print(f"Found solution: {file}")
    
    print(f"Total solutions found: {len(solutions)}")
    
    # Save solutions to JSON file
    output_file = f'output/solutions_{repo_name}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(solutions, f, indent=2)
    
    print(f"Saved solutions to {output_file}")
    
except Exception as e:
    print(f"Error finding solutions: {e}")
    result_status = "FAIL"

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update repo-results.csv
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},task-find-solutions,{result_status},{timestamp}\n")

# Update repo-progress.md
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} |" in line:
        parts = line.split('|')
        parts[4] = ' [x] ' if result_status == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Result: {result_status}")

if result_status == "FAIL":
    sys.exit(1)
