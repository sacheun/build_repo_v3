import os
import json
from pathlib import Path
from datetime import datetime

repo_name = 'ic3_spool_cosine-dep-spool'
DEBUG = os.environ.get('DEBUG', '0') == '1'

if DEBUG:
    print(f'[debug][task-process-solutions] START repo_name="{repo_name}"')

os.chdir(r'C:\Users\sacheu\source\build_repo_v3')

# Load solutions
with open('output/solutions.json', 'r', encoding='utf-8') as f:
    solutions = json.load(f)

if DEBUG:
    print(f'[debug][task-process-solutions] loaded {len(solutions)} solutions')

# Initialize solution-progress.md
with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.write('# Solution Progress Tracking\n\n')
    f.write('| Repository | Solution | task-restore-solution | task-build-solution |\n')
    f.write('|------------|----------|---------------------|-------------------|\n')
    for sol in solutions:
        f.write(f'| {repo_name} | {sol["name"]} | [ ] | [ ] |\n')

# Initialize solution-results files
with open('results/solution-results.md', 'w', encoding='utf-8') as f:
    f.write('# Solution Results\n\n')
    f.write('| Repository | Solution | Task | Result | Timestamp |\n')
    f.write('|------------|----------|------|--------|----------|\n')

with open('results/solution-results.csv', 'w', encoding='utf-8') as f:
    f.write('Repository,Solution,Task,Result,Timestamp\n')

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update repo tracking
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if repo_name in line:
        parts = line.split('|')
        if len(parts) >= 6 and '[ ]' in parts[5]:
            parts[5] = parts[5].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('results/repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-process-solutions | SUCCESS | {timestamp} |\n')
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-process-solutions,SUCCESS,{timestamp}\n')

if DEBUG:
    print(f'[debug][task-process-solutions] initialized tracking files for {len(solutions)} solutions')

# Process each solution sequentially
for idx, sol in enumerate(solutions, 1):
    print(f'\n[run10][process-solutions] === Processing solution {idx}/{len(solutions)}: {sol["name"]} ===')
    
    # Execute task-restore-solution
    exec(open('temp-script/task_restore_solution.py').read())
    
    # Execute task-build-solution
    exec(open('temp-script/task_build_solution.py').read())

if DEBUG:
    print(f'[debug][task-process-solutions] END processed {len(solutions)} solutions')

print(f'[run10][process-solutions] completed processing {len(solutions)} solutions')
