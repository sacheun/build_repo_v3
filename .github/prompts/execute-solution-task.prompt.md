@execute-solution-task solution_checklist=<required>

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
Required parameter:
   solution_checklist = <required> (path to a single solution checklist markdown file, e.g., `./tasks/ic3_spool_cosine-dep-spool_SDKTestApp_solution_checklist.md`)

Verify the `solution_checklist` file exists; if missing → execution_status="FAIL".

### Step 1: Read Solution Task Checklist and Find Next Unmarked Task (MANDATORY)
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
1. Invoke the task prompt with required parameters (e.g., @task-restore-solution)

2. Capture task output (status, result data)

3. **If task execution fails:**
   - Log failure using @task-update-decision-log with status: FAIL and error message
   - Stop processing remaining tasks in the checklist
   - Return execution_status: FAIL with error details

4. **If task execution is blocked:**
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

### End of Steps

Variables available:
- {{solution_checklist}} → Path to solution checklist markdown file (from solution_checklist= parameter - required)

## Output Contract (JSON object returned):
- execution_status: "ALL_TASKS_COMPLETE" | "FAIL" | "BLOCKED" (overall run outcome)
- status: "SUCCESS" | "FAIL" (contract emission status; FAIL only if serialization/validation failed independent of task outcomes)
- solution_name: string (derived from checklist header)
- solution_checklist_path: string (absolute or workspace-relative path used for processing)
- timestamp: string (ISO 8601 UTC time when summary emitted)
- tasks_total: integer (total tasks discovered in the checklist section at start of run)
- total_tasks_executed: integer (number of tasks processed during this invocation; equals length of tasks_executed)
- tasks_success: integer (count of tasks_executed entries with task_status=="SUCCESS")
- tasks_failed: integer (count with task_status=="FAIL")
- tasks_blocked: integer (count with task_status=="BLOCKED")
- tasks_skipped: integer (count with task_status=="SKIPPED")
- failed_task: string | null (task_name of first failed task, else null)
- blocking_reason: string | null (present only when execution_status=="BLOCKED")
- error_message: string | null (high-level failure description when execution_status=="FAIL")
- mode: "SEQUENTIAL" (static identifier for execution model)
- verification_errors: array of strings (empty if contract passes internal consistency checks)
- tasks_executed: array<object> (ordered by execution) where each object contains:
   - solution_name: string
   - task_name: string
   - execution_time: string (ISO 8601 timestamp per task completion)
   - task_status: "SUCCESS" | "FAIL" | "BLOCKED" | "SKIPPED"
   - result_data: object (task-specific output payload; MUST omit large raw file contents, include artifact paths instead)

## Implementation Notes:
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