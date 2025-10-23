@task-process-solutions solutions_json={{solutions_json}} repo_name={{repo_name}}
---
temperature: 0.1
model: gpt-5
---

** ⚠️ CRITICAL WARNING - READ BEFORE IMPLEMENTING ⚠️ **

This task is **NON-SCRIPTABLE** - DO NOT CREATE ANY SCRIPT FOR THIS TASK.

** ⚠️ VALIDATION REQUIREMENT - ABSOLUTELY MANDATORY ⚠️ **

**ROW COUNT VALIDATION RULE - ZERO TOLERANCE:**
- solution-progress.md row count MUST EQUAL the number of solutions found
- Example: task-find-solutions finds 8 .sln files → solution-progress.md MUST have exactly 8 rows
- **IF ROW COUNT MISMATCH**: Validation FAILS → You MUST restart from scratch
- **NO PARTIAL PROCESSING**: "Time constraints" / "Skipped 3 solutions" = VALIDATION FAILURE
- **CONSEQUENCE OF FAILURE**: Delete all rows for this repo, restart task-process-solutions for ALL solutions

**WHY THIS MATTERS:**
- Missing rows = Incomplete workflow execution = Unreliable results
- Validation ensures 100% solution coverage across all repositories  
- Partial processing corrupts the tracking system and invalidates reports
- Starting from scratch ensures consistency and prevents cascading failures

**VALIDATION EXAMPLE - YOUR WORK WILL BE REJECTED IF:**
```
❌ task-find-solutions output: 8 solutions found
❌ solution-progress.md: Only 5 rows exist
❌ Your excuse: "3 solutions not tested due to time constraints"
❌ Validation result: FAIL
❌ Required action: DELETE the 5 rows, START OVER, process ALL 8 solutions
```

❌ **NEVER DO THIS - CRITICAL MISTAKE:**
```python
# DO NOT CREATE SCRIPTS FOR NON-SCRIPTABLE TASKS!
# This task requires AI reasoning and cannot be automated
for sln_path, sln_name in solutions:
    subprocess.run(f'msbuild "{sln_path}" /restore /t:Clean,Build')
    # This skips the KB workflow entirely! ❌
```

✅ **YOU MUST DO THIS - CORRECT APPROACH:**
For EACH solution individually using direct tool calls:
1. run_in_terminal: msbuild restore → Check status
2. run_in_terminal: msbuild build → Check status
3. **IF BUILD FAILS:**
   a. Use AI reasoning to analyze errors
   b. @task-search-knowledge-base → Get kb_search_status
   c. **IF kb_search_status == NOT_FOUND:**
      - @task-create-knowledge-base (research with Microsoft Docs MCP)
      - Search again (kb_search_status will be FOUND now)
   d. **IF kb_search_status == FOUND:**
      - @task-apply-knowledge-base-fix → Apply the fix
      - run_in_terminal: msbuild restore (RETRY)
      - run_in_terminal: msbuild build (RETRY)
      - Log retry results
4. Only then move to next solution

** WHY NON-SCRIPTABLE: **
- Requires AI structural reasoning to analyze build errors
- Requires AI understanding to match errors to KB articles
- Requires conditional logic based on KB search results
- Cannot be automated - each solution needs human-like understanding

** ⚠️ MANDATORY WORKFLOW - DO NOT SKIP STEPS ⚠️ **

After processing each solution, if the build FAILS:
1. ✅ Search for KB article matching the error (MANDATORY)
2. ✅ If KB found: APPLY the fix using @task-apply-knowledge-base-fix (MANDATORY)
3. ✅ If KB not found: CREATE KB article (MANDATORY)
4. ✅ After creating KB: APPLY the fix (MANDATORY)
5. ✅ RETRY the build after applying fix (MANDATORY)
6. ✅ DO NOT move to next solution until retry is complete

** THIS IS A RETRY LOOP - NOT LINEAR PROCESSING **
You must loop back and retry builds after applying fixes!

