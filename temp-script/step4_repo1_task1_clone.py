import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

# Repository info
repo_url = "https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool"
repo_name = "ic3_spool_cosine-dep-spool"
clone_path = r"C:\Users\sacheu\speckit_repos"
repo_directory = Path(clone_path) / repo_name
workspace_dir = Path.cwd()  # Save current directory

print(f"[debug][task-clone-repo] START repo_url='{repo_url}' clone_path='{clone_path}'")

# Check if repository already exists
if repo_directory.exists():
    print(f"[debug][task-clone-repo] repository exists, refreshing: reverting local changes and pulling latest")
    operation = "REFRESH"
    
    # Navigate and refresh
    os.chdir(repo_directory)
    
    # Reset
    subprocess.run("git reset --hard HEAD", shell=True, check=False)
    
    # Clean
    subprocess.run("git clean -fd", shell=True, check=False)
    
    # Pull
    result = subprocess.run("git pull", shell=True, capture_output=True, text=True)
    exit_code = result.returncode
else:
    print(f"[debug][task-clone-repo] performing fresh clone: git clone --depth 1 {repo_url} {repo_directory}")
    operation = "CLONE"
    
    # Clone
    cmd = f'git clone --depth 1 "{repo_url}" "{repo_directory}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    exit_code = result.returncode

# Determine status
status = "SUCCESS" if exit_code == 0 else "FAIL"
symbol = '✓' if status == 'SUCCESS' else '✗'

print(f"[debug][task-clone-repo] operation={operation} exit_code={exit_code} status={status}")

# Return to workspace directory
os.chdir(workspace_dir)

# Save JSON output
output_data = {
    "repo_name": repo_name,
    "repo_directory": str(repo_directory),
    "clone_status": status,
    "operation": operation,
    "exit_code": exit_code,
    "timestamp": datetime.now().isoformat()
}

output_file = Path("output") / f"{repo_name}_task1_clone-repo.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

# Update progress table
progress_file = Path("results/repo-progress.md")
if progress_file.exists():
    with open(progress_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if repo_name in line:
            parts = line.split('|')
            if len(parts) >= 3:
                parts[2] = ' [x] '
                lines[i] = '|'.join(parts)
                break
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Append to results files
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

md_result = Path("results/repo-results.md")
with open(md_result, 'a', encoding='utf-8') as f:
    f.write(f"| {timestamp} | {repo_name} | task-clone-repo | {status} | {symbol} |\n")

csv_result = Path("results/repo-results.csv")
with open(csv_result, 'a', encoding='utf-8') as f:
    f.write(f"{timestamp},{repo_name},task-clone-repo,{status},{symbol}\n")

print(f"[debug][task-clone-repo] EXIT repo_directory='{repo_directory}' status='{status}'")
