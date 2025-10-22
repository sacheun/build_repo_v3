import os
import json
import re
from pathlib import Path

os.environ['DEBUG'] = '1'

print("Initializing solution progress table...")

# Load solutions info for repository 1
with open('output/ic3_spool_cosine-dep-spool_solutions_info.json', 'r', encoding='utf-8') as f:
    solutions_data = json.load(f)

repo_name = solutions_data['repo_name']
solutions = solutions_data['solutions']

# Read solution_tasks_list.md to extract task names
solution_tasks_file = Path(".copilot/prompts/solution_tasks_list.md")
with open(solution_tasks_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract task names: @task-restore-solution, @task-build-solution, @task-collect-knowledge-base
task_pattern = r'@(task-[\w-]+)'
task_matches = re.findall(task_pattern, content)

# Get unique tasks (excluding @solution-tasks-list)
tasks = []
for task in task_matches:
    if task not in tasks and task != 'solution-tasks-list':
        tasks.append(task)

# Expected tasks in order
expected_tasks = ['task-restore-solution', 'task-build-solution', 'task-collect-knowledge-base']
tasks = expected_tasks

print(f"Found {len(tasks)} solution tasks: {tasks}")
print(f"Found {len(solutions)} solutions for repository: {repo_name}")

# Create solution progress table
progress_file = Path("results/solution-progress.md")

# Create header
header = "| Repository | Solution | " + " | ".join(tasks) + " |\n"
separator = "|---|---|" + "|".join(["---"] * len(tasks)) + "|\n"

# Create rows for each solution
rows = []
for solution in solutions:
    solution_name = solution['solution_name']
    row = f"| {repo_name} | {solution_name} | " + " | ".join([" [ ] " for _ in tasks]) + " |\n"
    rows.append(row)

# Write to file
with open(progress_file, 'w', encoding='utf-8') as f:
    f.write(header)
    f.write(separator)
    f.writelines(rows)

print(f"Solution progress table created: {progress_file}")
print(f"  Solutions: {len(solutions)}")
print(f"  Tasks per solution: {len(tasks)}")
