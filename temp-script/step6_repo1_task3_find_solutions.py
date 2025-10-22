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
    print(f"[debug][task-find-solutions] START repo_directory='{repo_directory}'")

# Find all .sln files recursively
repo_path = Path(repo_directory)
solution_files = list(repo_path.rglob("*.sln"))

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-find-solutions] found {len(solution_files)} solution files")

# Create solutions list
solutions = []
for sln_path in solution_files:
    solution_name = sln_path.stem  # Filename without extension
    solutions.append({
        "solution_name": solution_name,
        "solution_path": str(sln_path.absolute()),
        "relative_path": str(sln_path.relative_to(repo_path))
    })
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-find-solutions]   - {solution_name}: {sln_path.relative_to(repo_path)}")

# Prepare output
output_data = {
    "repo_directory": repo_directory,
    "repo_name": repo_name,
    "solutions_count": len(solutions),
    "solutions": solutions,
    "status": "SUCCESS"
}

# Save to output directory
output_file = Path("output") / f"{repo_name}_solutions_info.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

# Update progress table
progress_file = Path("results/repo-progress.md")
if progress_file.exists():
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the row for this repository and update task-find-solutions column
    for i, line in enumerate(lines):
        if repo_name in line:
            parts = line.split('|')
            if len(parts) >= 5:
                # Column 4 is task-find-solutions
                parts[4] = ' [x] '
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Append to results files
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
symbol = '✓'

# Markdown result
md_result = Path("results/repo-results.md")
with open(md_result, 'a', encoding='utf-8') as f:
    f.write(f"| {timestamp} | {repo_name} | task-find-solutions | SUCCESS | {symbol} |\n")

# CSV result
csv_result = Path("results/repo-results.csv")
with open(csv_result, 'a', encoding='utf-8') as f:
    f.write(f"{timestamp},{repo_name},task-find-solutions,SUCCESS,{symbol}\n")

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-find-solutions] END repo_directory='{repo_directory}' status=SUCCESS solutions_count={len(solutions)}")

print(f"\nRepository 1 task-find-solutions completed: SUCCESS")
print(f"  Solutions found: {len(solutions)}")
for i, sol in enumerate(solutions, 1):
    print(f"    {i}. {sol['solution_name']}")
