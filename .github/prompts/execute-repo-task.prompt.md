@execute-repo-task repo_checklist=<required> clone=<required>
---
temperature: 0.1
---

## Description:
This prompt finds all unmarked tasks from a repository checklist markdown file and executes them sequentially.
It processes all uncompleted tasks in the specified checklist until all are complete or an error occurs.

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

## Behavior (Follow this Step by Step)

**Step 0: Initialize Parameters**
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

**Step 1: Read Repository Task Checklist and Find Next Unmarked Task**
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

**Step 2: Prepare Task Parameters**
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

**Step 3: Gather Required Input Data**
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

**Step 4: Execute the Task**
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

**Step 5: Update Checklist and Save Variables**

**CRITICAL REQUIREMENT: Only mark tasks as complete [x] when they are ACTUALLY COMPLETE**
- DO NOT mark a task as [x] if you did not execute all required steps
- DO NOT mark a task as [x] if you only created output files without performing the actual work
- DO NOT mark a task as [x] if you skipped execution steps
- Verify that all task requirements were fulfilled before changing `- [ ]` to `- [x]`
- If a task was partially completed or skipped, leave it as `- [ ]` or mark it explicitly as SKIPPED

1. **[MANDATORY] After the task is performed (regardless of success or failure), add 1 row to results/repo_result.csv using comma (`,`) as the separator:**
   - Column 1 (repo): {repo_name}
   - Column 2 (task name): {task_name}
   - Column 3 (status): SUCCESS | FAIL | BLOCKED | SKIPPED
2. **Append the row to the existing CSV file** (do not overwrite the file)
   Example row: `ic3_spool_cosine-dep-spool,@task-clone-repo,SUCCESS`

3. If task completed successfully AND all required work was performed, update the repository checklist file directly:
   - Read ./tasks/{repo_name}_repo_checklist.md
   - Find the task line matching {task_name} in "## Repo Tasks" section
   - **ONLY replace `- [ ]` with `- [x]` if the task was FULLY executed**
   - **If task was skipped or not fully executed, DO NOT mark as [x]**
   - Write the updated content back to the file
   
4. Extract and save task output variables to repository checklist:
   - **Parse repo_tasks_list.prompt.md to get list of all available variables**:
     - Read the "Variables available:" section
     - Extract all variable names (e.g., {{repo_url}}, {{repo_directory}}, {{readme_content}}, etc.)
   - **Read task output data from the JSON output file**:
     - @task-clone-repo [SCRIPTABLE] → Read output/{{repo_name}}_task1_clone.json
       * Extract: repo_directory (absolute path to cloned repo)
     - @task-search-readme [SCRIPTABLE] → Read output/{{repo_name}}_task2_search-readme.json
       * Extract: readme_filename, readme_content_path
     - @task-scan-readme [NON-SCRIPTABLE] → Read output/{{repo_name}}_task3_scan-readme.json
       * Extract: commands_json_path, commands_extracted count
     - @task-execute-readme [NON-SCRIPTABLE] → Read output/{{repo_name}}_task4_execute-readme.json
       * Extract: executed_commands count, skipped_commands count
     - @task-find-solutions [SCRIPTABLE] → Read output/{{repo_name}}_task5_find-solutions.json
       * Extract: solutions_json path, solutions count
     - @generate-solution-task-checklists [SCRIPTABLE] → Read output/{{repo_name}}_task6_generate-solution-checklists.json
       * Extract: checklist_updated status
   - **Read existing checklist "## Task Variables" section to preserve previous values**
   - Update/add new variables based on which task was executed:
     - @task-clone-repo [SCRIPTABLE] → Sets: repo_directory
     - @task-search-readme [SCRIPTABLE] → Sets: readme_content (reference to JSON file path), readme_filename
     - @task-scan-readme [NON-SCRIPTABLE] → Sets: commands_extracted (reference to JSON file path or count)
     - @task-execute-readme [NON-SCRIPTABLE] → Sets: executed_commands (count), skipped_commands (count)
     - @task-find-solutions [SCRIPTABLE] → Sets: solutions_json (reference to JSON file path)
     - @generate-solution-task-checklists [SCRIPTABLE] → Sets: checklist_updated (boolean indicating solution sections added)
   - **Preserve all existing variable values** from previous tasks
   - **Only update variables that this task produces**
   
