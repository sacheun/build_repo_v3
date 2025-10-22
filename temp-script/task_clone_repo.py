"""
Task: Clone or refresh repository
Input: repo_url, clone_path (command-line arguments)
Output: absolute path to repository directory
"""

import sys
import os
import subprocess
from datetime import datetime

if len(sys.argv) < 3:
    print("Usage: task_clone_repo.py <repo_url> <clone_path>")
    sys.exit(1)

repo_url = sys.argv[1]
clone_path = sys.argv[2]
repo_name = repo_url.rstrip('/').split('/')[-1]
repo_dir = os.path.join(clone_path, repo_name)

print(f"Task: task-clone-repo")
print(f"Repository: {repo_name}")
print(f"URL: {repo_url}")
print(f"Target: {repo_dir}")

# Ensure clone_path exists
os.makedirs(clone_path, exist_ok=True)

# Clone or pull
result_status = "SUCCESS"
try:
    if os.path.exists(repo_dir):
        print(f"Repository exists, pulling latest...")
        result = subprocess.run(['git', 'pull'], cwd=repo_dir, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"Git pull failed: {result.stderr}")
            result_status = "FAIL"
        else:
            print("Git pull successful")
    else:
        print(f"Cloning repository...")
        result = subprocess.run(['git', 'clone', repo_url, repo_dir], capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print(f"Git clone failed: {result.stderr}")
            result_status = "FAIL"
        else:
            print("Git clone successful")
except Exception as e:
    print(f"Error: {e}")
    result_status = "FAIL"

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update repo-results.csv
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},task-clone-repo,{result_status},{timestamp}\n")

# Update repo-progress.md
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} |" in line:
        parts = line.split('|')
        parts[2] = ' [x] ' if result_status == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Result: {result_status}")
print(f"Output: {repo_dir}")

if result_status == "FAIL":
    sys.exit(1)
