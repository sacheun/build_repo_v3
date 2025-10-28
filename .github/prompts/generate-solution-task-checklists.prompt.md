@generate-solution-task-checklists

Task name: generate-repo-task-checklists

**THIS TASK IS SCRIPTABLE**

## Description:
Generate a solution-level checklist file for a repository.  
This is used to track progress for each solution (.sln) discovered in the repo.

If DEBUG=1, print parameter values.

---

## Behavior (Follow this Step by Step)

1. **Read Solutions Data**
   • Load JSON from `solutions_json_path`  
   • Extract `solutions` array  
   • Convert each into object `{name, path}`  
   • Log solution count if DEBUG=1

2. **Parse Task Definitions**
   • Read `.github/prompts/solution_tasks_list.prompt.md` to extract:
     - All task directives (e.g., @task-restore-solution, @task-build-solution, etc.)
     - Short descriptions for each task
     - The complete "Variables available:" section content
   • If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted {{task_count}} tasks from solution_tasks_list.prompt.md`
   • Store the variables section for inclusion in each solution section

3. **Create Single Output File for All Solutions**
   • New file: `./tasks/{repo_name}_solutions_checklist.md`  
   • Overwrite if it already exists  
   • This file will contain ALL solutions for this repository
   • Log creation if DEBUG=1

4. **Write File Header**
   ```
   # Solutions Checklist: {repo_name}
   Repository: {repo_url}
   Total Solutions: {solutions_total}
   Generated: {timestamp}
   
   ---
   ```

5. **Generate Checklist Sections for ALL Solutions**
   For each solution in the solutions array:
   ```
   ## Solution {index}: {solution_name}
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

   ### Solution Variables
   (Variables set by tasks for this specific solution)
   - solution_path → `{solution_path}`
   - solution_name → `{solution_name}`
   - build_attempt → 0
   - max_build_attempts → 3
   
   [Content dynamically extracted from .github/prompts/solution_tasks_list.prompt.md "Variables available:" section]
   
   ---
   ```
   • Insert `---` as a separator between solutions  
   • Log generated section name if DEBUG=1
   • **Dynamic Variables Section:** Extract the entire "Variables available:" section from .github/prompts/solution_tasks_list.prompt.md and include it verbatim in each solution section under "### Solution Variables Available" heading

6. **Write and Close File**
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
| checklist_created | boolean | True if single consolidated file created successfully |
| checklist_path | string | `./tasks/{repo_name}_solutions_checklist.md` (single file for all solutions) |
| status | SUCCESS or FAIL |
| timestamp | ISO8601 timestamp |

---

## Debug Logging (DEBUG=1)
Prefix: `[debug][generate-solution-task-checklists]`

Log messages for:
• START (with input parameters)  
• Task extraction from .github/prompts/solution_tasks_list.prompt.md
• File creation  
• Each solution section  
• Completion summary  
• EXIT status

---

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task
2. **Dynamic Task Extraction**: Parse .github/prompts/solution_tasks_list.prompt.md to get:
   - Task list and descriptions
   - Variables section (extract entire "### Variables available:" section)
3. **Variables Section Format**: Include the extracted variables section exactly as it appears in .github/prompts/solution_tasks_list.prompt.md, preserving markdown formatting and variable descriptions
4. **Contract Compliance**: Always save JSON output file with all fields regardless of success/failure
5. **Markdown Format**: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes
6. **Timestamp Format**: Use ISO 8601 format (e.g., "2025-10-27T14:30:00")
7. **Error Handling**: If solutions_json_path not found, set status=FAIL and return with empty results
8. **Script Location**: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists.py (or .ps1/.sh)
9. **Environment**: Set DEBUG=1 environment variable at the start of the script if debug output is desired
10. **Single File Output**: All solutions for a repository go into ONE consolidated checklist file, not separate files per solution

````