import os
import subprocess
from pathlib import Path
from datetime import datetime

# This script is executed within task_process_solutions.py
# Variables from parent: sol (solution dict), repo_name, DEBUG

solution_name = sol['name']
solution_path = sol['path']
repo_dir = r'C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool'
full_path = Path(repo_dir) / solution_path

if DEBUG:
    print(f'[debug][task-build-solution] START solution="{solution_name}"')

os.chdir(repo_dir)

# Read solution-progress to check if restore succeeded
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')
with open('results/solution-results.md', 'r', encoding='utf-8') as f:
    content = f.read()
    restore_succeeded = f'{solution_name} | task-restore-solution | SUCCESS' in content

status = 'SKIP'
if restore_succeeded:
    os.chdir(repo_dir)
    try:
        result = subprocess.run(['dotnet', 'build', str(full_path), '--no-restore'], capture_output=True, text=True, timeout=120)
        exit_code = result.returncode
        status = 'SUCCESS' if exit_code == 0 else 'FAIL'
        
        if DEBUG:
            print(f'[debug][task-build-solution] dotnet build exit_code={exit_code}')
    except subprocess.TimeoutExpired:
        status = 'FAIL'
        if DEBUG:
            print('[debug][task-build-solution] build timeout (>120s)')
else:
    if DEBUG:
        print('[debug][task-build-solution] skipping build because restore failed')

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update tracking files
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')

with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if solution_name in line and repo_name in line:
        parts = line.split('|')
        if len(parts) >= 5 and '[ ]' in parts[4]:
            parts[4] = parts[4].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('results/solution-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | {solution_name} | task-build-solution | {status} | {timestamp} |\n')
with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},{solution_name},task-build-solution,{status},{timestamp}\n')

if DEBUG:
    print(f'[debug][task-build-solution] END status={status}')

print(f'[run10][build-solution] {solution_name}: {status}')
