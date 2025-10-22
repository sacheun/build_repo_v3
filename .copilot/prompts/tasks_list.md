@tasks-list repo_url={{repo_url}} clone_path={{clone_path}}

Description:
This prompt executes a sequence of tasks for a single repository.
Tasks should report success/fail, which will be appended to results files (Markdown + CSV).

Current Tasks List:
1. @task-clone-repo

Behavior:
- For each task in the list:
   1. Execute the task using repo_url and clone_path
   2. Mark success/fail in results.md and results.csv
- After all tasks, return a dictionary of task results for this repo
