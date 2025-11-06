@execute-solution-task solution_checklist=<required>

---
temperature: 0.0
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
Required parameter:
   solution_checklist = <required> (path to a single solution checklist markdown file, e.g., `./tasks/ic3_spool_cosine-dep-spool_SDKTestApp_solution_checklist.md`)

Initialization:
1. Verify the `solution_checklist` file exists; if missing → execution_status="FAIL".
2. **[MANDATORY] Initialize solution_result.csv tracking file:**
    - Check if file `results/solution_result.csv` exists
    - If it does NOT exist, create it with the following header row using comma (`,`) as the separator:
       ```
       repo,solution,task name,status
       ```

### Step 1: Read Task Checklist and Find Next Unmarked Task (MANDATORY)
1. Read the solution checklist file specified by solution_checklist parameter
2. Parse the "## Tasks (Sequential Pipeline - Complete in Order)" section
3. Find the FIRST task with `- [ ]` (unmarked/uncompleted)
4. If no unmarked tasks found, return status: ALL_TASKS_COMPLETE
5. Extract task_name from that line (e.g., "@task-restore-solution")
7. **Continue to next step to execute this task**

### Step 2: Evaluate Conditions and Execute Task (MANDATORY)
#### 2.1 Pre-Execution Conditional Evaluation
Before logging and invoking any task, FIRST determine if the task line is a CONDITIONAL task (contains the marker `[CONDITIONAL]`).

Step 2.1 actions:
1. If task is NOT conditional → skip to Step 2.2.
2. If task IS conditional → evaluate its condition BEFORE calling the task prompt:

**Conditional Logic by Task Number:**

**CONDITIONAL #3 - Search knowledge base:**
- Condition: {{restore_status}} == FAILED OR {{build_status}} == FAILED
- If TRUE → MUST execute @task-search-knowledge-base
- If FALSE (both succeeded) → Mark as [x] SKIPPED (build succeeded), move to next task

**CONDITIONAL #4 - Create knowledge base article:**
- Condition: {{kb_search_status}} == NOT_FOUND
- If TRUE → MUST execute @task-create-knowledge-base
- If FALSE (KB found) → Mark as [x] SKIPPED (KB found), move to next task

**CONDITIONAL #5 - Attempt 1 - Apply fix from KB:**
- Condition: {{kb_search_status}} == FOUND OR {{kb_article_status}} == CREATED
- If TRUE → MUST execute @task-apply-knowledge-base-fix
- If FALSE → Mark as [x] SKIPPED (build succeeded), move to next task
- Update variable: {{fix_applied_attempt_1}}

**CONDITIONAL #6 - Attempt 1 - Retry build after fix:**
- Condition: {{fix_applied_attempt_1}} == APPLIED
- If TRUE → MUST execute @task-build-solution-retry
- If FALSE → Mark as [x] SKIPPED (no fix applied), move to next task
- Update variable: {{retry_build_status_attempt_1}}

**CONDITIONAL #7 - Attempt 2 - Apply fix from KB:**
- Condition: {{retry_build_status_attempt_1}} == FAILED
- If TRUE → MUST execute @task-apply-knowledge-base-fix (attempt 2)
- If FALSE → Mark as [x] SKIPPED (build succeeded OR no previous retry OR previous retry succeeded), move to next task
- Update variable: {{fix_applied_attempt_2}}

**CONDITIONAL #8 - Attempt 2 - Retry build after fix:**
- Condition: {{fix_applied_attempt_2}} == APPLIED
- If TRUE → MUST execute @task-build-solution-retry
- If FALSE → Mark as [x] SKIPPED (no fix applied), move to next task
- Update variable: {{retry_build_status_attempt_2}}

**CONDITIONAL #9 - Attempt 3 - Apply fix from KB:**
- Condition: {{retry_build_status_attempt_2}} == FAILED
- If TRUE → MUST execute @task-apply-knowledge-base-fix (attempt 3)
- If FALSE → Mark as [x] SKIPPED (build succeeded OR no previous retry OR previous retry succeeded), move to next task
- Update variable: {{fix_applied_attempt_3}}

**CONDITIONAL #10 - Attempt 3 - Retry build after fix:**
- Condition: {{fix_applied_attempt_3}} == APPLIED
- If TRUE → MUST execute @task-build-solution-retry
- If FALSE → Mark as [x] SKIPPED (no fix applied), move to next task
- Update variable: {{retry_build_status_attempt_3}}

   - If condition FALSE:
     - Do NOT invoke the task prompt.
     - Mark checklist line `[x] ... - SKIPPED (condition not met)`.
     - Log decision entry status="SKIPPED" with reason.
     - Append tasks_executed entry task_status="SKIPPED".
     - Return to Step 1 for next unmarked task.
   - If condition TRUE → proceed to Step 2.2.

#### 2.2 Task Invocation Sequence
1. Log the execution attempt using @task-update-decision-log:
   - Invoke: @task-update-decision-log timestamp={current_timestamp} repo_name={repo_name} task={task_name} message="Starting task execution" status="IN_PROGRESS"
   - This appends a row to results/decision-log.csv with execution start details

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

### Step 3: Check for More Tasks and Continue
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
- {{solution_checklist}} → Path to solution checklist markdown file (from solution_checklist= parameter - required)

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

