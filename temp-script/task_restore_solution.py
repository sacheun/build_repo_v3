import subprocess
from datetime import datetime

# This script is executed via exec() from task_process_solutions.py
# Variables available from parent scope: sol, repo_name, DEBUG

solution_name = sol['name']
solution_path = sol['path']
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if DEBUG == '1':
    print(f'[run12][restore-solution] DEBUG: Restoring {solution_name} at {solution_path}')

try:
    # Try dotnet restore first
    result = subprocess.run(
        ['dotnet', 'restore', solution_path],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        print(f'[run12][restore-solution] {solution_name}: SUCCESS')
        restore_result = 'SUCCESS'
    else:
        # Fallback to NuGet restore
        if DEBUG == '1':
            print(f'[run12][restore-solution] DEBUG: dotnet restore failed, trying nuget')
        
        result = subprocess.run(
            ['nuget', 'restore', solution_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f'[run12][restore-solution] {solution_name}: SUCCESS (nuget)')
            restore_result = 'SUCCESS'
        else:
            print(f'[run12][restore-solution] {solution_name}: FAIL')
            if DEBUG == '1':
                print(f'[run12][restore-solution] DEBUG: {result.stderr}')
            restore_result = 'FAIL'

except subprocess.TimeoutExpired:
    print(f'[run12][restore-solution] {solution_name}: FAIL (timeout)')
    restore_result = 'FAIL'
except Exception as e:
    print(f'[run12][restore-solution] {solution_name}: FAIL ({str(e)})')
    restore_result = 'FAIL'

# Record result
with open('results/solution-results.csv', 'a') as f:
    f.write(f'{repo_name},{solution_name},task-restore-solution,{restore_result},{timestamp}\n')

# Add to solution progress if not exists
with open('results/solution-progress.md', 'r') as f:
    progress_content = f.read()

if f'| {repo_name} | {solution_name} |' not in progress_content:
    with open('results/solution-progress.md', 'a') as f:
        checkbox = '[x]' if restore_result == 'SUCCESS' else '[ ]'
        f.write(f'| {repo_name} | {solution_name} | {checkbox} | [ ] |\n')
else:
    # Update existing row
    import re
    pattern = f'(\\| {re.escape(repo_name)} \\| {re.escape(solution_name)} \\| )\\[ \\]'
    if restore_result == 'SUCCESS':
        progress_content = re.sub(pattern, r'\1[x]', progress_content, count=1)
        with open('results/solution-progress.md', 'w') as f:
            f.write(progress_content)
