@execute-repo-task clone=<required> clean_results=<optional>
---
temperature: 0.1
---

Description:
This prompt acts as an autonomous task executor that reads task checklists and executes tasks in a continuous loop.
It processes ALL uncompleted tasks across ALL repositories until everything is complete or an error occurs.

**CRITICAL - SEQUENTIAL EXECUTION REQUIREMENT:**
- Tasks MUST be executed in STRICT SEQUENTIAL ORDER as they appear in the checklist
- DO NOT skip CONDITIONAL tasks to prioritize MANDATORY tasks
- DO NOT execute tasks out of order under any circumstances
- Process each task in sequence: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6
- **CONDITIONAL tasks are NOT SKIPPABLE - they MUST EXECUTE when their condition is met**
- If a CONDITIONAL task's condition is met, it is MANDATORY to EXECUTE it before proceeding
- If a CONDITIONAL task's condition is NOT met, mark it SKIPPED and proceed to next task
- The MANDATORY vs CONDITIONAL labels indicate when to execute, NOT whether to execute
- Always execute the FIRST uncompleted [ ] task in the checklist, regardless of its label

**CONDITIONAL Task Execution Rules:**
- CONDITIONAL means "execute IF condition is met"
- When condition is TRUE → Task becomes MANDATORY and MUST be executed
- When condition is FALSE → Task is SKIPPED (mark as [x] SKIPPED)
- Example: "@task-scan-readme" is CONDITIONAL on readme_content existing
  - If readme_content exists → MUST execute @task-scan-readme
  - If readme_content does NOT exist → Mark as [x] SKIPPED, move to next task
- Never skip a CONDITIONAL task when its condition is satisfied

**CRITICAL: This prompt runs in a continuous loop. After completing each task, it immediately:**
1. Updates the repository checklist (marking task as [x])
2. Updates the Task Variables section with output from the completed task
3. Finds the next uncompleted task
4. Executes the next task
5. Repeats until all repositories and all tasks are complete

**The loop only stops when:**
- All repositories are marked [x] in all_repository_checklist.md
- A task fails (status: FAIL)
- A task is blocked due to missing dependencies (status: BLOCKED)

Behavior:

**Step 0: Initialize Parameters and Start Loop**
1. If the user provides `clone=` and `clean_results=` when invoking this prompt, use them.
   Requirements:
      clone = <required> (must be provided by user)
      clean_results = false (default if not provided)
2. If clean_results is true:
      - Remove all files in results/ directory to start from scratch
      - Remove all files in output/ directory to start from scratch
      - Remove all files in temp-script/ directory to start from scratch
      - **WARNING**: This will erase all task execution history and outputs
3. Ensure the clone directory exists; create if it does not.
4. Store clone_path value for use in task parameter preparation (Step 3)
5. **Initialize loop counter and tracking:**
   - tasks_executed_count = 0
   - repositories_completed_count = 0
   - execution_start_time = current timestamp
6. **BEGIN CONTINUOUS LOOP** - Repeat Steps 1-9 until all repositories complete or error occurs

**Step 1: Read Master Repository Checklist**
1. Read ./tasks/all_repository_checklist.md
2. Parse the "## Repositories" section
3. Find the first repository with `- [ ]` (uncompleted)
4. Extract repo_name and repo_url from that line
5. **If all repositories are marked `- [x]`:**
   - Set executor_status: ALL_COMPLETE
   - Log final summary to decision-log.csv: "All repositories completed. Total tasks executed: {tasks_executed_count}"
   - **EXIT LOOP** and proceed to Step 9 (Return Execution Summary)

**Step 2: Read Repository Task Checklist**
1. Read ./tasks/{repo_name}_repo_checklist.md
2. Parse the "## Tasks (Sequential Pipeline - Complete in Order)" section
3. Find the first task with `- [ ]` (uncompleted)
4. Extract task_name from that line (e.g., "@task-clone-repo")
5. **Read existing "## Task Variables" section (if it exists)**:
   - Parse all variable values from previous task executions
   - Store these values for use in task parameter preparation
   - This allows resuming work from a previous run with all context preserved

