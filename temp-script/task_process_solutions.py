import os
import sys
import json
import re
from datetime import datetime

# Accept parameters
if len(sys.argv) < 2:
    print("Usage: task_process_solutions.py <repo_name>")
    sys.exit(1)

repo_name = sys.argv[1]

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Load solutions from JSON file created by task-find-solutions
solutions_file = f'output/solutions_{repo_name}.json'
if not os.path.exists(solutions_file):
    print(f'[run12][process-solutions] ERROR: Solutions file not found: {solutions_file}')
    with open('results/repo-results.csv', 'a') as f:
        f.write(f'{repo_name},task-process-solutions,FAIL,{timestamp}\n')
    sys.exit(1)

with open(solutions_file, 'r') as f:
    solutions = json.load(f)

if not solutions:
    print('[run12][process-solutions] No solutions to process')
    with open('results/repo-results.csv', 'a') as f:
        f.write(f'{repo_name},task-process-solutions,SUCCESS,{timestamp}\n')
    
    # Update progress
    with open('results/repo-progress.md', 'r') as f:
        content = f.read()
    
    pattern = f'(\\| {re.escape(repo_name)} \\| \\[x\\] \\| \\[x\\] \\| \\[x\\] \\| )\\[ \\]'
    content = re.sub(pattern, r'\1[x]', content, count=1)
    
    with open('results/repo-progress.md', 'w') as f:
        f.write(content)
    
    sys.exit(0)

# Process each solution
DEBUG = os.environ.get('DEBUG', '0')

for idx, sol in enumerate(solutions, 1):
    print(f'[run12][process-solutions] === Processing solution {idx}/{len(solutions)}: {sol["name"]} ===')
    
    # Execute task-restore-solution
    exec(open('temp-script/task_restore_solution.py').read())
    
    # Execute task-build-solution
    exec(open('temp-script/task_build_solution.py').read())

print(f'[run12][process-solutions] completed processing {len(solutions)} solutions')

# Record success
with open('results/repo-results.csv', 'a') as f:
    f.write(f'{repo_name},task-process-solutions,SUCCESS,{timestamp}\n')

# Update progress
with open('results/repo-progress.md', 'r') as f:
    content = f.read()

pattern = f'(\\| {re.escape(repo_name)} \\| \\[x\\] \\| \\[x\\] \\| \\[x\\] \\| )\\[ \\]'
content = re.sub(pattern, r'\1[x]', content, count=1)

with open('results/repo-progress.md', 'w') as f:
    f.write(content)
