@task-process-solutions solutions_json={{solutions_json}}

Task name: task-process-solutions

Description:
This task takes a JSON object returned by task-find-solutions.md and processes each solution file found.
For each solution, it executes a list of tasks to perform operations on the solution.

Behavior:
1. Parse the input JSON object from {{solutions_json}} which contains:
   - local_path: repository directory path
   - solutions: array of absolute paths to .sln files

2. For each solution file in the solutions array:
   - Extract solution_name from the solution path (e.g., "C:\path\to\MyApp.sln" → "MyApp")
   - Invoke solution task pipeline:
     * Call `@solution-tasks-list solution_path={{solution_path}}`
   - Capture output from @solution-tasks-list (store as {{solution_task_output}})

3. Initialize solution tracking artifacts if not present:
      - results/solution-progress.md (table: Repository | Solution | task-restore-solution)
      - results/solution-results.md (Markdown table: Repository | Solution | Task | Status | Timestamp)
      - results/solution-results.csv (CSV with same columns)
      - For each solution row initialize task-restore-solution cell with [ ]

4. Track progress for each solution processed:
   - Log processing attempt and @solution-tasks-list status
   - Count successes vs failures

5. On success of task-restore-solution for a solution:
   - Update results/solution-results.* with a row
   - In solution-progress.md set task-restore-solution cell to [x]

6. If any solution fails → overall status = FAIL; continue logging remaining solutions but do not mark [x] for failed ones.
   If all succeed → overall status = SUCCESS

7. Append aggregate summary row (repository-level) to solution-results.* if desired (optional extension).

8. Return summary of processed solutions:
   - Total solutions found
   - Successfully processed count
   - Failed processing count

Output Contract:
- total_solutions: integer
- success_count: integer
- failure_count: integer
- processed: array[object] each { solution_name, solution_path, restore_status }
- overall_status: SUCCESS | FAIL

Implementation Notes (conceptual):
1. Initialization: Create tracking artifacts only if absent to allow incremental runs.
2. Idempotency: Skip adding duplicate result rows; only transition [ ] → [x] once per solution task.
3. Failure Strategy: Continue processing remaining solutions after a failure; overall_status reflects aggregate.
4. Extensibility: Additional per-solution tasks should append fields to each processed item’s object.
5. Logging Order per solution: a) parse name b) invoke pipeline c) record status d) update progress.

Variables available:
- {{solutions_json}} → Raw JSON input containing local_path and solutions array
- {{local_path}} → Repository directory extracted from solutions_json
- {{solution_path}} → Absolute path of current solution being processed
- {{solution_name}} → Friendly name of current solution file
- {{repo_name}} → Friendly repository name derived separately (provided by caller)
- {{solution_task_output}} → Output returned by @solution-tasks-list for the current solution