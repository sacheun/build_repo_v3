@task-build-solution solution_path={{solution_path}}
---
temperature: 0.0
---

Task name: task-build-solution

## Description
Performs a clean MSBuild (Clean + Build) of a Visual Studio solution in Release configuration, extracts diagnostic tokens, classifies them, and returns structured JSON summarizing build success. This version adds strict, checkpoint-driven execution to prevent skipped steps.

## Reliability Framework (MANDATORY)
- **Sequential enforcement**: Steps 1→11 must run in order. Do not skip, merge, or reorder steps.
- **Checkpointing**: After each step, print a checkpoint line: `✅ Step N complete` or on failure `❌ Step N failed — <reason>`.
- **Retry-once**: If a step's required validation fails, retry the step once; on second failure set `status=FAIL` and go to final structured output.
- **Atomic writes**: All file writes must be atomic — build to temp file then move/replace.
- **Audit**: Final integrity check confirms all checkpoints present; otherwise set `status=FAIL_MISSING_STEP`.

---

## Step 1 — Input Validation (MANDATORY)
1. Verify `{{solution_path}}` parameter provided, is a string, and file exists. If missing → set `status=FAIL` (error: "CONTRACT") and emit JSON as described in Step 8.
2. Must end with `.sln`; otherwise `status=FAIL` (error: "CONTRACT").
3. Derive `solution_name` = basename without extension.

---

## Step 2 — Pre-Build Artifact: Snapshot build_count (MANDATORY)
1. Open checklist: `{{solution_path}}`. If file missing, record warning but continue (task may still run).
2. Parse `### Solution Variables` and read single authoritative `- build_count → <int>` line. If missing, assume 0 and insert a single `- build_count → 0` placeholder atomically (but mark that insertion in verification_errors).
3. Cache `old_build_count` (integer) in memory for mapping logic and artifact naming (do not modify file here).
4. Also capture the current `build_status` value. If it is already `SUCCEEDED`, set a flag `skip_build_due_to_prior_success = true` and obey the following rules for the remainder of the task:
   - Skip Steps 3–8 entirely; no additional MSBuild invocation or JSON artifacts are required when the previous build succeeded.
   - In Step 9 leave `build_count` untouched (do **not** increment it) and simply ensure the existing task line remains checked.
   - In Step 10 leave `build_status` as-is and set the matching retry status slot (e.g., `retry_build_status_attempt_1`) to `SKIPPED (build already succeeded)` so the checklist records that no rerun occurred.

---

## Step 3 — MsBuild Invocation (MANDATORY)
1. Command (exact):
   ```
   msbuild "{{solution_path}}" --target:Clean,Build --property:Configuration=Release --maxcpucount --verbosity:quiet -noLogo
   ```
2. Execute synchronously, capture full stdout/stderr and exit code. Timeout: 30 minutes by default (configurable).
3. On execution failure to start (both msbuild and dotnet missing), set `status=FAIL` and proceed to Step 8.

---

## Step 4 — Success Determination (MANDATORY)
1. `success = (exit_code == 0)` based on final build invocation (after attempted fallbacks).

---

## Step 5 — Tail Truncation (MANDATORY)
1. Truncate stdout and stderr tails to the **last 12,000 characters** each (if shorter, keep full content).
2. Store as `stdout_tail`, `stderr_tail`.

---

## Step 6 — Token Extraction (MANDATORY)
1. Combine full captured output (prefer using truncated tails for performance) and scan for unique tokens matching patterns: `CS\d{4}`, `NETSDK\d{4}`, `CA\d{4}`, `NU\d{4}`, `MSB\d{4}` (case-insensitive).
2. Produce `tokens` = distinct list of matches.

---

## Step 7 — Classification Heuristic (MANDATORY)
1. For each token, search combined output for a case-insensitive line containing `warning` near the token (same line or +/-2 lines). If found → categorize as `warning`, else `error`.
2. Build two distinct arrays: `warnings[]` and `errors[]`; each element `{ code: <token>, message: "" }` (message reserved for future enrichment).
3. Cap arrays to first 200 entries total (100 each preferred); record truncation in verification_errors if exceeded.

