@execute-task clone=<required> clean_results=<optional>
---
temperature: 0.1
---

Description:
This prompt acts as an autonomous task executor that reads task checklists and executes tasks in a continuous loop.
It processes ALL uncompleted tasks across ALL repositories until everything is complete or an error occurs.

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
1. Read ./tasks/{repo_name}_checklist.md
2. Parse the "## Tasks (Sequential Pipeline - Complete in Order)" section
3. Find the first task with `- [ ]` (uncompleted)
4. Extract task_name from that line (e.g., "@task-clone-repo")
5. **Read existing "## Task Variables" section (if it exists)**:
   - Parse all variable values from previous task executions
   - Store these values for use in task parameter preparation
   - This allows resuming work from a previous run with all context preserved
6. Determine if this is a repository-level task or solution-level task:
   - Repository-level: Task appears before any "## Solution:" section
   - Solution-level: Task appears within a "## Solution: {name}" section

**Step 3: Determine Task Scope and Parameters**

**If repository-level task:**
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
  - @task-execute-readme: 
    - repo_directory: **Read from checklist variables**
    - repo_name: From checklist variables
  - @task-find-solutions: 
    - repo_directory: **Read from checklist variables**
  - @generate-solution-task-checklists:
    - repo_name: From checklist variables
    - solutions: **Read from checklist variables** (reference to solutions_json file, extract solutions array)
  - @task-process-solutions: 
    - solutions_json: **Read from checklist variables** (reference to JSON file)
    - repo_name: From checklist variables

**If solution-level task:**
- Extract solution_name from the "## Solution: {name}" section header
- Extract solution_path from the "Path: {path}" line
- Extract task_name (e.g., "@task-restore-solution")
- Prepare parameters based on task type:
  - @task-restore-solution: solution_path
  - @task-build-solution: solution_path
  - @task-search-knowledge-base: solution_path, solution_name, build_status, build_stderr, errors, warnings
  - @task-create-knowledge-base: solution_path, solution_name, kb_search_status, detection_tokens, error_signature, error_code, error_type, build_stderr, errors, warnings
  - @task-apply-knowledge-base-fix: solution_path, kb_file_path, error_code

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
- Example: @task-process-solutions needs solutions_json:
  1. Check checklist variables for `solutions_json`
  2. If value is "[saved to ./output/repo_task-find-solutions.json]", read that file
  3. Use the data from the file as input parameter
- Example: @generate-solution-task-checklists needs solutions array:
  1. Check checklist variables for `solutions_json`
  2. Read the JSON file to get the solutions array
  3. Transform array to required format (objects with name and path properties)

**Variable Resolution Priority:**
1. **Check ./tasks/{repo_name}_checklist.md → "## Task Variables" section** (FIRST)
2. **If variable references a JSON file**, read from ./output/{filename}
3. **If variable is not found in checklist**, check ./output/ directory directly (FALLBACK)

**Variable Value Formats:**
- Simple values: Used directly (e.g., `repo_directory`: `C:\cloned\repo`)
- File references: Parse and read (e.g., `readme_content`: `[saved to ./output/...]`)
- Not set: Shows "not set" - task cannot proceed if this variable is required

**If required input data is missing:**
- Return status: BLOCKED with error message indicating missing dependency
- Example: "Cannot execute @task-search-readme: Variable 'repo_directory' not set (previous task @task-clone-repo not completed)"

**Step 5: Execute the Task**
1. Log the execution attempt to results/decision-log.csv:
   - Timestamp: ISO 8601 format
   - Repo Name: {repo_name}
   - Solution Name: {solution_name} (or empty if repo-level task)
   - Task: {task_name}
   - Message: "Starting task execution (loop iteration {tasks_executed_count + 1})"
   - Status: "IN_PROGRESS"

2. Invoke the task prompt with required parameters:
   - Repository tasks: Invoke task directive directly (e.g., @task-clone-repo)
   - Solution tasks: May be invoked via @solution-tasks-list or individual task directives

3. **SPECIAL HANDLING for @task-process-solutions (KB Workflow Enforcement):**
   
   When executing @task-process-solutions, the prompt MUST follow this workflow for EACH solution:
   
   a. Execute restore and build for the solution
   
   b. **IF restore OR build fails:**
      - Execute @task-search-knowledge-base
        - Input: solution_path, solution_name, build_status, build_stderr, errors, warnings
        - Output: kb_search_status (FOUND or NOT_FOUND), kb_file_path (if FOUND)
        - Log to decision-log.csv with status FOUND or NOT_FOUND
      
      - **IF kb_search_status == NOT_FOUND:**
        - Execute @task-create-knowledge-base
          - Input: solution_path, solution_name, error details
          - Output: kb_create_status (SUCCESS or FAIL), new_kb_file_path
          - Uses Microsoft Docs MCP for research
          - Log to decision-log.csv with status SUCCESS or FAIL
        - Execute @task-search-knowledge-base AGAIN (will be FOUND now)
      
      - Execute @task-apply-knowledge-base-fix (MANDATORY)
        - Input: solution_path, kb_file_path, error_code
        - Output: fix_status (SUCCESS or FAIL)
        - Log to decision-log.csv with status SUCCESS or FAIL
      
      - RETRY restore + build after applying fix
        - Log retry attempt to decision-log.csv
        - Maximum 3 retry attempts per solution
        - Log final retry result (SUCCESS or FAIL)
   
   c. Update checklist checkboxes for KB tasks:
      - Mark "Search knowledge base" as [x] with status (FOUND/NOT_FOUND)
      - Mark "Create KB entry" as [x] if NOT_FOUND (with SUCCESS/FAIL)
      - Mark "Apply fix" as [x] with status (SUCCESS/FAIL)
   
   d. Only proceed to next solution after current solution's KB workflow completes
   
   **⚠️ CRITICAL: KB workflow is NOT optional! Never skip these steps for failed builds!**

