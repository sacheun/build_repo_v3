@tasks-list repo_url={{repo_url}} clone_path={{clone_path}}
---
temperature: 0.1
---

Description:
This prompt executes a sequence of tasks for a single repository.
Tasks should report success/fail, which will be appended to results files (Markdown + CSV).

### Available Tasks:
1. @task-clone-repo
2. @task-search-readme
3. @task-scan-readme
4. @task-execute-readme
5. @task-find-solutions
6. @generate-solution-task-checklists


### Repo Variables Available:
- {{repo_url}} → Original repository URL provided to the workflow.
- {{clone_path}} → Root folder where repositories are cloned.
- {{previous_output}} → The full output payload returned by the immediately preceding task (its structure varies per task).
- {{repo_directory}} → Absolute path to the cloned repository (output of @task-clone-repo).
- {{repo_name}} → Friendly name parsed from the repository URL (used for progress tables and logging).
- {{readme_content}} → README file content (output of @task-search-readme).
- {{readme_filename}} → README filename (output of @task-search-readme).
- {{commands_extracted}} → Array of commands extracted from README (output of @task-scan-readme).
- {{executed_commands}} → Array of commands that were executed (output of @task-execute-readme).
- {{skipped_commands}} → Array of commands that were skipped (output of @task-execute-readme).
- {{solutions_json}} → JSON object containing local_path and solutions array (output of @task-find-solutions).
- {{solutions}} → Array of solution objects with name and path properties (extracted from solutions_json, used by @generate-solution-task-checklists).

Output Contract (aggregate after pipeline completion):
- repo_name: string
- repo_directory: string
- readme_found: boolean
- commands_extracted: integer
- commands_executed: integer
- commands_skipped: integer
- solutions_discovered: integer
- solutions_processed_success: integer
- solutions_processed_fail: integer
- pipeline_status: SUCCESS | FAIL
