@task-clone-repo repo_url={{repo_url}} clone_path={{clone_path}} repo_name={{repo_name}}

Task name: task-clone-repo

Description:
This task clones a repository from repo_url into clone_path directory. This is a straightforward git operation that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Parses repository name from URL
2. Checks if repository already exists locally
3. Performs fresh clone or refresh (reset/pull) based on existence
4. Saves the result to JSON output
5. Updates progress and results files

Behavior:
0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-clone-repo] START repo_url='{{repo_url}}' clone_path='{{clone_path}}'`

1. Input Parameters: You are given repo_url, clone_path, and optionally repo_name from the calling context.

2. Repository Name Extraction: If repo_name not provided, extract from repo_url:
   - For Azure DevOps: Extract last segment after final "/" (e.g., "https://skype.visualstudio.com/SCC/_git/repo-name" → "repo-name")
   - For GitHub: Extract last segment before ".git" (e.g., "https://github.com/user/repo.git" → "repo")
   - If DEBUG=1, print: `[debug][task-clone-repo] extracted repo_name: {{repo_name}}`

3. Directory Existence Check: Check if target directory exists: {{clone_path}}/{{repo_name}}
   - If DEBUG=1 and directory exists, print: `[debug][task-clone-repo] repository directory exists, will refresh`
   - If DEBUG=1 and directory does not exist, print: `[debug][task-clone-repo] repository directory does not exist, will clone`

4. Clone or Refresh Operation:
   
   **If target directory does NOT exist (CLONE):**
   - If DEBUG=1, print: `[debug][task-clone-repo] executing: git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}`
   - Execute: git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}
   - Capture stdout, stderr, and exit code
   - If DEBUG=1 and exit code != 0, print: `[debug][task-clone-repo] clone failed with exit code: {{exit_code}}`
   - If DEBUG=1 and exit code == 0, print: `[debug][task-clone-repo] clone completed successfully`
   
   **If target directory already exists (REFRESH):**
   - If DEBUG=1, print: `[debug][task-clone-repo] executing refresh sequence`
   - Navigate to directory: cd {{clone_path}}/{{repo_name}}
   - Execute commands in sequence:
     a. git reset --hard HEAD (revert local changes)
     b. git clean -fd (remove untracked files)
     c. git pull (fetch latest changes)
   - If DEBUG=1, print status after each command
   - If any command fails (exit code != 0), set status=FAIL
   - If all commands succeed, set status=SUCCESS

5. Structured Output: Save JSON object to output/{repo_name}_task1_clone-repo.json with:
   - repo_url: echoed from input
   - clone_path: echoed from input
   - repo_name: extracted or provided
   - repo_directory: absolute path to cloned repository ({{clone_path}}/{{repo_name}})
   - operation: "CLONE" or "REFRESH"
   - clone_status: SUCCESS if operation completed with exit code 0, FAIL otherwise
   - status: SUCCESS | FAIL (same as clone_status for consistency)
   - timestamp: ISO 8601 format datetime when task completed
   - git_output: captured stdout/stderr from git commands (for debugging)

5a. Log to Decision Log:
   - Append to: results/decision-log.csv
   - Append row with: "{{timestamp}},{{repo_name}},,task-clone-repo,{{message}},{{clone_status}}"
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - The solution_name column (third column) is blank since this is a repository-level task
   - Message format:
     * If fresh clone: "git clone --depth 1 {{repo_url}}"
     * If refresh: "git reset --hard HEAD && git clean -fd && git pull"
   - Status: "SUCCESS" or "FAIL"

6. Result Tracking:
   - Append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-clone-repo | status | symbol (✓ or ✗)

7. Progress Update:
   - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-clone-repo"
   - Change [ ] to [x] to mark task as completed (only on SUCCESS)

8. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][task-clone-repo] EXIT repo_name='{{repo_name}}' status={{clone_status}} operation={{operation}} repo_directory='{{repo_directory}}'"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the clone-repo task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-clone-repo] allowing simple grep filtering.
- Entry Message: "[debug][task-clone-repo] START repo_url='<url>' clone_path='<path>'" emitted before step 1.
- Name Extraction: "[debug][task-clone-repo] extracted repo_name: <name>" after parsing URL.
- Directory Check: "[debug][task-clone-repo] repository directory exists, will refresh" or "does not exist, will clone".
- Command Execution: "[debug][task-clone-repo] executing: <git command>" before each git operation.
- Success Message: "[debug][task-clone-repo] clone completed successfully" or "refresh completed successfully".
- Failure Message: "[debug][task-clone-repo] operation failed with exit code: <code>" if any git command fails.
- Exit Message: "[debug][task-clone-repo] EXIT repo_name='<name>' status=<SUCCESS|FAIL> operation=<CLONE|REFRESH> repo_directory='<path>'" emitted after step 7.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_url: string (repository URL, echoed from input)
- clone_path: string (base directory for clones, echoed from input)
- repo_name: string (repository name extracted from URL or provided)
- repo_directory: string (absolute path to cloned repository: {{clone_path}}/{{repo_name}})
- operation: CLONE | REFRESH (indicates new clone vs existing reset/pull)
- clone_status: SUCCESS | FAIL (SUCCESS if git operation completed with exit code 0)
- status: SUCCESS | FAIL (same as clone_status for consistency)
- timestamp: string (ISO 8601 datetime when task completed)
- git_output: string (captured stdout/stderr from git commands)

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. Idempotency: If the directory exists, perform refresh sequence (reset/clean/pull) instead of recloning.
3. Error Handling: Any non-zero exit code from git commands sets clone_status=FAIL; do not mark progress checkbox.
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
5. Progress Update: Only set [x] in repo-progress for task-clone-repo on SUCCESS.
6. Security: Avoid embedding credentials in the URL; rely on pre-configured git auth (credential manager, SSH keys).
7. Depth Optimization: Use --depth 1 for fresh clones to minimize download size and time.
8. Directory Creation: Ensure clone_path directory exists before attempting clone; create if necessary.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task1_clone-repo.py
10. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired.

Behavior:
1. Extract repo_name from the repo_url (e.g., "https://github.com/user/repo.git" → "repo")

2. Check if target directory exists: {{clone_path}}/{{repo_name}}

3. If target directory does NOT exist:
   - If DEBUG environment is set to 1, print: `[debug][task-clone-repo] performing fresh clone: git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}`
   - Execute shell command: git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}

4. If target directory already exists:
   - If DEBUG environment is set to 1, print: `[debug][task-clone-repo] repository exists, refreshing: reverting local changes and pulling latest`
   - Navigate to the directory: cd {{clone_path}}/{{repo_name}}
   - Revert all local changes: git reset --hard HEAD
   - Remove all untracked files: git clean -fd
   - Pull the latest changes: git pull

5. If operation succeeds → return SUCCESS
   If operation fails → return FAIL

6. Log the decision to Decision Log:
   - Append to: results/decision-log.csv
   - Append row with: "{{current_timestamp}},{{repo_name}},,task-clone-repo,{{message}},{{clone_status}}"
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - The solution_name column (third column) should be blank (empty) since this is a repository-level task
   - Message should contain the git command(s) executed:
     * If fresh clone: "git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}"
     * If refresh: "git reset --hard HEAD && git clean -fd && git pull"

7. Append the result to:
   - results/repo-results.md (Markdown table row)
   - results/repo-results.csv (CSV row)

8. Update the progress table:
   - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-clone-repo"
   - Change [ ] to [x] to mark task as completed

9. Return  the absolute path to the directory where the repository was successfully cloned.

Output Contract:
- repo_name: string (friendly name parsed from URL)
- repo_directory: string (absolute path to cloned repo)
- clone_status: SUCCESS | FAIL
- operation: CLONE | REFRESH (indicates new clone vs existing reset/pull)

Implementation Notes (conceptual):
1. Idempotency: If the directory exists, perform refresh sequence (reset/clean/pull) instead of recloning.
2. Error Handling: Any non-zero exit code from git commands sets clone_status=FAIL; do not mark progress checkbox.
3. Logging Order Recommendation: a) determine repo_name b) perform clone/refresh c) append results d) update progress e) emit JSON.
4. Progress Update: Only set [x] in repo-progress for task-clone-repo on SUCCESS.
5. Security: Avoid embedding credentials in the URL; rely on pre-configured auth.