import os
from datetime import datetime

# Read all repositories from input file
repositories_file = '.copilot/prompts/repositories.txt'
repo_urls = []

with open(repositories_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            repo_urls.append(line)

# Extract friendly names
repo_names = [url.rstrip('/').split('/')[-1] for url in repo_urls]

# Task list
tasks = ['task-clone-repo', 'task-execute-readme', 'task-find-solutions', 'task-process-solutions']

# Ensure results directory exists
os.makedirs('results', exist_ok=True)

# Create repo-progress.md with Run 12 header
with open('results/repo-progress.md', 'w') as f:
    f.write('# Repository Progress - Run 12\n\n')
    
    # Header row
    header = '| Repository | ' + ' | '.join(tasks) + ' |'
    separator = '|' + '|'.join(['---'] * (len(tasks) + 1)) + '|'
    
    f.write(header + '\n')
    f.write(separator + '\n')
    
    # Row for each repository
    for repo_name in repo_names:
        checkboxes = ' | '.join(['[ ]'] * len(tasks))
        f.write(f'| {repo_name} | {checkboxes} |\n')

# Create repo-results.csv
with open('results/repo-results.csv', 'w') as f:
    f.write('Repository,Task,Result,Timestamp\n')

# Create solution-progress.md
with open('results/solution-progress.md', 'w') as f:
    f.write('# Solution Progress - Run 12\n\n')
    f.write('| Repository | Solution | task-restore-solution | task-build-solution |\n')
    f.write('|---|---|---|---|\n')

# Create solution-results.csv
with open('results/solution-results.csv', 'w') as f:
    f.write('Repository,Solution,Task,Result,Timestamp\n')

print(f'[run12][init] repo tracking initialized for {len(repo_names)} repositories with {len(tasks)} task columns')
