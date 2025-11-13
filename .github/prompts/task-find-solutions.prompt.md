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
**Completion & Confirmation**

1. Ensure all prior steps were executed in correct order.
2. Confirm that both checklist and output JSON files exist.
3. Print or log the final `status` result (SUCCESS or FAIL).
4. Do not terminate until all confirmations above are complete.

✅ **At end of Step 6:** all data should be consistent and files saved.

---

### Step 7 (FINAL VERIFICATION AND REDO SAFEGUARD)
**Explicit Variable & State Verification With Single Automatic Retry**

Re-open `{{checklist_path}}` from disk (fresh read; do not reuse cached content) and perform ALL checks below:

1. Task line correctness:
   - Locate the line containing `@task-find-solutions`.
   - If `status=SUCCESS` it MUST be `[x]`; if `status=FAIL` it MUST remain `[ ]`.
2. `solutions_json` variable line presence & format (exactly once):
   - Line MUST start with `- {{solutions_json}} →`.
   - When `status=SUCCESS`: value MUST equal `output/{{repo_name}}_task5_find-solutions.json`.
   - When `status=FAIL`: value MUST equal `FAIL`.
   - Single arrow `→`, one space on each side, no trailing spaces, no duplication.
3. JSON file validation (when `status=SUCCESS`):
   - File `output/{{repo_name}}_task5_find-solutions.json` MUST exist and be valid JSON.
   - Required fields: `local_path`, `repo_name`, `solutions` (array), `solution_count` (int), `status`, `timestamp`.
   - `solution_count == len(solutions)`.
   - Each path in `solutions` ends with `.sln` and is absolute (contains a drive letter or leading root indicator).
4. JSON file validation (when `status=FAIL`):
   - JSON file SHOULD still exist (empty `solutions` array, `solution_count=0`).
   - `solutions_json` variable line MUST be `FAIL` (not blank, not partial path).
5. Consistency checks:
   - `repo_name` inside JSON matches value from checklist.
   - No extraneous duplicate `{{solutions_json}}` lines.
6. Failure handling:
   - If ANY check fails (missing line, mismatched bracket state, bad path, JSON parse error, count mismatch) log: `WARNING: checklist verification failed - restarting from Step 1`.
   - Re-run Steps 1–6 completely once, then attempt this Step 7 again.
7. Finalization:
   - On success, log `VERIFICATION_PASSED`.
   - If retry also fails, set `status=FAIL` (if not already) and log `VERIFICATION_ABORTED`.

✅ **At end of Step 7:** Either verification passed (task COMPLETE & VERIFIED) or failure recorded after retry.

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
6. Verification (Step 7) is **mandatory** — never skip or ignore failed checklist updates.

---