** ⚠️ COMMON MISTAKE EXAMPLES - DO NOT DO THESE ⚠️ **

❌ **MISTAKE 1: Creating ANY script for this NON-SCRIPTABLE task**
```python
# DO NOT CREATE SCRIPTS - THIS TASK IS NON-SCRIPTABLE!
# You must use direct tool calls (run_in_terminal, read_file, etc.)
for solution in solutions:
    msbuild restore
    msbuild build
    # Missing: KB search, KB create, KB apply, retry ❌
    # Missing: AI reasoning for error analysis ❌
```

❌ **MISTAKE 2: Marking tasks complete without executing KB workflow**
```
- Solution builds: FAIL
- KB search: SKIPPED ❌ (Should be FOUND or NOT_FOUND)
- KB create: SKIPPED ❌ (Should be SUCCESS if NOT_FOUND)
- KB apply: SKIPPED ❌ (Should be SUCCESS after create)
- Retry build: SKIPPED ❌ (Should be executed after apply)
```

❌ **MISTAKE 3: Moving to next repository without validation**
```
Repository 1: task-process-solutions [x]
Repository 2: task-clone-repo [x] ❌ (Should NOT start Repo 2 yet!)
Missing: task-validate-all-solution-tasks-completed ❌
```

✅ **CORRECT PATTERN - ALL SOLUTIONS MUST SHOW:**
```
- Solution builds: SUCCESS or FAIL
- IF FAIL:
  - KB search: FOUND or NOT_FOUND (never SKIPPED)
  - IF NOT_FOUND: KB create: SUCCESS
  - KB apply: SUCCESS
  - Retry build: SUCCESS or FAIL (must attempt)
- Only then: Next solution or validation
```

** ⚠️ PATH VALIDATION CRITICAL ⚠️ **
READ THIS FIRST: knowledge_base_markdown/WORKFLOW_PATH_VALIDATION.md

Common fatal mistake: Assuming solution paths instead of reading them from task-find-solutions JSON output.
- ❌ WRONG: Using "src/Email/tools/codereview/codereview.sln" (assumed path)
- ✅ CORRECT: Reading exact path from JSON: "tools/codereview/codereview.sln"
- If you get "Project file does not exist", YOU ARE USING ASSUMED PATHS!
- ALWAYS read the solutions array from task-find-solutions JSON output and use EXACT absolute paths.

YOU MUST:
✓ Process each solution individually using direct tool calls
✓ For EACH solution, execute tasks from solution_tasks_list.md in order:
  1. @task-restore-solution - Run msbuild restore, capture output
  2. @task-build-solution - Run msbuild build, capture output
  3. **IF build_status == FAIL (MANDATORY KB WORKFLOW):**
     a. @task-search-knowledge-base - AI reasoning to find matching KB
     b. **IF kb_search_status == NOT_FOUND:**
        - @task-create-knowledge-base - Research with Microsoft Docs MCP
        - Search again (will be FOUND after creation)
     c. @task-apply-knowledge-base-fix - Apply the fix from KB
     d. **RETRY builds (loop back to step 1):**
        - run_in_terminal: msbuild restore (retry attempt)
        - run_in_terminal: msbuild build (retry attempt)
        - Log retry results to decision-log and solution-results
     e. Maximum 3 retry attempts per solution
  4. @task-collect-knowledge-base - Generate KB summary report
✓ Use run_in_terminal tool to execute msbuild commands for each solution
✓ Use AI structural reasoning to analyze build errors and match KB articles
✓ **NEVER skip KB workflow for failed builds** - This is the core purpose of the system
✓ Update solution-progress.md after EACH task for EACH solution
✓ Update solution-results.md/csv after EACH task for EACH solution
✓ Log ALL KB tasks (search, create, apply, retry) to decision-log.csv
✓ Process solutions sequentially (complete ALL tasks for solution 1 before moving to solution 2)
✓ Expect processing to take time (restore+build+KB can take 1-10min per solution)

