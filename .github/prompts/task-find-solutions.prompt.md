---
temperature: 0.0
---

@task-find-solutions checklist_path={{checklist_path}}

# Task name: task-find-solutions

## Description
This task discovers all Visual Studio solution files (`.sln`) within a repository directory tree. This is a straightforward file search operation that CAN be implemented as a script.

## Execution Policy
**STRICT MODE ON**
- All steps are **MANDATORY**.
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

### Step 2 (MANDATORY)
Input Validation:
- Verify that `repo_directory` exists and is accessible.
  - If directory does not exist, set `status=FAIL`.
  - If status=FAIL here, skip Steps 4–7 and go to Structured Output.

### Step 3 (MANDATORY)
Recursive Solution Discovery:
- Search all subdirectories recursively for files with `.sln` extension.
  - Use recursive glob pattern: `**/*.sln` (or equivalent for the language).
  - Convert each discovered path to absolute path string.

### Step 4 (MANDATORY)
Path Collection:
- Build array of absolute paths to all discovered `.sln` files.
  - Order may vary by filesystem traversal; no guaranteed sorting.


### Step 5 (MANDATORY)
Structured Output JSON:
Generate JSON only (no verification here) at `output/{{repo_name}}_task5_find-solutions.json`

Structured Output JSON at `(output/{{repo_name}}_task5_find-solutions.json)` MUST include:
- local_path
- repo_name
- solutions (array)
- solution_count
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 UTC seconds)
- verification_errors (array, empty if none)
  (debug array output omitted; no DEBUG mode supported)

### Step 6 (MANDATORY)
Checklist Update & Variable Refresh (INLINE ONLY):
1. Open `{{checklist_path}}`.
2. Set `[x]` only on the `@task-find-solutions` entry if status=SUCCESS. Leave `[ ]` on FAIL.
3. Locate lines beginning with:
   * `- {{solutions_json}}`
   * `- {{solutions}}`
4. Replace ONLY text after `→` as follows:
   * `{{solutions_json}}` → `output/{{repo_name}}_task5_find-solutions.json`
   * `{{solutions}}` → `<count> solutions: Name1; Name2; Name3 ...` (list up to 5 names, then `...` if more). If zero: `0 solutions`.
5. If FAIL status: set both to `FAIL` (do not mark checklist).
6. If a line lacks an arrow, normalize: `- {{token}} → <value>`.
7. **Inline Variable Policy:** Do not add new sections; update existing lines only; never duplicate variable lines.


 
### End of Steps

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

