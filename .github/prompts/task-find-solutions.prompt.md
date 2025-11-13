---
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

---

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

### Step 6 (MANDATORY)
**Final Verification & Completion (With Single Automatic Retry)**

1. Ensure Steps 1–5 executed sequentially and that both the checklist and `output/{{repo_name}}_task5_find-solutions.json` files currently exist on disk.
2. Print or log the final `status` result (SUCCESS or FAIL) before verification begins.
3. Re-open `{{checklist_path}}` from disk (fresh read; do not reuse cached content) and perform ALL checks below:
   - **Task line correctness**: the line containing `@task-find-solutions` must be `[x]` when `status=SUCCESS`, and must remain `[ ]` when `status=FAIL`.
   - **`solutions_json` variable**: exactly one line starts with `- {{solutions_json}} →`. When `status=SUCCESS`, its value is `output/{{repo_name}}_task5_find-solutions.json`; when `status=FAIL`, its value is `FAIL`. Ensure proper spacing around the arrow and no duplicates.
   - **JSON validation (SUCCESS cases)**: `output/{{repo_name}}_task5_find-solutions.json` exists, parses as JSON, and includes the required fields (`local_path`, `repo_name`, `solutions`, `solution_count`, `status`, `timestamp`). Confirm `solution_count == len(solutions)` and each entry in `solutions` is an absolute `.sln` path.
   - **JSON validation (FAIL cases)**: JSON file still exists with `solutions=[]`, `solution_count=0`, and `status=FAIL`. Confirm the checklist variable value is `FAIL`.
   - **Consistency**: `repo_name` inside the JSON matches the checklist value, and no duplicate `{{solutions_json}}` lines are present.
4. If ANY verification check fails (missing line, mismatched bracket state, invalid JSON, count mismatch, etc.):
   - Log `WARNING: checklist verification failed - restarting from Step 1`.
   - Re-run Steps 1–5 completely once, then repeat Step 6.
5. Finalize verification:
   - If the second attempt still fails, set `status=FAIL` (if not already) and log `VERIFICATION_ABORTED`.
   - Otherwise log `VERIFICATION_PASSED` and exit.

✅ **At end of Step 6:** Verification either passes (`VERIFICATION_PASSED`) or the failure is recorded after a single retry attempt.

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
5. Save generated script to:  
   `temp-script/step{N}_repo{M}_task5_find-solutions.py`
6. Final verification (Step 6) is **mandatory** — never skip or ignore failed checklist updates.

---