YOU MUST NOT:
✗ Create ANY script for this task (task-process-solutions is NON-SCRIPTABLE)
✗ Skip the AI reasoning step in task-collect-knowledge-base
✗ Mark task-process-solutions as SUCCESS without processing individual solutions
✗ Complete the task in 1-2 seconds (this indicates you skipped processing)
✗ Use scripts for ANY part of this workflow (requires AI structural reasoning throughout)

CORRECT IMPLEMENTATION PATTERN:
For each solution in solutions array:
  1. run_in_terminal: msbuild restore command
  2. Check exit code, update solution-progress.md, update solution-results
  3. run_in_terminal: msbuild build command  
  4. Check exit code, update solution-progress.md, update solution-results
  5. If build failed: Use AI reasoning to analyze errors → match KB files → create KB report
  6. Update solution-progress.md, update solution-results
  7. Move to next solution and repeat

VALIDATION CHECKLIST after execution:
□ Did you use DIRECT TOOL CALLS only? (NO scripts created - this is NON-SCRIPTABLE)
□ Did you use run_in_terminal for each msbuild command individually?
□ Did you use AI reasoning for task-collect-knowledge-base? (NOT regex/simple string matching)
□ Does solution-progress.md show ALL solutions from this repository?
□ Does solution-results.md/csv have 3 rows per solution (restore/build/kb)?
□ Did execution take reasonable time (minutes, not seconds)?
□ Can you see actual msbuild output in run_in_terminal results?

If you answer NO to any validation question, you did NOT complete this task correctly!
If you created ANY script, you VIOLATED the NON-SCRIPTABLE requirement!

** END WARNING **

Task name: task-process-solutions

Description:
This task takes a JSON object returned by task-find-solutions.md and processes each solution file found.
For each solution, it executes a list of tasks to perform operations on the solution.

