import subprocess
import sys

# Configuration
repositories_file = '.copilot/prompts/repositories.txt'
clone_path = r'C:\Users\sacheu\speckit_repos'

# Read all repositories
repo_urls = []
with open(repositories_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            repo_urls.append(line)

print(f'[run12][workflow-master] Processing {len(repo_urls)} repositories')
print('')

# Process each repository
for idx, repo_url in enumerate(repo_urls, 1):
    repo_name = repo_url.rstrip('/').split('/')[-1]
    print(f'[run12][workflow-master] ===== Repository {idx}/{len(repo_urls)}: {repo_name} =====')
    
    # Task 1: Clone
    print(f'[run12][workflow-master] Executing task 1/4: task-clone-repo')
    result = subprocess.run([
        sys.executable, 
        'temp-script/task_clone_repo.py',
        repo_url,
        clone_path
    ], capture_output=False)
    
    if result.returncode != 0:
        print(f'[run12][workflow-master] FAILED: task-clone-repo for {repo_name}')
        continue
    
    repo_dir = f'{clone_path}\\{repo_name}'
    
    # Task 2: Execute README
    print(f'[run12][workflow-master] Executing task 2/4: task-execute-readme')
    result = subprocess.run([
        sys.executable,
        'temp-script/task_execute_readme.py',
        repo_dir,
        repo_name
    ], capture_output=False)
    
    if result.returncode != 0:
        print(f'[run12][workflow-master] FAILED: task-execute-readme for {repo_name}')
        continue
    
    # Task 3: Find solutions
    print(f'[run12][workflow-master] Executing task 3/4: task-find-solutions')
    result = subprocess.run([
        sys.executable,
        'temp-script/task_find_solutions.py',
        repo_dir,
        repo_name
    ], capture_output=False)
    
    if result.returncode != 0:
        print(f'[run12][workflow-master] FAILED: task-find-solutions for {repo_name}')
        continue
    
    # Task 4: Process solutions
    print(f'[run12][workflow-master] Executing task 4/4: task-process-solutions')
    result = subprocess.run([
        sys.executable,
        'temp-script/task_process_solutions.py',
        repo_name
    ], capture_output=False)
    
    if result.returncode != 0:
        print(f'[run12][workflow-master] FAILED: task-process-solutions for {repo_name}')
        continue
    
    print(f'[run12][workflow-master] Completed all tasks for {repo_name}')
    print('')

print(f'[run12][workflow-master] Workflow completed for all {len(repo_urls)} repositories')
