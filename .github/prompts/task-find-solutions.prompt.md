---
temperature: 0.0
---

@task-find-solutions checklist_path={{checklist_path}}

# Task name: task-find-solutions

## Description
This task discovers all Visual Studio solution files (`.sln`) within a repository directory tree. This is a straightforward file search operation that **must** be implemented as a script.

## Execution Policy
**STRICT MODE ON**
- All steps are **MANDATORY**.
- **Verification (Step 8)** must **always** execute.
- If Step 8 fails, **re-run Steps 1–8** automatically (up to `max_verification_retries`).
- Never summarize or skip steps.
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
Checklist Load & Variable Extraction:
- Open the file at `{{checklist_path}}`.
- Extract (value after `→`) from lines:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
  - Confirm presence of tokens `- {{solutions_json}}` and `- {{solutions}}` (values may be placeholders initially).
- If any required line missing or value blank for repo_name/repo_directory, set `status=FAIL` and proceed to structured output.
- Base variables (`repo_name`, `repo_directory`) are immutable; do NOT modify them.
- If DEBUG=1, print: `[debug][task-find-solutions] extracted repo_name='{{repo_name}}' repo_directory='{{repo_directory}}'`

### Step 2 (MANDATORY)
Input Validation:
- Verify that `repo_directory` exists and is accessible.
  - If directory does not exist, set `status=FAIL`.
  - If DEBUG=1 and directory does not exist, print: `[debug][task-find-solutions] directory does not exist: {{repo_directory}}`
  - If DEBUG=1 and directory exists, print: `[debug][task-find-solutions] directory validated: {{repo_directory}}`
  - If status=FAIL here, skip Steps 4–7 and go to Structured Output.

### Step 3 (MANDATORY)
Recursive Solution Discovery:
- Search all subdirectories recursively for files with `.sln` extension.
  - Use recursive glob pattern: `**/*.sln` (or equivalent for the language).
  - Convert each discovered path to absolute path string.
  - If DEBUG=1, print: `[debug][task-find-solutions] searching for *.sln files recursively`
  - For each solution found, if DEBUG=1, print: `[debug][task-find-solutions] found: {{solution_path}}`

### Step 4 (MANDATORY)
Path Collection:
- Build array of absolute paths to all discovered `.sln` files.
  - Order may vary by filesystem traversal; no guaranteed sorting.
  - If DEBUG=1 after collection complete, print: `[debug][task-find-solutions] discovered {{count}} solution(s)`

### Step 5 (MANDATORY)
Structured Output JSON:
Generate JSON only (no verification here) at `output/{{repo_name}}_task5_find-solutions.json`. Emit empty `verification_errors` array; populate in Step 11.

Structured Output JSON (output/{{repo_name}}_task5_find-solutions.json) MUST include:
- local_path
- repo_name
- solutions (array)
- solution_count
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 UTC seconds)
- verification_errors (array, empty if none)
- debug (optional array when DEBUG=1)

### Step 6 (MANDATORY)
Repo Checklist Update:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-find-solutions` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 7 (MANDATORY)
Repo Variable Refresh (INLINE ONLY):
- Open `tasks/{{repo_name}}_repo_checklist.md`.
- Locate lines beginning with:
  * `- {{solutions_json}}`
  * `- {{solutions}}`
- Replace ONLY text after `→` as follows:
  * `{{solutions_json}}` → path to JSON output file `output/{{repo_name}}_task5_find-solutions.json`.
  * `{{solutions}}` → `<count> solutions: Name1; Name2; Name3 ...` (list up to 5 names, then `...` if more). If zero: `0 solutions`.
- If FAIL status: set both to FAIL.
- If a line lacks an arrow, append one then the value.
**Inline Variable Policy:** Do not add new sections; update existing lines only.

### Step 8 (MANDATORY)
Verification (Post-Refresh):
Perform verification AFTER Steps 6–7 (checklist update and variable refresh). Load JSON from Step 5 and current checklist.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once (case-sensitive tokens): repo_name, repo_directory, solutions_json, solutions.
3. Arrow formatting correct (single arrow).
4. Task directive `@task-find-solutions` appears exactly once.
5. JSON required keys present: local_path, repo_name, solutions, solution_count, status, timestamp.
6. If status=SUCCESS:
  - `solution_count == len(solutions array)`.
  - Each listed solution path ends with `.sln`.
7. If `solution_count == 0` and status=SUCCESS: solutions array empty.
8. No duplicate solution basenames (case-insensitive) in JSON solutions array.
9. Checklist refreshed values coherence:
  - `solutions_json` checklist line points to generated JSON path.
  - `solutions` checklist summary begins with `<solution_count> solutions` (or `0 solutions`).
10. Base variables (repo_name, repo_directory) unchanged from Step 2 extraction.
 


### Step 9 (MANDATORY)
If DEBUG=1, print: `[debug][task-find-solutions] EXIT repo_directory='{{repo_directory}}' status={{status}} solution_count={{solution_count}}`

## Output Contract
- `local_path`: string (absolute path to repository root, from checklist)
- `repo_name`: string (repository name, from checklist)
- `solutions`: array[string] (absolute paths to all `.sln` files discovered, empty array if none found)
- `solution_count`: integer (number of solutions discovered)
- `status`: SUCCESS or FAIL (SUCCESS if directory valid, FAIL if directory does not exist)
- `timestamp`: string (ISO 8601 datetime when task completed)

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task.
2. Idempotency: Discovery re-runs always produce a fresh list; same input yields same output.
3. Ordering: Filesystem traversal order may differ across runs; no guarantee of stable ordering unless explicitly sorted.
4. Filtering: Only `.sln` extension; does not validate solution file contents or accessibility.
5. Performance: Use efficient recursive search API (e.g., Path.rglob in Python, Get-ChildItem -Recurse in PowerShell).
6. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
7. Progress Update: Only set `[x]` in repo-progress for task-find-solutions on SUCCESS.
8. Empty Results: Finding 0 solutions is SUCCESS (directory was valid, just no solutions present).
9. Script Location: Save generated script to `temp-script/` directory with naming pattern: `step{N}_repo{M}_task5_find-solutions.py`
\n+## Error Handling
- For any step that fails:
  - Log error details (exception type, message, stdout/stderr if a subprocess was used)
  - If repository directory validation fails, set status=FAIL and abort further steps
  - Do not update checklist or results CSV on critical failure
  - Non-critical issues (e.g., permission denied on one subdirectory) should be logged; continue searching remaining paths
\n+## Consistency Checks
- After writing `output/{{repo_name}}_task5_find-solutions.json`, verify it exists and contains keys: `solutions`, `solution_count`, `status`.
- Confirm `solution_count == len(solutions)`.
- After updating checklist ensure only the `@task-find-solutions` line is marked `[x]` (others untouched).
- Verify results CSV row contains the expected columns and solution_count token.
- If any verification fails, log an error and abort further updates.
\n+## Cross-References
- Always use the latest derived values when writing outputs.
- Variables relevant to this task:
  - repo_directory (input path being scanned)
  - repo_name (repository identifier)
  - solutions (array of absolute .sln paths)
  - solution_count (integer length of solutions array)
  - status (SUCCESS | FAIL)
  - timestamp (ISO 8601)
- Ensure checklist tokens `{{solutions_json}}`, `{{solutions}}` are updated from the final JSON output.