** CRITICAL REQUIREMENT **:
- This task is **NON-SCRIPTABLE** - DO NOT CREATE ANY SCRIPT
- You MUST use direct tool calls ONLY (run_in_terminal, read_file, create_file, etc.)
- DO NOT create a Python/PowerShell script for ANY part of this task
- You MUST process each solution individually with AI reasoning at each step
- Each solution MUST go through: restore → build → KB collection (if build fails)
- The KB collection step requires reading error output and using AI to match KB articles
- Processing takes time per solution (30s-5min each), NOT just seconds total
- **WHY NON-SCRIPTABLE**: Requires AI structural reasoning to analyze errors, match KB articles, and make conditional decisions

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
   
   ** CRITICAL - READ THE ACTUAL SOLUTION PATHS FROM JSON **:
   - The solutions_json contains an array of ABSOLUTE PATHS discovered by task-find-solutions
   - **YOU MUST USE THE EXACT PATHS** from the JSON array - DO NOT construct or assume paths
   - Example JSON structure:
     ```json
     {
       "solutions": [
         "C:\\Users\\sacheu\\speckit_repos\\repo\\src\\Management\\Deployment\\Tools\\MigrateCosmosDb\\MigrateCosmosDb.sln",
         "C:\\Users\\sacheu\\speckit_repos\\repo\\tools\\codereview\\codereview.sln"
       ]
     }
     ```
   - **WRONG**: Assuming paths like `src/Email/tools/codereview/codereview.sln`
   - **CORRECT**: Reading exact path from JSON: `tools/codereview/codereview.sln`
   - **VALIDATION**: Before running msbuild, verify the solution file exists at the path from JSON
   
   ** MANDATORY - YOU MUST ACTUALLY PROCESS THE SOLUTION **:
   - Run `msbuild` restore command and wait for completion
   - Run `msbuild` build command and wait for completion  
   - If build fails, search KB files for error codes
   - DO NOT skip these steps - they are the core purpose of this task
   - You should see actual msbuild output with compilation messages, errors, warnings
   - Processing takes time (30s-5min per solution) - this is EXPECTED and REQUIRED
   
   a. **Extract solution_path from JSON array** (do NOT construct the path yourself)
   b. Derive solution_name from the file name (e.g., MyApp.sln → MyApp)
   c. **VALIDATION - Verify solution file exists**:
      - Use the EXACT path from the JSON array (do not modify or reconstruct)
      - If file doesn't exist, log error and skip to next solution
      - Common mistake: Using assumed paths instead of JSON paths
   d. Initialize a per-solution context object with: solution_path, solution_name
   e. **CRITICAL - Add solution to progress table FIRST**: Before executing any tasks for this solution:
      - Check if a row for {{repo_name}} + {{solution_name}} exists in solution-progress.md
      - If NOT found, append a new row: `| {{repo_name}} | {{solution_name}} |  [ ]  |  [ ]  |  [ ]  |`
      - This ensures the solution appears in the progress table even if task execution fails
   f. If environment variable DEBUG=1 emit a debug line: `[debug][task-process-solutions] starting pipeline for solution='MyApp' path='C:\full\path\MyApp.sln'`
   g. **Execute ALL tasks from solution_tasks_list sequentially for this solution**:
      
      ** YOU MUST USE DIRECT TOOL CALLS - NOT SCRIPTS **:
      - Use `run_in_terminal` to execute msbuild restore/build commands
      - Wait for each command to complete and capture output
      - Use `read_file` to load error output or KB files
      - Use AI structural reasoning to analyze build errors
      - Use AI structural reasoning to match errors to KB articles
      - Use `create_file` to generate KB reports when builds fail
      - DO NOT automate this in a script - AI reasoning is required
      - The processing will take time - do not timeout prematurely
      
      For each task directive in solution_tasks_list (in order):
        i. Substitute placeholders (e.g., {{solution_path}}, {{solution_name}})
        ii. **Execute the task using appropriate tools** (run_in_terminal for msbuild, AI reasoning for KB)
        iii. **Wait for completion** before proceeding to the next task
        iv. **CRITICAL**: Capture exit code/status from the task execution
        v. **Check the exit code** to determine if the task succeeded or failed
        vi. **IMMEDIATELY Update solution-progress.md**: Find the row for {{repo_name}} + {{solution_name}} and update the specific task column ([ ] → [x] for success, [ ] → [!] for failure)
        vii. Append task result to solution-results.md and solution-results.csv - include {{repo_name}} in the Repository column
        viii. Merge returned fields into the per-solution context
   h. **After ALL tasks complete for this solution**, accumulate the solution's overall status into aggregate counts
   i. **IMPORTANT**: Only after finishing all tasks for the current solution, move to the next solution in the array and repeat steps a-i

