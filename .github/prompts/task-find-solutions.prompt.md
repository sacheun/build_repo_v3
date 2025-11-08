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
Checklist Load, Variable Extraction, Existing Solutions Parse & Input Validation:
- Open the file at `{{checklist_path}}`.
- Extract (value after `→`) from lines:
   - `- {{repo_directory}}`
- Confirm presence of tokens (values may be placeholders initially):
   - `- {{solutions_json}}`
- Validate immediately:
   - If any required line missing OR `repo_directory` value blank → set `status=FAIL` and proceed directly to Step 5 (skip discovery and path collection).
- If `solutions_json` has a non-blank value and the file exists, load it as JSON and:
   - Expect key `solutions` (array of absolute `.sln` paths).
   - Derive `preexisting_solution_names` by taking each path's basename without extension.
   - This preexisting list does NOT replace discovery; it is used only for logging/comparison.
- Base variables (`repo_directory`) are immutable; do NOT modify them.


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
3. Under `## Repo Variables Available` ensure a line exists beginning with:
  * `- {{solutions_json}}` (if missing, append it at the end of that section with an empty placeholder before updating)
4. Replace ONLY the text after `→` on the `{{solutions_json}}` line as follows (always perform this replacement, regardless of SUCCESS or FAIL):
  * On SUCCESS: `output/{{repo_name}}_task5_find-solutions.json`
  * On FAIL: `FAIL`
5. Always ensure exactly one `→` per line; if the line was newly created, format it exactly: `- {{solutions_json}} → FAIL` (for FAIL) or `- {{solutions_json}} → output/{{repo_name}}_task5_find-solutions.json` (for SUCCESS).
6. Do not modify any other checklist variables.

### Step 5 (MANDATORY)
Structured Output JSON:
Generate JSON only at `output/{{repo_name}}_task5_find-solutions.json`.

Structured Output JSON at `(output/{{repo_name}}_task5_find-solutions.json)` MUST include:
- local_path
- repo_name
- solutions (array)
- solution_count
- status (SUCCESS|FAIL)---
temperature: 0.0
---

@task-find-solutions checklist_path={{checklist_path}}

# Task name: task-find-solutions

## Description
This task discovers all Visual Studio solution files (`.sln`) within a repository directory tree.  
It is a **deterministic, scriptable operation** that must follow each step in exact sequence.

## Execution Policy
**STRICT SEQUENTIAL MODE**
- Each step must be executed **in order** and **fully completed** before continuing.
- Do **not summarise**, combine, or skip any step.
- Confirm the output or state change at the end of each step before moving to the next.
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow these steps exactly in sequence)

### Step 1 (MANDATORY — must complete before Step 2)
**Checklist Load, Variable Extraction, Existing Solutions Parse & Validation**

1. Open `{{checklist_path}}`.
2. Locate and extract the value (after `→`) from:
   - `- {{repo_directory}}`
3. Confirm presence of the following token (value may be placeholder):
   - `- {{solutions_json}}`
4. Validation rules:
   - If any required line missing **OR** `repo_directory` value blank → set `status=FAIL`, **record the failure**, and **jump directly to Step 5**.
5. If `solutions_json` has a non-blank value and points to an existing file, load JSON, expect key `solutions` (array of absolute `.sln` paths), and derive `preexisting_solution_names` (basename without extension for each path). This is for comparison ONLY; discovery still runs.
6. Record `repo_directory` as immutable; **do not alter it**.

✅ **At end of Step 1:** confirm that required variables are loaded, any preexisting solution names parsed, and validation result (`SUCCESS` or `FAIL`) is recorded.

---

### Step 2 (MANDATORY — only if Step 1 succeeded)
**Recursive Solution Discovery**

1. Recursively search within `{{repo_directory}}` for all `.sln` files.
   - Use pattern: `**/*.sln` (case-insensitive).
2. Convert each found path to an absolute path string.
3. If directory invalid or access denied, mark discovery `FAIL`.

✅ **At end of Step 2:** confirm number of `.sln` files found (even if zero) and whether search completed successfully.

---

### Step 3 (MANDATORY)
**Path Collection**

1. Build an array containing all absolute paths to `.sln` files discovered.
2. If none found, the array is empty — this is still `SUCCESS`.
3. Do not sort or filter unless explicitly required.

✅ **At end of Step 3:** confirm that array structure is valid JSON array.

---

### Step 4 (MANDATORY)
**Checklist Update & Variable Refresh (INLINE ONLY)**

1. Open `{{checklist_path}}` again.
2. Locate the `@task-find-solutions` task line and:
   - Mark `[x]` only if `status=SUCCESS`; leave `[ ]` if `FAIL`.
3. Under `## Repo Variables Available`, ensure:
   - A line exists beginning with `- {{solutions_json}}`
     - If missing, append it to the end of the section.
4. Replace only the value after `→` on `{{solutions_json}}`:
   - On SUCCESS: `output/{{repo_name}}_task5_find-solutions.json`
   - On FAIL: `FAIL`
5. Maintain exact format:  
   ```
   - {{solutions_json}} → output/{{repo_name}}_task5_find-solutions.json
   ```
   or  
   ```
   - {{solutions_json}} → FAIL
   ```
6. Never duplicate variable lines or change unrelated content.

✅ **At end of Step 4:** confirm that checklist file was updated in place and saved successfully.

---

### Step 5 (MANDATORY)
**Structured Output JSON**

1. Always generate (or overwrite) JSON at:
   ```
   output/{{repo_name}}_task5_find-solutions.json
   ```
2. Include the following fields in every run (even on FAIL):
   - `local_path`
   - `repo_name`
   - `solutions` (array)
   - `solution_count`
   - `status` (SUCCESS|FAIL)
   - `timestamp` (ISO 8601 UTC seconds)
3. On FAIL, set empty array for `solutions` and `solution_count=0`.

✅ **At end of Step 5:** confirm JSON file creation, field presence, and that timestamp uses UTC seconds.

---

### Step 6 (FINAL)
**Completion & Verification**

- Ensure all prior steps were executed in order.
- Confirm that both the checklist and output JSON files exist.
- Print or log `status` result (`SUCCESS` or `FAIL`).
- Do not terminate until all confirmations above are complete.

---

## Output Contract
| Field | Type | Description |
|--------|------|-------------|
| `local_path` | string | Absolute path to repository root |
| `repo_name` | string | Repository name from checklist |
| `solutions` | array[string] | Absolute paths to `.sln` files found |
| `solution_count` | integer | Count of `.sln` files found |
| `status` | enum | SUCCESS or FAIL |
| `timestamp` | string | ISO 8601 UTC timestamp |

## Implementation Notes
1. **SCRIPTABLE:** Generate a Python script for this task.
2. Always output a valid JSON, even on failure.
3. Treat empty results as SUCCESS.
4. Each step requires explicit confirmation before moving on.
5. Save the generated script to:  
   `temp-script/step{N}_repo{M}_task5_find-solutions.py`

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

