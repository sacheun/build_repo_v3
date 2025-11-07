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
Checklist Load, Variable Extraction & Input Validation (Combined):
- Open the file at `{{checklist_path}}`.
- Extract (value after `→`) from lines:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
- Confirm presence of tokens (values may be placeholders initially):
  - `- {{solutions_json}}`
  - `- {{solutions}}`
- Validate immediately:
  - If any required line missing OR `repo_name`/`repo_directory` value blank → set `status=FAIL` and proceed directly to Step 5 (skip discovery and path collection).
  - If `repo_directory` does not exist or inaccessible → set `status=FAIL` and proceed directly to Step 5.
- Base variables (`repo_name`, `repo_directory`) are immutable; do NOT modify them.
- Rationale: Combining removes redundant early failure branching and centralizes preconditions.

### Step 2 (MANDATORY)
Recursive Solution Discovery:
- Search all subdirectories recursively for files with `.sln` extension.
  - Use recursive glob pattern: `**/*.sln` (or equivalent for the language).
  - Convert each discovered path to absolute path string.

### Step 3 (MANDATORY)
Path Collection:
- Build array of absolute paths to all discovered `.sln` files.
  - Order may vary by filesystem traversal; no guaranteed sorting.

### Step 4 (MANDATORY)
Checklist Update & Variable Refresh (INLINE ONLY):
1. Open `{{checklist_path}}`.
2. Set `[x]` only on the `@task-find-solutions` entry if status=SUCCESS. Leave `[ ]` on FAIL.
3. Under `## Repo Variables Available` locate lines beginning with:
  * `- {{solutions_json}}`
  * `- {{solutions}}`
4. Populate ONLY the values for:
  * `- {{solutions_json}}` → `output/{{repo_name}}_task5_find-solutions.json` (path to structured output file)
  * `- {{solutions}}` → `<count> solutions: Name1; Name2; Name3 ...` (list up to 5 solution file base names, then `...` if more; if zero, `0 solutions`)
5. On FAIL status: set both values to `FAIL` (do not mark checklist task).
6. Always ensure exactly one `→` per line.
7. Do not modify any other checklist variables.

### Step 5 (MANDATORY)
Structured Output JSON:
Generate JSON only at `output/{{repo_name}}_task5_find-solutions.json`.

Structured Output JSON at `(output/{{repo_name}}_task5_find-solutions.json)` MUST include:
- local_path
- repo_name
- solutions (array)
- solution_count
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 UTC seconds)


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

