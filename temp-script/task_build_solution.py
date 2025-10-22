import subprocess
from datetime import datetime

# This script is executed via exec() from task_process_solutions.py
# Variables available from parent scope: sol, repo_name, DEBUG, restore_result (from task_restore_solution.py)

solution_name = sol['name']
solution_path = sol['path']
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Only build if restore succeeded
if restore_result != 'SUCCESS':
    print(f'[run12][build-solution] {solution_name}: SKIP (restore failed)')
    build_result = 'SKIP'
    
    with open('results/solution-results.csv', 'a') as f:
        f.write(f'{repo_name},{solution_name},task-build-solution,{build_result},{timestamp}\n')
    
else:
    if DEBUG == '1':
        print(f'[run12][build-solution] DEBUG: Building {solution_name} at {solution_path}')
    
    try:
        result = subprocess.run(
            ['dotnet', 'build', solution_path, '--no-restore'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f'[run12][build-solution] {solution_name}: SUCCESS')
            build_result = 'SUCCESS'
        else:
            print(f'[run12][build-solution] {solution_name}: FAIL')
            if DEBUG == '1':
                print(f'[run12][build-solution] DEBUG: {result.stderr}')
            build_result = 'FAIL'
    
    except subprocess.TimeoutExpired:
        print(f'[run12][build-solution] {solution_name}: FAIL (timeout)')
        build_result = 'FAIL'
    except Exception as e:
        print(f'[run12][build-solution] {solution_name}: FAIL ({str(e)})')
        build_result = 'FAIL'
    
    # Record result
    with open('results/solution-results.csv', 'a') as f:
        f.write(f'{repo_name},{solution_name},task-build-solution,{build_result},{timestamp}\n')
    
    # Update solution progress
    if build_result == 'SUCCESS':
        with open('results/solution-progress.md', 'r') as f:
            progress_content = f.read()
        
        import re
        pattern = f'(\\| {re.escape(repo_name)} \\| {re.escape(solution_name)} \\| \\[x\\] \\| )\\[ \\]'
        progress_content = re.sub(pattern, r'\1[x]', progress_content, count=1)
        
        with open('results/solution-progress.md', 'w') as f:
            f.write(progress_content)
