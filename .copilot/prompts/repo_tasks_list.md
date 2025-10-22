@tasks-list repo_url={{repo_url}} clone_path={{clone_path}}

Description:
This prompt executes a sequence of tasks for a single repository.
Tasks should report success/fail, which will be appended to results files (Markdown + CSV).

Current Tasks List:
1. @task-clone-repo
2. @task-find-solutions
3. @task-process-solutions

Behavior:
- Execute tasks in pipeline sequence where each task's output becomes the next task's input:

   1. **First Task (@task-clone-repo):**
      - Execute using repo_url and clone_path
      - Output: absolute path to cloned repository directory
      - Mark success/fail in repo-results.md and repo-results.csv

   2. **Second Task (@task-find-solutions):**
      - Input: repository directory path from previous task
      - Execute: @task-find-solutions repo_directory={{previous_output}}
      - Output: JSON object with local_path and solutions array
      - Mark success/fail in repo-results.md and repo-results.csv

   3. **Third Task (@task-process-solutions):**
      - Input: JSON object from previous task
      - Execute: @task-process-solutions solutions_json={{previous_output}} repo_name={{repo_name}}
      - Output: summary of processed solutions
      - Mark success/fail in repo-results.md and repo-results.csv

   4. **Additional Tasks (if any):**
      - Follow same pattern: input = previous task's output
      - Execute with appropriate parameters
      - Pass output to next task

- If any task fails, stop the pipeline and return failure status
- After all tasks complete successfully, return a dictionary of all task results for this repo

Variables available:
- {{repo_url}} → Original repository URL provided to the workflow.
- {{clone_path}} → Root folder where repositories are cloned.
- {{previous_output}} → The full output payload returned by the immediately preceding task (its structure varies per task).
- {{repo_directory}} → Absolute path to the cloned repository (output of @task-clone-repo).
- {{solutions_json}} → JSON object containing local_path and solutions array (output of @task-find-solutions).
- {{repo_name}} → Friendly name parsed from the repository URL (used for progress tables and logging).

Output Contract (aggregate after pipeline completion):
- repo_name: string
- repo_directory: string
- solutions_discovered: integer
- solutions_processed_success: integer
- solutions_processed_fail: integer
- pipeline_status: SUCCESS | FAIL

Implementation Notes (conceptual):
1. Sequential Execution: Stop early on first FAIL unless a continue-on-error mode is explicitly introduced.
2. Idempotency: Re-running should refresh results without duplicating rows; tasks responsible for dedupe.
3. Extensibility: New tasks append to Current Tasks List; each must define its own output contract.
4. Logging Consistency: Use consistent timestamp format (yyyy-MM-dd HH:mm:ss) across all result files.
