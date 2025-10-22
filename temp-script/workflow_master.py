"""
Master workflow loop script
Processes all repositories from repositories.txt
"""

import sys
import os
import subprocess
from datetime import datetime

print("="*80)
print("WORKFLOW-LOOP - Run 13")
print("="*80)

# Parameters
repositories_file = '.copilot/prompts/repositories.txt'
clone_path = r'C:\Users\sacheu\speckit_repos'

start_time = datetime.now()
print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Ensure clone path exists
os.makedirs(clone_path, exist_ok=True)
print(f"Clone path: {clone_path}")

# Initialize tracking files
print("\n--- Initializing tracking files ---")
result = subprocess.run([sys.executable, 'temp-script/init_repo_tracking.py'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"Initialization failed: {result.stderr}")
    sys.exit(1)

# Read all repository URLs
print(f"\n--- Reading repositories from {repositories_file} ---")
repo_urls = []
with open(repositories_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            repo_urls.append(line)
            print(f"  - {line}")

print(f"\nTotal repositories: {len(repo_urls)}")

# Process each repository
repos_success = 0
repos_fail = 0

for idx, repo_url in enumerate(repo_urls, 1):
    repo_name = repo_url.rstrip('/').split('/')[-1]
    repo_dir = os.path.join(clone_path, repo_name)
    
    print(f"\n{'='*80}")
    print(f"REPOSITORY {idx}/{len(repo_urls)}: {repo_name}")
    print(f"{'='*80}")
    
    repo_status = "SUCCESS"
    
    # Task 1: Clone repository
    print(f"\n[{idx}.1] Executing task-clone-repo...")
    result = subprocess.run([sys.executable, 'temp-script/task_clone_repo.py', repo_url, clone_path], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"task-clone-repo FAILED")
        print(result.stderr)
        repo_status = "FAIL"
        repos_fail += 1
        continue
    
    # Task 2: Execute README
    print(f"\n[{idx}.2] Executing task-execute-readme...")
    result = subprocess.run([sys.executable, 'temp-script/task_execute_readme.py', repo_dir, repo_name], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"task-execute-readme FAILED")
        print(result.stderr)
        repo_status = "FAIL"
        repos_fail += 1
        continue
    
    # Task 3: Find solutions
    print(f"\n[{idx}.3] Executing task-find-solutions...")
    result = subprocess.run([sys.executable, 'temp-script/task_find_solutions.py', repo_dir, repo_name], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"task-find-solutions FAILED")
        print(result.stderr)
        repo_status = "FAIL"
        repos_fail += 1
        continue
    
    # Task 4: Process solutions
    print(f"\n[{idx}.4] Executing task-process-solutions...")
    result = subprocess.run([sys.executable, 'temp-script/task_process_solutions.py', repo_name], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"task-process-solutions FAILED")
        print(result.stderr)
        repo_status = "FAIL"
        repos_fail += 1
        continue
    
    if repo_status == "SUCCESS":
        repos_success += 1
    
    print(f"\nRepository {repo_name}: {repo_status}")

# Summary
end_time = datetime.now()
duration = end_time - start_time

print(f"\n{'='*80}")
print("WORKFLOW SUMMARY")
print(f"{'='*80}")
print(f"Total repositories: {len(repo_urls)}")
print(f"Success: {repos_success}")
print(f"Failed: {repos_fail}")
print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Duration: {duration}")

if repos_fail == 0:
    overall_status = "SUCCESS"
elif repos_success == 0:
    overall_status = "FAIL"
else:
    overall_status = "PARTIAL"

print(f"Overall Status: {overall_status}")
print(f"{'='*80}")

sys.exit(0 if overall_status != "FAIL" else 1)
