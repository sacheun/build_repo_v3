@task-git-clone repo_url={{repo_url}} clone_path={{clone_path}}

Task name: task-clone-repo

Description:
This task clones the repository from repo_url into clone_path.
It should execute a real shell command.

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

6. Append the result to:
   - results/repo-results.md (Markdown table row)
   - results/repo-results.csv (CSV row)

7. Update the progress table:
   - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-clone-repo"
   - Change [ ] to [x] to mark task as completed

8. Return  the absolute path to the directory where the repository was successfully cloned.

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