---
temperature: 0.0
---

@generate-solution-task-checklists

Task name: generate-repo-task-checklists

## Description:
Generate individual solution-level checklist files for a repository.  
This creates ONE checklist file per solution (.sln) discovered in the repo.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
Read Solutions Data
   • Load JSON from `solutions_json` variable in the ./tasks/{repo_name}_checklist.md context
   • Extract `solutions` array variable in the ./tasks/{repo_name}_checklist.md context
   • Convert each into object `{name, path}`  
   • Log solution count if DEBUG=1

### Step 2 (MANDATORY)
Parse Task Definitions
   • Read `.github/prompts/execute-solution-task.prompt.md` to extract:
     - All task directives (e.g., @task-restore-solution, @task-build-solution, etc.)
     - Short descriptions for each task
     - The complete "### Solution Variables" section content
   • If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted {{task_count}} tasks from execute-solution-task.prompt.md`
   • Store the variables section for inclusion in each solution section

### Step 3 (MANDATORY)
Create One Checklist File Per Solution
   For each solution in the solutions array:
   • Create new file: `./tasks/{repo_name}_{solution_name}_solution_checklist.md`  
   • Sanitize solution_name for filename (replace spaces/special chars with underscores)
   • Overwrite if it already exists  
   • Each solution gets its own dedicated checklist file
   • Log creation if DEBUG=1

### Step 4 (MANDATORY)
Write File Header (for each solution file)
   ```
   # Solution Checklist: {solution_name}
   Repository: {repo_name}
   Solution Path: `{solution_path}`
   Generated: {timestamp}
   ```
   
### Step 5 (MANDATORY)
Generate Checklist Content (for each solution file)
   ```
   ## Solution: {solution_name}
   Path: `{solution_path}`

   ### Tasks
   - [ ] [MANDATORY #1] [SCRIPTABLE] Restore NuGet packages @task-restore-solution
   - [ ] [MANDATORY #2] [SCRIPTABLE] Build solution (Clean + Build) @task-build-solution
   - [ ] [CONDITIONAL #3] [NON-SCRIPTABLE] Search knowledge base for error fix @task-search-knowledge-base
   - [ ] [CONDITIONAL #4] [NON-SCRIPTABLE] Create knowledge base article @task-create-knowledge-base
   - [ ] [CONDITIONAL #5 - Attempt 1] [NON-SCRIPTABLE] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #6 - Attempt 1] [SCRIPTABLE] Retry build after fix @task-build-solution-retry
   - [ ] [CONDITIONAL #7 - Attempt 2] [NON-SCRIPTABLE] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #8 - Attempt 2] [SCRIPTABLE] Retry build after fix @task-build-solution-retry
   - [ ] [CONDITIONAL #9 - Attempt 3] [NON-SCRIPTABLE] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL #10 - Attempt 3] [SCRIPTABLE] Retry build after fix @task-build-solution-retry

   ## For Agents Resuming Work

   **Next Action:** 
   1. Check if all [MANDATORY] tasks (#1-#2) are completed
   2. If restore/build failed, execute conditional tasks (#3-#4) for knowledge base search/creation
   3. If knowledge base articles exist, execute retry attempts (#5-#10) as needed
   4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

   **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-restore-solution`) as defined in `.github\prompts\execute-solution-task.prompt.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.

   **Quick Reference:**
   - [MANDATORY] tasks must be completed in numbered order (#1 → #2)
   - [CONDITIONAL] tasks (#3-#10) execute based on success/failure of mandatory tasks and retry logic
   - [SCRIPTABLE] tasks can be automated with scripts
   - [NON-SCRIPTABLE] tasks require AI reasoning and direct tool calls
   - Mark completed tasks with [x]
   - Check Solution Variables section below for current task status and retry attempt tracking

   ### Solution Variables
   (Variables set by tasks for this specific solution)
   - solution_path → `{solution_path}`
   - solution_name → `{solution_name}`
   - max_build_attempts → 3
   - restore_status → NOT_EXECUTED
   - build_status → NOT_EXECUTED
   - kb_search_status → NOT_EXECUTED
   - kb_file_path → N/A
   - kb_article_status → NOT_EXECUTED
   
   **Retry Attempt 1:**
   - fix_applied_attempt_1 → NOT_EXECUTED
   - kb_option_applied_attempt_1 → null
   - retry_build_status_attempt_1 → NOT_EXECUTED
   
   **Retry Attempt 2:**
   - fix_applied_attempt_2 → NOT_EXECUTED
   - kb_option_applied_attempt_2 → null
   - retry_build_status_attempt_2 → NOT_EXECUTED
   
   **Retry Attempt 3:**
   - fix_applied_attempt_3 → NOT_EXECUTED
   - kb_option_applied_attempt_3 → null
   - retry_build_status_attempt_3 → NOT_EXECUTED

   [Content dynamically extracted from .github/prompts/execute-solution-task.prompt.md "### Solution Variables" section]
   ```
   • Each solution file is self-contained with all its tasks and variables
   • No separator needed (each solution is in its own file)
   • Log generated file path if DEBUG=1
   • **Variables Section**: Include the explicit retry attempt variables above PLUS dynamically extract any additional variables from execute-solution-task.prompt.md to ensure complete compatibility

### Step 6 (MANDATORY)
Write and Close Each File
   • Confirm each file written successfully  
   • Log total solution files created if DEBUG=1


### Step 7 (MANDATORY)
Result Tracking:
   - Append the result to:
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | generate-repo-task-checklists | status | symbol (✓ or ✗)

### Step 8 (MANDATORY)
Repo Checklist Update:
   - Open `tasks/{{repo_name}}_repo_checklist.md`
   - Set `[x]` only on the `@generate-repo-task-checklists` entry for the current repository markdown `tasks/{{repo_name}}_repo_checklist.md`
  - Do not modify other checklist items or other repositories' files

## Output Contract
JSON saved to:  
`output/{repo_name}_task6_generate-solution-checklists.json`

| Field | Type | Description |
|-------|------|-------------|
| repo_name | string | Echo of input |
| solutions_json_path | string | Echo of input |
| solutions_total | integer | Count of solutions processed |
| checklists_created | integer | Number of individual checklist files created successfully |
| checklist_paths | array of strings | List of all created checklist file paths (e.g., `./tasks/{repo_name}_{solution_name}_solution_checklist.md`) |
| status | SUCCESS or FAIL |
| timestamp | ISO8601 timestamp |

---


## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. **Mixed Variables Approach**: Include the explicit retry attempt variables template above AND dynamically extract additional content from .github/prompts/execute-solution-task.prompt.md "### Solution Variables" section
3. **Variables Section Format**: Combine the static template with any additional variables found in execute-solution-task.prompt.md to ensure complete compatibility
4. **Contract Compliance**: Always save JSON output file with all fields regardless of success/failure
5. **Timestamp Format**: Use ISO 8601 format (e.g., "2025-10-27T14:30:00")
6. **Error Handling**: If solutions_json_path not found, set status=FAIL and return with empty results
7. **Script Location**: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists.py (or .ps1/.sh)
8. **Environment**: Set DEBUG=1 environment variable at the start of the script if debug output is desired
9. **One File Per Solution**: Each solution gets its own dedicated checklist file: `./tasks/{repo_name}_{solution_name}_solution_checklist.md`
10. **Filename Sanitization**: Replace spaces and special characters in solution_name with underscores for valid filenames