**CRITICAL - SEQUENTIAL EXECUTION REQUIREMENT:**
- **Tasks MUST be completed in the EXACT order they appear in the checklist**
- **DO NOT skip CONDITIONAL tasks to prioritize MANDATORY tasks**
- **DO NOT execute tasks out of order, even if they are marked MANDATORY**
- The sequence is: Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6
- If a task is CONDITIONAL and its condition is met, it MUST be executed before moving to the next task
- If a task is CONDITIONAL and its condition is NOT met, mark it as SKIPPED and move to the next task
- Example sequence for ic3_spool_cosine-dep-spool:
  1. [MANDATORY #1] @task-clone-repo ✅ Execute
  2. [MANDATORY #2] @task-search-readme ✅ Execute
  3. [CONDITIONAL] @task-scan-readme ✅ Execute (condition met: readme_content exists)
  4. [CONDITIONAL] @task-execute-readme ✅ Execute (condition met: commands_extracted exists)
  5. [MANDATORY #3] @task-find-solutions ✅ Execute (only after tasks 1-4 complete)
  6. [MANDATORY #4] @generate-solution-task-checklists ✅ Execute (only after tasks 1-5 complete)

**Step 3: Prepare Task Parameters**

- Extract task_name (e.g., "@task-clone-repo")
- **Prepare parameters using variables from checklist first**:
  - @task-clone-repo: 
    - repo_url: From checklist variables OR from all_repository_checklist.md
    - clone_path: From checklist variables OR from clone= parameter (required)
  - @task-search-readme: 
    - repo_directory: **Read from checklist variables** (set by @task-clone-repo)
    - repo_name: From checklist variables
  - @task-scan-readme: 
    - repo_directory: **Read from checklist variables**
    - repo_name: From checklist variables
    - readme_content_path: **Read from checklist variables** (set by @task-search-readme)
  - @task-execute-readme: 
    - repo_directory: **Read from checklist variables**
    - repo_name: From checklist variables
    - commands_json_path: **Read from checklist variables** (set by @task-scan-readme)
  - @task-find-solutions: 
    - repo_directory: **Read from checklist variables**
  - @generate-solution-task-checklists:
    - repo_name: From checklist variables
    - solutions: **Read from checklist variables** (reference to solutions_json file, extract solutions array)

**Step 4: Gather Required Input Data**

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
- Return status: BLOCKED with error message indicating missing dependency
- Example: "Cannot execute @task-search-readme: Variable 'repo_directory' not set (previous task @task-clone-repo not completed)"

**Step 5: Execute the Task**
1. Log the execution attempt to results/decision-log.csv:
   - Timestamp: ISO 8601 format
   - Repo Name: {repo_name}
   - Solution Name: (empty for repo-level tasks)
   - Task: {task_name}
   - Message: "Starting task execution (loop iteration {tasks_executed_count + 1})"
   - Status: "IN_PROGRESS"

2. Invoke the task prompt with required parameters (e.g., @task-clone-repo)

3. Capture task output (status, result data)

4. **If task execution fails:**
   - Log failure to decision-log.csv with status: FAIL
   - Set executor_status: FAIL
   - **EXIT LOOP** and proceed to Step 9 (Return Execution Summary with error details)

5. **If task execution is blocked:**
   - Log blocked status to decision-log.csv
   - Set executor_status: BLOCKED
   - **EXIT LOOP** and proceed to Step 9 (Return Execution Summary with blocking reason)

6. Increment tasks_executed_count by 1

**Step 6: Update Checklists and Save Variables**
1. If task completed successfully, update the repository checklist file directly:
   - Read ./tasks/{repo_name}_repo_checklist.md
   - Find the task line matching {task_name} in "## Repo Tasks" section
   - Replace `- [ ]` with `- [x]` for that specific task
   - Write the updated content back to the file
   
2. Extract and save task output variables to repository checklist:
   - **Parse repo_tasks_list.md to get list of all available variables**:
     - Read the "Variables available:" section
     - Extract all variable names (e.g., {{repo_url}}, {{repo_directory}}, {{readme_content}}, etc.)
   - Read task output data from execution result
   - **Read existing checklist "## Task Variables" section to preserve previous values**
   - Update/add new variables based on which task was executed:
     - @task-clone-repo → Sets: repo_directory
     - @task-search-readme → Sets: readme_content (reference to JSON file path), readme_filename
     - @task-scan-readme → Sets: commands_extracted (reference to JSON file path or count)
     - @task-execute-readme → Sets: executed_commands (count), skipped_commands (count)
     - @task-find-solutions → Sets: solutions_json (reference to JSON file path)
     - @generate-solution-task-checklists → Sets: checklist_updated (boolean indicating solution sections added)
   - **Preserve all existing variable values** from previous tasks
   - **Only update variables that this task produces**
   
3. Update repository checklist with variable values:
   - Read ./tasks/{repo_name}_repo_checklist.md (if not already read in step 1)
   - Find or create "## Task Variables" section
     * If section doesn't exist, add it after "## Repo Variables Available" section
     * If section exists, update it while preserving previous variables
   - For each variable from completed tasks, write the appropriate value:
   
   **Variable Writing Rules:**
   - After @task-clone-repo completes:
     * Write `repo_url`: {repo_url}
     * Write `clone_path`: {clone_path}
     * Write `repo_directory`: {absolute_path} (e.g., "C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool")
     * Write `repo_name`: {repo_name}
   
   - After @task-search-readme completes:
     * Write `readme_content_path`: "output/{repo_name}_task2_search-readme.json"
     * Write `readme_filename`: {actual_filename} (e.g., "README.md")
     * If status is NOT_FOUND (no README found), write `readme_filename`: "NONE"
   
   - After @task-scan-readme completes:
     * Write `commands_json_path`: "output/{repo_name}_task3_scan-readme.json"
     * Write `commands_extracted`: "{count} commands" or "NONE (0 commands - {reason})"
   
   - After @task-execute-readme completes:
     * Write `executed_commands`: "SKIPPED (0 commands executed - {reason})" or "{count} commands executed"
     * Write `skipped_commands`: "SKIPPED (0 commands skipped - {reason})" or "{count} commands skipped"
   
   - After @task-find-solutions completes:
     * Write `solutions_json`: "output/{repo_name}_task5_find-solutions.json ({count} solutions found)"
   
   Format of Task Variables section:
     ```
     ## Task Variables
     
     Variables from completed tasks (for resuming work):
     
     - `repo_url`: {repo_url}
     - `clone_path`: {clone_path}
     - `repo_directory`: {absolute_path_to_cloned_repo}
     - `repo_name`: {repo_name}
     - `readme_content_path`: {path_to_json_file}
     - `readme_filename`: {filename}
     - `commands_json_path`: {path_to_json_file}
     - `commands_extracted`: {description}
     - `executed_commands`: {description}
     - `skipped_commands`: {description}
     - `solutions_json`: {path_and_count}
     
     **Note:** Large content (readme_content_path, commands_json_path, solutions_json) is stored in ./output/ directory.
     File paths and counts are shown here for quick reference.
     When executing tasks, use these paths to construct the required parameters:
     - For @task-scan-readme: Pass readme_content_path value (e.g., "output/{repo_name}_task2_search-readme.json")
     - For @task-execute-readme: Pass commands_json_path value (e.g., "output/{repo_name}_task3_scan-readme.json")
     ```
   - For large data (readme_content, solutions_json), reference the JSON file path instead of embedding full content
   - For simple values (paths, counts, filenames), embed directly in checklist
   - **Important**: Only include variables for tasks that have been completed
   - Write the updated checklist content back to the file
   
2. Log completion to results/decision-log.csv:
   - Timestamp: ISO 8601 format
   - Repo Name: {repo_name}
   - Solution Name: (empty for repo-level tasks)
   - Task: {task_name}
   - Message: Task result message
   - Status: "SUCCESS" or "FAIL"

3. Save task output to ./output/ directory (if task produces JSON output):
   - Filename: {repo_name}_{task_name}.json

**Step 7: Check Completion Status**
1. After updating checklist, check completion levels:
   - If all tasks for current solution are complete, log milestone
   - **If all repository tasks are complete (all tasks marked [x] in repo checklist):**
     a. Read ./tasks/all_repository_checklist.md
     b. Find the line for current repository
     c. Update checkbox from `- [ ]` to `- [x]` for this repository
     d. Write updated content back to all_repository_checklist.md
     e. Log milestone to decision-log.csv: "{repo_name} - All tasks completed"
     f. Increment repositories_completed_count by 1
   - If all repositories are complete, log final completion

**Step 8: Continue Loop**
1. **Print progress update:**
   - "✓ Task {task_name} completed for {repo_name}"
   - "→ Progress: {tasks_executed_count} tasks executed, {repositories_completed_count} repositories completed"

2. **LOOP BACK to Step 1** to find and execute the next task
   - The loop continues automatically
   - No user intervention required
   - Processes all tasks for all repositories sequentially

**Step 9: Return Execution Summary**

**This step is only reached when:**
- All repositories are complete (executor_status: ALL_COMPLETE), OR
- A task failed (executor_status: FAIL), OR  
- A task is blocked (executor_status: BLOCKED)

Return final summary with complete execution history.

Variables available:
- {{tasks_dir}} → Directory where checklists are saved (./tasks)
- {{output_dir}} → Directory where task outputs are saved (./output)
- {{results_dir}} → Directory where results and logs are saved (./results)
- {{clone_path}} → Root folder for cloned repositories (from clone= parameter - required)
- {{clean_results}} → Whether to clean results/output/temp-script directories (from clean_results= parameter or default "false")

Output Contract:
- executor_status: "ALL_COMPLETE" | "FAIL" | "BLOCKED"
- loop_execution_summary: object
  - tasks_executed_count: integer (total tasks completed in this run)
  - repositories_completed_count: integer (repositories marked [x] during this run)
  - execution_start_time: timestamp
  - execution_end_time: timestamp
  - total_duration_seconds: integer
- last_completed_task: object
  - repo_name: string
  - task_name: string
  - task_status: "SUCCESS" | "FAIL"
- blocking_reason: string | null (if executor_status == BLOCKED)
- error_message: string | null (if executor_status == FAIL)
- error_task: string | null (task name that failed, if executor_status == FAIL)
- completion_progress: object
  - total_repos: integer
  - completed_repos: integer (cumulative - includes previously completed)
  - remaining_repos: integer
- status: SUCCESS | FAIL

Special Cases:

**Case 1: First task for a repository (@task-clone-repo)**
- Use repo_url from master checklist
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
- Example workflow for @task-scan-readme:
  1. Check checklist variables for `repo_directory`
  2. Value found: `C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool`
  3. Check checklist variables for `readme_content_path`
  4. Value found: `output/ic3_spool_cosine-dep-spool_task2_search-readme.json`
  5. Execute: @task-scan-readme repo_directory="C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool" repo_name="ic3_spool_cosine-dep-spool" readme_content_path="output/ic3_spool_cosine-dep-spool_task2_search-readme.json"

**Case 3: All tasks complete**
- Return executor_status: ALL_COMPLETE
- Log final summary to decision-log.csv
- No further action needed

Implementation Notes:
1. **Continuous Loop Execution**: The prompt runs in a loop, executing tasks sequentially until all repositories are complete
2. **Automatic Progression**: After each task completes, immediately proceeds to next task without user intervention
3. **Idempotent Execution**: If interrupted and re-run, it resumes from the next uncompleted task by reading checklist state
4. **Task Dependencies**: Validates required inputs before execution to avoid partial failures
5. **Error Handling**: Any task failure stops the loop and returns FAIL status with error details
6. **Checkpoint Recovery**: All task completions are immediately written to checklists, enabling resume at any point
7. **Output Persistence**: Save task outputs to ./output/ for use by subsequent tasks
8. **Variable Tracking**: Update "## Task Variables" section in repo checklist after each task
9. **Variable Resolution**: Check checklist first for quick variable access before reading JSON files
10. **Progress Visibility**: Log execution attempts and results for monitoring, print progress after each task
11. **Sequential Execution**: Always execute tasks in order (MANDATORY #1, #2, #3, #4...)
12. **Programming Language**: All code generated should be written in Python
13. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory
14. **Loop Termination**: Only stops when ALL_COMPLETE, FAIL, or BLOCKED - ensures maximum progress before stopping

Execution Flow Example:
```
INITIALIZATION:
  - Clone path: ./cloned
  - Clean results: false
  - Tasks executed count: 0
  - Repositories completed: 0
  - Start time: 2025-10-23T10:00:00Z

LOOP ITERATION 1:
  - Read all_repository_checklist.md → Find "repo1" uncompleted
  - Read repo1_repo_checklist.md → Find "@task-clone-repo" uncompleted
  - Execute @task-clone-repo → SUCCESS
  - Update checklist: Mark @task-clone-repo as [x]
  - Update Task Variables: repo_directory = C:\cloned\repo1
  - Save output: ./output/repo1_task-clone-repo.json
  - Tasks executed: 1
  - Print: "✓ Task @task-clone-repo completed for repo1"
  - LOOP BACK to Step 1

LOOP ITERATION 2:
  - Read all_repository_checklist.md → Find "repo1" still uncompleted
  - Read repo1_repo_checklist.md → Find "@task-search-readme" uncompleted
  - Load repo_directory from checklist Task Variables
  - Execute @task-search-readme → SUCCESS
  - Update checklist: Mark @task-search-readme as [x]
  - Update Task Variables: readme_content = [saved to ./output/...]
  - Save output: ./output/repo1_task-search-readme.json
  - Tasks executed: 2
  - Print: "✓ Task @task-search-readme completed for repo1"
  - LOOP BACK to Step 1

... (loop continues for all repo1 tasks)

LOOP ITERATION N-1:
  - Read all_repository_checklist.md → Find "repo1" still uncompleted
  - Read repo1_repo_checklist.md → Find "@generate-solution-task-checklists" uncompleted
  - Load solutions_json from checklist Task Variables
  - Execute @generate-solution-task-checklists → SUCCESS
  - Update checklist: Mark @generate-solution-task-checklists as [x]
  - Update Task Variables: checklist_updated = true
  - Repository checklist now has solution-specific task sections
  - **ALL tasks in repo1 are now [x]**
  - **Update all_repository_checklist.md: Mark repo1 as [x]**
  - Log: "repo1 - All tasks completed"
  - Repositories completed: 1
  - Tasks executed: 6
  - Print: "✓ Repository repo1 completed!"
  - LOOP BACK to Step 1

LOOP ITERATION N+1:
  - Read all_repository_checklist.md → Find "repo2" uncompleted
  - Read repo2_repo_checklist.md → Find "@task-clone-repo" uncompleted
  - Execute @task-clone-repo for repo2 → SUCCESS
  - Update checklist: Mark @task-clone-repo as [x]
  - Tasks executed: 7
  - Print: "✓ Task @task-clone-repo completed for repo2"
  - LOOP BACK to Step 1

... (loop continues for all repo2 tasks, then repo3, etc.)

FINAL LOOP ITERATION:
  - Read all_repository_checklist.md → ALL repos marked [x]
  - Executor status: ALL_COMPLETE
  - Log: "All repositories completed. Total tasks executed: 18"
  - End time: 2025-10-23T10:45:30Z
  - EXIT LOOP → Proceed to Step 9

RETURN SUMMARY:
  - executor_status: ALL_COMPLETE
  - tasks_executed_count: 18
  - repositories_completed_count: 3
  - total_duration_seconds: 2730
  - status: SUCCESS
```

**Key Differences from Single-Task Execution:**
- ✅ **Runs continuously** - No manual intervention between tasks
- ✅ **Auto-progresses** - Automatically moves from task to task, repo to repo
- ✅ **Checkpoints preserved** - Every task completion updates checklist immediately
- ✅ **Resumable** - If interrupted, next run picks up from first uncompleted task
- ✅ **Complete execution** - Processes all repositories in one invocation
- ✅ **Progress tracking** - Prints updates after each task for visibility

**Error Recovery:**
If the executor is interrupted (Ctrl+C, crash, etc.):
1. All completed tasks are marked [x] in checklists
2. All task variables are saved for completed tasks
3. Re-running @execute-task will resume from the first uncompleted task
4. No work is lost - resumes exactly where it stopped

This prompt enables fully autonomous, resumable task execution with complete traceability and checkpoint recovery.
