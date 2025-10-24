@tasks-list repo_url={{repo_url}} clone_path={{clone_path}}
---
temperature: 0.1
---

Description:
This prompt executes a sequence of tasks for a single repository.
Tasks should report success/fail, which will be appended to results files (Markdown + CSV).

Current Tasks List:
1. @task-clone-repo
2. @task-search-readme
3. @task-scan-readme
4. @task-execute-readme
5. @task-find-solutions
6. @generate-solution-task-checklists
7. @task-process-solutions

Behavior:

** ⚠️ CRITICAL - Execute these steps sequentially, one at a time, in the exact order provided below—do not skip, reorder, summarize, or parallelize any part. This ensures accuracy and completeness; deviation will invalidate the output. ⚠️ **

- Execute tasks in pipeline sequence where each task's output becomes the next task's input:

   1. **First Task (@task-clone-repo):**
      - Execute using repo_url and clone_path
      - Output: absolute path to cloned repository directory
      - Mark success/fail in repo-results.md and repo-results.csv

   2. **Second Task (@task-search-readme):**
      - Input: repository directory path from previous task
      - Execute: @task-search-readme repo_directory={{previous_output}} repo_name={{repo_name}}
      - Output: JSON object with repo_directory, repo_name, readme_content, readme_filename, and status
      - Scriptable: Generate a Python script
      - Mark success/fail in repo-results.md and repo-results.csv

   3. **Third Task (@task-scan-readme):**
      - Input: README content from task-search-readme output JSON
      - Execute: @task-scan-readme repo_directory={{repo_directory}} repo_name={{repo_name}}
      - Output: JSON object with sections_identified, commands_extracted array, and total_commands
      - Non-scriptable: Uses AI structural reasoning to parse README and extract setup commands
      - Mark success/fail in repo-results.md and repo-results.csv

   4. **Fourth Task (@task-execute-readme):**
      - Input: Commands array from task-scan-readme output JSON
      - Execute: @task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}}
      - Output: JSON object with executed_commands and skipped_commands arrays
      - Non-scriptable: Uses AI reasoning to classify command safety and execute safe commands individually
      - Mark success/fail in repo-results.md and repo-results.csv

   5. **Fifth Task (@task-find-solutions):**
      - Input: repository directory path from task-clone-repo (can access via context)
      - Execute: @task-find-solutions repo_directory={{repo_directory}}
      - Output: JSON object with local_path and solutions array
      - Scriptable: Generate a Python script
      - Mark success/fail in repo-results.md and repo-results.csv

   6. **Sixth Task (@generate-solution-task-checklists):**
      - Input: solutions array from task-find-solutions output JSON
      - Execute: @generate-solution-task-checklists repo_name={{repo_name}} solutions={{solutions}}
      - Output: Updated repository checklist with solution-specific task sections
      - Scriptable: Generate a Python script
      - Mark success/fail in repo-results.md and repo-results.csv

   7. **Seventh Task (@task-process-solutions):**
      - Input: JSON object from task-find-solutions
      - Execute: @task-process-solutions solutions_json={{solutions_json}} repo_name={{repo_name}}
      - Output: summary of processed solutions
      - Non-scriptable: Uses AI reasoning to analyze build errors and match KB articles
      - Mark success/fail in repo-results.md and repo-results.csv

- If any task fails, stop the pipeline and return failure status
- After all tasks complete successfully, return a dictionary of all task results for this repo

Variables available:
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

Implementation Notes (conceptual):
1. Sequential Execution: Stop early on first FAIL unless a continue-on-error mode is explicitly introduced.
2. Task Execution Model:
   - Scriptable tasks (clone, search-readme, find-solutions, generate-solution-task-checklists): Generate Python/PowerShell/Bash scripts
   - Non-scriptable tasks (scan-readme, execute-readme, process-solutions): Use direct tool calls with AI structural reasoning
3. Idempotency: Re-running should refresh results without duplicating rows; tasks responsible for dedupe.
4. Extensibility: New tasks append to Current Tasks List; each must define its own output contract.
5. Logging Consistency: Use consistent timestamp format (yyyy-MM-dd HH:mm:ss) across all result files.
