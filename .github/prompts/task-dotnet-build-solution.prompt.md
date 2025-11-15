@task-dotnet-build-solution solution_checklist={{solution_checklist}}
---
temperature: 0.0
---

Task name: task-dotnet-build-solution

## Description
Runs a deterministic two-stage `dotnet` clean/build pipeline for a Visual Studio solution referenced by a solution checklist, then records results and updates checklist state including the `dotnetbuild_status` variable.

## Reliability Framework (MANDATORY)
- **Sequential execution**: Follow the steps in order; do not reorder, merge, or skip.
- **Checkpointing**: After every major step print either `✅ Step N complete` or `❌ Step N failed — <reason>`.
- **Retry-once**: If a validation fails, retry the whole step exactly once before declaring failure.
- **Atomic writes**: Any checklist or artifact update must be atomic (write to temp file then replace).
- **Audit**: Before finishing, confirm that all checkpoints were printed; otherwise set `status=FAIL_MISSING_STEP`.

---

## Step 1 — Input & Checklist Validation (MANDATORY)
1. Expect parameter `solution_checklist` (path to `tasks/<repo>_<solution>_solution_checklist.md`).
2. Confirm file exists and is UTF-8 decodable. On failure → `status=FAIL` (`error="checklist_missing"`).
3. Parse `### Solution Variables` section and extract:
   - `solution_path` (after `- solution_path →`).
   - `dotnetbuild_status` (create placeholder `- dotnetbuild_status → UNKNOWN` if missing; note in verification_errors).
4. Validate `solution_path` exists and ends with `.sln`. If missing or invalid → `status=FAIL` (`error="solution_path_invalid"`).
5. Derive `solution_name` = basename without extension and `solution_dir` = directory path.

---

## Step 2 — dotnet clean (MANDATORY)
1. Command:
   ```
   dotnet clean "{{solution_path}}"
   ```
2. Execute synchronously with 20-minute timeout; capture stdout, stderr, exit code.
3. If the command cannot be started (dotnet missing) → `status=FAIL` (`error="dotnet_missing"`) and proceed to Step 5.
4. Record results (`clean_stdout`, `clean_stderr`, `clean_exit_code`).

---

## Step 3 — dotnet build Release (MANDATORY)
1. Command:
   ```
   dotnet build "{{solution_path}}" --configuration Release
   ```
2. Execute synchronously; capture stdout, stderr, exit code (`build_stdout`, `build_stderr`, `build_exit_code`).
3. Determine `success = (clean_exit_code == 0 and build_exit_code == 0)`.
4. Trim each captured stream to last 12,000 characters to form `clean_stdout_tail`, `clean_stderr_tail`, `build_stdout_tail`, `build_stderr_tail`.

---

## Step 4 — Structured Output & Artifacts (MANDATORY)
1. Compose JSON payload:
   ```json
   {
     "solution_checklist": "...",
     "solution_path": "...",
     "solution_name": "...",
     "success": true|false,
     "clean_exit_code": <int>,
     "build_exit_code": <int>,
     "clean_stdout_tail": "...",
     "clean_stderr_tail": "...",
     "build_stdout_tail": "...",
     "build_stderr_tail": "...",
     "warnings": [...],
     "errors": [...]
   }
   ```
2. Emit JSON to stdout and atomically store at `output/{{solution_name}}_task-dotnet-build-solution.json`.

---

## Step 5 — Checklist Update (MANDATORY)
1. Re-open checklist content from disk.
2. Mark the first unchecked line containing `@task-dotnet-build-solution` as completed (`- [ ]` → `- [x]`). If no such line exists, log verification error but continue.
3. In `### Solution Variables`, set `dotnetbuild_status` to `"SUCCEEDED"` when `success` else `"FAILED"` (preserve exact arrow symbol `→`). Ensure exactly one `dotnetbuild_status` line exists.
4. Preserve other variables unchanged. Write updated checklist atomically.

---

## Step 6 — Final Verification & Summary (MANDATORY)
1. Re-open checklist and confirm:
   - Task line was marked (if present).
   - `dotnetbuild_status` matches outcome.
2. Ensure all checkpoints were printed; if not, set `status=FAIL_MISSING_STEP` and record details in `verification_errors`.
3. Emit final JSON (stdout and `output/{{solution_name}}_task-dotnet-build-solution-final.json`) containing:
   - Fields from Step 4 plus `verification_errors`, `status`, and a timestamp.
4. Print `[task-dotnet-build-solution] Completed` with success/failure note.

---

## Implementation Notes
- All file I/O must use UTF-8 with `errors='ignore'` when reading legacy content.
- Treat placeholder insertions or missing lines as verification warnings, not silent repairs.
- Do not attempt to infer success from text; rely strictly on exit codes.
- Run commands from the checklist directory (`solution_dir`) when possible to ensure relative paths resolve.

````
