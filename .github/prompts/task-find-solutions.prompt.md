---
temperature: 0.0
---

@task-find-solutions repo_directory={{repo_directory}} repo_name={{repo_name}}

# Task name: task-find-solutions

## Process Overview
1. Debug Entry Trace
2. Input Validation & Checklist Verification
3. Recursive `.sln` Search
4. Path Collection & Counting
5. Structured Output JSON
6. Decision Log Entries (per solution or none found)
7. Result Tracking CSV Append
8. Repo Checklist Update
9. Repo Variable Refresh
10. Debug Exit Trace

## Prerequisites
- Valid repository directory path
- Accessible filesystem permissions for recursive search
- Repo checklist contains `{{solutions_json}}` and `{{solutions}}` tokens
- git not required; Python or PowerShell available for scripting

## Description
This task discovers all Visual Studio solution files (`.sln`) within a repository directory tree. This is a straightforward file search operation that **must** be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-find-solutions] START repo_directory='{{repo_directory}}'`

### Step 2 (MANDATORY)
Input Parameters:
- You are given `repo_directory` (absolute path to repository root) and `repo_name` from the calling context.

Input Validation:
- Verify that `repo_directory` exists and is accessible.
  - If directory does not exist, set `status=FAIL`.
  - If DEBUG=1 and directory does not exist, print: `[debug][task-find-solutions] directory does not exist: {{repo_directory}}`
  - If DEBUG=1 and directory exists, print: `[debug][task-find-solutions] directory validated: {{repo_directory}}`

Pre-flight Checklist Verification:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  - `{{solutions_json}}`
  - `{{solutions}}`
- If any token is missing or altered, restore it prior to continuing.

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
Structured Output:
- Save JSON object to `output/{{repo_name}}_task5_find-solutions.json` with:
  - `local_path`: echoed from input (`repo_directory`)
  - `repo_name`: echoed from input
  - `solutions`: array of absolute paths to `.sln` files (empty array if none found)
  - `solution_count`: integer count of discovered solutions
  - `status`: SUCCESS if directory validated (even if 0 solutions found), FAIL if directory invalid
  - `timestamp`: ISO 8601 format datetime when task completed

### Step 6 (MANDATORY)
Log to Decision Log:
- Call @task-update-decision-log to log task execution:
  - For EACH solution discovered:
    - Extract solution name from path (e.g., `C:\...\MyApp.sln` → `MyApp`)
    - Call:
      ```
      @task-update-decision-log
      timestamp="{{timestamp}}"
      repo_name="{{repo_name}}"
      solution_name=""
      task="task-find-solutions"
      message="Found solution: {{solution_name}}"
      status="SUCCESS"
      ```
  - If NO solutions found:
    - Call:
      ```
      @task-update-decision-log
      timestamp="{{timestamp}}"
      repo_name="{{repo_name}}"
      solution_name=""
      task="task-find-solutions"
      message="No solutions found"
      status="SUCCESS"
      ```
  - Use ISO 8601 format for timestamp (e.g., `2025-10-22T14:30:45Z`)
  - The `solution_name` is blank since this is a repository-level task
  - Status: "SUCCESS" (even if 0 solutions found, as long as directory was valid)

### Step 7 (MANDATORY)
Result Tracking:
- Append the result to:
  - `results/repo-results.csv` (CSV row)
  - Row format: `timestamp, repo_name, task-find-solutions, {{solution_count}} solutions, status, symbol (✓ or ✗)`

### Step 8 (MANDATORY)
Repo Checklist Update:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-find-solutions` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 9 (MANDATORY)
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

### Step 10 (MANDATORY)
If DEBUG=1, print: `[debug][task-find-solutions] EXIT repo_directory='{{repo_directory}}' status={{status}} solution_count={{solution_count}}`

## Output Contract
- `local_path`: string (absolute path to repository root, echoed from input)
- `repo_name`: string (repository name, echoed from input)
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