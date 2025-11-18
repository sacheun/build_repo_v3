@task-run-solution solution_checklist={{solution_checklist}}
---
temperature: 0.0
---

Task name: task-run-solution

## Description
Runs the primary executable for a solution based on the `verified_artifacts` recorded in the solution checklist.

If verification has not yet succeeded, this task will (re)invoke the build-artifact verification task first. If verification has failed, it will skip running the solution.

## Reliability Framework (MANDATORY)
- **Sequential execution**: Perform the steps strictly in order; never skip or merge steps.
- **Checkpointing**: After each step print `✅ Step N complete` or `❌ Step N failed — <reason>`.
- **Retry-once policy**: On validation failure retry the entire step once; if it still fails set `status=FAIL` and continue to structured output.
- **Atomic writes**: Any file mutation must be atomic (write temp file then replace original).
- **Audit**: Before finishing ensure all checkpoints were printed; otherwise set `status=FAIL_MISSING_STEP`.

---
## Instructions (Follow Exactly — Each Step Emits a Checkpoint)

### Step 1 — Checklist & Verification Status Validation (MANDATORY)
1. Expect `solution_checklist` pointing to `tasks/<repo>_<solution>_solution_checklist.md`.
2. Confirm file exists and decode as UTF-8 (use `errors='ignore'`). Missing file → `status=FAIL` (`error="checklist_missing"`).
3. In section `### Solution Variables`, extract at minimum:
   - `solution_path`
   - `verify_status`
   - `verified_artifacts`
   - `executable_artifacts` (if present)
4. Validate `solution_path` is non-empty, exists on disk, and ends with `.sln`. Failure → `status=FAIL` (`error="solution_path_invalid"`).
5. Behaviour for `verify_status`:
   - If `verify_status == "SUCCEED"` (or `"SUCCEEDED"`), continue.
   - If `verify_status` is blank/empty:
     - Re-run the artifact verification task **by invoking** `@task-validate-build-artifacts` (task-verify-build-artifacts) according to `.github/prompts/task-validate-build-artifacts.prompt.md`.
     - After it completes, reload the checklist and re-read `verify_status` and `verified_artifacts`.
   - If `verify_status` indicates failure (e.g., `"FAIL"` or `"FAILED"`), set `status="VERIFY_FAILED"`, skip Steps 2–4, and proceed to Step 5 (structured output only).
6. **Checkpoint**: Print `✅ Step 1 complete` (or the failure variant) and continue.

---

### Step 2 — Ensure Verified Artifacts Present (MANDATORY)
1. With the refreshed checklist content, check `verified_artifacts` in `### Solution Variables`.
2. If `verified_artifacts` is blank or missing:
   - Re-run the artifact verification task (`@task-validate-build-artifacts`) once more.
   - Reload the checklist and re-read `verified_artifacts`.
   - If still blank, set `status="NO_VERIFIED_ARTIFACTS"`, skip Steps 3–4, and continue to Step 5.
3. If `verified_artifacts` is non-blank, parse it as a list of paths (comma- or newline-separated; preserve exact formatting but treat each entry as a candidate artifact path).
4. From this list, filter entries that look like executable files (typically paths ending with `.exe`). Save this filtered list as `candidate_executables`.
5. Update the `executable_artifacts` variable line in `### Solution Variables` to contain the list of executable paths (e.g., joined by `, `). If no executables are found, leave `executable_artifacts` blank.
6. Write the updated checklist back to disk atomically and re-open it to confirm the `executable_artifacts` value.
7. **Checkpoint**: Print `✅ Step 2 complete` (or failure variant) and continue.

---

### Step 3 — Select and Run Executable (MANDATORY)
1. Reload `solution_checklist` and read `executable_artifacts`.
2. Parse `executable_artifacts` into a list of absolute paths (comma- or newline-separated).
3. If at least one executable path exists:
   - Select the first valid existing `.exe` path as `primary_exe`.
   - Run it in a shell from its containing directory, e.g.:
     - Working directory = `os.path.dirname(primary_exe)`
     - Command (conceptually): `"primary_exe"` (no extra arguments by default).
   - Capture stdout, stderr, and exit code; apply a reasonable timeout (e.g., 10 minutes) and allow user-interactive behaviour only as supported by the environment.
   - Record `run_mode="direct_exe"`.
