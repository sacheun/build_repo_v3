import os
import sys
import json
import re
from datetime import datetime

# Accept parameters
if len(sys.argv) < 3:
    print("Usage: task_find_solutions.py <repo_directory> <repo_name>")
    sys.exit(1)

repo_dir = sys.argv[1]
repo_name = sys.argv[2]

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Find all .sln files recursively
solutions = []
for root, dirs, files in os.walk(repo_dir):
    for file in files:
        if file.endswith('.sln'):
            full_path = os.path.join(root, file)
            solutions.append({
                'name': os.path.splitext(file)[0],
                'path': full_path
            })

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Save solutions to JSON (will be used by next task)
output_file = f'output/solutions_{repo_name}.json'
with open(output_file, 'w') as f:
    json.dump(solutions, f, indent=2)

print(f'[run12][find-solutions] found {len(solutions)} solution(s)')

# Record success
with open('results/repo-results.csv', 'a') as f:
    f.write(f'{repo_name},task-find-solutions,SUCCESS,{timestamp}\n')

# Update progress
with open('results/repo-progress.md', 'r') as f:
    content = f.read()

pattern = f'(\\| {re.escape(repo_name)} \\| \\[x\\] \\| \\[x\\] \\| )\\[ \\]'
content = re.sub(pattern, r'\1[x]', content, count=1)

with open('results/repo-progress.md', 'w') as f:
    f.write(content)
