import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

# Load repository list
with open('output/repositories_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    all_repos = data['repositories']
    clone_base_path = data['clone_base_path']

# Process repositories 2-5 (indices 1-4)
repositories_to_process = all_repos[1:5]

print(f"Processing repositories 2-5 ({len(repositories_to_process)} repositories)")
print("="*60)

def extract_error_tokens(stderr_text, stdout_text):
    """Extract error tokens like CS1234, NU1234, MSB1234"""
    combined = stderr_text + "\n" + stdout_text
    error_pattern = r'\b(CS\d{4}|NU\d{4}|MSB\d{4})\b'
    tokens = re.findall(error_pattern, combined, re.IGNORECASE)
    return list(set(tokens))

def update_repo_progress(repo_name, task_name):
    """Update repo-progress.md"""
    progress_file = Path("results/repo-progress.md")
    if not progress_file.exists():
        return
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    task_col_map = {
        "task-clone-repo": 2,
        "task-execute-readme": 3,
        "task-find-solutions": 4,
        "task-process-solutions": 5
    }
    
    col_idx = task_col_map.get(task_name)
    if col_idx is None:
        return
    
    for i, line in enumerate(lines):
        if repo_name in line:
            parts = line.split('|')
            if len(parts) > col_idx:
                parts[col_idx] = ' [x] '
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def append_repo_result(repo_name, task_name, status):
    """Append to repo-results files"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    symbol = '✓' if status == 'SUCCESS' else '✗'
    
    md_file = Path("results/repo-results.md")
    with open(md_file, 'a', encoding='utf-8') as f:
        f.write(f"| {timestamp} | {repo_name} | {task_name} | {status} | {symbol} |\n")
    
    csv_file = Path("results/repo-results.csv")
    with open(csv_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp},{repo_name},{task_name},{status},{symbol}\n")

def update_solution_progress(repo_name, solution_name, task_name, status):
    """Update solution-progress.md"""
    progress_file = Path("results/solution-progress.md")
    if not progress_file.exists():
        return
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    task_col_map = {
        "task-restore-solution": 3,
        "task-build-solution": 4,
        "task-collect-knowledge-base": 5
    }
    
    col_idx = task_col_map.get(task_name)
    if col_idx is None:
        return
    
    for i, line in enumerate(lines):
        if repo_name in line and solution_name in line:
            parts = line.split('|')
            if len(parts) > col_idx:
                marker = ' [x] ' if status in ['SUCCESS', 'SKIPPED'] else ' [!] '
                parts[col_idx] = marker
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def append_solution_result(repo_name, solution_name, task_name, status):
    """Append to solution-results files"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if status == 'SUCCESS':
        symbol = '✓'
    elif status == 'SKIPPED':
        symbol = '○'
    else:
        symbol = '✗'
    
    md_file = Path("results/solution-results.md")
    with open(md_file, 'a', encoding='utf-8') as f:
        f.write(f"| {timestamp} | {repo_name} | {solution_name} | {task_name} | {status} | {symbol} |\n")
    
    csv_file = Path("results/solution-results.csv")
    with open(csv_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp},{repo_name},{solution_name},{task_name},{status},{symbol}\n")

def ensure_solution_in_progress(repo_name, solution_name):
    """Add solution to progress table if not present"""
    progress_file = Path("results/solution-progress.md")
    if not progress_file.exists():
        return
    
    with open(progress_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if f"| {repo_name} | {solution_name} |" in content:
        return
    
    new_row = f"| {repo_name} | {solution_name} |  [ ]  |  [ ]  |  [ ]  |\n"
    with open(progress_file, 'a', encoding='utf-8') as f:
        f.write(new_row)

# Process each repository
for repo_idx, repo in enumerate(repositories_to_process, start=2):
    repo_url = repo['repo_url']
    repo_name = repo['repo_name']
    clone_path = os.path.join(clone_base_path, repo_name)
    
    print(f"\n{'#'*60}")
    print(f"# REPOSITORY {repo_idx}/5: {repo_name}")
    print(f"{'#'*60}\n")
    
    # ======================
    # TASK 1: Clone Repository
    # ======================
    print(f"[Task 1/4] Cloning repository...")
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-clone-repo] START repo_url='{repo_url}'")
    
    repo_exists = os.path.exists(clone_path)
    
    try:
        if repo_exists:
            # REFRESH
            subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=clone_path, capture_output=True)
            subprocess.run(["git", "clean", "-fd"], cwd=clone_path, capture_output=True)
            pull_result = subprocess.run(["git", "pull"], cwd=clone_path, capture_output=True, text=True)
            exit_code = pull_result.returncode
            operation = "REFRESH"
        else:
            # CLONE
            if os.environ.get('DEBUG') == '1':
                print(f"[debug][task-clone-repo] executing: git clone --depth 1 {repo_url} {clone_path}")
            clone_result = subprocess.run(["git", "clone", "--depth", "1", repo_url, clone_path], 
                                        capture_output=True, text=True)
            exit_code = clone_result.returncode
            operation = "CLONE"
        
        clone_status = "SUCCESS" if exit_code == 0 else "FAIL"
        
        # Save output
        output_data = {"repo_url": repo_url, "repo_name": repo_name, "clone_path": clone_path, 
                      "operation": operation, "exit_code": exit_code, "status": clone_status}
        with open(f"output/{repo_name}_task1_clone-repo.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        update_repo_progress(repo_name, "task-clone-repo")
        append_repo_result(repo_name, "task-clone-repo", clone_status)
        
        print(f"  Clone: {clone_status} ({operation})")
        
        if clone_status == "FAIL":
            print(f"  ERROR: Failed to clone repository, skipping remaining tasks")
            continue
            
    except Exception as e:
        print(f"  ERROR: {e}")
        continue
    
    # ======================
    # TASK 2: Execute README
    # ======================
    print(f"[Task 2/4] Finding README...")
    
    readme_candidates = ["README.md", "readme.md", "README.txt", "README.rst", "README", "Readme.md"]
    readme_filename = None
    readme_content = None
    
    for candidate in readme_candidates:
        candidate_path = Path(clone_path) / candidate
        if candidate_path.exists():
            readme_filename = candidate
            try:
                with open(candidate_path, 'r', encoding='utf-8', errors='ignore') as f:
                    readme_content = f.read()
            except:
                pass
            break
    
    readme_status = "SUCCESS" if readme_filename else "FAIL"
    
    output_data = {"repo_directory": clone_path, "repo_name": repo_name, "readme_filename": readme_filename,
                  "readme_content": readme_content, "setup_commands_executed": [], 
                  "setup_commands_skipped": [], "status": readme_status}
    with open(f"output/{repo_name}_task2_execute-readme.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    update_repo_progress(repo_name, "task-execute-readme")
    append_repo_result(repo_name, "task-execute-readme", readme_status)
    
    if readme_filename:
        print(f"  README: {readme_status} (found {readme_filename})")
    else:
        print(f"  README: {readme_status} (not found)")
    
    # ======================
    # TASK 3: Find Solutions
    # ======================
    print(f"[Task 3/4] Finding solutions...")
    
    repo_path = Path(clone_path)
    solution_files = list(repo_path.rglob("*.sln"))
    
    solutions = []
    for sln_path in solution_files:
        solutions.append({
            "solution_name": sln_path.stem,
            "solution_path": str(sln_path.absolute()),
            "relative_path": str(sln_path.relative_to(repo_path))
        })
    
    output_data = {"repo_directory": clone_path, "repo_name": repo_name, 
                  "solutions_count": len(solutions), "solutions": solutions, "status": "SUCCESS"}
    with open(f"output/{repo_name}_solutions_info.json", 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    update_repo_progress(repo_name, "task-find-solutions")
    append_repo_result(repo_name, "task-find-solutions", "SUCCESS")
    
    print(f"  Solutions: SUCCESS (found {len(solutions)})")
    
    # ======================
    # TASK 4: Process Solutions
    # ======================
    print(f"[Task 4/4] Processing {len(solutions)} solutions...")
    
    for sol_idx, solution in enumerate(solutions, start=1):
        solution_name = solution['solution_name']
        solution_path = solution['solution_path']
        
        print(f"\n  Solution {sol_idx}/{len(solutions)}: {solution_name}")
        
        # Add to progress table
        ensure_solution_in_progress(repo_name, solution_name)
        
        # RESTORE
        cmd = ["msbuild", solution_path, "/restore", "/p:Configuration=Release", "/nologo"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        restore_status = "SUCCESS" if result.returncode == 0 else "FAIL"
        
        if result.returncode != 0:
            subprocess.run(["nuget", "restore", solution_path], capture_output=True)
        
        error_tokens = extract_error_tokens(result.stderr, result.stdout)
        
        with open(f"output/{repo_name}_{solution_name}_task1_restore-solution.json", 'w', encoding='utf-8') as f:
            json.dump({"repo_name": repo_name, "solution_name": solution_name, "solution_path": solution_path,
                      "exit_code": result.returncode, "error_tokens": error_tokens, "status": restore_status}, f, indent=2)
        
        update_solution_progress(repo_name, solution_name, "task-restore-solution", restore_status)
        append_solution_result(repo_name, solution_name, "task-restore-solution", restore_status)
        
        # BUILD
        cmd = ["msbuild", solution_path, "/t:Clean,Build", "/p:Configuration=Release", "/nologo", "/m"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        build_status = "SUCCESS" if result.returncode == 0 else "FAIL"
        error_tokens = extract_error_tokens(result.stderr, result.stdout)
        
        with open(f"output/{repo_name}_{solution_name}_task2_build-solution.json", 'w', encoding='utf-8') as f:
            json.dump({"repo_name": repo_name, "solution_name": solution_name, "solution_path": solution_path,
                      "exit_code": result.returncode, "error_tokens": error_tokens, "status": build_status}, f, indent=2)
        
        update_solution_progress(repo_name, solution_name, "task-build-solution", build_status)
        append_solution_result(repo_name, solution_name, "task-build-solution", build_status)
        
        # KB COLLECTION
        if build_status == "SUCCESS":
            kb_status = "SKIPPED"
            kb_articles = []
        else:
            kb_status = "SUCCESS"
            kb_articles = []
            kb_dir = Path("knowledge_base_markdown")
            for token in error_tokens:
                for kb_file in kb_dir.glob("*.md"):
                    if kb_file.name == "README.md":
                        continue
                    try:
                        with open(kb_file, 'r', encoding='utf-8') as f:
                            if token.upper() in f.read().upper():
                                kb_articles.append({"error_token": token, "kb_file": kb_file.name, 
                                                  "kb_path": str(kb_file)})
                    except:
                        pass
        
        with open(f"output/{repo_name}_{solution_name}_task3_collect-knowledge-base.json", 'w', encoding='utf-8') as f:
            json.dump({"repo_name": repo_name, "solution_name": solution_name, "solution_path": solution_path,
                      "build_status": build_status, "error_tokens": error_tokens, "kb_articles_count": len(kb_articles),
                      "kb_articles": kb_articles, "status": kb_status}, f, indent=2)
        
        update_solution_progress(repo_name, solution_name, "task-collect-knowledge-base", kb_status)
        append_solution_result(repo_name, solution_name, "task-collect-knowledge-base", kb_status)
        
        print(f"    Restore: {restore_status}, Build: {build_status}, KB: {kb_status}")
    
    # Mark repository task-process-solutions as complete
    update_repo_progress(repo_name, "task-process-solutions")
    append_repo_result(repo_name, "task-process-solutions", "SUCCESS")
    
    print(f"\n  Repository {repo_idx} complete: {len(solutions)} solutions processed")

print(f"\n{'='*60}")
print(f"Completed processing repositories 2-5")
print(f"{'='*60}")
