---
temperature: 0.0
---

@task-find-solutions checklist_path={{checklist_path}}

# Task name: task-find-solutions

## Process Overview
1. Debug Entry Trace
2. Checklist Load & Variable Extraction
3. Input Validation
4. Recursive `.sln` Search
5. Path Collection & Counting
6. Structured Output JSON
7. Decision Log Entries (per solution or none found)
8. Result Tracking CSV Append
9. Repo Checklist Update
10. Repo Variable Refresh
11. Verification (Post-Refresh)
12. Debug Exit Trace

## Prerequisites
- Checklist file at `checklist_path` containing variable lines for:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
  - `- {{solutions_json}}`
  - `- {{solutions}}`
- Accessible filesystem permissions for recursive search
- git not required; Python or PowerShell available for scripting

## Description
This task discovers all Visual Studio solution files (`.sln`) within a repository directory tree. This is a straightforward file search operation that **must** be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-find-solutions] START checklist_path='{{checklist_path}}'`

### Step 2 (MANDATORY)
Checklist Load & Variable Extraction:
- Open the file at `{{checklist_path}}`.
- Extract (value after `→`) from lines:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
  - Confirm presence of tokens `- {{solutions_json}}` and `- {{solutions}}` (values may be placeholders initially).
- If any required line missing or value blank for repo_name/repo_directory, set `status=FAIL` and proceed to structured output.
- Base variables (`repo_name`, `repo_directory`) are immutable; do NOT modify them.
- If DEBUG=1, print: `[debug][task-find-solutions] extracted repo_name='{{repo_name}}' repo_directory='{{repo_directory}}'`

### Step 3 (MANDATORY)
Input Validation:
- Verify that `repo_directory` exists and is accessible.
  - If directory does not exist, set `status=FAIL`.
  - If DEBUG=1 and directory does not exist, print: `[debug][task-find-solutions] directory does not exist: {{repo_directory}}`
  - If DEBUG=1 and directory exists, print: `[debug][task-find-solutions] directory validated: {{repo_directory}}`
  - If status=FAIL here, skip Steps 4–7 and go to Structured Output.

### Step 4 (MANDATORY)
Recursive Solution Discovery:
- Search all subdirectories recursively for files with `.sln` extension.
  - Use recursive glob pattern: `**/*.sln` (or equivalent for the language).
  - Convert each discovered path to absolute path string.
  - If DEBUG=1, print: `[debug][task-find-solutions] searching for *.sln files recursively`
  - For each solution found, if DEBUG=1, print: `[debug][task-find-solutions] found: {{solution_path}}`

### Step 5 (MANDATORY)
Path Collection:
- Build array of absolute paths to all discovered `.sln` files.
  - Order may vary by filesystem traversal; no guaranteed sorting.
  - If DEBUG=1 after collection complete, print: `[debug][task-find-solutions] discovered {{count}} solution(s)`

### Step 6 (MANDATORY)
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

### Step 7 (MANDATORY)
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

### Step 8 (MANDATORY)
Result Tracking:
- Append the result to:
  - `results/repo-results.csv` (CSV row)
  - Row format: `timestamp, repo_name, task-find-solutions, {{solution_count}} solutions, status, symbol (✓ or ✗)`
 - (Do NOT verify presence here; CSV row presence/format is validated only in Step 11.)

### Step 9 (MANDATORY)
Repo Checklist Update:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-find-solutions` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 10 (MANDATORY)
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

### Step 11 (MANDATORY)
Verification (Post-Refresh):
Perform verification AFTER Steps 9–10 (checklist update and variable refresh). Load JSON from Step 6 and current checklist.

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
11. Results CSV row present and correctly formatted for this task execution (pattern begins with `{{timestamp}},{{repo_name}},task-find-solutions,{{solution_count}} solutions,{{status}},` and ends with ✓ or ✗).

Violations recorded as `{ "type": "<code>", "target": "<file|variable|json>", "detail": "<description>" }`.
Suggested codes: file_missing, variable_missing, variable_empty, duplicate_variable, arrow_format_error, json_missing_key, count_mismatch, invalid_extension, duplicate_solution_basename, summary_mismatch, base_variable_modified, results_row_missing.

Status Adjustment:
- Start with JSON status. If status=SUCCESS and violations exist → set status=FAIL. Leave FAIL unchanged.

Update JSON: overwrite verification_errors (sorted by type then target) and updated status if changed. Preserve timestamp.

### Step 12 (MANDATORY)
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