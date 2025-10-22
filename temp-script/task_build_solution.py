"""
Task: Build solution and collect knowledge base for failures
Executed via exec() from task_process_solutions.py
Variables from parent scope: sol, repo_name, DEBUG, restore_status
"""

import subprocess
from datetime import datetime

solution_name = sol['name']
solution_path = sol['path']

print(f"\n--- Task: task-build-solution ---")
print(f"Solution: {solution_name}")

build_result = "SKIPPED"
result = None

# Only build if restore succeeded
if restore_status != "SUCCESS":
    print("Build SKIPPED (restore failed)")
    build_result = "SKIPPED"
    # Create mock result for KB collection
    result = type('obj', (object,), {'stderr': 'Build skipped due to restore failure', 'returncode': 0})()
    # Execute KB collection task
    exec(open('temp-script/task_collect_knowledge_base.py').read())
else:
    try:
        print("Running: dotnet build --no-restore...")
        result = subprocess.run(
            ['dotnet', 'build', solution_path, '--no-restore'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"Build FAILED (exit code {result.returncode})")
            if DEBUG:
                print(f"stderr: {result.stderr[:1000]}")
            build_result = "FAIL"
        else:
            print("Build SUCCESS")
            if DEBUG and result.stdout:
                print(f"stdout: {result.stdout[:500]}")
            build_result = "SUCCESS"
        
    except subprocess.TimeoutExpired:
        print("Build TIMEOUT (120 seconds)")
        build_result = "FAIL"
        # Create mock result for KB collection
        result = type('obj', (object,), {'stderr': 'Build timeout after 120 seconds', 'returncode': 1})()
    except Exception as e:
        print(f"Build ERROR: {e}")
        build_result = "FAIL"
        # Create mock result for KB collection
        result = type('obj', (object,), {'stderr': str(e), 'returncode': 1})()
    
    # Execute knowledge base collection task
    exec(open('temp-script/task_collect_knowledge_base.py').read())

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Update solution-results.csv
with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},{solution_name},task-build-solution,{build_result},{timestamp}\n")

# Update solution-progress.md checkbox
with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} | {solution_name} |" in line:
        parts = line.split('|')
        parts[4] = ' [x] ' if build_result == "SUCCESS" else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Build Result: {build_result}")
