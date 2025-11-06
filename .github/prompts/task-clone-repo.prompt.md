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
- **Verification (Step 9)** must **always** execute.
- If Step 9 fails, **re-run Steps 1–9** automatically (up to `max_verification_retries`).
- Never summarize or skip steps.

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
5. If any required variable line is missing, insert `- {{token}} →` (blank) and mark status=FAIL unless later corrected.
6. If DEBUG=1 print: `[debug][task-clone-repo] loaded repo_url='{repo_url}' repo_name='{repo_name}' from {checklist_path}`.
7. External repo_url values MUST be ignored; checklist content is single source of truth.

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
10. verification_errors (ALWAYS emit an array; leave empty since verification removed from Step 5)
11. debug (optional array of debug lines when DEBUG=1)

Notes:
- Do NOT run any validation/verification in this step (previous in-step verification has been intentionally removed).
- Leave `verification_errors: []` for forward compatibility; another step may populate it in future revisions.

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
  "git_output": "Cloning into 'repo'...",
  "verification_errors": []
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
- No new sections may be added; all updates must be inline.

### Step 10 (MANDATORY VERIFICATION)
Verification (Post-Refresh):
Perform a verification pass AFTER Step 9 variable refresh and AFTER checklist marking (Step 8). This step validates correctness and, if needed, updates the JSON file produced in Step 5 by populating verification_errors and adjusting overall status.

Scope of Verification:
1. Checklist File Presence: `{{checklist_path}}` exists.
2. Variable Lines (Authoritative): Exactly one occurrence each of:
  - `- {{repo_url}}` with non-empty value
  - `- {{repo_name}}` with non-empty value
3. Mutable Variable Lines Present (may now be non-empty; must exist):
  - `- {{clone_path}}` (value MUST equal the runtime clone_path argument)
  - `- {{repo_directory}}` (value MUST equal `{{clone_path}}/{{repo_name}}`)
4. Arrow Formatting: All variable lines in `## Repo Variables Available` use `- {{token}} → value` (record violation if arrow missing or multiple arrows).
5. Repository Directory:
  - If clone_status=SUCCESS: directory `{{clone_path}}/{{repo_name}}` exists AND contains a `.git` folder.
  - If clone_status=FAIL: absence of directory does NOT create an additional violation (only record missing directory if operation reported SUCCESS inconsistently).
6. Checklist Task Marking:
  - If clone_status=SUCCESS: the `@task-clone-repo` checklist entry MUST be `[x]`.
  - If clone_status=FAIL: the checklist entry MUST NOT be `[x]`.
7. No Duplicate Task Directive: `@task-clone-repo` appears exactly once in the checklist file.
8. Consistency: repo_name in variable line matches the directory name actually used. If mismatch, violation.
9. JSON Output Integrity: The JSON file from Step 5 exists and contains all required top-level keys.
10. Results CSV Row: `results/repo-results.csv` contains at least one line matching the row format:
    `timestamp,repo_name,task-clone-repo,status,symbol` where symbol is `✓` if SUCCESS or `✗` if FAIL. (Header line excluded from this check.)

Violation Recording:
- For each violation append object: `{ "type": "<code>", "target": "<file|path|variable>", "detail": "<human-readable description>" }` to `verification_errors`.
- Recommended codes: file_missing, variable_missing, variable_empty, variable_mismatch, arrow_format_error, duplicate_variable, directory_missing, git_folder_missing, checklist_mark_incorrect, directive_duplicate, json_missing_key.
  - Additional code: results_row_missing (row for task-clone-repo not found in results/repo-results.csv)
- If DEBUG=1 emit: `[debug][task-clone-repo][verification] FAIL code=<code> detail="<description>"` for each recorded violation.

Status Adjustment Logic:
- Start with `status = clone_status`.
- If clone_status=SUCCESS but any violations exist, set `status=FAIL` (clone_status remains SUCCESS).
- If clone_status=FAIL keep `status=FAIL` regardless of additional violations.

JSON Output Update:
1. Load existing `output/{{repo_name}}_task1_clone-repo.json`.
2. Inject/overwrite fields: `verification_errors` (array), `status` (possibly updated), and (optionally) `debug` lines appended.
3. Re-write file atomically (temp file → replace) to avoid partial writes.

Determinism Requirements:
- Sort `verification_errors` by `type` then `target` for stable output.
- Timestamp from Step 5 is NOT regenerated; do not change it.

Success Criteria for Step 10: JSON file updated (if needed) and reflects accurate verification_errors content.

### Step 11 (MANDATORY)
DEBUG Exit Trace:  
If DEBUG=1, print:  
`[debug][task-clone-repo] EXIT repo_name='{{repo_name}}' status={{clone_status}} final_status={{status}} operation={{operation}} repo_directory='{{repo_directory}}'`

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
10. Post-Refresh Verification: Step 10 performs non-destructive validation and ONLY mutates `verification_errors` and `status` fields inside the JSON output.

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
