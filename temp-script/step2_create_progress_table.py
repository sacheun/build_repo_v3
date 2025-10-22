import os
import json
from pathlib import Path

os.environ['DEBUG'] = '1'

print("[debug][create-progress] START creating repository progress table")

# Load repositories
with open("output/repositories_list.json", 'r') as f:
    data = json.load(f)
    repositories = data['repositories']

# Define tasks from repo_tasks_list.md
tasks = [
    "task-clone-repo",
    "task-search-readme",
    "task-scan-readme",
    "task-execute-readme",
    "task-find-solutions",
    "task-process-solutions"
]

print(f"[debug][create-progress] creating table for {len(repositories)} repos × {len(tasks)} tasks")

# Create repo-progress.md
progress_file = Path("results/repo-progress.md")
with open(progress_file, 'w', encoding='utf-8') as f:
    # Header
    header = "| Repository | " + " | ".join(tasks) + " |"
    separator = "|" + "|".join(["-" * 12] + ["-" * (len(task) + 2) for task in tasks]) + "|"
    
    f.write(header + "\n")
    f.write(separator + "\n")
    
    # Rows - one per repository
    for repo in repositories:
        repo_name = repo['repo_name']
        checkboxes = " | ".join([" [ ] "] * len(tasks))
        row = f"| {repo_name} | {checkboxes} |"
        f.write(row + "\n")

print(f"[debug][create-progress] created {progress_file} with {len(repositories)} repositories")
print("[debug][create-progress] EXIT status='SUCCESS'")
