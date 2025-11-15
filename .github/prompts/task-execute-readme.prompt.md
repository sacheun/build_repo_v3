---
temperature: 0.1
---

@task-execute-readme checklist_path={{checklist_path}}

# Task name: task-execute-readme

## Description
This task processes commands extracted by task-scan-readme, classifies them for safety, and executes safe ones. Reliability and sequence integrity are **critical**.

## Reliability Framework (MANDATORY)
**STRICT EXECUTION GUARANTEE:**  
- Each step MUST complete before the next begins.  
- After every step, the AI must **explicitly confirm completion internally** before proceeding.  
- If any data required by the next step is missing or invalid, the AI must **retry the step once** before failing gracefully.  
- Steps must not be skipped, combined, or reordered.

**FAIL-SAFE POLICY:**  
If any step fails validation → status=FAIL → jump directly to Structured Output with recorded failure.  
If inputs are empty → status=SKIPPED → continue to output with SKIPPED status.

---

## Step 1 – Checklist Load & Verification (MANDATORY)
1. Load checklist from `{{checklist_path}}`.
2. Extract required variables:
   - `repo_name`, `repo_directory`, `commands_extracted`.
3. Validate all are present and non-empty.
4. If missing or invalid → `status=FAIL` and proceed to Step 5 (output only).
5. Parse `commands_extracted`:
   - If NONE, SKIPPED, FAIL, or empty → `status=SKIPPED`.
   - Else split by comma into `raw_commands` array.
6. Confirm directory existence using tool call.
7. Record verification log (OK/FAIL) internally before proceeding.

---

## Step 2 – Safety Classification (MANDATORY)
*Run only if Step 1 != SKIPPED or FAIL.*  
For each command, classify as SAFE or UNSAFE using structural reasoning and the defined rules.  
If uncertain → UNSAFE.  
Record classification result per command before continuing.  
At end, verify: `safe_count + unsafe_count == total_commands_scanned`.

If mismatch → retry classification once, else mark `status=FAIL`.

---

## Step 3 – Execution of SAFE Commands (MANDATORY)
1. For each SAFE command:
   - Select appropriate shell.
   - Execute with `run_in_terminal` in `{{repo_directory}}`.
   - Timeout = 5 minutes.
   - Record stdout, stderr, and exit_code.
2. Do NOT stop on individual failures. Continue all.
3. After each command, append structured record to `executed_commands`.
4. Verify counts match SAFE commands before proceeding.

---

## Step 4 – Checklist Update (MANDATORY)
1. Open `tasks/{{repo_name}}_repo_checklist.md`.
2. Update only task lines for `@task-execute-readme` and the executed/skipped fields.
3. Set `- {{executed_commands}} →` to the pipe-delimited list of executed safe commands (or `None` if none executed).
4. Ensure only **one** `→` per line.
5. Confirm `[x]` set correctly (SUCCESS or SKIPPED only).
6. Validate summary counts match Step 3 output before saving.
7. If validation fails, retry update once.

---

## Step 5 – Structured Output (MANDATORY)
Write structured JSON at `./output/{{repo_name}}_task4_execute-readme.json` with:
- repo_directory
- repo_name
- total_commands_scanned
- safe_commands_count
- unsafe_commands_count
- executed_commands
- skipped_commands
- status
- timestamp (ISO 8601 UTC)

Validate JSON field presence before writing file.

---

## Step 6 – Post-Run Verification And Retry Guard (MANDATORY)
Re-open and re-parse `tasks/{{repo_name}}_repo_checklist.md` from disk (no cached content). Perform ALL checks below:

1. Task line correctness:
   - Locate the line containing `@task-execute-readme`.
   - If `status=SUCCESS` or `status=SKIPPED` it MUST be `[x]`; if `status=FAIL` it MUST remain `[ ]`.
2. Required variable lines (exactly once each) under `## Repo Variables Available`:
   - `- {{executed_commands}} → <concise pipe-delimited list OR empty>`
   - `- {{skipped_commands}} → <concise pipe-delimited list OR empty>`
   (Single arrow `→`, one space before and after, no trailing spaces, no duplication.)
3. JSON file integrity:
   - Open `output/{{repo_name}}_task4_execute-readme.json`; verify presence of `executed_commands`, `skipped_commands`, `safe_commands_count`, `unsafe_commands_count`, `total_commands_scanned`.
4. Semantic alignment by status:
   - SUCCESS: `safe_commands_count == len(executed_commands)` AND all executed were classified SAFE.
   - SKIPPED: `safe_commands_count == 0` AND `executed_commands` empty; `unsafe_commands_count` may be >=0.
   - FAIL: JSON exists; counts may reflect partial progress but MUST be internally consistent: `safe_commands_count + unsafe_commands_count == total_commands_scanned`.
5. Consistency between checklist variables and JSON arrays:
   - Each command in the checklist pipe-delimited list appears in corresponding JSON array (order may differ).
   - Empty checklist variable lines correspond to empty arrays.
6. Safety: Ensure no destructive commands (e.g., `rm -rf`, `del /s`) appear in `executed_commands`; if found after execution, log warning but do not retroactively remove—mark `status=FAIL`.
7. Failure handling:
   - If ANY check fails (missing lines, mismatched counts, wrong bracket state, path missing, destructive command detected) log `WARNING: checklist verification failed - restarting from Step 1` then re-run Steps 1–5 completely (single automatic retry) and attempt Step 6 again.
8. Finalization:
   - On success log `VERIFICATION_PASSED step_completed=6`.
   - If retry still fails set `status=FAIL` (if not already) and log `VERIFICATION_ABORTED`.
9. Do NOT mutate previously written JSON beyond adding an internal verification flag if framework supports it.

---

## Final Reliability Assertions
- **Sequential Enforcement:** Each step must verify completion and validity before the next begins.
- **Redundancy:** If a step’s validation fails, retry once.
- **Completion Proof:** Final JSON must include `"status": "<SUCCESS|SKIPPED|FAIL>"` and exact count integrity check.

---
