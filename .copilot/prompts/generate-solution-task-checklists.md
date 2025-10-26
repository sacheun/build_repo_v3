# Task: @generate-solution-task-checklists

**THIS TASK IS SCRIPTABLE**

## Description:
Generate a solution-level checklist file for a repository.  
This is used to track progress for each solution (.sln) discovered in the repo.

If DEBUG=1, print parameter values.

---

## Behavior (Step by Step)

1. **Read Solutions Data**
   • Load JSON from `solutions_json_path`  
   • Extract `solutions` array  
   • Convert each into object `{name, path}`  
   • Log solution count if DEBUG=1

2. **Create Output File**
   • New file: `./tasks/{repo_name}_solution_checklist.md`  
   • Overwrite if it already exists  
   • Log creation if DEBUG=1

3. **Write File Header**
   ```
   # Solution Checklist: {repo_name}
   Repository: {repo_url}
   Generated: {timestamp}
   ---
   ```

4. **Generate Checklist Sections**
   For each solution:
   ```
   ## Solution: {solution_name}
   Path: {solution_path}

   ### Tasks
   - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution
   - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution
   - [ ] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base
   - [ ] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base
   - [ ] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry
   - [ ] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry
   - [ ] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry

   ### Solution Variables
   (Variables set by tasks for this specific solution)
   - solution_path → {solution_path}
   - solution_name → {solution_name}
   - max_build_attempts → 3
   - restore_status → NOT_EXECUTED
   - build_status → NOT_EXECUTED
   - kb_search_status → NOT_EXECUTED
   - kb_file_path → N/A
   - kb_article_status → NOT_EXECUTED
   - fix_applied_attempt_1 → NOT_EXECUTED
   - retry_build_status_attempt_1 → NOT_EXECUTED
   - fix_applied_attempt_2 → NOT_EXECUTED
   - retry_build_status_attempt_2 → NOT_EXECUTED
   - fix_applied_attempt_3 → NOT_EXECUTED
   - retry_build_status_attempt_3 → NOT_EXECUTED
   ```
   • Insert `---` as a separator between solutions  
   • Log generated section name if DEBUG=1

5. **Write and Close File**
   • Confirm file written successfully  
   • Log solution count if DEBUG=1

---

## Output Contract
JSON saved to:  
`output/{repo_name}_task6_generate-solution-checklists.json`

| Field | Type | Description |
|-------|------|-------------|
| repo_name | string | Echo of input |
| solutions_json_path | string | Echo of input |
| solutions_total | integer | Count of solutions processed |
| checklist_created | boolean | True if file created successfully |
| checklist_path | string | `./tasks/{repo_name}_solution_checklist.md` |
| status | SUCCESS or FAIL |
| timestamp | ISO8601 timestamp |

---

## Debug Logging (DEBUG=1)
Prefix: `[debug][generate-solution-task-checklists]`

Log messages for:
• START (with input parameters)  
• File creation  
• Each solution section  
• Completion summary  
• EXIT status

