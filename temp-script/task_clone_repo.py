import os
import subprocess
import sys
from datetime import datetime

# Accept parameters
if len(sys.argv) < 3:
    print("Usage: task_clone_repo.py <repo_url> <clone_path>")
    sys.exit(1)

repo_url = sys.argv[1]
clone_path = sys.argv[2]
repo_name = repo_url.rstrip('/').split('/')[-1]

# Ensure clone directory exists
os.makedirs(clone_path, exist_ok=True)

repo_dir = os.path.join(clone_path, repo_name)
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Check if repository already exists
if os.path.exists(repo_dir):
    # Repository exists, refresh it
    print(f'[run12][clone] Repository already exists, refreshing: {repo_name}')
    
    result = subprocess.run(
        ['git', 'fetch', '--all'],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f'[run12][clone] FAIL - git fetch failed: {result.stderr}')
        with open('results/repo-results.csv', 'a') as f:
            f.write(f'{repo_name},task-clone-repo,FAIL,{timestamp}\n')
        sys.exit(1)
    
    result = subprocess.run(
        ['git', 'reset', '--hard', 'origin/HEAD'],
        cwd=repo_dir,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f'[run12][clone] FAIL - git reset failed: {result.stderr}')
        with open('results/repo-results.csv', 'a') as f:
            f.write(f'{repo_name},task-clone-repo,FAIL,{timestamp}\n')
        sys.exit(1)
    
    print(f'[run12][clone] repo_directory="{repo_dir}" (REFRESHED)')
else:
    # Clone the repository
    print(f'[run12][clone] Cloning repository: {repo_name}')
    
    result = subprocess.run(
        ['git', 'clone', repo_url, repo_dir],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode != 0:
        print(f'[run12][clone] FAIL - git clone failed: {result.stderr}')
        with open('results/repo-results.csv', 'a') as f:
            f.write(f'{repo_name},task-clone-repo,FAIL,{timestamp}\n')
        sys.exit(1)
    
    print(f'[run12][clone] repo_directory="{repo_dir}" (CLONED)')

# Record success
with open('results/repo-results.csv', 'a') as f:
    f.write(f'{repo_name},task-clone-repo,SUCCESS,{timestamp}\n')

# Update progress
import re
with open('results/repo-progress.md', 'r') as f:
    content = f.read()

pattern = f'(\\| {re.escape(repo_name)} \\| )\\[ \\]'
content = re.sub(pattern, r'\1[x]', content, count=1)

with open('results/repo-progress.md', 'w') as f:
    f.write(content)

print(f'[run12][clone] SUCCESS')
