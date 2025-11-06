---
temperature: 0.0
---

@generate-solution-task-checklists checklist_path={{checklist_path}}

Task name: generate-solution-task-checklists

## Description:
Generate individual solution-level checklist files for a repository.  
This creates ONE checklist file per solution (.sln) discovered in the repo.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY) – Load Repo Checklist via checklist_path
Checklist & Variable Extraction (source of truth)
   • Treat the `checklist_path` argument as the ABSOLUTE path to the repository checklist markdown file (e.g. `tasks/{repo_name}_repo_checklist.md`).
   • Validate file exists and filename ends with `_repo_checklist.md`; if not, set status=FAIL and skip remaining steps.
   • Read the file content (UTF-8) and extract arrow values from EXACT variable lines:
       - `- {{repo_name}} →` (must not be blank)
       - `- {{repo_directory}} →` (must not be blank)
       - `- {{solutions_json}} →` (must not be blank)
       - `- {{solutions}} →` (may be blank prior to generation)
   • If any mandatory variable line missing or blank (except `solutions`) set status=FAIL and write output JSON immediately.
   • Load JSON from the `solutions_json` path (if status still SUCCESS); expect key `solutions` (array of absolute .sln paths). On failure (file missing / malformed / key absent) set status=FAIL.
   • Derive internal list of solution objects: `{name: <filename_without_ext>, path: <absolute_path>}`.
   • Log (DEBUG=1): `[debug][generate-solution-task-checklists] checklist='{{checklist_path}}' repo_name='{{repo_name}}' solutions_json='{{solutions_json}}' solutions_count={{count}}`.
   • All subsequent steps MUST rely on these extracted values (do NOT parse other sections or mutate base variables here).

### Step 2 (MANDATORY)
Parse Task Definitions
    • Read `.github/prompts/solution_task_list.prompt.md` to extract:
       - All task directives (e.g., @task-restore-solution, @task-build-solution, etc.)
       - Short descriptions for each task
       - The complete "### Solution Variables" section content (if present)
    • If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted {{task_count}} tasks from solution_task_list.prompt.md`
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
Write Solution Checklist File (Header + Content)
   - Combine header and content generation into a single atomic write per solution file.
   - Canonical template (the ONLY template – do not duplicate below):
   ```
   # Solution Checklist: {solution_name}
   Repository: {repo_url}
   Generated: {timestamp}

   ## Solution: {solution_name}

   ### Tasks
   - [ ] [MANDATORY] Restore NuGet packages @task-restore-solution
   - [ ] [MANDATORY] Build solution (Clean + Build) @task-build-solution
   - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base
   - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base
   - [ ] [CONDITIONAL Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL Attempt 1] Retry build after fix @task-build-solution
   - [ ] [CONDITIONAL Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL Attempt 2] Retry build after fix @task-build-solution
   - [ ] [CONDITIONAL Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix
   - [ ] [CONDITIONAL Attempt 3] Retry build after fix @task-build-solution

   ## For Agents Resuming Work

   **Next Action:** 
   1. Complete mandatory tasks first (restore then initial build)
   2. If initial build fails, perform knowledge base search / article creation
   3. Apply fixes and perform retry attempts in order (Attempt 1 → Attempt 2 → Attempt 3)
   4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

   **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-restore-solution`) as defined in `.github\prompts\solution_task_list.prompt.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.

   **Quick Reference:**
   - [MANDATORY] tasks must be completed before conditional retries
   - [CONDITIONAL] tasks execute only after a failure requiring remediation
   - [SCRIPTABLE] tasks can be automated with scripts
   - [NON-SCRIPTABLE] tasks require AI reasoning and direct tool calls
   - Mark completed tasks with [x]
   - Check Solution Variables section below for current task status and retry attempt tracking

   ### Solution Variables
   (Variables set by tasks for this specific solution)
   - solution_path → `{solution_path}`
   - solution_name → `{solution_name}`
   - build_count → 0
   - max_rebuild_attempts → 3
   - restore_status → NOT_EXECUTED
   - build_status → NOT_EXECUTED
   - build_stderr_content → NOT_EXECUTED
   - kb_search_status → NOT_EXECUTED
   - kb_file_path → N/A
   - kb_article_status → NOT_EXECUTED
   
   **Retry Attempt 1:**
   - fix_applied_attempt_1 → NOT_EXECUTED
   - kb_option_applied_attempt_1 → null
   - retry_build_status_attempt_1 → NOT_EXECUTED
   - retry_build_stderr_content_attempt_1 → NOT_EXECUTED
   
   **Retry Attempt 2:**
   - fix_applied_attempt_2 → NOT_EXECUTED
   - kb_option_applied_attempt_2 → null
   - retry_build_status_attempt_2 → NOT_EXECUTED
   - retry_build_stderr_content_attempt_2 → NOT_EXECUTED

   **Retry Attempt 3:**
   - fix_applied_attempt_3 → NOT_EXECUTED
   - kb_option_applied_attempt_3 → null
   - retry_build_status_attempt_3 → NOT_EXECUTED
   - retry_build_stderr_content_attempt_3 → NOT_EXECUTED

   ```

   - Each solution file is self-contained with all its tasks and variables
   - No separator needed (each solution is in its own file)


### Step 5 (MANDATORY)
Repo Checklist Update:
   - Open `tasks/{{repo_name}}_repo_checklist.md`
   - Set `[x]` only on the `@generate-repo-task-checklists` entry for the current repository markdown `tasks/{{repo_name}}_repo_checklist.md`
  - Do not modify other checklist items or other repositories' files

### Step 6 (MANDATORY) – Verification & Structured Output
Perform a verification pass ensuring:
1. All generated solution checklist files exist and begin with the canonical header block.
2. Each file contains the sections and task directives exactly as in Step 4.
3. Retry attempt variable blocks (1–3) all present with required keys.
4. No extraneous sections inserted.
5. Filenames match pattern `{repo_name}_{solution_name}_solution_checklist.md`.
6. All arrow variable lines end with `→ value` (value may be blank except counters initialized to 0 or NOT_EXECUTED/N/A).
7. Timestamps are ISO 8601 (ends with 'Z').

Write JSON: `output/{repo_name}_task5_generate-solution-checklists.json` with keys:
 - repo_name
 - solutions_total
 - checklist_paths
 - status (SUCCESS|FAIL)
 - timestamp
 - verification_errors (array of objects {type,target,detail})

Status rule: any verification_errors -> FAIL, else SUCCESS.

### Step 7: (MANDATORY)
DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][generate-solution-task-checklists] EXIT status={{status}} processed={{repositories_processed}} generated={{checklists_generated}}"

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
11. **Verification JSON Naming**: Uses task5 to reflect updated step numbering.
