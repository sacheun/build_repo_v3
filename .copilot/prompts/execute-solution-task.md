@execute-solution-task
---
temperature: 0.1
---

Description:
This prompt autonomously executes solution-level tasks by processing *solution_checklist.md files in the ./tasks directory. It finds uncompleted tasks, reads required variables from the markdown file, executes the corresponding task prompts, and updates the checklist as tasks complete.

**⚠️ CRITICAL: This is an EXECUTOR prompt - it ONLY calls other task prompts. It does NOT execute commands directly.**

**DO NOT:**
- Run `dotnet restore` commands directly
- Run `dotnet build` commands directly
- Execute ANY terminal commands yourself
- Generate scripts for solution tasks
- Deviate from calling the defined task prompts

**DO:**
- Call @task-restore-solution prompt for restore tasks
- Call @task-build-solution prompt for build tasks
- Call @task-search-knowledge-base prompt for KB search
- Call @task-apply-knowledge-base-fix prompt for applying fixes
- Let those task prompts handle command execution (scriptable or non-scriptable)

This is an autonomous executor similar to @execute-repo-task but designed for solution-level workflows.

**Autonomous Execution Flow:**
1. Scan ./tasks directory for *solution_checklist.md files
2. For each solution checklist file:
   - Read all solution sections
   - For each solution section, find FIRST uncompleted [ ] task
   - Read required variables from markdown file
   - Execute corresponding task prompt
   - Update checklist when task completes
   - Move to NEXT uncompleted task in same solution
   - When solution complete, move to next solution
3. Continue until ALL tasks in ALL solution checklists are complete

Behavior:

**Step 1: Discover Solution Checklist Files**
1. Search ./tasks directory for files matching pattern: *solution_checklist.md
2. Expected files:
   - ic3_spool_cosine-dep-spool_solution_checklist.md
   - people_spool_usertokenmanagement_solution_checklist.md
   - sync_calling_concore-conversation_solution_checklist.md
3. Sort files alphabetically for consistent processing order
4. If no solution checklist files found, return status: NO_WORK

**Step 2: Process Each Solution Checklist File**
For each solution checklist file found:

