import os
import subprocess
from datetime import datetime

repo_url = 'https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool'
clone_path = r'C:\Users\sacheu\speckit_repos'
repo_name = repo_url.rstrip('/').split('/')[-1]
repo_dir = os.path.join(clone_path, repo_name)

DEBUG = os.environ.get('DEBUG', '0') == '1'

if DEBUG:
    print(f'[debug][task-clone-repo] START repo="{repo_name}" url="{repo_url}"')

# Check if repo exists
if not os.path.exists(repo_dir):
    if DEBUG:
        print(f'[debug][task-clone-repo] performing fresh clone: git clone --depth 1 {repo_url} {repo_dir}')
    result = subprocess.run(['git', 'clone', '--depth', '1', repo_url, repo_dir], 
                          capture_output=True, text=True)
    exit_code = result.returncode
    operation = 'CLONE'
else:
    if DEBUG:
        print(f'[debug][task-clone-repo] repository exists, refreshing: reverting local changes and pulling latest')
    os.chdir(repo_dir)
    subprocess.run(['git', 'reset', '--hard', 'HEAD'], capture_output=True)
    subprocess.run(['git', 'clean', '-fd'], capture_output=True)
    result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    exit_code = result.returncode
    operation = 'REFRESH'

status = 'SUCCESS' if exit_code == 0 else 'FAIL'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if DEBUG:
    print(f'[debug][task-clone-repo] END operation={operation} status={status} exitCode={exit_code}')

# Update repo-progress.md
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')
with open('results/repo-progress.md', 'r', encoding='utf-8') as f:
    content = f.read()
if status == 'SUCCESS':
    content = content.replace(f'| {repo_name} | [ ]', f'| {repo_name} | [x]', 1)
    with open('results/repo-progress.md', 'w', encoding='utf-8') as f:
        f.write(content)

# Append to results files
with open('results/repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-clone-repo | {status} | {timestamp} |\n')
with open('results/repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-clone-repo,{status},{timestamp}\n')

print(f'[run10][clone] repo_directory="{repo_dir}"')
