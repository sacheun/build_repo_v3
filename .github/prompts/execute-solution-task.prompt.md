@execute-solution-task solution_checklist=<required>
---
temperature: 0.1
---

## Description:
This prompt finds all unmarked tasks from a solution checklist markdown file and executes them sequentially. Each checklist file contains tasks for ONE solution only. It processes all uncompleted tasks in the specified checklist until all are complete or an error occurs.

**CRITICAL REQUIREMENT:** After completing a task, you must update the designated solution markdown file by changing the task status from "[ ]" to "[x]" to reflect completion.

**⚠️ CRITICAL: This is an EXECUTOR prompt - it ONLY calls other task prompts. It does NOT execute commands directly.**

**CRITICAL - SEQUENTIAL EXECUTION:**
- This prompt executes ALL unmarked [ ] tasks in the checklist sequentially
- Tasks are executed in the order they appear in the checklist
- CONDITIONAL tasks execute when their condition is met, otherwise marked as SKIPPED
- Processing continues until all tasks are complete or a failure/blocking occurs

**CONDITIONAL Task Execution Rules:**
- CONDITIONAL means "execute IF condition is met"
- When condition is TRUE → Task is executed
- When condition is FALSE → Task is SKIPPED (mark as [x] SKIPPED)
- Example: "@task-search-knowledge-base" is CONDITIONAL on build failure
  - If build FAILED → Execute @task-search-knowledge-base
  - If build SUCCEEDED → Mark as [x] SKIPPED

## Behavior (Follow this Step by Step)

**Step 0: Initialize Parameters**
1. Required parameters:
      solution_checklist = <required> (path to solution checklist markdown file for ONE solution, e.g., "./tasks/ic3_spool_cosine-dep-spool_ResourceProvider_solution_checklist.md")
2. **[MANDATORY] Initialize solution_result.csv tracking file:**
   - Check if file `results/solution_result.csv` exists
   - If it does NOT exist, create it with the following header row:
     ```
     repo,solution,task name,status
     ```