4. **Validate All Solutions Completed (MANDATORY - DO NOT SKIP)**:
   - After processing ALL solutions in the array (step 3 complete), execute validation
   - **CRITICAL**: This step is MANDATORY before marking task-process-solutions as complete
   - Call: @task-validate-all-solution-tasks-completed repo_name={{repo_name}} repo_path={{local_path}}
   - **VALIDATION REQUIREMENTS - ALL MUST BE TRUE**:
     a. **Row Count Check**: solution-progress.md MUST have EXACTLY the same number of rows as solutions found
        - Example: If task-find-solutions found 8 .sln files, solution-progress.md MUST have 8 rows for this repository
        - **FAILURE CONDITION**: If solution-progress.md has fewer rows (e.g., 5 rows when 8 solutions exist), validation FAILS
        - **CONSEQUENCE**: If row count mismatch, you MUST start task-process-solutions FROM SCRATCH and process ALL solutions
        - Missing rows means you skipped solutions - this is NOT ALLOWED
     b. **Task Completion Check**: Each row must have restore [x] and build [x] OR [!]
        - Every solution MUST be attempted (success [x] or failure [!])
        - Empty checkboxes [ ] indicate incomplete processing
     c. **KB Workflow Validation** for all failed builds:
        * Each FAIL build must have: task-search-knowledge-base logged
        * If NOT_FOUND: Must have task-create-knowledge-base logged
        * If FOUND or after creation: Must have task-apply-knowledge-base-fix logged
        * Must have retry build attempts logged
   - **VALIDATION FAILURE HANDLING**:
     * If validation_status == INCOMPLETE (row count mismatch OR incomplete tasks):
       - **YOU MUST START FROM SCRATCH** - Delete solution-progress.md rows for this repo
       - Re-run task-process-solutions processing ALL solutions (not just missing ones)
       - This ensures consistency and prevents partial/corrupted tracking
     * If validation_status == SUCCESS, proceed to step 5 (Return summary)
     * If validation_status == ERROR, log the error but continue to step 5 (to return partial results)
   - **DO NOT proceed to next repository until validation_status == SUCCESS**
   - **This ensures all solutions are fully processed before moving to the next repository**
   
   **VIOLATION EXAMPLE - DO NOT DO THIS:**
   ```
   ❌ Solutions found: 8 (task-find-solutions output)
   ❌ Rows in solution-progress.md: 5 (3 solutions missing!)
   ❌ Validation result: FAIL - Row count mismatch
   ❌ Action required: START FROM SCRATCH, process all 8 solutions
   ```
   
   **CORRECT EXAMPLE:**
   ```
   ✅ Solutions found: 8 (task-find-solutions output)
   ✅ Rows in solution-progress.md: 8 (all solutions present)
   ✅ Each row: restore [x] or [!], build [x] or [!]
   ✅ Validation result: SUCCESS
   ✅ Can now proceed to next repository
   ```
   
   **PARTIAL COMPLETION VIOLATION - NEVER ACCEPTABLE:**
   ```
   ❌ "I processed 5 of 8 solutions due to time constraints"
   ❌ "3 solutions marked as 'Not tested'"
   ❌ solution-progress.md has 5 rows but 8 solutions exist
   ❌ This is a VALIDATION FAILURE - must restart from scratch
   ```
   
   **CRITICAL RULE - NO PARTIAL PROCESSING:**
   - You MUST process ALL solutions found by task-find-solutions
   - "Time constraints" is NOT a valid reason to skip solutions
   - Partial completion = Validation failure = Start from scratch
   - solution-progress.md row count MUST EQUAL solutions found count
   
   **CORRECT EXAMPLE:**
   ```
   ✅ Repository 1: task-process-solutions [x]
   ✅ Repository 1: task-validate-all-solution-tasks-completed [x]
   ✅ Only then: Repository 2: task-clone-repo [ ] (Now safe to start)
   ```

5. Create and initialize a solution progress markdown file:
      - results/solution-progress.md (Solution Progress tracking table)
      - Parse solution_tasks_list.md to extract ALL task directive names (e.g., @task-restore-solution, @task-build-solution, etc.)
      - Get all the solution names from the solution array
      - Create table with columns: Repository | Solution | task-restore-solution | task-build-solution | [additional tasks...]
      - **IMPORTANT**: Include a column for EVERY task found in solution_tasks_list.md, not just restore
      - **Repository Column**: Fill in the Repository column for each row with the value from the {{repo_name}} input argument passed to this prompt
      - **CRITICAL - Append to existing file**: If solution-progress.md already exists from previous repositories, APPEND new rows to it. DO NOT replace the entire file.
      - **Check for duplicates**: Before appending, verify that a row for {{repo_name}} + {{solution_name}} doesn't already exist
      - Initialize all task cells with [ ] (empty checkboxes) for new rows only
      - Example header: `| Repository | Solution | task-restore-solution | task-build-solution |`
      - Example row: `| ic3_spool_cosine-dep-spool | ResourceProvider | [ ] | [ ] |`
      - **REMEMBER**: Each repository can have multiple solutions, and all solutions from all repositories must be visible in this single table

