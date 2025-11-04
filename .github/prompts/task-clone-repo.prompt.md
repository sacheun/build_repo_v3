---
temperature: 0.0
---

@task-clone-repo clone_path={{clone_path}} checklist_path={{checklist_path}}

# Task name: task-clone-repo

## Process Overview
1. Debug Entry Trace
2. Input Parameter Extraction & Checklist Verification
3. Directory Existence Check
4. Clone or Refresh Operation
5. Structured Output
6. Log to Decision Log
7. Result Tracking
8. Repo Checklist Update
9. Repo Variable Refresh
10. Debug Exit Trace

## Prerequisites
- git installed and available in PATH
- Python 3.x installed (if scripting)
- DEBUG environment variable set (optional, for debug output)
- Directory permissions for clone_path
- Required input parameters: clone_path, checklist_path (absolute or relative path to `tasks/<repo_name>_repo_checklist.md`).
- The authoritative values for repo_url and repo_name are READ from the variable lines inside the checklist file (`## Repo Variables Available`).
- The repo_name MUST be obtained from the `- {{repo_name}}` line's arrow value, not derived from filename; filename is only a consistency check.

## Description
This task clones a repository from repo_url into clone_path directory. This is a straightforward git operation that CAN be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**  
**DO NOT SKIP OR SUMMARIZE.**  
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
DEBUG Entry Trace:  
If DEBUG=1, print:  
`[debug][task-clone-repo] START checklist_path='{{checklist_path}}' clone_path='{{clone_path}}'`

### Step 2 (MANDATORY)
Load Authoritative Variables From Checklist:
1. Resolve `checklist_path`; ensure file exists. If missing, set status=FAIL and abort.
2. Open the checklist file and locate the `## Repo Variables Available` section.
3. Parse lines beginning with:
   * `- {{repo_url}}`
   * `- {{repo_name}}`
4. Extract values to right of `→` (trim whitespace). These become authoritative `repo_url` and `repo_name` for all subsequent steps.
5. Derive filename_repo_name by stripping suffix `_repo_checklist.md` from filename for consistency check only.
6. If the checklist `repo_name` value is blank and filename_repo_name is available, set the line's arrow value to filename_repo_name and treat that as authoritative.
7. If both values exist and differ, log a debug warning; continue using the variable line value.
8. If any required variable line is missing, insert `- {{token}} →` (blank) and mark status=FAIL unless later corrected.
9. Ensure presence (may be blank) of:
   * `- {{clone_path}}`
   * `- {{repo_directory}}`
   Insert if absent (blank value) for later refresh.
10. If DEBUG=1 print: `[debug][task-clone-repo] loaded repo_url='{repo_url}' repo_name='{repo_name}' from {checklist_path}`.
11. External repo_url values MUST be ignored; checklist content is single source of truth.

### Step 3 (MANDATORY)
Directory Existence Check:  
Check if target directory exists: {{clone_path}}/{{repo_name}}
- If DEBUG=1 and directory exists, print: `[debug][task-clone-repo] repository directory exists, will refresh`
- If DEBUG=1 and directory does not exist, print: `[debug][task-clone-repo] repository directory does not exist, will clone`

### Step 4 (MANDATORY)
Clone or Refresh Operation:

**If target directory does NOT exist (CLONE):**
- If DEBUG=1, print: `[debug][task-clone-repo] executing: git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}`
- Execute: `git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}`
- Capture stdout, stderr, and exit code
- If DEBUG=1 and exit code != 0, print: `[debug][task-clone-repo] clone failed with exit code: {{exit_code}}`
- If DEBUG=1 and exit code == 0, print: `[debug][task-clone-repo] clone completed successfully`

**If target directory already exists (REFRESH):**
- If DEBUG=1, print: `[debug][task-clone-repo] executing refresh sequence`
- Navigate to directory: `cd {{clone_path}}/{{repo_name}}`
- Execute commands in sequence:
  a. `git reset --hard HEAD` (revert local changes)
  b. `git clean -fd` (remove untracked files)
  c. `git pull` (fetch latest changes)
- If DEBUG=1, print status after each command
- If any command fails (exit code != 0), set status=FAIL
- If all commands succeed, set status=SUCCESS

### Step 5 (MANDATORY)
Verification & Structured Output:
Before writing JSON you MUST run a verification pass for Steps 2–4. Any violation sets status=FAIL (unless already FAIL) and is recorded.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for:
  - `- {{repo_url}}` (non-empty arrow value)
  - `- {{repo_name}}` (non-empty arrow value)
3. Mutable variable lines exist (may be blank prior to update):
  - `- {{clone_path}}`
  - `- {{repo_directory}}`
4. If clone_status=SUCCESS then:
  - Target directory `{{clone_path}}/{{repo_name}}` exists.
  - Directory contains a `.git` folder (for CLONE) OR `.git` folder remains (for REFRESH).
5. No duplicate occurrences of any `- {{repo_url}}` or `- {{repo_name}}` lines.
6. Task directive line `@task-clone-repo` appears exactly once in checklist.
7. If operation=REFRESH ensure target directory existed prior to commands (skip if not trackable; informational only).
8. Arrow formatting: each variable line uses `- {{token}} → value` (record violation if arrow missing).

