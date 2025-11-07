---
temperature: 0.0
---

@task-clone-repo clone_path={{clone_path}} checklist_path={{checklist_path}}

# Task name: task-clone-repo

## Description
This task clones a repository from repo_url into clone_path directory. This is a straightforward git operation that CAN be implemented as a script.

## Execution Policy
**STRICT MODE ON**
- All steps are **MANDATORY**.
- Never summarize or skip steps.
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
Load Variables From Checklist:
1. Resolve `checklist_path`; ensure file exists. If missing, set status=FAIL and abort.
2. Open the checklist file and locate the `## Repo Variables Available` section.
3. Parse lines beginning with:
   * `- {{repo_url}}`
   * `- {{repo_name}}`
4. Extract values to right of `→` (trim whitespace). These become authoritative `repo_url` and `repo_name` for all subsequent steps.

### Step 2 (MANDATORY)
Directory Existence Check:  
Check if target directory exists: {{clone_path}}/{{repo_name}}

### Step 3 (MANDATORY)
Clone or Refresh Operation:

If target directory does NOT exist (CLONE):
  - Perform shallow clone: `git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}`

If target directory already exists (REFRESH):
  - Navigate: `cd {{clone_path}}/{{repo_name}}`
  - Commands in order:
    1. `git reset --hard HEAD`
    2. `git clean -fd`
    3. `git pull`
  - Any non-zero exit sets clone_status=FAIL.

### Step 4 (MANDATORY)
Structured Output:
Generate a JSON file only (no verification logic in this step) at: `output/{{repo_name}}_task1_clone-repo.json`.

Required JSON fields (emit all fields every run):
1. repo_url
2. clone_path
3. repo_name
4. repo_directory
5. operation (CLONE|REFRESH)
6. clone_status (SUCCESS|FAIL)
7. status (SUCCESS|FAIL) (mirror clone_status)
8. timestamp (ISO 8601 UTC, truncated to whole seconds)
9. git_output (aggregated stdout + stderr; may be truncated if extremely large)

### Step 5 (MANDATORY)
Checklist Update & Variable Refresh (INLINE ONLY):
1. Open checklist file at `{{checklist_path}}`.
2. Mark `[x]` ONLY on the `@task-clone-repo` entry (do not alter other task lines).
3. Under `## Repo Variables Available` update ONLY:
  * `- {{clone_path}}` → set to the runtime `clone_path` argument (absolute or normalized path you are using for clones)
  * `- {{repo_directory}}` → set to `{{clone_path}}/{{repo_name}}`
4. Do NOT modify:
  * `- {{repo_url}}`
  * `- {{repo_name}}`
5. Preserve arrow format exactly: `- {{token}} → value` (single space before and after arrow, value may be blank only if operation failed and field legitimately unknown).
6. Make changes inline—do NOT add duplicate variable lines or new sections.
7. If clone failed (clone_status=FAIL), still update `- {{clone_path}}` (echo argument) but leave `- {{repo_directory}}` blank if directory absent.
8. Always ensure exactly one `→` per line. 

### End of Steps

## Output Contract
- `repo_url`: string (repository URL extracted from checklist file)
- `clone_path`: string (base directory for clones, echoed from input)
- `repo_name`: string (repository name loaded from `- {{repo_name}}` variable line; filename used only for consistency check)
- `repo_directory`: string (absolute path to cloned repository: {{clone_path}}/{{repo_name}})
- `operation`: CLONE / REFRESH (indicates new clone vs existing reset/pull)
- `clone_status`: SUCCESS / FAIL (SUCCESS if git operation completed with exit code 0)
- `status`: SUCCESS / FAIL (same as clone_status for consistency)
- `timestamp`: string (ISO 8601 datetime when task completed)
- `git_output`: string (captured stdout/stderr from git commands)

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. Idempotency: If the directory exists, perform refresh sequence (reset/clean/pull) instead of recloning.
3. Error Handling: Any non-zero exit code from git commands sets clone_status=FAIL; do not mark progress checkbox.
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
5. Progress Update: Only set `[x]` in repo-progress for task-clone-repo on SUCCESS.
6. Script Location: Save generated script to `temp-script/` directory with naming pattern: `step{N}_repo{M}_task1_clone-repo.py`