5a. **⚠️ CRITICAL PRE-PROCESSING VALIDATION - MANDATORY STEP ⚠️**:
   - **IMMEDIATELY after creating/appending rows in Step 5**, execute validation:
     ```
     @task-validate-all-solution-tasks-completed repo_name={{repo_name}} repo_path={{local_path}} checked=false
     ```
   - **Purpose**: Verify all cells for this repository are EMPTY [ ] before processing begins
   - **Expected Result**: validation_status = SUCCESS (all cells [ ])
   - **IF VALIDATION FAILS** (validation_status = INCOMPLETE or ERROR):
     * Some cells already have [x] or [!] from a previous incomplete run
     * **REQUIRED ACTION**: Delete ALL rows for {{repo_name}} from solution-progress.md
     * **GO BACK TO STEP 5**: Recreate the rows with empty cells [ ]
     * **RE-RUN THIS VALIDATION** (Step 5a) until validation_status = SUCCESS
     * **DO NOT PROCEED** to Step 6 until validation passes
   - **Log to Decision Log:**
     ```
     "{{timestamp}},{{repo_name}},,task-process-solutions,Pre-processing validation: {validation_status},INFO"
     ```
   - **CRITICAL**: This step is NON-NEGOTIABLE - it prevents processing solutions with corrupted/partial state

6. Initialize solution tracking artifacts if not present:
      - results/solution-results.md (Markdown table: Repository | Solution | Task | Status | Timestamp)
      - results/solution-results.csv (CSV with same columns)
      - **Repository Column**: When appending rows to solution-results.md and solution-results.csv, fill in the Repository column with the value from the {{repo_name}} input argument
      - For each solution row initialize task-restore-solution cell with [ ]

7. Track progress for each solution:
   - **CRITICAL - Update solution-progress.md after EACH task completion**: When a task (restore/build/kb) completes for a solution, immediately update the corresponding cell in solution-progress.md
   - **Find the correct row**: Locate the row matching BOTH {{repo_name}} AND {{solution_name}}
   - **Update the correct column**: Change [ ] to [x] for success or [!] for failure in the appropriate task column
   - **Task column mapping**:
     * Column 3 (index 2 after repo/solution): task-restore-solution
     * Column 4 (index 3): task-build-solution  
     * Column 5 (index 4): task-collect-knowledge-base
   - After successful completion of all tasks for that solution, verify all checkboxes are properly marked
   - On partial failure, mark failed tasks with [!] and leave remaining task columns with [ ] (future multi-task support)
   - **This ensures real-time progress visibility across all repositories and solutions**

8. **⚠️ CRITICAL POST-PROCESSING VALIDATION - MANDATORY STEP ⚠️**:
   - **BEFORE exiting this task**, execute final validation:
     ```
     @task-validate-all-solution-tasks-completed repo_name={{repo_name}} repo_path={{local_path}} checked=true
     ```
   - **Purpose**: Verify all cells for this repository are COMPLETED [x] or FAILED [!] after processing
   - **Expected Result**: validation_status = SUCCESS (all cells [x] or [!])
   - **IF VALIDATION FAILS** (validation_status = INCOMPLETE or ERROR):
     * Some cells still have [ ] (empty) - solutions were not fully processed
     * **REQUIRED ACTION - ONE RETRY ONLY**:
       1. Log warning: "Post-processing validation FAILED. Attempting ONE reprocess of all solutions for {{repo_name}}"
       2. **GO BACK TO STEP 3**: Reprocess ALL solutions in the solutions array
       3. After reprocessing completes, **RE-RUN THIS VALIDATION** (Step 8) one more time
       4. **IF VALIDATION STILL FAILS** after retry:
          - Log error: "Post-processing validation FAILED after retry. Moving on from {{repo_name}}"
          - **PROCEED TO STEP 9** (do not retry again - only one retry attempt allowed)
       5. **IF VALIDATION SUCCEEDS** after retry:
          - Log success: "Post-processing validation SUCCESS after retry for {{repo_name}}"
          - **PROCEED TO STEP 9**
   - **IF VALIDATION SUCCEEDS** on first attempt:
     * Log success: "Post-processing validation SUCCESS for {{repo_name}}"
     * **PROCEED TO STEP 9**
   - **Log to Decision Log:**
     ```
     "{{timestamp}},{{repo_name}},,task-process-solutions,Post-processing validation: {validation_status},INFO"
     ```
   - **CRITICAL**: This step ensures all solutions were fully processed before moving to next repository

