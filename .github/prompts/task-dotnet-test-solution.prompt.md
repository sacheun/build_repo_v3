@task-dotnet-test-solution solution_checklist={{solution_checklist}}
---
temperature: 0.0
---

Task name: task-dotnet-test-solution

## Description
Executes `dotnet test` against a Visual Studio solution referenced by the solution checklist, captures TRX results, extracts summary statistics, and updates testing variables in the checklist.

## Reliability Framework (MANDATORY)
- **Sequential execution**: Perform the steps strictly in order; never skip or merge steps.
- **Checkpointing**: After each step print `✅ Step N complete` or `❌ Step N failed — <reason>`.
- **Retry-once policy**: On validation failure retry the entire step once; if it still fails set `status=FAIL` and continue to structured output.
- **Atomic writes**: Any file mutation must be atomic (write temp file then replace original).
- **Audit**: Before finishing ensure all checkpoints were printed; otherwise set `status=FAIL_MISSING_STEP`.

---

## Step 1 — Checklist & Input Validation (MANDATORY)
1. Expect `solution_checklist` pointing to `tasks/<repo>_<solution>_solution_checklist.md`.
2. Confirm file exists and decode as UTF-8 (use `errors='ignore'`). Missing file → `status=FAIL` (`error="checklist_missing"`).
3. In section `### Solution Variables`, extract:
   - `solution_path`
   - Existing values (if any) for `test_run_status`, `total_tests_count`, `passed_tests_count`, `failed_tests_count`.
4. Validate `solution_path` is non-empty, exists on disk, and ends with `.sln`. Failure → `status=FAIL` (`error="solution_path_invalid"`).
5. Derive `solution_name` (basename w/out extension) and `solution_dir` (directory of the solution).

---

## Step 2 — dotnet test Execution (MANDATORY)
1. Build absolute TRX output path inside a dedicated temp directory under `output/tests/<solution_name>/` (create directory if needed).
2. Command (execute from `solution_dir`):
   ```
   dotnet test "{{solution_path}}" --logger "trx;LogFileName=test_results.trx"
   ```
3. Capture stdout, stderr, and exit code. Enforce 30-minute timeout.
4. After command completes, verify that a TRX file exists at the expected path; if not found record verification error but continue.
5. Determine `test_success = (exit_code == 0)`.

---

## Step 3 — TRX Parsing & Metrics (MANDATORY)
1. If TRX file exists, parse it as XML to extract counts from the `<ResultSummary>/<Counters>` element (`total`, `passed`, `failed`, `skipped`).
2. If parsing fails or counters missing, set counts to:
   - `total = max(passed + failed + skipped, 0)`
   - `passed = failed = skipped = 0` and add verification error.
3. Record `skipped_tests_count` for completeness, but only `total`, `passed`, `failed` required for checklist update.
4. Compute `test_run_status`:
   - `SUCCEEDED` when `test_success` and `failed == 0`
   - `FAILED` when `failed > 0` or exit code non-zero
   - `SKIPPED` if total == 0 and exit code == 0 (no tests discovered)

---

## Step 4 — Structured Output (MANDATORY)
1. Compose JSON payload:
   ```json
   {
     "solution_checklist": "...",
     "solution_name": "...",
     "solution_path": "...",
     "test_exit_code": <int>,
     "test_run_status": "SUCCEEDED|FAILED|SKIPPED",
     "total_tests_count": <int>,
     "passed_tests_count": <int>,
     "failed_tests_count": <int>,
     "skipped_tests_count": <int>,
     "trx_path": "...",
     "stdout_tail": "...",
     "stderr_tail": "..."
   }
   ```
2. Tails should contain the last 12,000 characters of stdout/stderr.
3. Emit JSON to stdout and atomically save to `output/{{solution_name}}_task-dotnet-test-solution.json`.

---

## Step 5 — Checklist Update (MANDATORY)
1. Reload checklist content from disk (fresh read).
2. Mark the first unchecked task line containing `@task-dotnet-test-solution` as complete (`- [ ]` → `- [x]`). If no such line exists, log a verification error but continue. Perform this checkbox update first and keep the modified line in memory before changing any solution variables (mirrors ordering pattern used in Step 9 of `task-verify-build-artifacts`).
3. After confirming the task line update, locate `### Solution Variables` and update (or insert if missing) exactly one line for each:
   - `- test_run_status → SUCCEEDED|FAILED|SKIPPED`
   - `- total_tests_count → <int>`
   - `- passed_tests_count → <int>`
   - `- failed_tests_count → <int>`
4. Preserve other variables and formatting (maintain arrow character `→`). Do not alter unrelated lines.
5. Write the updated checklist atomically (temp file + replace) so the checkbox and variable edits land together.

---

## Step 6 — Final Verification & Summary (MANDATORY)
1. Re-open the checklist to confirm the task line was marked and all four variables match Step 3 results.
2. Ensure every checkpoint message exists. Missing checkpoint → set `status=FAIL_MISSING_STEP` and note in `verification_errors`.
3. Emit final JSON (stdout and `output/{{solution_name}}_task-dotnet-test-solution-final.json`) including:
   - Fields from Step 4
   - `verification_errors`: list of strings (empty if none)
   - `status`: `SUCCESS` when all verifications pass else `FAIL`
   - ISO-8601 timestamp
4. Print `[task-dotnet-test-solution] Completed` noting success/failure.

---

## Implementation Notes
- Use UTF-8 with `errors='ignore'` for file I/O.
- When parsing XML, guard against namespace prefixes; prefer `.find('.//{*}Counters')` style or manual traversal.
- If multiple TRX files are produced, use the most recent within the temp directory.
- Do not attempt to infer pass/fail from textual output; rely on exit code and TRX counters.