4. Capture task output (status, result data)

5. **If task execution fails:**
   - Log failure to decision-log.csv with status: FAIL
   - Set executor_status: FAIL
   - **EXIT LOOP** and proceed to Step 9 (Return Execution Summary with error details)

6. **If task execution is blocked:**
   - Log blocked status to decision-log.csv
   - Set executor_status: BLOCKED
   - **EXIT LOOP** and proceed to Step 9 (Return Execution Summary with blocking reason)

7. Increment tasks_executed_count by 1

**Step 6: Update Checklists and Save Variables**
1. If task completed successfully:
   - Invoke @task-update-checklist with:
     - repo_name: {repo_name}
     - task_name: {task_name}
     - solution_name: {solution_name} (if solution-level task)
   
2. Extract and save task output variables to repository checklist:
   - **Parse repo_tasks_list.md to get list of all available variables**:
     - Read the "Variables available:" section
     - Extract all variable names (e.g., {{repo_url}}, {{repo_directory}}, {{readme_content}}, etc.)
   - Read task output data from execution result
   - **Read existing checklist "## Task Variables" section to preserve previous values**
   - Update/add new variables based on which task was executed:
     - @task-clone-repo → Sets: repo_directory
     - @task-search-readme → Sets: readme_content, readme_filename
     - @task-scan-readme → Sets: commands_extracted
     - @task-execute-readme → Sets: executed_commands, skipped_commands
     - @task-find-solutions → Sets: solutions_json
     - @generate-solution-task-checklists → Sets: checklist_updated (boolean indicating solution sections added)
   - **Preserve all existing variable values** from previous tasks
   - **Only update variables that this task produces**
   
3. Update repository checklist with variable values:
   - Read ./tasks/{repo_name}_checklist.md
   - Find or create "## Task Variables" section at the end of the file
   - For each variable from repo_tasks_list.md "Variables available:" section:
     - If variable has a value (from current or previous tasks), show the value
     - If variable is not yet set, show "not set" or omit
   - Format:
     ```
     ## Task Variables
     
     Variables from completed tasks (for resuming work):
     Variables list dynamically generated from repo_tasks_list.md
     
     - `repo_url`: {repo_url}
     - `clone_path`: ./cloned
     - `repo_directory`: {absolute_path_to_cloned_repo} (or "not set")
     - `repo_name`: {repo_name}
     - `readme_content`: [saved to ./output/{repo_name}_task-search-readme.json] (or "not set")
     - `readme_filename`: {README.md} (or "not set")
     - `commands_extracted`: {count} (or "not set")
     - `executed_commands`: {count} (or "not set")
     - `skipped_commands`: {count} (or "not set")
     - `solutions_json`: [saved to ./output/{repo_name}_task-find-solutions.json] (or "not set")
     
     **Note:** Large content (readme_content, solutions_json) is stored in ./output/ directory.
     Paths and counts are shown here for quick reference.
     ```
   - For large data (readme_content, solutions_json), reference the JSON file path instead of embedding full content
   - For simple values (paths, counts, filenames), embed directly in checklist
   - **Important**: The variable list is always generated from repo_tasks_list.md to stay in sync
   
2. Log completion to results/decision-log.csv:
   - Timestamp: ISO 8601 format
   - Repo Name: {repo_name}
   - Solution Name: {solution_name} (or empty)
   - Task: {task_name}
   - Message: Task result message
   - Status: "SUCCESS" or "FAIL"

3. Save task output to ./output/ directory (if task produces JSON output):
   - Filename: {repo_name}_{task_name}.json (for repo tasks)
   - Filename: {repo_name}_{solution_name}_{task_name}.json (for solution tasks)

4. Write updated checklist with variables back to file

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
  - solution_name: string | null
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
  - If value is a file reference, read ./output/{filename}
  - If value is embedded, use directly
- If variable is not set in checklist (shows "not set"):
  - Check ./output/{repo_name}_{previous_task}.json as fallback
- If missing from both sources, return BLOCKED status
- Example workflow:
  1. Task @task-search-readme needs `repo_directory`
  2. Check checklist variables: `repo_directory: C:\cloned\repo`
  3. Use this value as parameter for task invocation

