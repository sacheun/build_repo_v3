import os
import json
from pathlib import Path
from datetime import datetime

repo_dir = r'C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool'
repo_name = 'ic3_spool_cosine-dep-spool'
DEBUG = os.environ.get('DEBUG', '0') == '1'

if DEBUG:
    print(f'[debug][task-find-solutions] START repo_directory="{repo_dir}"')

# Find all .sln files recursively
solutions = []
for sln_path in Path(repo_dir).rglob('*.sln'):
    solution_name = sln_path.stem
    solutions.append({
        'name': solution_name,
        'path': str(sln_path.relative_to(repo_dir)).replace('\\', '/')
    })
    if DEBUG:
        print(f'[debug][task-find-solutions] found solution: {solution_name} at {sln_path.relative_to(repo_dir)}')

# Write to output/solutions.json
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')
with open('output/solutions.json', 'w', encoding='utf-8') as f:
    json.dump(solutions, f, indent=2)

status = 'SUCCESS' if solutions else 'FAIL'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update tracking files
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if repo_name in line:
        parts = line.split('|')
        if len(parts) >= 5 and '[ ]' in parts[4]:
            parts[4] = parts[4].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Append to results files
with open('results/repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-find-solutions | {status} | {timestamp} |\n')
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-find-solutions,{status},{timestamp}\n')

if DEBUG:
    print(f'[debug][task-find-solutions] END solutions_count={len(solutions)} status={status}')

print(f'[run10][find-solutions] found {len(solutions)} solution(s)')
