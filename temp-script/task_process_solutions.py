"""
Task: Process all solutions for a repository
Input: repo_name (command-line argument)
Output: Summary of processed solutions
"""

import sys
import os
import json
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: task_process_solutions.py <repo_name>")
    sys.exit(1)

repo_name = sys.argv[1]

print(f"Task: task-process-solutions")
print(f"Repository: {repo_name}")

# Load solutions JSON
solutions_file = f'output/solutions_{repo_name}.json'
if not os.path.exists(solutions_file):
    print(f"Solutions file not found: {solutions_file}")
    result_status = "FAIL"
else:
    with open(solutions_file, 'r', encoding='utf-8') as f:
        solutions = json.load(f)
    
    print(f"Processing {len(solutions)} solutions...")
    
    # Set DEBUG environment variable
    os.environ['DEBUG'] = '1'
    DEBUG = True
    
    # Process each solution
    for sol in solutions:
        solution_name = sol['name']
        solution_path = sol['path']
        
        print(f"\n{'='*80}")
        print(f"Solution: {solution_name}")
        print(f"Path: {solution_path}")
        print(f"{'='*80}")
        
        # Add row to solution-progress.md
        with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if row already exists
        if f"| {repo_name} | {solution_name} |" not in content:
            with open('results/solution-progress.md', 'a', encoding='utf-8') as f:
                f.write(f"| {repo_name} | {solution_name} | [ ] | [ ] | [ ] |\n")
        
        # Execute task-restore-solution
        exec(open('temp-script/task_restore_solution.py').read())
        
        # Execute task-build-solution (only if restore succeeded)
        # The build task will handle the logic and also call KB collection
        exec(open('temp-script/task_build_solution.py').read())
    
    result_status = "SUCCESS"

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update repo-results.csv
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},task-process-solutions,{result_status},{timestamp}\n")

# Update repo-progress.md
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} |" in line:
        parts = line.split('|')
        parts[5] = ' [x] ' if result_status == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nResult: {result_status}")

if result_status == "FAIL":
    sys.exit(1)