**Case 3: Solution tasks**
- Solution checklists must exist (created by @generate-solution-task-checklists)
- Solution path must be available in checklist or from @task-find-solutions output
- Solution tasks may have conditional execution (e.g., KB tasks only run if build fails)

**Case 4: Conditional tasks (solution workflow) - KB WORKFLOW ENFORCEMENT**

**⚠️ CRITICAL: KB Workflow is MANDATORY for ALL build/restore failures!**

When processing solutions via @task-process-solutions:
1. Execute @task-restore-solution and @task-build-solution
2. **IF either restore OR build fails:**
   - ✅ MUST execute @task-search-knowledge-base (search for existing KB article)
   - ✅ IF search returns NOT_FOUND: MUST execute @task-create-knowledge-base (research + create new KB)
   - ✅ MUST execute @task-apply-knowledge-base-fix (apply the fix from KB)
   - ✅ MUST retry restore + build after applying fix
   - ✅ Log ALL KB task executions to decision-log.csv
   - ❌ NEVER mark KB tasks as "SKIPPED" - they are MANDATORY on failure

**Conditional Execution Logic:**
- @task-search-knowledge-base: Executes when build_status == FAIL or restore_status == FAIL
- @task-create-knowledge-base: Executes when kb_search_status == NOT_FOUND (after search)
- @task-apply-knowledge-base-fix: ALWAYS executes after search (or after create if NOT_FOUND)
- Retry build: ALWAYS executes after applying fix (maximum 3 retry attempts)

**Example Correct Flow for Failed Build:**
```
Solution 3: ResourceProvider.sln
1. Restore → SUCCESS
2. Build → FAIL (Service Fabric error)
3. Search KB → FOUND (kb_file: sf_baseoutputpath_missing.md)
4. Apply Fix → SUCCESS (modified .sfproj file)
5. Retry Restore → SUCCESS
6. Retry Build → SUCCESS (or FAIL after max retries)
```

**What NOT to do:**
- ❌ Skip KB workflow and move to next solution
- ❌ Mark KB tasks as "SKIPPED" in checklist
- ❌ Process all builds first, then try to fix them later
- ❌ Give up after first failure without searching KB

**Case 5: All tasks complete**
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
11. **Conditional Logic**: Handle solution workflow conditionals (KB tasks only on build failure)
12. **Sequential Execution**: Always execute tasks in order (MANDATORY #1, #2, #3, #4...)
13. **Solution Iteration**: For repo tasks that process multiple solutions (like @task-process-solutions), each solution's tasks are tracked separately
14. **Programming Language**: All code generated should be written in Python
15. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory
16. **Loop Termination**: Only stops when ALL_COMPLETE, FAIL, or BLOCKED - ensures maximum progress before stopping
11. **Solution Iteration**: For repo tasks that process multiple solutions (like @task-process-solutions), each solution's tasks are tracked separately
12. **Programming Language**: All code generated should be written in Python
13. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

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
  - Read repo1_checklist.md → Find "@task-clone-repo" uncompleted
  - Execute @task-clone-repo → SUCCESS
  - Update checklist: Mark @task-clone-repo as [x]
  - Update Task Variables: repo_directory = C:\cloned\repo1
  - Save output: ./output/repo1_task-clone-repo.json
  - Tasks executed: 1
  - Print: "✓ Task @task-clone-repo completed for repo1"
  - LOOP BACK to Step 1

LOOP ITERATION 2:
  - Read all_repository_checklist.md → Find "repo1" still uncompleted
  - Read repo1_checklist.md → Find "@task-search-readme" uncompleted
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
  - Read repo1_checklist.md → Find "@generate-solution-task-checklists" uncompleted
  - Load solutions_json from checklist Task Variables
  - Execute @generate-solution-task-checklists → SUCCESS
  - Update checklist: Mark @generate-solution-task-checklists as [x]
  - Update Task Variables: checklist_updated = true
  - Repository checklist now has solution-specific task sections
  - Tasks executed: 6
  - Print: "✓ Task @generate-solution-task-checklists completed for repo1"
  - LOOP BACK to Step 1

LOOP ITERATION N:
  - Read all_repository_checklist.md → Find "repo1" still uncompleted
  - Read repo1_checklist.md → Find "@task-process-solutions" uncompleted (last task)
  - Load solutions_json from checklist Task Variables
  - Execute @task-process-solutions → SUCCESS
  - Update checklist: Mark @task-process-solutions as [x]
  - **ALL tasks in repo1 are now [x]**
  - **Update all_repository_checklist.md: Mark repo1 as [x]**
  - Log: "repo1 - All tasks completed"
  - Repositories completed: 1
  - Tasks executed: 7
  - Print: "✓ Repository repo1 completed!"
  - LOOP BACK to Step 1

LOOP ITERATION N+1:
  - Read all_repository_checklist.md → Find "repo2" uncompleted
  - Read repo2_checklist.md → Find "@task-clone-repo" uncompleted
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
