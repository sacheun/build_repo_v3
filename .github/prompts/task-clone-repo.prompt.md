---
temperature: 0.0
---

@task-clone-repo repo_url={{repo_url}} clone_path={{clone_path}} repo_name={{repo_name}}

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
- Required input parameters: repo_url, clone_path, (optional) repo_name

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
`[debug][task-clone-repo] START repo_url='{{repo_url}}' clone_path='{{clone_path}}'`

### Step 2 (MANDATORY)
Input Parameters: You are given repo_url, clone_path, and optionally repo_name from the calling context.

Repository Name Extraction:  
If repo_name not provided, extract from repo_url:
- For Azure DevOps: Extract last segment after final "/" (e.g., "https://skype.visualstudio.com/SCC/_git/repo-name" → "repo-name")
- For GitHub: Extract last segment before ".git" (e.g., "https://github.com/user/repo.git" → "repo")
- If DEBUG=1, print: `[debug][task-clone-repo] extracted repo_name: {{repo_name}}`

Pre-flight Checklist Verification:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  * `{{repo_url}}`
  * `{{clone_path}}`
  * `{{repo_directory}}`
  * `{{repo_name}}`
- If any token is missing or altered, restore it prior to continuing

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
Save JSON object to output/{{repo_name}}_task1_clone-repo.json with:
- repo_url: echoed from input
- clone_path: echoed from input
- repo_name: extracted or provided
- repo_directory: absolute path to cloned repository ({{clone_path}}/{{repo_name}})
- operation: "CLONE" or "REFRESH"
- clone_status: SUCCESS if operation completed with exit code 0, FAIL otherwise
- status: SUCCESS / FAIL (same as clone_status for consistency)
- timestamp: ISO 8601 format datetime when task completed
- git_output: captured stdout/stderr from git commands (for debugging)

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
Repo Variable Refresh:
- Open `tasks/{{repo_name}}_repo_checklist.md` file
- Confirm the `## Repo Variables Available` section still contains the expected templated tokens exactly as shown below:
  * `{{repo_url}}`
  * `{{clone_path}}`
  * `{{repo_directory}}`
  * `{{repo_name}}`
- Update the following variables with the latest values produced by this task:
  * `{{repo_url}}`
  * `{{clone_path}}`
  * `{{repo_directory}}`
  * `{{repo_name}}`
- Ensure each variable reflects the refresh results before saving the file

### Step 10 (MANDATORY)
DEBUG Exit Trace:  
If DEBUG=1, print:  
`[debug][task-clone-repo] EXIT repo_name='{{repo_name}}' status={{clone_status}} operation={{operation}} repo_directory='{{repo_directory}}'`

## Output Contract
- repo_url: string (repository URL, echoed from input)
- clone_path: string (base directory for clones, echoed from input)
- repo_name: string (repository name extracted from URL or provided)
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