4. If **no executable paths** are present in `executable_artifacts` **or none of them exist** on disk, do **not** fail immediately. Instead, proceed to solution-level fallback in Step 4.
5. **Checkpoint**: Print `✅ Step 3 complete` (or failure variant) and continue.

---

### Step 4 — Fallback: dotnet sln list & dotnet run (MANDATORY)
1. If Step 3 did not successfully run an executable (e.g., no valid `.exe` found), fall back to running the solution via `dotnet`.
2. Derive:
   - `solution_name` = basename of `solution_path` without extension.
   - `solution_dir` = directory containing the `.sln` file.
3. From `solution_dir`, execute:
   ```
   dotnet sln "{{solution_path}}" list
   ```
   - Capture stdout and stderr.
4. From the output, identify a **startup project** heuristically. Examples of heuristics (apply in this order):
   - Prefer projects whose name ends with `.App`, `.Application`, or `.Api`.
   - Otherwise prefer projects whose path contains `Startup`, `Program`, or `Host`.
   - If multiple candidates match, pick the first.
5. Once a candidate project path (relative to `solution_dir`) is identified, build an absolute path `startup_csproj`.
6. Execute (from `solution_dir`):
   ```
   dotnet run --project "startup_csproj" --configuration Release
   ```
   - Capture stdout, stderr, and exit code; apply a reasonable timeout (e.g., 10–20 minutes).
   - Record `run_mode="dotnet_run_project"`.
7. If no suitable project can be determined from `dotnet sln list`, set `status="NO_STARTUP_PROJECT_FOUND"` and record diagnostics; still proceed to Step 5.
8. **Checkpoint**: Print `✅ Step 4 complete` (or failure variant) and continue.

---

### Step 5 — Structured Output & Checklist Update (MANDATORY)
1. Compose JSON payload including at least:
   - `solution_checklist`
   - `solution_path`
   - `run_mode` (`"direct_exe"`, `"dotnet_run_project"`, or `"none"`)
   - `primary_exe` (if used)
   - `startup_csproj` (if used)
   - `run_exit_code` (if any command ran)
   - `verify_status`
   - `verified_artifacts`
   - `executable_artifacts`
   - `stdout_tail` and `stderr_tail` for the last run command (last 12,000 characters each)
   - `status` summarising overall result (`SUCCESS`, `VERIFY_FAILED`, `NO_VERIFIED_ARTIFACTS`, `NO_STARTUP_PROJECT_FOUND`, `FAIL`, etc.)
   - ISO-8601 timestamp
2. Emit JSON to stdout and atomically save to `output/{{solution_name}}_task-run-solution.json`.
3. Reload the checklist, locate the first unchecked task line containing `@task-run-solution`, and mark it complete (`- [ ]` → `- [x]`). If not present, log a verification warning but continue.
4. Ensure `executable_artifacts` and any other variables updated in previous steps remain consistent; do not modify unrelated variables.
5. Write the updated checklist atomically and re-open to validate that the checkbox and variables are in place.
6. Print final checkpoint message and audit that all intermediate checkpoint messages exist; if any are missing, set `status="FAIL_MISSING_STEP"` in the JSON summary.

---

## Implementation Notes
- Use UTF-8 with `errors='ignore'` for file I/O.
- Treat `verified_artifacts` and `executable_artifacts` as opaque strings when writing to the checklist, but parse them as simple comma/newline-separated lists when needed.
- Invocation of `@task-validate-build-artifacts` should follow its own strict prompt contract (all steps, checkpoints, and atomic writes), and this task must re-read the checklist after that task completes.
- Do not assume interactive console support for the executable; capture output and exit code without requiring user input.
- When multiple executables are present, selecting the first is sufficient unless a more specific heuristic is added later.
