@execute-repo-task repo_checklist=<required> clone=<required>
---
temperature: 0.1
---

## Description:
This prompt finds all unmarked tasks from a repository checklist markdown file and executes them sequentially.
It processes all uncompleted tasks in the specified checklist until all are complete or an error occurs.

## Execution Policy
**CRITICAL REQUIREMENT:** After completing a task, you must update the designated repository markdown file by changing the task status from "[ ]" to "[x]" to reflect completion.

**CRITICAL - SEQUENTIAL EXECUTION:**
- This prompt executes ALL unmarked [ ] tasks in the checklist sequentially
- Tasks are executed in the order they appear in the checklist
- CONDITIONAL tasks execute when their condition is met, otherwise marked as SKIPPED
- Processing continues until all tasks are complete or a failure/blocking occurs

**CONDITIONAL Task Execution Rules:**
- CONDITIONAL means "execute IF condition is met"
- When condition is TRUE → Task is executed
- When condition is FALSE → Task is SKIPPED (mark as [x] SKIPPED)
- Example: "@task-scan-readme" is CONDITIONAL on readme_content existing
  - If readme_content exists → Execute @task-scan-readme
  - If readme_content does NOT exist → Mark as [x] SKIPPED

## Instructions (Follow this Step by Step)
### Step 0: Initialize Parameters (MANDATORY)
1. Required parameters:
      repo_checklist = <required> (path to repository checklist markdown file, e.g., "./tasks/ic3_spool_cosine-dep-spool_repo_checklist.md")
      clone = <required> (root directory for cloned repositories)
2. Ensure the clone directory exists; create if it does not.
3. **[MANDATORY] Initialize repo_result.csv tracking file:**
   - Check if file `results/repo_result.csv` exists
   - If it does NOT exist, create it with the following header row using comma (`,`) as the separator:
     ```
     repo,task name,status
     ```

### Step 1: Read Repository Task Checklist and Find Next Unmarked Task (MANDATORY)
1. Read the repository checklist file specified by repo_checklist parameter
2. Parse the "## Repo Tasks (Sequential Pipeline - Complete in Order)" section
3. Find the FIRST task with `- [ ]` (unmarked/uncompleted)
4. If no unmarked tasks found, return status: ALL_TASKS_COMPLETE
5. Extract task_name from that line (e.g., "@task-clone-repo")
6. Extract repo_name from checklist header (e.g., "# Task Checklist: {repo_name}")
7. **Read existing "## Task Variables" section (if it exists)**:
   - Parse all variable values from previous task executions
   - Store these values for use in task parameter preparation
8. **Continue to next step to execute this task**

### Step 2: Prepare Task Parameters (MANDATORY)
Extract task_name (e.g., "@task-clone-repo")
- **Prepare parameters using variables from checklist "## Task Variables" section first**:
  - @task-clone-repo: [SCRIPTABLE]
    - repo_url: From checklist variables OR from all_repository_checklist.md
    - clone_path: From checklist variables OR from clone= parameter (required)
  - @task-search-readme: [SCRIPTABLE]
    - repo_directory: **Read from checklist "## Task Variables" section** (must be set by @task-clone-repo)
    - repo_name: From checklist variables
    - **If repo_directory is missing or "NONE"**: BLOCK with error - @task-clone-repo must be completed first
  - @task-scan-readme: [NON-SCRIPTABLE]
    - repo_directory: **Read from checklist "## Task Variables" section**
    - repo_name: From checklist variables
    - readme_content_path: **Read from checklist variables** (set by @task-search-readme)
    - **If repo_directory or readme_content_path is missing**: BLOCK with error
  - @task-execute-readme: [NON-SCRIPTABLE]
    - repo_directory: **Read from checklist "## Task Variables" section**
    - repo_name: From checklist variables
    - commands_json_path: **Read from checklist variables** (set by @task-scan-readme)
    - **If repo_directory or commands_json_path is missing**: BLOCK with error
  - @task-find-solutions: [SCRIPTABLE]
    - repo_directory: **Read from checklist "## Task Variables" section** (must be set by @task-clone-repo)
    - **If repo_directory is missing or "NONE"**: BLOCK with error - @task-clone-repo must be completed first
  - @generate-solution-task-checklists: [SCRIPTABLE]
    - repo_name: From checklist variables
    - solutions: **Read from checklist variables** (reference to solutions_json file, extract solutions array)
    - **If solutions_json is missing**: BLOCK with error - @task-find-solutions must be completed first

