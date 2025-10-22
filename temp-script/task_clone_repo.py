import os
import subprocess
from datetime import datetime

repo_url = 'https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool'
clone_path = r'C:\Users\sacheu\speckit_repos'
repo_name = repo_url.rstrip('/').split('/')[-1]
repo_dir = os.path.join(clone_path, repo_name)

print(f'[debug][task-clone-repo] START repo="{repo_name}" url="{repo_url}"')

# Check if repo exists
if not os.path.exists(repo_dir):
    print(f'[debug][task-clone-repo] performing fresh clone: git clone --depth 1 {repo_url} {repo_dir}')
    result = subprocess.run(['git', 'clone', '--depth', '1', repo_url, repo_dir], 
                          capture_output=True, text=True)
    exit_code = result.returncode
    operation = 'CLONE'
else:
    print(f'[debug][task-clone-repo] repository exists, refreshing: reverting local changes and pulling latest')
    os.chdir(repo_dir)
    subprocess.run(['git', 'reset', '--hard', 'HEAD'], capture_output=True)
    subprocess.run(['git', 'clean', '-fd'], capture_output=True)
    result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    exit_code = result.returncode
    operation = 'REFRESH'

status = 'SUCCESS' if exit_code == 0 else 'FAIL'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

print(f'[debug][task-clone-repo] END operation={operation} status={status} exitCode={exit_code}')

# Update repo-progress.md
with open(r'C:\Users\sacheu\source\build_repo_v3\results\repo-progress.md', 'r', encoding='utf-8') as f:
    content = f.read()
if status == 'SUCCESS':
    content = content.replace(f'| {repo_name} | [ ]', f'| {repo_name} | [x]', 1)
    with open(r'C:\Users\sacheu\source\build_repo_v3\results\repo-progress.md', 'w', encoding='utf-8') as f:
        f.write(content)

# Append to results files
with open(r'C:\Users\sacheu\source\build_repo_v3\results\repo-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | task-clone-repo | {status} | {timestamp} |\n')
with open(r'C:\Users\sacheu\source\build_repo_v3\results\repo-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},task-clone-repo,{status},{timestamp}\n')

print(f'[run9][clone] repo_directory="{repo_dir}"')
