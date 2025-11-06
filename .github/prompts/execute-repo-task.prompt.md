@execute-repo-task repo_checklist=<required> clone=<required>
---
temperature: 0.0
---

## Description:
This prompt finds all unmarked tasks from a repository checklist markdown file and executes them sequentially.
It processes all uncompleted tasks in the specified checklist until all are complete or an error occurs.


## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
This task MUST be performed using **direct tool calls** and **structural reasoning**:
*STRICT MODE ON**
- All steps are **MANDATORY**.

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

### Step 1: Read Repository Task Checklist and Find Next Unmarked Task (MANDATORY)
1. Read the repository checklist file specified by repo_checklist parameter
2. Parse the "## Repo Tasks (Sequential Pipeline - Complete in Order)" section
3. Find the FIRST task with `- [ ]` (unmarked/uncompleted)
4. If no unmarked tasks found, return status: ALL_TASKS_COMPLETE
5. Extract task_name from that line (e.g., "@task-clone-repo")
6. Extract repo_name from checklist header (e.g., "# Task Checklist: {repo_name}")
7. **Continue to next step to execute this task**

### Step 2: Evaluate Conditions and Execute Task (MANDATORY)
#### 2.1 Pre-Execution Conditional Evaluation
Before logging and invoking any task, FIRST determine if the task line is a CONDITIONAL task (contains the marker `[CONDITIONAL]`).

Step 2.1 actions:
1. If task is NOT conditional → skip to Step 2.2.
2. If task IS conditional → evaluate its condition BEFORE calling the task prompt:
    - Locate the `**Quick Reference:**` section in the repo checklist and use its stated condition rules (e.g., readme_content not blank and not "NONE" for `@task-scan-readme`). Treat this checklist section as the authoritative source; do not invent or alter conditions.
    - Read previously populated repo variables ("## Task Variables" or "## Repo Variables Available" section) and any artifact JSONs needed for condition evaluation.
    - Explicit examples (must align with Quick Reference):
       - `@task-scan-readme` executes ONLY if `{{readme_content}}` exists, is non-blank, and not equal to "NONE".
       - `@task-execute-readme` executes ONLY if `{{commands_extracted}}` exists, is non-blank, and not equal to "NONE".
    - If condition FALSE:
       - Do NOT invoke the task prompt.
       - Mark checklist line `[x] ... - SKIPPED (condition not met)`.
       - Log decision entry status="SKIPPED" with reason (include evaluated variable name and its value).
       - Append tasks_executed entry task_status="SKIPPED".
       - Return to Step 1 for next unmarked task.
    - If condition TRUE → proceed to Step 2.2 (log the variable values that satisfied the condition if DEBUG=1).

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

### Step 4: Return Final Execution Summary

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
