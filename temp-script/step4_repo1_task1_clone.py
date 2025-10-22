import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

# Load repository list
with open('output/repositories_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    repo = data['repositories'][0]  # First repository

repo_url = repo['repo_url']
repo_name = repo['repo_name']
clone_base_path = data['clone_base_path']
clone_path = os.path.join(clone_base_path, repo_name)

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-clone-repo] START repo_url='{repo_url}' clone_path='{clone_path}'")

# Check if repository already exists
repo_exists = os.path.exists(clone_path)

if os.environ.get('DEBUG') == '1':
    print(f"[debug][task-clone-repo] repository exists: {repo_exists}")

try:
    if repo_exists:
        # REFRESH: Reset and pull latest
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-clone-repo] executing REFRESH operation")
        
        # git reset --hard HEAD
        reset_result = subprocess.run(
            ["git", "reset", "--hard", "HEAD"],
            cwd=clone_path,
            capture_output=True,
            text=True
        )
        
        # git clean -fd
        clean_result = subprocess.run(
            ["git", "clean", "-fd"],
            cwd=clone_path,
            capture_output=True,
            text=True
        )
        
        # git pull
        pull_result = subprocess.run(
            ["git", "pull"],
            cwd=clone_path,
            capture_output=True,
            text=True
        )
        
        exit_code = pull_result.returncode
        operation = "REFRESH"
        
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-clone-repo] REFRESH exit_code={exit_code}")
    else:
        # CLONE: Fresh clone with depth 1
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-clone-repo] executing CLONE operation")
            print(f"[debug][task-clone-repo] executing: git clone --depth 1 {repo_url} {clone_path}")
        
        # git clone --depth 1
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, clone_path],
            capture_output=True,
            text=True
        )
        
        exit_code = clone_result.returncode
        operation = "CLONE"
        
        if os.environ.get('DEBUG') == '1':
            print(f"[debug][task-clone-repo] CLONE exit_code={exit_code}")
    
    # Determine status
    status = "SUCCESS" if exit_code == 0 else "FAIL"
    
    # Prepare output
    output_data = {
        "repo_url": repo_url,
        "repo_name": repo_name,
        "clone_path": clone_path,
        "operation": operation,
        "exit_code": exit_code,
        "status": status
    }
    
    # Save to output directory
    output_dir = Path("output")
    output_file = output_dir / f"{repo_name}_task1_clone-repo.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    # Update progress table
    progress_file = Path("results/repo-progress.md")
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the row for this repository and update task-clone-repo column
        for i, line in enumerate(lines):
            if repo_name in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    # Column 2 is task-clone-repo (after repo_name and first separator)
                    parts[2] = ' [x] '
                    lines[i] = '|'.join(parts)
                    break
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    # Append to results files
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    symbol = '✓' if status == 'SUCCESS' else '✗'
    
    # Markdown result
    md_result = Path("results/repo-results.md")
    with open(md_result, 'a', encoding='utf-8') as f:
        f.write(f"| {timestamp} | {repo_name} | task-clone-repo | {status} | {symbol} |\n")
    
    # CSV result
    csv_result = Path("results/repo-results.csv")
    with open(csv_result, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp},{repo_name},task-clone-repo,{status},{symbol}\n")
    
    if os.environ.get('DEBUG') == '1':
        print(f"[debug][task-clone-repo] END repo_url='{repo_url}' status={status} operation={operation}")
    
    print(f"\nRepository 1 clone completed: {status} ({operation})")
    print(f"  Repository: {repo_name}")
    print(f"  Path: {clone_path}")

except Exception as e:
    print(f"Error during clone operation: {e}", file=sys.stderr)
    sys.exit(1)
