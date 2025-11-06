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
- **Verification (Step 7)** must **always** execute.
- If Step 7 fails, **re-run Steps 1–7** automatically (up to `max_verification_retries`).
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
- If DEBUG=1 and directory exists, print: `[debug][task-clone-repo] repository directory exists, will refresh`
- If DEBUG=1 and directory does not exist, print: `[debug][task-clone-repo] repository directory does not exist, will clone`

### Step 3 (MANDATORY)
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
  "git_output": "Cloning into 'repo'..."
}
```
### Step 5 (MANDATORY)
Repo Checklist Update:
- Open checklist file at `{{checklist_path}}`.
- Set `[x]` only on the `@task-clone-repo` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 6 (MANDATORY)
Repo Variable Refresh (INLINE ONLY):
- Open checklist file at `{{checklist_path}}`.
- Update ONLY the following lines under `## Repo Variables Available`:
  * `- {{clone_path}}`
  * `- {{repo_directory}}`
- Do NOT modify the lines for `- {{repo_url}}` or `- {{repo_name}}`; these remain authoritative values set during checklist generation / Step 2 load and are immutable in this task.
- No new sections may be added; all updates must be inline.

### Step 7 (MANDATORY VERIFICATION)
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
9. JSON Output Integrity: The JSON file from Step 4 exists and contains all required top-level keys.

Success Criteria for Step 10: JSON file updated (if needed) and reflects accurate verification_errors content.

### Step 8 (MANDATORY)
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
6. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task1_clone-repo.py
7. Inline Variable Policy: Step 9 must update values directly on existing `- {{token}} → value` lines; never create a secondary "refreshed" block. Step 2 loads repo_url and repo_name strictly from variable lines; they are immutable for this task.
8. Post-Refresh Verification: Step 7 performs non-destructive validation and ONLY mutates `verification_errors` and `status` fields inside the JSON output.

