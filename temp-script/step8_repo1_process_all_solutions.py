import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

repo_name = "ic3_spool_cosine-dep-spool"

# Load solutions info
solutions_file = Path("output") / f"{repo_name}_solutions_info.json"
with open(solutions_file, 'r', encoding='utf-8') as f:
    solutions_data = json.load(f)

solutions = solutions_data['solutions']

print(f"Processing {len(solutions)} solutions for repository: {repo_name}")

def extract_error_tokens(stderr_text, stdout_text):
    """Extract error tokens like CS1234, NU1234, MSB1234"""
    combined = stderr_text + "\n" + stdout_text
    error_pattern = r'\b(CS\d{4}|NU\d{4}|MSB\d{4})\b'
    tokens = re.findall(error_pattern, combined, re.IGNORECASE)
    return list(set(tokens))  # Remove duplicates

def update_solution_progress(solution_name, task_name, status):
    """Update solution-progress.md"""
    progress_file = Path("results/solution-progress.md")
    if not progress_file.exists():
        return
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the row for this solution
    for i, line in enumerate(lines):
        if repo_name in line and solution_name in line:
            parts = line.split('|')
            if len(parts) >= 5:
                # Determine which column to update
                if task_name == "task-restore-solution":
                    col_idx = 3
                elif task_name == "task-build-solution":
                    col_idx = 4
                elif task_name == "task-collect-knowledge-base":
                    col_idx = 5
                else:
                    continue
                
                # Update the marker
                marker = ' [x] ' if status in ['SUCCESS', 'SKIPPED'] else ' [!] '
                parts[col_idx] = marker
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def append_solution_result(solution_name, task_name, status):
    """Append to solution-results files"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if status == 'SUCCESS':
        symbol = '✓'
    elif status == 'SKIPPED':
        symbol = '○'
    else:
        symbol = '✗'
    
    # Markdown
    md_file = Path("results/solution-results.md")
    with open(md_file, 'a', encoding='utf-8') as f:
        f.write(f"| {timestamp} | {repo_name} | {solution_name} | {task_name} | {status} | {symbol} |\n")
    
    # CSV
    csv_file = Path("results/solution-results.csv")
    with open(csv_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp},{repo_name},{solution_name},{task_name},{status},{symbol}\n")

def task_restore(solution_name, solution_path):
    """Task 1: Restore solution"""
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-restore-solution] START solution='{solution_name}' path='{solution_path}'")
        print(f"[debug][task-restore-solution] executing: msbuild {solution_path} /restore /p:Configuration=Release /nologo")
    
    # Execute restore command
    cmd = ["msbuild", solution_path, "/restore", "/p:Configuration=Release", "/nologo"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    exit_code = result.returncode
    status = "SUCCESS" if exit_code == 0 else "FAIL"
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-restore-solution] msbuild exit_code={exit_code}")
    
    # If failed, try NuGet restore fallback
    if exit_code != 0:
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-restore-solution] NuGet fallback triggered (msbuild exitCode={exit_code})")
            print(f"[debug][task-restore-solution] executing: nuget restore {solution_path}")
        
        nuget_cmd = ["nuget", "restore", solution_path]
        nuget_result = subprocess.run(nuget_cmd, capture_output=True, text=True)
        
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-restore-solution] nuget exit_code={nuget_result.returncode}")
    
    # Extract error tokens
    error_tokens = extract_error_tokens(result.stderr, result.stdout)
    
    # Count errors and warnings
    combined_output = result.stdout + result.stderr
    error_count = combined_output.lower().count('error')
    warning_count = combined_output.lower().count('warning')
    
    # Save output
    output_data = {
        "repo_name": repo_name,
        "solution_name": solution_name,
        "solution_path": solution_path,
        "exit_code": exit_code,
        "error_tokens": error_tokens,
        "error_count": error_count,
        "warning_count": warning_count,
        "status": status
    }
    
    output_file = Path("output") / f"{repo_name}_{solution_name}_task1_restore-solution.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    # Update progress and results
    update_solution_progress(solution_name, "task-restore-solution", status)
    append_solution_result(solution_name, "task-restore-solution", status)
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-restore-solution] END solution='{solution_name}' status={status}")
    
    return status, exit_code

def task_build(solution_name, solution_path):
    """Task 2: Build solution"""
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-build-solution] START solution='{solution_name}' path='{solution_path}'")
        print(f"[debug][task-build-solution] executing: msbuild {solution_path} /t:Clean,Build /p:Configuration=Release /nologo /m")
    
    # Execute build command
    cmd = ["msbuild", solution_path, "/t:Clean,Build", "/p:Configuration=Release", "/nologo", "/m"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    exit_code = result.returncode
    status = "SUCCESS" if exit_code == 0 else "FAIL"
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-build-solution] msbuild exit_code={exit_code}")
    
    # Extract error tokens
    error_tokens = extract_error_tokens(result.stderr, result.stdout)
    
    # Count errors and warnings
    combined_output = result.stdout + result.stderr
    error_count = combined_output.lower().count('error')
    warning_count = combined_output.lower().count('warning')
    
    # Save output
    output_data = {
        "repo_name": repo_name,
        "solution_name": solution_name,
        "solution_path": solution_path,
        "exit_code": exit_code,
        "error_tokens": error_tokens,
        "error_count": error_count,
        "warning_count": warning_count,
        "status": status
    }
    
    output_file = Path("output") / f"{repo_name}_{solution_name}_task2_build-solution.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    # Update progress and results
    update_solution_progress(solution_name, "task-build-solution", status)
    append_solution_result(solution_name, "task-build-solution", status)
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-build-solution] END solution='{solution_name}' status={status} errors={len(error_tokens)} warnings={warning_count}")
    
    return status, error_tokens

def task_kb(solution_name, solution_path, build_status, error_tokens):
    """Task 3: Collect knowledge base"""
    if os.environ.get('DEBUG') == '1':
        print(f"[KB-DEBUG] START solution='{solution_name}' build_status={build_status}")
    
    if build_status == "SUCCESS":
        status = "SKIPPED"
        kb_articles = []
        
        if os.environ.get('DEBUG') == '1':
            print(f"[KB-DEBUG] build succeeded, skipping KB collection")
    else:
        status = "SUCCESS"
        kb_articles = []
        
        # Collect KB articles for each error token
        kb_dir = Path("knowledge_base_markdown")
        for token in error_tokens:
            if os.environ.get('DEBUG') == '1':
                print(f"[KB-DEBUG] searching for token: {token}")
            
            # Search for markdown files containing this error token
            for kb_file in kb_dir.glob("*.md"):
                if kb_file.name == "README.md":
                    continue
                
                try:
                    with open(kb_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if token.upper() in content.upper():
                            kb_articles.append({
                                "error_token": token,
                                "kb_file": kb_file.name,
                                "kb_path": str(kb_file)
                            })
                            if os.environ.get('DEBUG') == '1':
                                print(f"[KB-DEBUG] found KB article: {kb_file.name} for token {token}")
                except Exception as e:
                    if os.environ.get('DEBUG') == '1':
                        print(f"[KB-DEBUG] error reading {kb_file.name}: {e}")
    
    # Save output
    output_data = {
        "repo_name": repo_name,
        "solution_name": solution_name,
        "solution_path": solution_path,
        "build_status": build_status,
        "error_tokens": error_tokens,
        "kb_articles_count": len(kb_articles),
        "kb_articles": kb_articles,
        "status": status
    }
    
    output_file = Path("output") / f"{repo_name}_{solution_name}_task3_collect-knowledge-base.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    # Update progress and results
    update_solution_progress(solution_name, "task-collect-knowledge-base", status)
    append_solution_result(solution_name, "task-collect-knowledge-base", status)
    
    if os.environ.get('DEBUG') == '1':
        print(f"[KB-DEBUG] END solution='{solution_name}' status={status} articles_found={len(kb_articles)}")
    
    return status

# Process each solution sequentially
for idx, solution in enumerate(solutions, start=1):
    solution_name = solution['solution_name']
    solution_path = solution['solution_path']
    
    print(f"\n{'='*60}")
    print(f"Solution {idx}/{len(solutions)}: {solution_name}")
    print(f"{'='*60}")
    
    # Task 1: Restore
    restore_status, restore_exit_code = task_restore(solution_name, solution_path)
    print(f"  Restore: {restore_status} (exit code: {restore_exit_code})")
    
    # Task 2: Build
    build_status, error_tokens = task_build(solution_name, solution_path)
    print(f"  Build: {build_status} (errors found: {len(error_tokens)})")
    
    # Task 3: KB Collection
    kb_status = task_kb(solution_name, solution_path, build_status, error_tokens)
    print(f"  KB Collection: {kb_status}")

print(f"\n{'='*60}")
print(f"Completed processing {len(solutions)} solutions for repository 1")
print(f"{'='*60}")
