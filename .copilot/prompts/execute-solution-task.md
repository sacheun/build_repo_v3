@execute-solution-task repo_name={{repo_name}} solution_name={{solution_name}} solution_path={{solution_path}}
---
temperature: 0.1
---

Description:
This prompt executes solution-level tasks for a single Visual Studio solution. It handles restore, build, and knowledge base workflow for build failures.

This is typically invoked by @execute-repo-task when processing solutions, or can be called directly for a specific solution.

**Solution Task Workflow:**
1. Execute @task-restore-solution
2. Execute @task-build-solution
3. IF restore OR build fails → Execute KB Workflow (MANDATORY)
4. Update solution section in repository checklist
5. Return status

Behavior:

**Step 1: Validate Input Parameters**
1. Required parameters:
   - repo_name: Repository name (for checklist updates and logging)
   - solution_name: Solution name (e.g., "MySolution.sln")
   - solution_path: Absolute path to .sln file
2. Validate solution_path exists
3. If solution file not found, return status: BLOCKED with error message

**Step 2: Read Solution Task Checklist**
1. Read ./tasks/{repo_name}_checklist.md
2. Find the section: "## Solution: {solution_name}"
3. Parse solution-level tasks within this section
4. Find the first task with `- [ ]` (uncompleted)
5. If all solution tasks are complete `- [x]`, return status: COMPLETE

**Step 3: Execute Solution Tasks in Sequence**

**Task 1: Restore Solution**
1. Log to decision-log.csv: "Starting restore for {solution_name}"
2. Execute @task-restore-solution with:
   - solution_path: {solution_path}
3. Capture output:
   - restore_status: SUCCESS | FAIL
   - restore_stdout: command output
   - restore_stderr: error output
   - restore_exit_code: exit code
4. Log result to decision-log.csv
5. Update checklist: Mark "Restore solution" as [x]

**Task 2: Build Solution**
1. Log to decision-log.csv: "Starting build for {solution_name}"
2. Execute @task-build-solution with:
   - solution_path: {solution_path}
3. Capture output:
   - build_status: SUCCESS | FAIL
   - build_stdout: command output
   - build_stderr: error output
   - build_exit_code: exit code
   - errors: array of error objects
   - warnings: array of warning objects
4. Log result to decision-log.csv
5. Update checklist: Mark "Build solution" as [x]

**Step 4: KB Workflow (Conditional - Execute if Restore OR Build Failed)**

**⚠️ CRITICAL: KB Workflow is MANDATORY for ALL build/restore failures!**

IF restore_status == FAIL OR build_status == FAIL:

**Sub-step 4a: Search Knowledge Base**
1. Log to decision-log.csv: "Searching knowledge base for {solution_name}"
2. Execute @task-search-knowledge-base with:
   - solution_path: {solution_path}
   - solution_name: {solution_name}
   - build_status: {build_status}
   - build_stderr: {build_stderr}
   - errors: {errors}
   - warnings: {warnings}
3. Capture output:
   - kb_search_status: FOUND | NOT_FOUND
   - kb_file_path: path to KB markdown file (if FOUND)
   - error_signature: detected error pattern
   - error_code: extracted error code
4. Log result to decision-log.csv with status FOUND or NOT_FOUND
5. Update checklist: Mark "Search knowledge base" as [x] with status

**Sub-step 4b: Create Knowledge Base Entry (Conditional - if NOT_FOUND)**
IF kb_search_status == NOT_FOUND:
1. Log to decision-log.csv: "Creating knowledge base entry for {solution_name}"
2. Execute @task-create-knowledge-base with:
   - solution_path: {solution_path}
   - solution_name: {solution_name}
   - kb_search_status: NOT_FOUND
   - detection_tokens: {detection_tokens}
   - error_signature: {error_signature}
   - error_code: {error_code}
   - error_type: {error_type}
   - build_stderr: {build_stderr}
   - errors: {errors}
   - warnings: {warnings}
3. Capture output:
   - kb_create_status: SUCCESS | FAIL
   - new_kb_file_path: path to newly created KB markdown file
4. Log result to decision-log.csv with status SUCCESS or FAIL
5. Update checklist: Mark "Create KB entry" as [x] with status
6. Execute @task-search-knowledge-base AGAIN (will be FOUND now)
   - Update kb_file_path with new_kb_file_path

**Sub-step 4c: Apply Knowledge Base Fix (MANDATORY)**
1. Log to decision-log.csv: "Applying knowledge base fix for {solution_name}"
2. Execute @task-apply-knowledge-base-fix with:
   - solution_path: {solution_path}
   - kb_file_path: {kb_file_path}
   - error_code: {error_code}
3. Capture output:
   - fix_status: SUCCESS | FAIL
   - fix_applied: description of fix
   - files_modified: list of files changed
4. Log result to decision-log.csv with status SUCCESS or FAIL
5. Update checklist: Mark "Apply fix" as [x] with status

**Sub-step 4d: Retry Build After Fix (MANDATORY)**
1. Log to decision-log.csv: "Retrying build after fix for {solution_name} (attempt {retry_count})"
2. Execute @task-restore-solution (if restore failed initially)
3. Execute @task-build-solution
4. Capture output (same as Step 3)
5. Log result to decision-log.csv
6. IF build still fails AND retry_count < 3:
   - Increment retry_count
   - Go back to Sub-step 4a (search KB again for new error)
7. IF build still fails AND retry_count >= 3:
   - Log to decision-log.csv: "Maximum retries reached for {solution_name}"
   - Set final_status: FAIL
