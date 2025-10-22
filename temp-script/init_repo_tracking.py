import os
from datetime import datetime

# Ensure directories exist
os.makedirs('results', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Extract repo name from URL
repo_url = 'https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool'
repo_name = repo_url.rstrip('/').split('/')[-1]

# Create repo-progress.md with all task columns
progress_md = '''## Repository Progress Tracking (Run 9)

| Repository | task-clone-repo | task-find-solutions | task-process-solutions |
|------------|----------------|---------------------|------------------------|
| ''' + repo_name + ''' | [ ] | [ ] | [ ] |
'''

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.write(progress_md)

# Initialize repo-results.md
results_md = '''## Repository Task Results (Run 9)

| Repository | Task | Status | Timestamp |
|-----------|------|--------|-----------|
'''

with open('results/repo-results.md', 'w', encoding='utf-8') as f:
    f.write(results_md)

# Initialize repo-results.csv
with open('results/repo-results.csv', 'w', encoding='utf-8') as f:
    f.write('Repository,Task,Status,Timestamp\n')

print('[run9][init] repo tracking initialized with 3 task columns')
print(f'[run9][init] repository: {repo_name}')
