"""
Task: Restore NuGet packages for solution
Executed via exec() from task_process_solutions.py
Variables from parent scope: sol, repo_name, DEBUG
"""

import subprocess
from datetime import datetime

solution_name = sol['name']
solution_path = sol['path']

print(f"\n--- Task: task-restore-solution ---")
print(f"Solution: {solution_name}")

restore_result = "SUCCESS"

try:
    print("Running: dotnet restore...")
    result = subprocess.run(
        ['dotnet', 'restore', solution_path],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f"Restore FAILED (exit code {result.returncode})")
        if DEBUG:
            print(f"stderr: {result.stderr}")
        restore_result = "FAIL"
    else:
        print("Restore SUCCESS")
        if DEBUG and result.stdout:
            print(f"stdout: {result.stdout[:500]}")
    
except subprocess.TimeoutExpired:
    print("Restore TIMEOUT (120 seconds)")
    restore_result = "FAIL"
except Exception as e:
    print(f"Restore ERROR: {e}")
    restore_result = "FAIL"

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update solution-results.csv
with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},{solution_name},task-restore-solution,{restore_result},{timestamp}\n")

# Update solution-progress.md checkbox
with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} | {solution_name} |" in line:
        parts = line.split('|')
        parts[3] = ' [x] ' if restore_result == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Restore Result: {restore_result}")

# Export for next task
restore_status = restore_result
