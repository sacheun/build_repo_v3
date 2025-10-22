@task-process-solutions solutions_json={{solutions_json}} repo_name={{repo_name}}

Task name: task-process-solutions

Description:
This task takes a JSON object returned by task-find-solutions.md and processes each solution file found.
For each solution, it executes a list of tasks to perform operations on the solution.

Behavior:
0. DEBUG Entry Trace: If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   "[debug][task-process-solutions] START processing {{total_solutions}} solutions"
   This line precedes all other task operations.

1. Parse the input JSON object from {{solutions_json}} which contains:
   - local_path: repository directory path
   - solutions: array of absolute paths to .sln files

2. Load solution task list definition:
   - Read `solution_tasks_list.md`
   - Extract ordered task directives of the form `@task-<name> key=value ...`
   - Build an in-memory pipeline array preserving order

3. **For each solution file in the solutions array (process one solution completely before moving to the next)**:
   a. Derive solution_name from the file name (e.g., MyApp.sln → MyApp)
   b. Initialize a per-solution context object with: solution_path, solution_name
   c. If environment variable DEBUG=1 emit a debug line: `[debug][task-process-solutions] starting pipeline for solution='MyApp' path='C:\full\path\MyApp.sln'`
   d. **Execute ALL tasks from solution_tasks_list sequentially for this solution**:
      - For each task directive in solution_tasks_list (in order):
        i. Substitute placeholders (e.g., {{solution_path}}, {{solution_name}})
        ii. **Run the task synchronously and wait for completion** before proceeding to the next task
        iii. **CRITICAL**: After the task completes, capture its exit code/status (e.g., `$LASTEXITCODE` in PowerShell, `$?` in Bash)
        iv. **Check the exit code** to determine if the task succeeded or failed
        v. Update the corresponding task column in solution-progress.md ([ ] → [x] for success) - use {{repo_name}} to locate the correct row
        vi. Append task result to solution-results.md and solution-results.csv - include {{repo_name}} in the Repository column
        vii. Merge returned fields into the per-solution context
   e. **After ALL tasks complete for this solution**, accumulate the solution's overall status into aggregate counts
   f. **IMPORTANT**: Only after finishing all tasks for the current solution, move to the next solution in the array and repeat steps a-e

4. Create and initialize a solution progress markdown file:
      - results/solution-progress.md (Solution Progress tracking table)
      - Parse solution_tasks_list.md to extract ALL task directive names (e.g., @task-restore-solution, @task-build-solution, etc.)
      - Get all the solution names from the solution array
      - Create table with columns: Repository | Solution | task-restore-solution | task-build-solution | [additional tasks...]
      - **IMPORTANT**: Include a column for EVERY task found in solution_tasks_list.md, not just restore
      - **Repository Column**: Fill in the Repository column for each row with the value from the {{repo_name}} input argument passed to this prompt
      - Initialize all task cells with [ ] (empty checkboxes)
      - Example header: `| Repository | Solution | task-restore-solution | task-build-solution |`
      - Example row: `| ic3_spool_cosine-dep-spool | ResourceProvider | [ ] | [ ] |`

5. Initialize solution tracking artifacts if not present:
      - results/solution-results.md (Markdown table: Repository | Solution | Task | Status | Timestamp)
      - results/solution-results.csv (CSV with same columns)
      - **Repository Column**: When appending rows to solution-results.md and solution-results.csv, fill in the Repository column with the value from the {{repo_name}} input argument
      - For each solution row initialize task-restore-solution cell with [ ]

6. Track progress for each solution:
   - After successful completion of all tasks for that solution, mark the corresponding checkbox(es)
   - On partial failure do not mark remaining task columns (future multi-task support)

7. Return summary of processed solutions:
   - Total solutions found
   - Successfully processed count
   - Failed processing count

8. DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), emit a final line to stdout (or terminal) after all solutions processed:
   "[debug][task-process-solutions] END total={{total_solutions}} success={{success_count}} fail={{failure_count}}"
   This line marks task completion and provides aggregate status visibility.

Invocation Pattern:
- Repository pipeline calls: `@task-process-solutions solutions_json={{previous_output}} repo_name={{repo_name}}`
- This task internally invokes: `@solution-tasks-list solution_path={{solution_path}}`
- The solution task list expands into concrete task directives actually executed per solution.
- ** Important ** Execute each step individually. Pass the output from one task to the next. Do not create a single monolithic script that runs all tasks at once.


Directive Format (solution task list):
`@task-restore-solution solution_path={{solution_path}}`
Additional tasks can be appended following the same pattern. Each task must define its own Output Contract.

Output Contract:
- total_solutions: integer
- success_count: integer
- failure_count: integer
- processed: array[object] each { solution_name, solution_path, restore_status }
- overall_status: SUCCESS | FAIL

Implementation Notes (conceptual):
1. Initialization: Create tracking artifacts only if absent to allow incremental runs.
2. Idempotency: Avoid duplicate rows by checking existing entries before append; only transition [ ] → [x] once.
3. Failure Strategy: Continue processing remaining solutions after a failure; overall_status reflects aggregate.
4. Extensibility: Multi-task support relies on solution_tasks_list ordering; add new directives without changing this file.
5. Logging Order per solution: a) parse name b) execute each directive c) record per-task status d) update progress e) append final context.
6. Separation of Concerns: This file orchestrates; individual task prompts define actionable behavior.
7. DEBUG Entry: When DEBUG=1 emit START line before step 1 with total solution count.
8. DEBUG Per-Solution: In step 3, emit per-solution start line before executing directives: `[debug][task-process-solutions] starting pipeline for solution='<solution_name>' path='<solution_path>'`
9. DEBUG Exit: After step 6 (summary), emit END line with aggregate counts (total, success, fail).
10. Debug Line Format: All debug lines prefixed `[debug][task-process-solutions]` (greppable, no color codes).
11. **Synchronous Task Execution**: Each task directive must complete before the next one starts. Use synchronous execution (NOT background jobs). In PowerShell: `& task-command ; $exitCode = $LASTEXITCODE`. In Bash: `task-command ; exitCode=$?`.
12. **Exit Code Checking**: After each task completes, immediately check its exit code to determine success/failure. Use this for aggregate counting (success_count vs failure_count) and for deciding whether to continue or skip remaining tasks.

Variables available:
- {{solutions_json}} → Raw JSON input containing local_path and solutions array
- {{local_path}} → Repository directory extracted from solutions_json
- {{solution_path}} → Absolute path of current solution being processed
- {{solution_name}} → Friendly name of current solution file
- {{repo_name}} → Friendly repository name (passed as input argument from caller)
- {{solution_task_output}} → Output returned by @solution-tasks-list for the current solution