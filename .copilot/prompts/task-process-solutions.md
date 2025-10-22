@task-process-solutions solutions_json={{solutions_json}} repo_name={{repo_name}}
---
temperature: 0.1
model: gpt-5
---

** ⚠️ CRITICAL WARNING - READ BEFORE IMPLEMENTING ⚠️ **

This task is **NON-SCRIPTABLE** because it includes @task-collect-knowledge-base which requires AI structural reasoning.

DO NOT create a single Python/PowerShell script that processes all solutions!

YOU MUST:
✓ Process each solution individually using direct tool calls
✓ For EACH solution, execute the 3 tasks from solution_tasks_list.md:
  1. @task-restore-solution - Run msbuild restore, capture output
  2. @task-build-solution - Run msbuild build, capture output  
  3. @task-collect-knowledge-base - Use AI reasoning to match errors to KB files
✓ Use run_in_terminal tool to execute msbuild commands for each solution
✓ Use AI structural reasoning to analyze build errors and match KB articles
✓ Update solution-progress.md after EACH task for EACH solution
✓ Update solution-results.md/csv after EACH task for EACH solution
✓ Process solutions sequentially (complete all 3 tasks for solution 1 before moving to solution 2)
✓ Expect processing to take time (restore+build can take 30s-5min per solution)

YOU MUST NOT:
✗ Create a single script that processes all solutions at once
✗ Skip the AI reasoning step in task-collect-knowledge-base
✗ Mark task-process-solutions as SUCCESS without processing individual solutions
✗ Complete the task in 1-2 seconds (this indicates you skipped processing)
✗ Use scripts for task-collect-knowledge-base (requires AI structural reasoning)

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
□ Did you use run_in_terminal for each msbuild command? (NOT a Python script)
□ Did you use AI reasoning for task-collect-knowledge-base? (NOT regex/simple string matching)
□ Does solution-progress.md show ALL solutions from this repository?
□ Does solution-results.md/csv have 3 rows per solution (restore/build/kb)?
□ Did execution take reasonable time (minutes, not seconds)?
□ Can you see actual msbuild output in run_in_terminal results?

If you answer NO to any validation question, you did NOT complete this task correctly!

** END WARNING **

Task name: task-process-solutions

Description:
This task takes a JSON object returned by task-find-solutions.md and processes each solution file found.
For each solution, it executes a list of tasks to perform operations on the solution.

** CRITICAL REQUIREMENT **:
- This task is **NON-SCRIPTABLE** because it includes @task-collect-knowledge-base
- @task-collect-knowledge-base requires AI structural reasoning to analyze build errors
- You MUST use direct tool calls (run_in_terminal, read_file, create_file, etc.)
- DO NOT create a Python/PowerShell script that processes all solutions
- You MUST process each solution individually with AI reasoning at each step
- Each solution MUST go through: restore → build → KB collection (if build fails)
- The KB collection step requires reading error output and using AI to match KB articles
- Processing takes time per solution (30s-5min each), NOT just seconds total

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
   
   ** MANDATORY - YOU MUST ACTUALLY PROCESS THE SOLUTION **:
   - Run `msbuild` restore command and wait for completion
   - Run `msbuild` build command and wait for completion  
   - If build fails, search KB files for error codes
   - DO NOT skip these steps - they are the core purpose of this task
   - You should see actual msbuild output with compilation messages, errors, warnings
   - Processing takes time (30s-5min per solution) - this is EXPECTED and REQUIRED
   
   a. Derive solution_name from the file name (e.g., MyApp.sln → MyApp)
   b. Initialize a per-solution context object with: solution_path, solution_name
   c. **CRITICAL - Add solution to progress table FIRST**: Before executing any tasks for this solution:
      - Check if a row for {{repo_name}} + {{solution_name}} exists in solution-progress.md
      - If NOT found, append a new row: `| {{repo_name}} | {{solution_name}} |  [ ]  |  [ ]  |  [ ]  |`
      - This ensures the solution appears in the progress table even if task execution fails
   d. If environment variable DEBUG=1 emit a debug line: `[debug][task-process-solutions] starting pipeline for solution='MyApp' path='C:\full\path\MyApp.sln'`
   e. **Execute ALL tasks from solution_tasks_list sequentially for this solution**:
      
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
   f. **After ALL tasks complete for this solution**, accumulate the solution's overall status into aggregate counts
   g. **IMPORTANT**: Only after finishing all tasks for the current solution, move to the next solution in the array and repeat steps a-g

4. Create and initialize a solution progress markdown file:
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

5. Initialize solution tracking artifacts if not present:
      - results/solution-results.md (Markdown table: Repository | Solution | Task | Status | Timestamp)
      - results/solution-results.csv (CSV with same columns)
      - **Repository Column**: When appending rows to solution-results.md and solution-results.csv, fill in the Repository column with the value from the {{repo_name}} input argument
      - For each solution row initialize task-restore-solution cell with [ ]

6. Track progress for each solution:
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
- ** Important ** Execute each step individually using direct tool calls (run_in_terminal, read_file, create_file, replace_string_in_file)
- ** Important ** Do NOT create a monolithic script - use tool calls for each solution
- ** CRITICAL ** This task is **NON-SCRIPTABLE** because @task-collect-knowledge-base requires AI structural reasoning
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

Variables available:
- {{solutions_json}} → Raw JSON input containing local_path and solutions array
- {{local_path}} → Repository directory extracted from solutions_json
- {{solution_path}} → Absolute path of current solution being processed
- {{solution_name}} → Friendly name of current solution file
- {{repo_name}} → Friendly repository name (passed as input argument from caller)
- {{solution_task_output}} → Output returned by @solution-tasks-list for the current solution