5. Update repository checklist with variable values:
   - Read ./tasks/{repo_name}_repo_checklist.md (if not already read in step 1)
   - Find or create "## Task Variables" section
     * If section doesn't exist, add it after "## Repo Variables Available" section
     * If section exists, update it while preserving previous variables
   - For each variable from completed tasks, write the appropriate value:
   
   **Variable Writing Rules:**
   - After @task-clone-repo [SCRIPTABLE] completes:
     * Write `repo_url`: {repo_url}
     * Write `clone_path`: {clone_path}
     * Write `repo_directory`: {absolute_path} (e.g., "C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool")
     * Write `repo_name`: {repo_name}
   
   - After @task-search-readme [SCRIPTABLE] completes:
     * Write `readme_content_path`: "output/{repo_name}_task2_search-readme.json"
     * Write `readme_filename`: {actual_filename} (e.g., "README.md")
     * If status is NOT_FOUND (no README found), write `readme_filename`: "NONE"
   
   - After @task-scan-readme [NON-SCRIPTABLE] completes:
     * Write `commands_json_path`: "output/{repo_name}_task3_scan-readme.json"
     * Write `commands_extracted`: "{count} commands" or "NONE (0 commands - {reason})"
   
   - After @task-execute-readme [NON-SCRIPTABLE] completes:
     * Write `executed_commands`: "SKIPPED (0 commands executed - {reason})" or "{count} commands executed"
     * Write `skipped_commands`: "SKIPPED (0 commands skipped - {reason})" or "{count} commands skipped"
   
   - After @task-find-solutions [SCRIPTABLE] completes:
     * Write `solutions_json`: "output/{repo_name}_task5_find-solutions.json ({count} solutions found)"
   
   **⚠️ CRITICAL - FORMAT CONSISTENCY REQUIREMENT:**
   
   ALL {repo_name}_repo_checklist.md files MUST follow this exact format for Task Variables section:
   
   ```markdown
   ## Task Variables
   
   Variables set by completed tasks:
   - `repo_url`: {repo_url}
   - `clone_path`: {clone_path}
   - `repo_directory`: {absolute_path_to_cloned_repo}
   - `repo_name`: {repo_name}
   - `readme_content`: {description_with_character_count_or_NONE}
   - `readme_filename`: {filename_or_NONE}
   - `commands_extracted`: {count_and_source_or_NONE}
   - `executed_commands`: {count_and_description_or_0}
   - `skipped_commands`: {count_and_reason_or_0}
   - `solutions_json`: {count_solutions_found_with_names_or_NONE}
   ```
   
   **Format Rules (MANDATORY):**
   1. Section header MUST be exactly: `## Task Variables`
   2. Subheading MUST be exactly: `Variables set by completed tasks:`
   3. Variable format MUST be: `` `variable_name`: {value} `` (backticks around variable name, colon separator)
   4. Variables MUST be in the order listed above (repo_url first, solutions_json last)
   5. All 10 variables MUST be present in every repo checklist
   6. Variable names MUST use backticks: `` `repo_url` ``, `` `clone_path` ``, etc.
   7. Values should be descriptive (e.g., "2892 characters - README.md found", "13 commands (from getting_started.md)")
   8. If a task hasn't been completed, use placeholder values: NONE, 0, or descriptive text
   
   **Before updating any variables:**
   - Verify the Task Variables section exists and follows this exact format
   - If format is incorrect or section is missing, recreate it with the correct structure
   - Preserve all existing variable values when updating
   - Only update variables that the current task produces
   
   - For large data, provide descriptive summaries with counts instead of full content
   - For simple values (paths, counts, filenames), embed directly with clear descriptions
   - **Important**: Only include actual values for tasks that have been completed
   - Write the updated checklist content back to the file

**Step 6: Check for More Tasks and Continue** 
Log completion using @task-update-decision-log:
   - Invoke: @task-update-decision-log timestamp={current_timestamp} repo_name={repo_name} solution_name="" task={task_name} message={task_result_message} status="SUCCESS"
   - This will append task completion to results/decision-log.csv

**Step 7: Check for More Tasks and Continue**
Save task output to ./output/ directory (if task produces JSON output):
   - Filename: {repo_name}_{task_name}.json

**Step 8: Check for More Tasks and Continue**
1. After completing the current task, **return to Step 1**
2. Read the checklist again to find the next unmarked task
3. If more unmarked tasks exist, execute them
4. Continue this loop until:
   - All tasks are marked [x] (return ALL_TASKS_COMPLETE)
   - A task fails (return FAIL with error details)
   - A task is blocked (return BLOCKED with blocking reason)

**Step 9: Return Final Execution Summary**

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
