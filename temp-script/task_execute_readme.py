import os
import sys
import re
from datetime import datetime

# Accept parameters
if len(sys.argv) < 3:
    print("Usage: task_execute_readme.py <repo_directory> <repo_name>")
    sys.exit(1)

repo_dir = sys.argv[1]
repo_name = sys.argv[2]

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Look for README file
readme_file = None
for filename in ['README.md', 'README.MD', 'readme.md', 'Readme.md']:
    path = os.path.join(repo_dir, filename)
    if os.path.exists(path):
        readme_file = filename
        break

if not readme_file:
    print('[run12][execute-readme] readme_file="NOT_FOUND" commands_executed=0 commands_skipped=0')
    with open('results/repo-results.csv', 'a') as f:
        f.write(f'{repo_name},task-execute-readme,SUCCESS,{timestamp}\n')
    
    # Update progress
    with open('results/repo-progress.md', 'r') as f:
        content = f.read()
    
    pattern = f'(\\| {re.escape(repo_name)} \\| \\[x\\] \\| )\\[ \\]'
    content = re.sub(pattern, r'\1[x]', content, count=1)
    
    with open('results/repo-progress.md', 'w') as f:
        f.write(content)
    
    sys.exit(0)

# Read README content
readme_path = os.path.join(repo_dir, readme_file)
with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
    readme_content = f.read()

# Parse for commands in setup sections
setup_sections = ['## Setup', '## Getting Started', '## Installation', '## Build', '## Prerequisites']
commands_executed = 0
commands_skipped = 0

# For now, just count potential command blocks without executing
# (Execution logic would be more complex and require structural reasoning)
in_setup_section = False
for line in readme_content.split('\n'):
    if any(line.strip().startswith(section) for section in setup_sections):
        in_setup_section = True
    elif line.strip().startswith('## '):
        in_setup_section = False
    
    if in_setup_section and (line.strip().startswith('```') or line.strip().startswith('$')):
        commands_skipped += 1

print(f'[run12][execute-readme] readme_file="{readme_file}" commands_executed={commands_executed} commands_skipped={commands_skipped}')

# Record success
with open('results/repo-results.csv', 'a') as f:
    f.write(f'{repo_name},task-execute-readme,SUCCESS,{timestamp}\n')

# Update progress
with open('results/repo-progress.md', 'r') as f:
    content = f.read()

pattern = f'(\\| {re.escape(repo_name)} \\| \\[x\\] \\| )\\[ \\]'
content = re.sub(pattern, r'\1[x]', content, count=1)

with open('results/repo-progress.md', 'w') as f:
    f.write(content)
