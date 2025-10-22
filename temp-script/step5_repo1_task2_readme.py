import os
import sys
import json
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

# Load repository info
with open('output/repositories_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    repo = data['repositories'][0]

repo_name = repo['repo_name']
repo_directory = os.path.join(data['clone_base_path'], repo_name)

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-execute-readme] START repo_directory='{repo_directory}'")

# README candidate filenames in priority order
readme_candidates = [
    "README.md",
    "readme.md",
    "README.txt",
    "README.rst",
    "README",
    "Readme.md"
]

readme_filename = None
readme_content = None

# Search for README
for candidate in readme_candidates:
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-execute-readme] checking for: {candidate}")
    
    candidate_path = Path(repo_directory) / candidate
    if candidate_path.exists():
        readme_filename = candidate
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-execute-readme] found README file: {readme_filename}")
        
        # Read content
        try:
            with open(candidate_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
            
            if os.environ.get('DEBUG') == '1':
                print(f"[debug][task-execute-readme] content length: {len(readme_content)} characters")
        except Exception as e:
            if os.environ.get('DEBUG') == '1':
                print(f"[debug][task-execute-readme] error reading file: {e}")
        
        break

if readme_filename is None:
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-execute-readme] no README file found in repository root")

# Determine status
status = "SUCCESS" if readme_filename else "FAIL"

# Prepare output
output_data = {
    "repo_directory": repo_directory,
    "repo_name": repo_name,
    "readme_filename": readme_filename,
    "readme_content": readme_content,
    "setup_commands_executed": [],  # Per spec: Do not execute scripts
    "setup_commands_skipped": [],    # Per spec: Do not execute scripts
    "status": status
}

# Save to output directory
output_file = Path("output") / f"{repo_name}_task2_execute-readme.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

# Update progress table
progress_file = Path("results/repo-progress.md")
if progress_file.exists():
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the row for this repository and update task-execute-readme column
    for i, line in enumerate(lines):
        if repo_name in line:
            parts = line.split('|')
            if len(parts) >= 4:
                # Column 3 is task-execute-readme
                parts[3] = ' [x] '
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Append to results files
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
symbol = '✓' if status == 'SUCCESS' else '✗'

# Markdown result
md_result = Path("results/repo-results.md")
with open(md_result, 'a', encoding='utf-8') as f:
    f.write(f"| {timestamp} | {repo_name} | task-execute-readme | {status} | {symbol} |\n")

# CSV result
csv_result = Path("results/repo-results.csv")
with open(csv_result, 'a', encoding='utf-8') as f:
    f.write(f"{timestamp},{repo_name},task-execute-readme,{status},{symbol}\n")

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-execute-readme] END repo_directory='{repo_directory}' status={status} readme_found={readme_filename} commands_executed=0")

print(f"\nRepository 1 task-execute-readme completed: {status}")
if readme_filename:
    print(f"  Found: {readme_filename}")
    print(f"  Content length: {len(readme_content)} characters")
else:
    print(f"  No README file found")
