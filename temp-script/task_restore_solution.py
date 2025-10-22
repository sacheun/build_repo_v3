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
    print(f'[debug][task-restore-solution] START solution="{solution_name}" path="{solution_path}"')

os.chdir(repo_dir)

# Attempt restore
try:
    result = subprocess.run(['dotnet', 'restore', str(full_path)], capture_output=True, text=True, timeout=120)
    exit_code = result.returncode
    status = 'SUCCESS' if exit_code == 0 else 'FAIL'
    
    if DEBUG:
        print(f'[debug][task-restore-solution] dotnet restore exit_code={exit_code}')
except subprocess.TimeoutExpired:
    status = 'FAIL'
    if DEBUG:
        print('[debug][task-restore-solution] restore timeout (>120s)')

# NuGet fallback if restore failed
nuget_fallback_triggered = False
if status == 'FAIL':
    if DEBUG:
        print('[debug][task-restore-solution] restore failed, trying NuGet fallback')
    
    nuget_fallback_triggered = True
    try:
        nuget_result = subprocess.run(['nuget', 'restore', str(full_path)], capture_output=True, text=True, timeout=120)
        nuget_exit_code = nuget_result.returncode
        
        if nuget_exit_code == 0:
            status = 'SUCCESS'
            if DEBUG:
                print(f'[debug][task-restore-solution] NuGet fallback succeeded')
        else:
            if DEBUG:
                print(f'[debug][task-restore-solution] NuGet fallback failed, exit_code={nuget_exit_code}')
    except subprocess.TimeoutExpired:
        if DEBUG:
            print('[debug][task-restore-solution] NuGet fallback timeout (>120s)')

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Update tracking files
os.chdir(r'C:\Users\sacheu\source\build_repo_v3')

with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if solution_name in line and repo_name in line:
        parts = line.split('|')
        if len(parts) >= 4 and '[ ]' in parts[3]:
            parts[3] = parts[3].replace('[ ]', '[x]', 1)
            lines[i] = '|'.join(parts)
            break

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('results/solution-results.md', 'a', encoding='utf-8') as f:
    f.write(f'| {repo_name} | {solution_name} | task-restore-solution | {status} | {timestamp} |\n')
with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
    f.write(f'{repo_name},{solution_name},task-restore-solution,{status},{timestamp}\n')

if DEBUG:
    print(f'[debug][task-restore-solution] END status={status} nuget_fallback={nuget_fallback_triggered}')

fallback_msg = ' (NuGet fallback)' if nuget_fallback_triggered and status == 'SUCCESS' else ''
print(f'[run10][restore-solution] {solution_name}: {status}{fallback_msg}')