9. Return summary of processed solutions:
   - Total solutions found
   - Successfully processed count
   - Failed processing count
   - Post-processing validation status

10. DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), emit a final line to stdout (or terminal) after all solutions processed:
   "[debug][task-process-solutions] END total={{total_solutions}} success={{success_count}} fail={{failure_count}} validation={{validation_status}}"
   This line marks task completion and provides aggregate status visibility.

Invocation Pattern:
- Repository pipeline calls: `@task-process-solutions solutions_json={{previous_output}} repo_name={{repo_name}}`
- This task internally invokes: `@solution-tasks-list solution_path={{solution_path}}`
- The solution task list expands into concrete task directives actually executed per solution.
- ** Important ** Execute each step individually using direct tool calls (run_in_terminal, read_file, create_file, replace_string_in_file)
- ** Important ** DO NOT CREATE ANY SCRIPT - this is a NON-SCRIPTABLE task
- ** CRITICAL ** This task is **NON-SCRIPTABLE** - requires AI structural reasoning throughout, cannot be automated
- ** VALIDATION ** After execution completes, verify that:
  * solution-progress.md has rows for ALL solutions from this repository
  * solution-results.md/csv has 3 entries per solution (restore, build, KB)
  * The processing took reasonable time (not just 1-2 seconds for multiple solutions)
  * You used run_in_terminal for msbuild commands (visible in conversation)
  * You used AI reasoning for KB matching (not simple regex/grep)


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
11. **Synchronous Task Execution**: Each task directive must complete before the next one starts. Use direct tool calls in sequence. For restore/build: use run_in_terminal tool. For KB collection: use AI reasoning to analyze error output.
12. **Exit Code Checking**: After each msbuild command completes (via run_in_terminal), immediately check its exit code from the tool result to determine success/failure. Use this for aggregate counting (success_count vs failure_count) and for deciding whether to continue or skip remaining tasks.
13. **AI Reasoning for KB**: The @task-collect-knowledge-base step CANNOT be scripted. You must use AI structural reasoning to:
    - Read and analyze the build error output
    - Identify error codes (CS0234, MSB3644, etc.)
    - Match error codes to KB article filenames in knowledge_base_markdown/
    - Read relevant KB articles
    - Synthesize a KB report explaining how to fix the errors
    - This is why task-process-solutions is NON-SCRIPTABLE
14. **PATH VALIDATION - CRITICAL**: Before processing ANY solution:
    - Read the solutions array from solutions_json input
    - Extract the EXACT absolute path for each solution
    - DO NOT construct paths based on assumptions (e.g., assuming "Email/tools/...")
    - DO NOT modify paths from the JSON (they are already absolute)
    - VALIDATE the file exists before running msbuild
    - If file doesn't exist, it means you're using the wrong path
    - Common error: Using hardcoded path patterns instead of JSON values
    - Example correct usage:
      ```
      Read solutions_json → Get solutions[0] → Use that exact path in msbuild command
      ```
    - Example incorrect usage:
      ```
      Assume solution is in "src/Email/tools/..." → Construct path → File not found ❌
      ```

Variables available:
- {{solutions_json}} → Raw JSON input containing local_path and solutions array
- {{local_path}} → Repository directory extracted from solutions_json
- {{solution_path}} → Absolute path of current solution being processed
- {{solution_name}} → Friendly name of current solution file
- {{repo_name}} → Friendly repository name (passed as input argument from caller)
- {{solution_task_output}} → Output returned by @solution-tasks-list for the current solution