For each failure add object: `{ "type": "<code>", "target": "<file|repo|path>", "detail": "<description>" }` to `verification_errors`.
If DEBUG=1 emit one line per failure:
`[debug][task-clone-repo][verification] FAIL code=<code> detail="<description>"`

Structured Output JSON (output/{{repo_name}}_task1_clone-repo.json) MUST include:
- repo_url
- clone_path
- repo_name
- repo_directory
- operation (CLONE|REFRESH)
- clone_status (SUCCESS|FAIL)
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 truncated to seconds, UTC)
- git_output (stdout/stderr aggregated, truncated if large)
- verification_errors (array, empty if none)
- debug (optional array of debug lines when DEBUG=1)

#### Example Output
```json
{
  "repo_url": "https://github.com/user/repo.git",
  "clone_path": "/home/user/repos",
  "repo_name": "repo",
  "repo_directory": "/home/user/repos/repo",
  "operation": "CLONE",
  "clone_status": "SUCCESS",
  "status": "SUCCESS",
  "timestamp": "2025-11-02T21:35:48Z",
  "git_output": "Cloning into 'repo'..."
}
```

### Step 6 (MANDATORY)
Log to Decision Log:
- Call @task-update-decision-log to log task execution:
```
@task-update-decision-log
timestamp="{{timestamp}}"
repo_name="{{repo_name}}"
solution_name=""
task="task-clone-repo"
message="{{message}}"
status="{{clone_status}}"
```
- Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
- The solution_name is blank since this is a repository-level task
- Message format:
  * If fresh clone: "git clone --depth 1 {{repo_url}}"
  * If refresh: "git reset --hard HEAD && git clean -fd && git pull"
- Status: "SUCCESS" or "FAIL"

### Step 7 (MANDATORY)
Result Tracking:
- Append the result to:
  - results/repo-results.csv (CSV row)
- Row format: timestamp, repo_name, task-clone-repo, status, symbol (✓ or ✗)

#### Example CSV Row
```
2025-11-02T21:35:48Z,repo,task-clone-repo,SUCCESS,✓
```

### Step 8 (MANDATORY)
Repo Checklist Update:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-clone-repo` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 9 (MANDATORY)
Repo Variable Refresh (INLINE ONLY):
- Open checklist file at `{{checklist_path}}`.
- Update ONLY the following lines under `## Repo Variables Available`:
  * `- {{clone_path}}`
  * `- {{repo_directory}}`
- Do NOT modify the lines for `- {{repo_url}}` or `- {{repo_name}}`; these remain authoritative values set during checklist generation / Step 2 load and are immutable in this task.
- Replace ONLY the text after the arrow (`→`) for the mutable lines with current concrete values.
- Example transformation: `- {{clone_path}} → Root folder where repositories are cloned.` becomes `- {{clone_path}} → D:\repos`.
- If a mutable line lacks an arrow, append ` → <value>`.
- If a mutable required line was inserted blank in Step 2, populate it now.
- No new sections may be added; all updates must be inline.

### Step 10 (MANDATORY)
DEBUG Exit Trace:  
If DEBUG=1, print:  
`[debug][task-clone-repo] EXIT repo_name='{{repo_name}}' status={{clone_status}} operation={{operation}} repo_directory='{{repo_directory}}'`

## Output Contract
- repo_url: string (repository URL extracted from checklist file)
- clone_path: string (base directory for clones, echoed from input)
- repo_name: string (repository name loaded from `- {{repo_name}}` variable line; filename used only for consistency check)
- repo_directory: string (absolute path to cloned repository: {{clone_path}}/{{repo_name}})
- operation: CLONE / REFRESH (indicates new clone vs existing reset/pull)
- clone_status: SUCCESS / FAIL (SUCCESS if git operation completed with exit code 0)
- status: SUCCESS / FAIL (same as clone_status for consistency)
- timestamp: string (ISO 8601 datetime when task completed)
- git_output: string (captured stdout/stderr from git commands)

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. Idempotency: If the directory exists, perform refresh sequence (reset/clean/pull) instead of recloning.
3. Error Handling: Any non-zero exit code from git commands sets clone_status=FAIL; do not mark progress checkbox.
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
5. Progress Update: Only set [x] in repo-progress for task-clone-repo on SUCCESS.
6. Security: Avoid embedding credentials in the URL; rely on pre-configured git auth (credential manager, SSH keys).
7. Directory Creation: Ensure clone_path directory exists before attempting clone; create if necessary.
8. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task1_clone-repo.py
9. Inline Variable Policy: Step 9 must update values directly on existing `- {{token}} → value` lines; never create a secondary "refreshed" block. Step 2 loads repo_url and repo_name strictly from variable lines; they are immutable for this task.

## Error Handling
- For any step that fails:
  - Log the error with details (stdout, stderr, exit code)
  - Abort further steps if critical (e.g., clone/refresh fails)
  - Do not update checklist or results CSV on failure

## Consistency Checks
- After updating files (checklist tasks/{{repo_name}}_repo_checklist.md, results/repo-results.csv, output JSON), verify that the changes were written successfully.
- If verification fails, log an error and abort.

## Cross-References
- When using repo_name, repo_directory, or other variables, ensure they are referenced from the latest extracted or computed value in previous steps.
