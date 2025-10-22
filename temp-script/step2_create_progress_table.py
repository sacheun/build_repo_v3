import os
import json
import re
from pathlib import Path

os.environ['DEBUG'] = '1'

print("Creating repository progress table...")

# Load repository list
with open('output/repositories_list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    repositories = data['repositories']

# Read repo_tasks_list.md to extract task names
repo_tasks_file = Path(".copilot/prompts/repo_tasks_list.md")
with open(repo_tasks_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract task names using regex: @task-<name>
task_pattern = r'@(task-[\w-]+)'
task_matches = re.findall(task_pattern, content)

# Get unique tasks in order of appearance
tasks = []
for task in task_matches:
    if task not in tasks and task != 'task-clone-repo':  # Skip duplicates
        tasks.append(task)

# Ensure we have the expected tasks
expected_tasks = ['task-clone-repo', 'task-execute-readme', 'task-find-solutions', 'task-process-solutions']
tasks = expected_tasks  # Use expected order

print(f"Found {len(tasks)} tasks: {tasks}")

# Create progress table
progress_file = Path("results/repo-progress.md")

# Create header
header = "| Repository | " + " | ".join(tasks) + " |\n"
separator = "|---|" + "|".join(["---"] * len(tasks)) + "|\n"

# Create rows for each repository
rows = []
for repo in repositories:
    repo_name = repo['repo_name']
    row = f"| {repo_name} | " + " | ".join([" [ ] " for _ in tasks]) + " |\n"
    rows.append(row)

# Write to file
with open(progress_file, 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(separator)
    f.writelines(rows)

print(f"Progress table created: {progress_file}")
print(f"  Repositories: {len(repositories)}")
print(f"  Tasks per repo: {len(tasks)}")
