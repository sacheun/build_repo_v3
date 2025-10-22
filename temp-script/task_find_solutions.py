import os
import json
from pathlib import Path
from datetime import datetime

repo_dir = r'C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool'
repo_name = 'ic3_spool_cosine-dep-spool'

print(f'[debug][task-find-solutions] START repo_directory="{repo_dir}"')

# Find all .sln files recursively
solutions = []
for sln_file in Path(repo_dir).rglob('*.sln'):
    solutions.append(str(sln_file.absolute()))

solution_count = len(solutions)
print(f'[debug][task-find-solutions] discovered {solution_count} solutions')

# Save solutions to output directory
os.makedirs('output', exist_ok=True)
output_data = {
    'solutions': solutions
}

with open('output/solutions.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

status = 'SUCCESS' if solution_count > 0 else 'FAIL'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f'[debug][task-find-solutions] END solution_count={solution_count} status={status}')

# Update repo-progress.md
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if repo_name in line:
        parts = line.split('|')
        if len(parts) >= 4 and '[ ]' in parts[3]:
            parts[3] = parts[3].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Append to results files
with open('results/repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-find-solutions | {status} | {timestamp} |\n')
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-find-solutions,{status},{timestamp}\n')

print(f'[run9][find-solutions] found {solution_count} solutions, saved to output/solutions.json')