### Step 3: Gather Required Input Data (MANDATORY)
For tasks that need output from previous tasks:
- **Primary Source: Check repo checklist "## Task Variables" section** for variable values
  - These values are preserved from previous task executions
  - Enables resuming work after interruption
- **If variable value is a reference to a JSON file** (e.g., "saved to ./output/..."):
  - Extract the file path from the reference
  - Read the JSON file to get the actual data
- **If variable is embedded directly in checklist**, use that value
- **Fallback: Check ./output/ directory** for JSON files (if variable not in checklist)
- Read relevant JSON files to get required input parameters
- Example: @generate-solution-task-checklists needs solutions array:
  1. Check checklist variables for `solutions_json`
  2. Read the JSON file to get the solutions array
  3. Transform array to required format (objects with name and path properties)

**Variable Resolution Priority:**
1. **Check ./tasks/{repo_name}_repo_checklist.md → "## Task Variables" section** (FIRST)
2. **If variable references a JSON file**, read from ./output/{filename}
3. **If variable is not found in checklist**, check ./output/ directory directly (FALLBACK)

**Variable Value Formats:**
- Simple values: Used directly (e.g., `repo_directory`: `C:\cloned\repo`)
- File references: Parse and read (e.g., `readme_content_path`: `output/repo_task2_search-readme.json`)
- Not set: Shows "not set" - task cannot proceed if this variable is required

**How to Use Variables When Executing Tasks:**
- For @task-search-readme: 
  * Read `repo_directory` from checklist variables
  * Pass as parameter: repo_directory={value_from_checklist}

- For @task-scan-readme:
  * Read `repo_directory` from checklist variables
  * Read `readme_content_path` from checklist variables (e.g., "output/repo_task2_search-readme.json")
  * Pass as parameters: repo_directory={value} readme_content_path={value}

- For @task-execute-readme:
  * Read `repo_directory` from checklist variables
  * Read `commands_json_path` from checklist variables (e.g., "output/repo_task3_scan-readme.json")
  * Pass as parameters: repo_directory={value} commands_json_path={value}

**If required input data is missing:**
- Mark the current task as BLOCKED in the checklist
- Log blocked status using @task-update-decision-log: timestamp={current_timestamp} repo_name={repo_name} solution_name="" task={task_name} message={blocking_reason} status="BLOCKED"
- Stop processing remaining tasks in the checklist
- Return execution_status: BLOCKED with error message indicating missing dependency
- Example: "Cannot execute @task-search-readme: Variable 'repo_directory' not set (previous task @task-clone-repo not completed)"

### Step 4: Execute the Task (MANDATORY)
1. Log the execution attempt using @task-update-decision-log:
   - Invoke: @task-update-decision-log timestamp={current_timestamp} repo_name={repo_name} solution_name="" task={task_name} message="Starting task execution" status="IN_PROGRESS"
   - This will append a row to results/decision-log.csv with execution start details

2. Invoke the task prompt with required parameters (e.g., @task-clone-repo)

3. Capture task output (status, result data)

4. **If task execution fails:**
   - Log failure using @task-update-decision-log with status: FAIL and error message
   - Stop processing remaining tasks in the checklist
   - Return execution_status: FAIL with error details

5. **If task execution is blocked:**
   - Log blocked status using @task-update-decision-log with blocking reason
   - Stop processing remaining tasks in the checklist
   - Return execution_status: BLOCKED with blocking reason

### Step 5: Check for More Tasks and Continue
1. After completing the current task, **return to Step 1**
2. Read the checklist again to find the next unmarked task
3. If more unmarked tasks exist, execute them
4. Continue this loop until:
   - All tasks are marked [x] (return ALL_TASKS_COMPLETE)
   - A task fails (return FAIL with error details)
   - A task is blocked (return BLOCKED with blocking reason)

### Step 6: Return Final Execution Summary

Return execution summary after all tasks are processed or execution stops.

Variables available:
- {{tasks_dir}} → Directory where checklists are saved (./tasks)
- {{output_dir}} → Directory where task outputs are saved (./output)
- {{results_dir}} → Directory where results and logs are saved (./results)
- {{clone_path}} → Root folder for cloned repositories (from clone= parameter - required)
- {{repo_checklist}} → Path to repository checklist markdown file (from repo_checklist= parameter - required)

Output Contract:
- execution_status: "ALL_TASKS_COMPLETE" | "FAIL" | "BLOCKED"
- tasks_executed: array of objects
  - repo_name: string
  - task_name: string
  - execution_time: timestamp
  - task_status: "SUCCESS" | "FAIL" | "BLOCKED" | "SKIPPED"
  - result_data: object (task-specific output)