**Step 1: Read Solution Checklist and Find Next Unmarked Task**
1. Read the solution checklist file specified by solution_checklist parameter
2. Parse the solution section (## Solution: {solution_name})
   - Note: Each checklist file contains ONLY ONE solution
3. Within that solution section, find the FIRST task with `- [ ]` (unmarked/uncompleted)
4. If no unmarked tasks found, return status: ALL_TASKS_COMPLETE
5. Extract task_name and task_number from that line (e.g., "#1", "@task-restore-solution")
6. Extract repo_name from checklist filename (e.g., "ic3_spool_cosine-dep-spool" from "ic3_spool_cosine-dep-spool_ResourceProvider_solution_checklist.md")
7. Extract solution_name from section heading (e.g., "## Solution: ResourceProvider")
8. **Read existing "### Solution Variables" section (if it exists)**:
   - Parse all variable values from previous task executions
   - Store these values for use in task parameter preparation
9. **Continue to next step to execute this task**

**Step 2: Prepare Task Parameters**

**Task Numbering and Attempt Tracking:**
Tasks are numbered #1-10 with specific attempt numbers for retry tasks:
- [MANDATORY #1] Restore NuGet packages
- [MANDATORY #2] Build solution (Clean + Build)
- [CONDITIONAL #3] Search knowledge base for error fix
- [CONDITIONAL #4] Create knowledge base article
- [CONDITIONAL #5 - Attempt 1] Apply fix from KB
- [CONDITIONAL #6 - Attempt 1] Retry build after fix
- [CONDITIONAL #7 - Attempt 2] Apply fix from KB
- [CONDITIONAL #8 - Attempt 2] Retry build after fix
- [CONDITIONAL #9 - Attempt 3] Apply fix from KB
- [CONDITIONAL #10 - Attempt 3] Retry build after fix

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

For the FIRST uncompleted [ ] task found:

1. Identify task type from task description and task number:
   - [MANDATORY #1] → @task-restore-solution
   - [MANDATORY #2] → @task-build-solution  
   - [CONDITIONAL #3] → @task-search-knowledge-base
   - [CONDITIONAL #4] → @task-create-knowledge-base
   - [CONDITIONAL #5/7/9] → @task-apply-knowledge-base-fix (with attempt number)
   - [CONDITIONAL #6/8/10] → @task-build-solution-retry (with attempt number)

2. **Prepare parameters using variables from checklist**:
   - Read "### Solution Variables" section from the current solution in the checklist
   - Extract solution_path, solution_name, and task-specific variables
   - For CONDITIONAL tasks, read condition variables to determine if task should execute

**Step 3: Gather Required Input Data**

Before executing the task, gather all required variables from the "### Solution Variables" section:

**Variables Section Format:**
```markdown

### Solution Variables

(Variables set by tasks for this specific solution)

- {{solution_path}} → path value
- {{solution_name}} → name value
- {{max_build_attempts}} → 3
- {{restore_status}} → SUCCEEDED | FAILED | NOT_EXECUTED
- {{build_status}} → SUCCEEDED | FAILED | NOT_EXECUTED | SKIPPED
- {{kb_search_status}} → COMPLETED | SKIPPED | NOT_FOUND
- {{kb_file_path}} → path or N/A
- {{kb_article_status}} → EXISTS | CREATED | SKIPPED

**Retry Attempt 1:**
- {{fix_applied_attempt_1}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_1}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_1}} → SUCCEEDED | FAILED | SKIPPED

**Retry Attempt 2:**
- {{fix_applied_attempt_2}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_2}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_2}} → SUCCEEDED | FAILED | SKIPPED

**Retry Attempt 3:**
- {{fix_applied_attempt_3}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_3}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_3}} → SUCCEEDED | FAILED | SKIPPED
```

**Variable Reading Logic:**
1. Parse the **Solution Variables** section for the current solution
2. Extract all variable values (text after →)
3. Use these values to determine conditional task execution
4. For retry attempts, read the specific attempt variables:
   - For tasks #5-6 (Attempt 1): Use {{fix_applied_attempt_1}} and {{retry_build_status_attempt_1}}
   - For tasks #7-8 (Attempt 2): Use {{fix_applied_attempt_2}} and {{retry_build_status_attempt_2}}
   - For tasks #9-10 (Attempt 3): Use {{fix_applied_attempt_3}} and {{retry_build_status_attempt_3}}

**If Variables section does NOT exist:**
- Extract solution_name from section heading
- Extract solution_path from "Path:" line in solution section
- Initialize all variables with default values (e.g., NOT_EXECUTED, N/A, SKIPPED)

**Step 4: Execute Corresponding Task Prompt**
Based on task type identified in Step 3:

**⚠️ CRITICAL: DO NOT execute commands directly! Call the task prompts:**

**📋 IMPORTANT REMINDER FOR RETRY TASKS (#6, #8, #10):**
After every retry build completes, you MUST call @task-update-knowledgebase-log to track KB fix effectiveness.
This is a mandatory step - do not skip it. See step 6 in the retry workflow below for details.

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
2. **Determine last_option_applied parameter:**
   - For CONDITIONAL #5 (Attempt 1): last_option_applied is NOT provided (use Option 1)
   - For CONDITIONAL #7 (Attempt 2): Read {{kb_option_applied_attempt_1}} from variables and pass as last_option_applied
   - For CONDITIONAL #9 (Attempt 3): Read {{kb_option_applied_attempt_2}} from variables and pass as last_option_applied
3. **Call @task-apply-knowledge-base-fix** (let the task prompt handle fix application):
   
   For Attempt 1:
   ```
   @task-apply-knowledge-base-fix solution_path="{solution_path}" kb_file_path="{kb_file_path}" error_code="{error_code}"
   ```
   
   For Attempt 2:
   ```
   @task-apply-knowledge-base-fix solution_path="{solution_path}" kb_file_path="{kb_file_path}" error_code="{error_code}" last_option_applied="{kb_option_applied_attempt_1}"
   ```
   
   For Attempt 3:
   ```
   @task-apply-knowledge-base-fix solution_path="{solution_path}" kb_file_path="{kb_file_path}" error_code="{error_code}" last_option_applied="{kb_option_applied_attempt_2}"
   ```
4. The task prompt will handle:
   - Reading fix instructions from KB markdown
   - Determining which option to apply based on last_option_applied
   - Applying file modifications
   - Running fix commands
5. Capture output from task prompt and update variables:
   - fix_status: SUCCESS | FAIL | NO_MORE_OPTIONS
   - option_applied: 1 | 2 | 3 | null (from JSON output)
   - files_modified: list of files changed
6. Update attempt-specific variables:
   - For Attempt 1: {{kb_option_applied_attempt_1}} = option_applied
   - For Attempt 2: {{kb_option_applied_attempt_2}} = option_applied
   - For Attempt 3: {{kb_option_applied_attempt_3}} = option_applied
7. Log to decision-log.csv

**For "Retry build after applying fixes":**
1. **CONDITIONAL EXECUTION - This task MUST execute if condition is met:**
   - Condition: fix_status == SUCCESS
   - If condition is TRUE → This task is MANDATORY and MUST be executed
   - If condition is FALSE (fix not applied) → Mark as [x] SKIPPED and move to next task
2. Increment retry_count
3. **Call @task-restore-solution** again (if restore failed initially)
4. **Call @task-build-solution** again
5. Capture output from task prompts and update variables (same as build task)

**🔴 CRITICAL STEP 6 - DO NOT SKIP:**

6. **[MANDATORY] Call @task-update-knowledgebase-log** after EVERY rebuild to log the KB fix result:
   
   **⚠️ THIS STEP IS REQUIRED - DO NOT SKIP THIS STEP ⚠️**
   
   You MUST call this task immediately after the rebuild completes to track which KB fixes work.
   
   **Parameters to extract:**
   - `knowledgebase_file`: Extract filename from {{kb_file_path}} (filename only, e.g., "code_analyzer_errors_ide0040_ca1859.md")
   - `option`: Use the option number from the corresponding attempt:
     * For Task #6 (Attempt 1): Use {{kb_option_applied_attempt_1}} value
     * For Task #8 (Attempt 2): Use {{kb_option_applied_attempt_2}} value
     * For Task #10 (Attempt 3): Use {{kb_option_applied_attempt_3}} value
   - `status`: Use the retry build result:
     * If retry_build_status == SUCCEEDED → status="SUCCESS"
     * If retry_build_status == FAILED → status="FAIL"
   - `repo_name`: Use {{repo_name}}
   
   **How to call:**
   ```
   @task-update-knowledgebase-log knowledgebase_file="{kb_filename}" option="{option_number}" status="{status}" repo_name="{repo_name}"
   ```
   
   **Example for this case (Attempt 1):**
   ```
   @task-update-knowledgebase-log knowledgebase_file="code_analyzer_errors_ide0040_ca1859.md" option="1" status="FAIL" repo_name="ic3_spool_cosine-dep-spool"
   ```
   
   **This updates:**
   - Knowledgebase usage log (results/knowledgebase-usage-log.csv)
   - KB statistics (which fixes work, which don't)

7. Log to decision-log.csv
8. If build still fails AND retry_count < 3:
   - Go back to "Search knowledge base" task for new error
9. If retry_count >= 3:
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

**Step 5: Update Checklist After Task Execution**

**Step 6: [MANDATORY] Log task execution to solution_result.csv**
1. **After each task is performed (regardless of success, failure, or skip), add 1 row to results/solution_result.csv:**
   - Column 1 (repo): {repo_name} (e.g., "ic3_spool_cosine-dep-spool")
   - Column 2 (solution): {solution_name} (e.g., "ResourceProvider")
   - Column 3 (task name): {task_name} (e.g., "@task-restore-solution" or "@task-build-solution")
   - Column 4 (status): SUCCESS | FAIL | BLOCKED | SKIPPED
2. **Append the row to the existing CSV file** (do not overwrite the file)
3. **This step is MANDATORY and must be performed for EVERY task execution**
4. Example row: `ic3_spool_cosine-dep-spool,ResourceProvider,@task-restore-solution,SUCCESS`
5. Example row for skipped: `ic3_spool_cosine-dep-spool,ResourceProvider,@task-search-knowledge-base,SKIPPED`

1. Read the same solution_checklist.md file
2. Find the specific solution section (## Solution: {solution_name})
3. Find the task that was just executed by task number
4. Update task checkbox from [ ] to [x]
5. Append status/reason to task line based on execution result:
   - For MANDATORY tasks: Include result (e.g., "- [x] [MANDATORY #1] Restore NuGet packages @task-restore-solution")
   - For CONDITIONAL tasks that executed: Include result (e.g., "- [x] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base")
   - For CONDITIONAL tasks that were skipped: Include reason in parentheses:
     * "- [x] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base - SKIPPED (build succeeded)"
     * "- [x] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base - SKIPPED (KB found)"
     * "- [x] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix - SKIPPED (build succeeded)"
     * "- [x] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry - SKIPPED (no fix applied)"
     * "- [x] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix - SKIPPED (previous retry succeeded)"
6. Write updated content back to file

**Step 7: Update Variables Section in Markdown**
1. Find the **Solution Variables** section in the current solution section
2. Update variable values based on task execution results:
   
   **After MANDATORY #1 (Restore):**
   - Update {{restore_status}} → SUCCEEDED | FAILED
   
   **After MANDATORY #2 (Build):**
   - Update {{build_status}} → SUCCEEDED | FAILED | SKIPPED
   
   **After CONDITIONAL #3 (KB Search):**
   - Update {{kb_search_status}} → COMPLETED | SKIPPED
   - Update {{kb_file_path}} → path or N/A
   
   **After CONDITIONAL #4 (KB Create):**
   - Update {{kb_article_status}} → CREATED | SKIPPED
   
   **After CONDITIONAL #5 (Apply fix - Attempt 1):**
   - Update **Retry Attempt 1** section:
     * {{fix_applied_attempt_1}} → APPLIED | NOT_APPLIED | SKIPPED (with reason)
     * {{kb_option_applied_attempt_1}} → option number (1, 2, 3) from task output, or null if NO_MORE_OPTIONS or not applied
   
   **After CONDITIONAL #6 (Retry build - Attempt 1):**
   - Update **Retry Attempt 1** section:
     * {{retry_build_status_attempt_1}} → SUCCEEDED | FAILED | SKIPPED (with reason)
   
   **After CONDITIONAL #7 (Apply fix - Attempt 2):**
   - Update **Retry Attempt 2** section:
     * {{fix_applied_attempt_2}} → APPLIED | NOT_APPLIED | SKIPPED (with reason)
     * {{kb_option_applied_attempt_2}} → option number (1, 2, 3) from task output, or null if NO_MORE_OPTIONS or not applied
   
   **After CONDITIONAL #8 (Retry build - Attempt 2):**
   - Update **Retry Attempt 2** section:
     * {{retry_build_status_attempt_2}} → SUCCEEDED | FAILED | SKIPPED (with reason)
   
   **After CONDITIONAL #9 (Apply fix - Attempt 3):**
   - Update **Retry Attempt 3** section:
     * {{fix_applied_attempt_3}} → APPLIED | NOT_APPLIED | SKIPPED (with reason)
     * {{kb_option_applied_attempt_3}} → option number (1, 2, 3) from task output, or null if NO_MORE_OPTIONS or not applied
   
   **After CONDITIONAL #10 (Retry build - Attempt 3):**
   - Update **Retry Attempt 3** section:
     * {{retry_build_status_attempt_3}} → SUCCEEDED | FAILED | SKIPPED (with reason)

3. Write updated variables back to markdown file
4. Ensure proper formatting with → separator and attempt subsections

**⚠️ CRITICAL - FORMAT CONSISTENCY REQUIREMENT:**

ALL solution_checklist.md files MUST follow this exact format for Solution Variables section:

```markdown
### Solution Variables

(Variables set by tasks for this specific solution)

- solution_path → {value}
- solution_name → {value}
- max_build_attempts → 3
- restore_status → {value}
- build_status → {value}
- kb_search_status → {value}
- kb_file_path → {value}
- kb_article_status → {value}
- fix_applied_attempt_1 → {value}
- retry_build_status_attempt_1 → {value}
- fix_applied_attempt_2 → {value}
- retry_build_status_attempt_2 → {value}
- fix_applied_attempt_3 → {value}
- retry_build_status_attempt_3 → {value}

---
```

**Format Rules (MANDATORY):**
1. Section header MUST be exactly: `### Solution Variables`
2. Parenthetical MUST be exactly: `(Variables set by tasks for this specific solution)`
3. Variable format MUST be: `variable_name → value` (with → arrow character U+2192, not ASCII ->)
4. Variables MUST be in the order listed above
5. Solution separator MUST be exactly: `---` (three dashes on separate line)
6. All 14 variables MUST be present in every solution section

**Before updating any variables:**
- Verify the Solution Variables section exists and follows this exact format
- If format is incorrect or section is missing, recreate it with the correct structure
- If you're creating a new solution_checklist.md file, always include this section

**Step 8: Loop Back to Process Next Unmarked Task**
1. After updating checklist and variables, return to **Step 1**
2. Step 1 will read the updated checklist and find the NEXT unmarked [ ] task in the solution
3. If found, Steps 2-5 will execute that task
4. If NO unmarked tasks remain, execution is COMPLETE for this solution checklist file

**Note:** This creates a continuous loop: Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → back to Step 1, until all tasks in the provided solution_checklist file are marked [x]. Since each checklist file contains only ONE solution, this processes all tasks for that single solution.

Variables available during execution:
- {{repo_name}} → Extracted from filename
- {{solution_name}} → From section heading or variables
- {{solution_path}} → From "Path:" line or variables
- {{max_build_attempts}} → Maximum retry attempts (3)
- {{restore_status}} → SUCCEEDED | FAILED | NOT_EXECUTED
- {{build_status}} → SUCCEEDED | FAILED | NOT_EXECUTED | SKIPPED
- {{kb_search_status}} → COMPLETED | SKIPPED | NOT_FOUND
- {{kb_file_path}} → Path to KB file or N/A
- {{kb_article_status}} → EXISTS | CREATED | SKIPPED
- {{fix_applied_attempt_1}} → APPLIED | NOT_APPLIED | SKIPPED (reason)
- {{kb_option_applied_attempt_1}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_1}} → SUCCEEDED | FAILED | SKIPPED (reason)
- {{fix_applied_attempt_2}} → APPLIED | NOT_APPLIED | SKIPPED (reason)
- {{kb_option_applied_attempt_2}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_2}} → SUCCEEDED | FAILED | SKIPPED (reason)
- {{fix_applied_attempt_3}} → APPLIED | NOT_APPLIED | SKIPPED (reason)
- {{kb_option_applied_attempt_3}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_3}} → SUCCEEDED | FAILED | SKIPPED (reason)
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
4. **Conditional Tasks**: Evaluate condition based on specific variables for each task number
5. **Retry Logic**: Maximum 3 retry attempts (tasks #5-10), each with separate status tracking
6. **Attempt-Specific Variables**: Track {{fix_applied_attempt_N}} and {{retry_build_status_attempt_N}} for each attempt
7. **Skip Reasons**: Include clear reasons when marking CONDITIONAL tasks as SKIPPED
8. **Variable Format**: Use → separator and maintain **Retry Attempt N** subsections
9. **Autonomous Loop**: Continue processing until all work complete or interrupted
10. **Safety Limit**: Stop if execution exceeds reasonable time (e.g., 2 hours)
11. **Logging**: Log every task execution to decision-log.csv
12. **File Parsing**: Robust parsing to handle different markdown formatting styles
13. **Error Recovery**: If a task fails, still mark it complete and move to next task
14. **⚠️ CRITICAL: NEVER execute commands directly - ALWAYS call task prompts**
15. **Task prompts handle scriptable vs non-scriptable internally**
16. **This executor is a coordinator, not a command executor**
17. **Condition Checking**: For retry attempts, check previous attempt status to determine if current attempt should execute or be skipped

Example Solution Section in Markdown:
```markdown
## Solution: SDKTestApp

Path: `C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool\samples\External\samples\SDKTestApp\SDKTestApp.sln`

### Tasks (Conditional Workflow - See execute-solution-task.md)

- [x] [MANDATORY #1] Restore NuGet packages @task-restore-solution
- [x] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution
- [x] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base
- [x] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base
- [x] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix
- [x] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry
- [x] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix
- [x] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry
- [x] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix
- [x] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry

### Solution Variables

(Variables set by tasks for this specific solution)

- {{solution_path}} → `C:\Users\sacheu\speckit_repos\ic3_spool_cosine-dep-spool\samples\External\samples\SDKTestApp\SDKTestApp.sln`
- {{solution_name}} → `SDKTestApp`
- {{max_build_attempts}} → 3
- {{restore_status}} → SUCCEEDED
- {{build_status}} → FAILED - NU1605 package downgrade error
- {{kb_search_status}} → COMPLETED
- {{kb_file_path}} → knowledge_base_markdown/nu1605_package_downgrade.md
- {{kb_article_status}} → EXISTS

**Retry Attempt 1:**
- {{fix_applied_attempt_1}} → APPLIED (updated PackageReference versions)
- {{kb_option_applied_attempt_1}} → 1
- {{retry_build_status_attempt_1}} → SUCCEEDED

**Retry Attempt 2:**
- {{fix_applied_attempt_2}} → SKIPPED (previous retry succeeded)
- {{kb_option_applied_attempt_2}} → null
- {{retry_build_status_attempt_2}} → SKIPPED (no fix applied)

**Retry Attempt 3:**
- {{fix_applied_attempt_3}} → SKIPPED (previous retry succeeded)
- {{kb_option_applied_attempt_3}} → null
- {{retry_build_status_attempt_3}} → SKIPPED (no fix applied)

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
