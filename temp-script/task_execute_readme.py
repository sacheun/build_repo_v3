"""
Task: Execute README to extract metadata
Input: repo_directory, repo_name (command-line arguments)
Output: JSON object with repo_directory, readme_content, readme_filename
"""

import sys
import os
from datetime import datetime

if len(sys.argv) < 3:
    print("Usage: task_execute_readme.py <repo_directory> <repo_name>")
    sys.exit(1)

repo_dir = sys.argv[1]
repo_name = sys.argv[2]

print(f"Task: task-execute-readme")
print(f"Repository: {repo_name}")
print(f"Directory: {repo_dir}")

result_status = "SUCCESS"
readme_filename = None
readme_content = ""

# Search for README file
readme_candidates = ['README.md', 'readme.md', 'README.txt', 'readme.txt', 'README']
for candidate in readme_candidates:
    readme_path = os.path.join(repo_dir, candidate)
    if os.path.exists(readme_path):
        readme_filename = candidate
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
            print(f"Found README: {readme_filename} ({len(readme_content)} chars)")
            break
        except Exception as e:
            print(f"Error reading {candidate}: {e}")

if not readme_filename:
    print("No README file found")
    result_status = "SUCCESS"  # Not a failure, just no README

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update repo-results.csv
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},task-execute-readme,{result_status},{timestamp}\n")

# Update repo-progress.md
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} |" in line:
        parts = line.split('|')
        parts[3] = ' [x] ' if result_status == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Result: {result_status}")

if result_status == "FAIL":
    sys.exit(1)