---

## Step 8 — Pre-Commit Artifact JSON (MANDATORY)
1. Compose base JSON payload (regardless of success):
   - solution_path, solution_name, success, return_code, stdout_tail, stderr_tail, errors[], warnings[]
2. Write JSON to stdout and also save to `output/{{solution_name}}_task-build-solution.json` atomically.
3. Additionally, create count-suffixed copy **using PRE-INCREMENT** `old_build_count` (see Step 2) at:
   - `output/{{repo_name}}_{{solution_name}}_task-build-solution_buildcount-{{old_build_count}}.json`

---

## Step 9 — Checklist Marking & build_count Increment (MANDATORY)
1. Load checklist file and authoritative `- build_count → <old>` line (if missing, was inserted in Step 2).
2. Determine `target_line_to_mark` using **old_build_count** mapping:
   - 0 → mark the primary `@task-build-solution` line
   - 1 → mark first retry line `@task-build-solution-retry` (Attempt 1)
   - >=4 → do NOT mark any task line (limit reached)
3. For the chosen target: if it exists and is currently `- [ ]`, change leading `- [ ]` → `- [x]`. If already `- [x]`, leave unchanged (do not unmark others).
4. Compute `new_build_count = old_build_count + 1`. Overwrite the single `- build_count → <old>` line with `- build_count → <new_build_count>` (insert if missing; ensure only one occurrence remains).
5. Write file atomically. Validation: exactly one `- build_count →` line exists with the new value.

---

## Step 10 — Repo Variable Refresh (MANDATORY)
1. Using cached `old_build_count` (NOT the newly written value), update exactly ONE status variable in `### Solution Variables` per mapping:
   - old_build_count==0 → set `build_status` to `SUCCEEDED` or `FAILED` based on `success`
   - old_build_count==1 → set `retry_build_status_attempt_1`
   - old_build_count>=2 → do not modify any status variable
2. Do NOT modify other variables (`restore_status`, `kb_*`, `fix_applied_*`, etc.).
3. Ensure exactly one variable change occurs; write atomically.

---

## Step 11 — Verification & Final JSON (MANDATORY)
1. Verify integrity:
   - Exactly one `- build_count →` line present and value == new_build_count.
   - Only one task line was flipped (if applicable).
   - Re-open checklist to determine the exact status variable from Step 10 using `old_build_count` (0→`build_status`, 1→`retry_build_status_attempt_1`). If `old_build_count <= 1`, confirm that variable exists exactly once and its value matches `success` (`SUCCEEDED` when true, otherwise `FAILED`). If `old_build_count >= 2`, confirm that none of those variables were touched during Step 10.
   - Counts of executed steps' checkpoints exist.
2. If verification fails, record verification error and set `status=FAIL` (but still emit final JSON).
3. Final JSON (write to stdout and `output/{{solution_name}}_task-build-solution-final.json`):
   - solution_path, solution_name, success, return_code, stdout_tail, stderr_tail, errors, warnings, old_build_count, new_build_count, verification_errors
4. Print `[task-build-solution] JSON emitted (size={{json_size}} bytes)` and `✅ Step 11 complete - final verification passed` (or failed with reason).
5. If any step earlier failed and was unrecoverable, overall `success=false` and include `errors` with codes per contract.

---

## Implementation Notes
- All file edits are atomic; modify in-memory then replace file. Preserve original spacing/other variable lines.
- Use exact arrow U+2192 for variable lines: `- build_count → <n>`.
- When searching for task lines to mark, match the substring `@task-build-solution` or `@task-build-solution-retry` exactly (case-sensitive).
- Do NOT attempt to "repair" inconsistent checklists by re-calculating build_count from markings; always use authoritative `build_count` value read in Step 2.
- Timeouts: build step default 30 min.
- Tail sizes: 12,000 characters for stdout/stderr.
- Ensure outputs are deterministic and idempotent aside from build_count increment.
