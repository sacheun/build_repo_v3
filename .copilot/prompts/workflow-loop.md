@workflow-loop input=<optional> clone=<optional> clean_results=<optional>

Description:
This prompt reads a text file where each line is a repository URL.
For each line, it executes a list of tasks defined in the `@tasks` prompt.
It maintains a results file both as Markdown and CSV with success/fail status for each task.

Behavior:
1. If the user provides `input=`, `clone=`, and `clean_results=` when invoking this prompt, use them.
   Defaults:
      input = "repositories.txt"
      clone = "./cloned"
      clean_results = true
2. If clean_results is true (default):
      - Remove all files in results/ directory to start from scratch
3. Ensure the clone directory exists; create if it does not.

3. Create and initialize a repository progress markdown file:
      - results/repo-progress.md (Repository Progress tracking table)
      - Parse all repository URLs from input file to get friendly repo names
      - Parse repo_tasks_list.md to get all task names
      - Create table with repo names as rows and task names as columns
      - Initialize all cells with [ ] (empty checkboxes)

4. Initialize results files:
      - results/repo-results.md (Repository Markdown table)
      - results/repo-results.csv (Repository CSV table)
    
5. Read the text file line by line:
   For each line (repo_url):
      - Extract a friendly repo_name
      - Call `@tasks-list` with repo_url and clone_path
      - Append success/fail for each task to Markdown + CSV
6. After all lines are processed, return a summary message.

Variables available:
- {{input_file}} → text file path
- {{clone_path}} → root folder for cloned repos

Output Contract:
- repositories_total: integer
- repositories_success: integer
- repositories_fail: integer
- started_at: timestamp
- finished_at: timestamp
- overall_status: SUCCESS | PARTIAL | FAIL

Implementation Notes (conceptual):
1. Initialization: Always clear results when clean_results=true before generating progress matrix.
2. Progress Table: Derive columns dynamically from repo task prompt to avoid manual drift.
3. Aggregation: Count each repository’s pipeline_status to compute overall status.
4. Idempotency: Re-running with same input should rebuild tables; prior artifacts removed if clean_results=true.
5. Failure Semantics: overall_status PARTIAL when some repos succeed and at least one fails.