8. IF build succeeds:
   - Log to decision-log.csv: "Build succeeded after fix for {solution_name}"
   - Set final_status: SUCCESS

ELSE (restore and build both succeeded):
- Skip KB workflow entirely
- Set final_status: SUCCESS

**Step 5: Update Solution Checklist**
1. Read ./tasks/{repo_name}_checklist.md
2. Find section: "## Solution: {solution_name}"
3. Update task checkboxes based on execution:
   - Mark "Restore solution" as [x]
   - Mark "Build solution" as [x] with status (SUCCESS/FAIL)
   - IF KB workflow executed:
     - Mark "Search knowledge base" as [x] with status (FOUND/NOT_FOUND)
     - Mark "Create KB entry" as [x] if NOT_FOUND (with SUCCESS/FAIL)
     - Mark "Apply fix" as [x] with status (SUCCESS/FAIL)
4. Write updated checklist back to file

**Step 6: Save Solution Output**
1. Create JSON file: output/{repo_name}_{solution_name}_solution-tasks.json
2. Include all execution results:
   - solution_name
   - solution_path
   - restore_status
   - build_status
   - kb_workflow_executed: true/false
   - kb_search_status (if KB executed)
   - kb_create_status (if KB entry created)
   - fix_status (if fix applied)
   - retry_count
   - final_status: SUCCESS | FAIL
   - timestamp

**Step 7: Return Solution Task Summary**
Return object with:
- solution_name: string
- solution_path: string
- tasks_executed: array of task names
- final_status: SUCCESS | FAIL
- kb_workflow_executed: boolean
- retry_count: integer
- output_file: path to JSON output

Variables available:
- {{repo_name}} → Repository name for checklist updates
- {{solution_name}} → Solution filename (e.g., "MySolution.sln")
- {{solution_path}} → Absolute path to .sln file
- {{restore_status}} → Result of restore task (SUCCESS/FAIL)
- {{build_status}} → Result of build task (SUCCESS/FAIL)
- {{kb_search_status}} → Result of KB search (FOUND/NOT_FOUND)
- {{kb_file_path}} → Path to KB markdown file
- {{fix_status}} → Result of applying fix (SUCCESS/FAIL)
- {{retry_count}} → Number of retry attempts after fix

Output Contract:
- solution_name: string
- solution_path: string
- tasks_executed: array of strings (task names)
- final_status: SUCCESS | FAIL
- kb_workflow_executed: boolean
- kb_search_status: FOUND | NOT_FOUND | null
- kb_create_status: SUCCESS | FAIL | null
- fix_status: SUCCESS | FAIL | null
- retry_count: integer
- output_file: string (path to JSON output)

Implementation Notes:
1. **KB Workflow is MANDATORY**: Never skip KB workflow for build/restore failures
2. **Sequential Execution**: Execute tasks in order: restore → build → (KB if needed) → retry
3. **Retry Logic**: Maximum 3 retry attempts after applying fix
4. **Checklist Updates**: Update checkboxes immediately after each task completes
5. **Logging**: Log every task execution to decision-log.csv with status
6. **Error Handling**: If KB workflow fails, still mark tasks as attempted and log failure
7. **Status Propagation**: final_status is SUCCESS only if build succeeds (with or without KB workflow)
8. **Output Persistence**: Save all execution details to JSON for debugging and reporting

Example Execution Flow:

**Scenario 1: Build Succeeds Without Issues**
```
1. Restore → SUCCESS
2. Build → SUCCESS
3. Skip KB workflow
4. final_status: SUCCESS
```

**Scenario 2: Build Fails, KB Fix Applied Successfully**
```
1. Restore → SUCCESS
2. Build → FAIL (error: NU1605)
3. Search KB → FOUND (kb_file: nu1605_package_downgrade.md)
4. Apply Fix → SUCCESS (downgraded package in .csproj)
5. Retry Restore → SUCCESS
6. Retry Build → SUCCESS
7. final_status: SUCCESS
```

**Scenario 3: Build Fails, KB Entry Created**
```
1. Restore → SUCCESS
2. Build → FAIL (error: NETSDK1045)
3. Search KB → NOT_FOUND
4. Create KB → SUCCESS (researched solution, created new KB file)
5. Search KB → FOUND (newly created KB file)
6. Apply Fix → SUCCESS
7. Retry Build → SUCCESS
8. final_status: SUCCESS
```

**Scenario 4: Build Fails, Max Retries Reached**
```
1. Restore → SUCCESS
2. Build → FAIL (error: CS0246)
3. Search KB → FOUND
4. Apply Fix → SUCCESS
5. Retry Build → FAIL (same error)
6. Search KB → FOUND (same KB)
7. Apply Fix → SUCCESS
8. Retry Build → FAIL (same error)
9. Search KB → FOUND
10. Apply Fix → SUCCESS
11. Retry Build → FAIL
12. Max retries (3) reached
13. final_status: FAIL
```

**What This Prompt Does NOT Do:**
- Does not process multiple solutions (use @execute-repo-task for that)
- Does not update master repository checklist (only solution section)
- Does not make decisions about which solutions to process (that's executor's job)
- Does not handle solution-level task generation (that's @generate-solution-task-checklists)

**Integration with @execute-repo-task:**
The parent executor (@execute-repo-task) will:
1. Find solutions from @task-find-solutions output
2. For each solution, invoke @execute-solution-task
3. Aggregate results from all solutions
4. Update master repository checklist when all solutions complete