- total_tasks_executed: integer (count of tasks processed in this run)
- blocking_reason: string | null (if execution_status == BLOCKED)
- error_message: string | null (if execution_status == FAIL)
- failed_task: string | null (task name that failed)
- status: SUCCESS | FAIL

Special Cases:

**Case 1: First task for a repository (@task-clone-repo [SCRIPTABLE])**
- Extract repo_url from the repository checklist header section
- Use clone_path from clone= parameter (required)
- After completion, repo_directory will be in task output

**Case 2: Task depends on previous task output**
- **First, check checklist "## Task Variables" section** for the required variable
- If variable is set in checklist:
  - If value is a file path (e.g., readme_content_path, commands_json_path), use directly as parameter
  - If value is embedded, use directly
- If variable is not set in checklist (shows "not set"):
  - Check ./output/{repo_name}_{previous_task}.json as fallback
- If missing from both sources, return BLOCKED status

**Case 3: All tasks complete**
- Return execution_status: ALL_TASKS_COMPLETE
- Log final completion using @task-update-decision-log with appropriate message

Implementation Notes:
1. **Sequential Task Execution**: This prompt executes ALL unmarked tasks sequentially in one run
2. **Continuous Processing**: After completing each task, automatically finds and executes the next unmarked task
3. **Idempotent Execution**: Can be interrupted and re-run - will resume from first uncompleted task
4. **Task Dependencies**: Validates required inputs before execution to avoid partial failures
5. **Error Handling**: Task failures stop execution and return FAIL status with error details
6. **Checkpoint Recovery**: Each task completion is written to checklist immediately, enabling resume at any point
7. **Output Persistence**: Save task outputs to ./output/ for use by subsequent tasks
8. **Variable Tracking**: Update "## Task Variables" section in repo checklist after each task completion
9. **Variable Resolution**: Check checklist first for quick variable access before reading JSON files
10. **Loop Execution**: Continues processing until all tasks complete, a failure occurs, or blocking detected
11. **Programming Language**: All code generated should be written in Python
12. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

**Error Recovery:**
If the executor is interrupted (Ctrl+C, crash, etc.):
1. All completed tasks are marked [x] in checklists
2. All task variables are saved for completed tasks
3. Re-running @execute-task will resume from the first uncompleted task
4. No work is lost - resumes exactly where it stopped

This prompt enables fully autonomous, resumable task execution with complete traceability and checkpoint recovery.
## Error Handling
- Missing required parameter repo_checklist or clone: Immediately return execution_status="FAIL" with error_message.
- Checklist file not found: execution_status="FAIL"; do not create or modify files.
- Unable to parse "## Repo Tasks" section: execution_status="FAIL" with parsing error details.
- Dependency variable missing (e.g., repo_directory for @task-search-readme): Mark task BLOCKED; execution_status="BLOCKED"; blocking_reason explains prerequisite.
- JSON output referenced but unreadable: Treat variable as missing and apply BLOCKED logic.
- Decision log write failure: Retry once; if still failing continue but include warning in error_message field for that task.
- Unexpected exception: Catch, log failed_task and error_message; execution_status="FAIL".

## Consistency Checks
- tasks_executed length MUST equal total_tasks_executed.
- Each tasks_executed entry must have task_status in {SUCCESS, FAIL, BLOCKED, SKIPPED}.
- If execution_status == ALL_TASKS_COMPLETE then no entry task_status == FAIL or BLOCKED.
- If execution_status == BLOCKED then blocking_reason is non-empty and exactly one task_status == BLOCKED.
- If execution_status == FAIL then failed_task is non-empty and at least one task_status == FAIL.
- When a CONDITIONAL task is skipped, checklist line updated to "[x] SKIPPED".

## Cross-References
- {{repo_checklist}} → Path to the repository checklist being processed.
- {{clone_path}} → Root directory for cloned repositories.
- {{tasks_dir}} / {{output_dir}} / {{results_dir}} → Standard workspace directories for state and artifacts.
- {{execution_status}} → Final status summarizing run outcome.
- {{tasks_executed}} → Detailed per-task execution records.
- {{total_tasks_executed}} → Count of tasks processed in this invocation.
- {{failed_task}} → Name of the task that failed (if any).
- {{blocking_reason}} → Dependency or condition that prevented a task from executing.
- {{error_message}} → Error detail for FAIL scenarios.

