import json
import subprocess
import os
from datetime import datetime

DEBUG = os.environ.get('DEBUG', '0') == '1'

# Load solutions
with open('output/solutions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    solutions = data['solutions']

print(f'[run9][process-solutions] processing {len(solutions)} solutions sequentially')

def update_solution_progress(sln_name, task_name):
    """Mark task as completed in solution-progress.md"""
    with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if sln_name in line:
            parts = line.split('|')
            if task_name == 'task-restore-solution' and len(parts) >= 3 and '[ ]' in parts[2]:
                parts[2] = parts[2].replace('[ ]', '[x]', 1)
                lines[i] = '|'.join(parts)
            elif task_name == 'task-build-solution' and len(parts) >= 4 and '[ ]' in parts[3]:
                parts[3] = parts[3].replace('[ ]', '[x]', 1)
                lines[i] = '|'.join(parts)
            break
    
    with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
        f.writelines(lines)

def append_solution_results(sln_name, task_name, status):
    """Append task result to tracking files"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('results/solution-results.md', 'a', encoding='utf-8') as f:
        f.write(f'| {sln_name} | {task_name} | {status} | {timestamp} |\n')
    with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
        f.write(f'{sln_name},{task_name},{status},{timestamp}\n')

def task_restore_solution(solution_path):
    """Execute task-restore-solution with NuGet fallback"""
    sln_name = solution_path.split('\\')[-1].replace('.sln', '')
    
    if DEBUG:
        print(f'[debug][task-restore-solution] START solution="{sln_name}" path="{solution_path}"')
    
    # Step 1: Check if solution file exists
    if not os.path.exists(solution_path):
        if DEBUG:
            print(f'[debug][task-restore-solution] solution file not found: {solution_path}')
        print(f'[run9][restore] solution="{sln_name}" status=FAIL reason="file not found"')
        update_solution_progress(sln_name, 'task-restore-solution')
        append_solution_results(sln_name, 'task-restore-solution', 'FAIL')
        return 1
    
    # Step 2: Try msbuild /restore
    cmd_msbuild = ['msbuild', solution_path, '/restore', '/p:Configuration=Release', '/nologo']
    if DEBUG:
        print(f'[debug][task-restore-solution] executing: msbuild "{solution_path}" /restore /p:Configuration=Release /nologo')
    
    result = subprocess.run(cmd_msbuild, capture_output=True, text=True)
    msbuild_exit_code = result.returncode
    
    if DEBUG and msbuild_exit_code != 0:
        print(f'[debug][task-restore-solution] command failed with exit code {msbuild_exit_code}, stderr: {result.stderr[:200] if result.stderr else "(empty)"}')
    
    # Step 2b: If error 9009 (command not found), try dotnet msbuild
    if msbuild_exit_code == 9009:
        if DEBUG:
            print(f'[debug][task-restore-solution] msbuild not found (9009), trying dotnet msbuild')
        cmd_dotnet = ['dotnet', 'msbuild', solution_path, '/restore', '/p:Configuration=Release', '/nologo']
        result = subprocess.run(cmd_dotnet, capture_output=True, text=True)
        msbuild_exit_code = result.returncode
        if DEBUG and msbuild_exit_code != 0:
            print(f'[debug][task-restore-solution] dotnet msbuild failed with exit code {msbuild_exit_code}, stderr: {result.stderr[:200] if result.stderr else "(empty)"}')
    
    # CRITICAL FIX: Step 3 - NuGet fallback triggered on ANY non-zero exit code
    if msbuild_exit_code != 0:
        if DEBUG:
            print(f'[debug][task-restore-solution] NuGet fallback triggered (msbuild exitCode={msbuild_exit_code})')
        
        cmd_nuget = ['nuget', 'restore', solution_path]
        if DEBUG:
            print(f'[debug][task-restore-solution] executing: nuget restore "{solution_path}"')
        
        nuget_result = subprocess.run(cmd_nuget, capture_output=True, text=True)
        nuget_exit_code = nuget_result.returncode
        
        if nuget_exit_code == 0:
            # Step 4: Retry msbuild /restore after successful nuget
            if DEBUG:
                print(f'[debug][task-restore-solution] NuGet succeeded, retrying msbuild /restore')
            retry_result = subprocess.run(cmd_msbuild, capture_output=True, text=True)
            final_exit_code = retry_result.returncode
        else:
            if DEBUG:
                print(f'[debug][task-restore-solution] NuGet restore failed with exitCode={nuget_exit_code}, skipping MSBuild retry')
            final_exit_code = nuget_exit_code
    else:
        final_exit_code = msbuild_exit_code
    
    status = 'SUCCESS' if final_exit_code == 0 else 'FAIL'
    
    if DEBUG:
        print(f'[debug][task-restore-solution] END solution="{sln_name}" status={status} exitCode={final_exit_code}')
    
    print(f'[run9][restore] solution="{sln_name}" status={status}')
    update_solution_progress(sln_name, 'task-restore-solution')
    append_solution_results(sln_name, 'task-restore-solution', status)
    
    return final_exit_code

def task_build_solution(solution_path, restore_exit_code):
    """Execute task-build-solution"""
    sln_name = solution_path.split('\\')[-1].replace('.sln', '')
    
    # Skip build if restore failed
    if restore_exit_code != 0:
        if DEBUG:
            print(f'[debug][task-build-solution] SKIP solution="{sln_name}" reason="restore failed"')
        print(f'[run9][build] solution="{sln_name}" status=SKIP reason="restore failed"')
        update_solution_progress(sln_name, 'task-build-solution')
        append_solution_results(sln_name, 'task-build-solution', 'SKIP')
        return 0
    
    if DEBUG:
        print(f'[debug][task-build-solution] START solution="{sln_name}" path="{solution_path}"')
    
    cmd_build = ['msbuild', solution_path, '/t:Clean,Build', '/p:Configuration=Release', '/nologo', '/m']
    if DEBUG:
        print(f'[debug][task-build-solution] executing: msbuild "{solution_path}" /t:Clean,Build /p:Configuration=Release /nologo /m')
    
    result = subprocess.run(cmd_build, capture_output=True, text=True)
    exit_code = result.returncode
    
    if DEBUG and exit_code != 0:
        print(f'[debug][task-build-solution] command failed with exit code {exit_code}, stderr: {result.stderr[:200] if result.stderr else "(empty)"}')
    
    status = 'SUCCESS' if exit_code == 0 else 'FAIL'
    
    if DEBUG:
        print(f'[debug][task-build-solution] END solution="{sln_name}" status={status} exitCode={exit_code}')
    
    print(f'[run9][build] solution="{sln_name}" status={status}')
    update_solution_progress(sln_name, 'task-build-solution')
    append_solution_results(sln_name, 'task-build-solution', status)
    
    return exit_code

# Process each solution sequentially
for solution_path in solutions:
    sln_name = solution_path.split('\\')[-1].replace('.sln', '')
    print(f'\n[run9][process] === Processing solution: {sln_name} ===')
    
    # Execute restore task
    restore_exit_code = task_restore_solution(solution_path)
    
    # Execute build task (will skip if restore failed)
    task_build_solution(solution_path, restore_exit_code)
    
    print(f'[run9][process] === Completed solution: {sln_name} ===\n')

print('[run9][process-solutions] all solutions processed')