1. Read the entire file content
2. Extract repository name from filename (e.g., "ic3_spool_cosine-dep-spool" from "ic3_spool_cosine-dep-spool_solution_checklist.md")
3. Parse all solution sections (## {N}. {solution_name})
4. For each solution section, identify:
   - Solution name
   - Solution path
   - Solution variables (if any)
   - Task list with completion status

**Step 3: Find and Execute First Uncompleted Task**

**CRITICAL - SEQUENTIAL EXECUTION REQUIREMENT:**
- Process tasks in STRICT SEQUENTIAL ORDER within each solution
- Find the FIRST uncompleted [ ] task in the current solution
- Execute ONLY that ONE task
- Update the checklist
- Then find the NEXT uncompleted [ ] task
- DO NOT skip tasks or execute multiple tasks simultaneously
- DO NOT move to next solution until current solution has ALL tasks [x] completed

**CRITICAL - CONDITIONAL TASK EXECUTION:**
- **CONDITIONAL tasks are NOT SKIPPABLE - they MUST EXECUTE when their condition is met**
- CONDITIONAL means "execute IF condition is met"
- When condition is TRUE → Task becomes MANDATORY and MUST be executed
- When condition is FALSE → Task is SKIPPED (mark as [x] SKIPPED)
- Example: "@task-search-knowledge-base" is CONDITIONAL on build failure
  - If restore_status == FAIL OR build_status == FAIL → MUST execute @task-search-knowledge-base
  - If both restore and build succeeded → Mark as [x] SKIPPED, move to next task
- Example: "@task-apply-knowledge-base-fix" is CONDITIONAL on KB search result
  - If kb_search_status == FOUND → MUST execute @task-apply-knowledge-base-fix
  - If kb_search_status == NOT_FOUND → Mark as [x] SKIPPED, move to next task
- Never skip a CONDITIONAL task when its condition is satisfied

For the FIRST uncompleted [ ] task found:

1. Identify task type from task description:
   - "Restore packages for {solution_name}" → @task-restore-solution
   - "Build solution {solution_name}" → @task-build-solution  
   - "Search knowledge base for known issues" → @task-search-knowledge-base
   - "Apply fixes if build/restore fails" → @task-apply-knowledge-base-fix
   - "Retry build after applying fixes" → @task-build-solution (retry)

**Step 4: Read Variables from Markdown File**
Before executing each task, extract required variables from the markdown file:

**Variables Section (if present in file):**
```markdown
## Variables

- solution_name: {value}
- solution_path: {value}
- restore_status: {value}
- build_status: {value}
- kb_search_status: {value}
- kb_file_path: {value}
- fix_status: {value}
- retry_count: {value}
```

**If Variables section exists:**
- Parse each line to extract variable names and values
- Use these values when calling task prompts

**If Variables section does NOT exist:**
- Extract solution_name from section heading
- Extract solution_path from "**Path:**" line in solution section
- Initialize other variables as needed (e.g., retry_count = 0)

**Step 5: Execute Corresponding Task Prompt**
Based on task type identified in Step 3:

**Step 5: Execute Corresponding Task Prompt**
Based on task type identified in Step 3:

**⚠️ CRITICAL: DO NOT execute commands directly! Call the task prompts:**

**For "Restore packages for {solution_name}":**
1. **Call @task-restore-solution** (let the task prompt handle execution):
   ```
   @task-restore-solution solution_path="{solution_path}" solution_name="{solution_name}"
   ```
2. The task prompt will handle:
   - Whether it's scriptable (generates Python script) or non-scriptable (uses direct tool calls)
   - Executing `dotnet restore` command
   - Capturing output and status
3. Capture output from task prompt and update variables:
   - restore_status: SUCCESS | FAIL
   - restore_exit_code: exit code
4. Log to decision-log.csv

**For "Build solution {solution_name}":**
1. **Call @task-build-solution** (let the task prompt handle execution):
   ```
   @task-build-solution solution_path="{solution_path}" solution_name="{solution_name}"
   ```
2. The task prompt will handle:
   - Whether it's scriptable or non-scriptable
   - Executing `dotnet build` command
   - Parsing errors and warnings
3. Capture output from task prompt and update variables:
   - build_status: SUCCESS | FAIL
   - build_exit_code: exit code
   - errors: array of build errors
   - warnings: array of warnings
4. Log to decision-log.csv

**For "Search knowledge base for known issues":**
1. **CONDITIONAL EXECUTION - This task MUST execute if condition is met:**
   - Condition: restore_status == FAIL OR build_status == FAIL
   - If condition is TRUE → This task is MANDATORY and MUST be executed
   - If condition is FALSE (both restore and build succeeded) → Mark as [x] SKIPPED and move to next task
2. **Call @task-search-knowledge-base** (let the task prompt handle search logic):
   ```
   @task-search-knowledge-base solution_path="{solution_path}" solution_name="{solution_name}" build_status="{build_status}" errors="{errors}"
   ```
3. The task prompt will handle:
   - Searching knowledge_base_markdown/*.md files
   - Matching error patterns
   - Identifying KB file or creating new entry
4. Capture output from task prompt and update variables:
   - kb_search_status: FOUND | NOT_FOUND
   - kb_file_path: path to KB file (if FOUND)
   - error_code: detected error code
5. Log to decision-log.csv

**For "Apply fixes if build/restore fails":**
1. **CONDITIONAL EXECUTION - This task MUST execute if condition is met:**
   - Condition: kb_search_status == FOUND
   - If condition is TRUE → This task is MANDATORY and MUST be executed
   - If condition is FALSE (kb_search_status == NOT_FOUND) → Mark as [x] SKIPPED and move to next task (no fix available)
2. **Call @task-apply-knowledge-base-fix** (let the task prompt handle fix application):
   ```
   @task-apply-knowledge-base-fix solution_path="{solution_path}" kb_file_path="{kb_file_path}" error_code="{error_code}"
   ```
3. The task prompt will handle:
   - Reading fix instructions from KB markdown
   - Applying file modifications
   - Running fix commands
4. Capture output from task prompt and update variables:
   - fix_status: SUCCESS | FAIL
   - files_modified: list of files changed
5. Log to decision-log.csv

**For "Retry build after applying fixes":**
1. **CONDITIONAL EXECUTION - This task MUST execute if condition is met:**
   - Condition: fix_status == SUCCESS
   - If condition is TRUE → This task is MANDATORY and MUST be executed
   - If condition is FALSE (fix not applied) → Mark as [x] SKIPPED and move to next task
2. Increment retry_count
3. **Call @task-restore-solution** again (if restore failed initially)
4. **Call @task-build-solution** again
5. Capture output from task prompts and update variables (same as build task)
6. Log to decision-log.csv
7. If build still fails AND retry_count < 3:
   - Go back to "Search knowledge base" task for new error
8. If retry_count >= 3:
   - Mark as FAILED (max retries reached)

**🚫 NEVER do this:**
- `run_in_terminal("dotnet restore ...")` ❌
- `run_in_terminal("dotnet build ...")` ❌
- Creating Python scripts for solution tasks ❌
- Executing ANY commands yourself ❌

**✅ ALWAYS do this:**
- Call @task-restore-solution prompt ✅
- Call @task-build-solution prompt ✅
- Call @task-search-knowledge-base prompt ✅
- Call @task-apply-knowledge-base-fix prompt ✅
- Let task prompts decide scriptable vs non-scriptable ✅

**Step 6: Update Checklist After Task Execution**
1. Read the same solution_checklist.md file
2. Find the specific solution section (## {N}. {solution_name})
3. Find the task that was just executed
4. Update task checkbox from [ ] to [x]
5. Optionally append status to task line (e.g., "- [x] Restore packages for MySolution (SUCCESS)")
6. Write updated content back to file

**Step 7: Update Variables Section in Markdown**
1. Find or create ## Variables section in the solution section
2. Update variable values based on task execution results:
   ```markdown
   ## Variables
   
   - solution_name: MySolution
   - solution_path: C:\repos\myrepo\src\MySolution.sln
   - restore_status: SUCCESS
   - build_status: FAIL
   - kb_search_status: FOUND
   - kb_file_path: knowledge_base_markdown\nu1605_package_downgrade.md
   - error_code: NU1605
   - fix_status: SUCCESS
   - retry_count: 1
   ```
3. Write updated variables back to markdown file

**Step 8: Move to Next Uncompleted Task**
1. After updating checklist and variables, read the file again
2. Find the NEXT uncompleted [ ] task in the SAME solution section
3. If found, go back to Step 4 (read variables) and execute that task
4. If NO uncompleted tasks in current solution, mark solution as COMPLETE
5. Move to NEXT solution section in the same file
6. If NO more solutions in current file, move to NEXT solution_checklist.md file
7. If NO more files, autonomous execution is COMPLETE

**Step 9: Continue Loop Until All Work Complete**
Repeat Steps 3-8 until:
- ALL tasks in ALL solutions in ALL *solution_checklist.md files are marked [x]
- OR maximum execution time reached (safety limit)
- OR user interrupts execution

**Step 10: Generate Execution Summary**
When all work complete, create summary:
```
✅ Solution Task Execution Complete

Processed Files:
- ic3_spool_cosine-dep-spool_solution_checklist.md (8 solutions, 40 tasks)
- people_spool_usertokenmanagement_solution_checklist.md (5 solutions, 25 tasks)
- sync_calling_concore-conversation_solution_checklist.md (13 solutions, 65 tasks)

Summary:
- Total Solutions: 26
- Total Tasks Executed: 130
- Successful Builds: 20
- Failed Builds: 6
- KB Fixes Applied: 6
- Retries Performed: 8
```

Variables available during execution:
- {{repo_name}} → Extracted from filename
- {{solution_name}} → From section heading or variables
- {{solution_path}} → From "Path:" line or variables
- {{restore_status}} → From variables section (updated after restore)
- {{build_status}} → From variables section (updated after build)
- {{kb_search_status}} → From variables section (updated after KB search)
- {{kb_file_path}} → From variables section (updated after KB search)
- {{error_code}} → From variables section (updated after KB search)
- {{fix_status}} → From variables section (updated after fix applied)
- {{retry_count}} → From variables section (incremented on each retry)
- {{errors}} → Build errors array (from task output, not stored in markdown)
- {{warnings}} → Build warnings array (from task output, not stored in markdown)

Output Contract:
After autonomous execution completes, return:
- total_files_processed: integer
- total_solutions_processed: integer
- total_tasks_executed: integer
- successful_builds: integer
- failed_builds: integer
- kb_fixes_applied: integer
- retries_performed: integer
- execution_status: COMPLETE | PARTIAL | INTERRUPTED
- files_updated: array of solution_checklist.md files modified

Implementation Notes:
1. **Strict Sequential Execution**: Process ONE task at a time, in order, per solution
2. **Read Before Execute**: Always read current variable values from markdown before calling task
3. **Update After Execute**: Always update checklist and variables after task completes
4. **Conditional Tasks**: Skip KB tasks if build/restore succeeded
5. **Retry Logic**: Maximum 3 retries per solution after applying fixes
6. **Autonomous Loop**: Continue processing until all work complete or interrupted
7. **Safety Limit**: Stop if execution exceeds reasonable time (e.g., 2 hours)
8. **Logging**: Log every task execution to decision-log.csv
9. **File Parsing**: Robust parsing to handle different markdown formatting styles
10. **Error Recovery**: If a task fails, still mark it complete and move to next task
11. **⚠️ CRITICAL: NEVER execute commands directly - ALWAYS call task prompts**
12. **Task prompts handle scriptable vs non-scriptable internally**
13. **This executor is a coordinator, not a command executor**

Example Solution Section in Markdown:
```markdown
### 1. SDKTestApp

**Path:** `samples\External\samples\SDKTestApp\SDKTestApp.sln`

**Tasks:**
- [x] Restore packages for SDKTestApp (SUCCESS)
- [x] Build solution SDKTestApp (FAIL - NU1605)
- [x] Search knowledge base for known issues (FOUND)
- [x] Apply fixes if build/restore fails (SUCCESS)
- [x] Retry build after applying fixes (SUCCESS)

## Variables

- solution_name: SDKTestApp
- solution_path: C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool\samples\External\samples\SDKTestApp\SDKTestApp.sln
- restore_status: SUCCESS
- build_status: SUCCESS
- kb_search_status: FOUND
- kb_file_path: knowledge_base_markdown\nu1605_package_downgrade.md
- error_code: NU1605
- fix_status: SUCCESS
- retry_count: 1

---
```

**What This Prompt Does:**
- Autonomously discovers and processes all *solution_checklist.md files
- Executes tasks sequentially, one at a time
- Reads variables from markdown before each task
- Updates checklist and variables after each task
- Handles conditional task execution (KB workflow)
- Implements retry logic with maximum attempts
- Provides execution summary when complete

**What This Prompt Does NOT Do:**
- Does not generate solution checklists (use @generate-solution-task-checklists)
- Does not process repository-level tasks (use @execute-repo-task)
- Does not require manual input for each task
- Does not skip tasks or execute out of order
- Does not modify task definitions (only executes what's in checklist)
