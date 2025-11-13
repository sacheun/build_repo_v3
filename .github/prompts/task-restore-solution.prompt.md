@task-restore-solution solution_checklist={{solution_checklist}}
---
temperature: 0.0
---

Task name: task-restore-solution

## Description:
Performs NuGet package restore for a Visual Studio solution file using MSBuild with fallback to `dotnet msbuild` or `nuget restore`. Ensures structured, validated execution with deterministic step completion and output.

---

## RELIABILITY FRAMEWORK (MANDATORY)

**Execution Mode:**  
- All steps are **strictly sequential**.  
- Each step must **explicitly complete and verify its success condition** before the next begins.  
- If a step fails validation or produces incomplete data → retry once; if still invalid → `status=FAIL` → jump to Structured Output.

**Integrity Requirements:**  
- Never skip or summarize steps.  
- Do not combine steps or assume prior results.  
- Each major phase (validation, restore, retry, output, checklist update) must have **an explicit internal checkpoint** confirming that its completion criteria are met.

---

## Step 1 — Input & Checklist Validation (MANDATORY)

1. Expect input: `solution_checklist` → path to `tasks/<repo_name>_<solution_name>_solution_checklist.md`.
2. Confirm file exists; if not → `status=FAIL` → emit JSON `{success:false, error:"checklist_missing"}` and **terminate**.
3. Read UTF-8 content and locate section `### Solution Variables`.
4. Extract `solution_path` value (text after `- solution_path →`).
5. If missing or blank → `status=FAIL` (`error_code="variable_missing"`) → terminate.
6. Validate file exists and ends with `.sln`; if not → `status=FAIL` (`error_code="sln_missing"`).
7. Derive `solution_name` from the basename.
9. Proceed **only if Step 1 checkpoint is printed**.

---

## Step 2 — Primary Restore Attempt (MANDATORY)

1. Command:
   ```
   msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo
   ```
2. Run synchronously and capture stdout, stderr, and exit code.
3. If msbuild not found → fallback:
   ```
   dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo
   ```
4. Record exit_code, restore_stdout, restore_stderr.
5. If command or fallback both fail to run → `status=FAIL` (`error_code="restore_failed_init"`).
6. Proceed only if **exit_code** or **stderr/stdout** are captured successfully.

---

## Step 3 — NuGet Fallback (MANDATORY IF Step 2 FAILED)

Run this step **only if Step 2’s final exit_code != 0**.

1. Execute:  
   ```
   nuget restore "{{solution_path}}"
   ```
2. If success → re-run MSBuild restore once:
   ```
   msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo
   ```
3. Aggregate outputs with section headers (MSBUILD_PRIMARY, NUGET_FALLBACK, MSBUILD_RETRY).
4. Ensure captured outputs are merged before proceeding.

---

## Step 4 — Success Determination & Error Parsing (MANDATORY)

1. `success = (final_exit_code == 0)`.
2. Combine stdout+stderr → search for lines containing `warning` or `error` (case-insensitive).
3. Extract up to 50 warning lines and 50 error lines.

---

## Step 5 — Output Truncation (MANDATORY)

1. Truncate both stdout and stderr to last 8000 characters.
2. Confirm truncation succeeded (`len<=8000` each).

---

## Step 6 — Structured Output JSON (MANDATORY)

1. Compose JSON:
   ```json
   {
     "success": <bool>,
     "stdout": "<trimmed>",
     "stderr": "<trimmed>",
     "warnings": [...],
     "errors": [...],
     "exit_code": <int>
   }
   ```
2. Verify JSON field presence and validity.
3. Proceed only after JSON validated.

---

## Step 7 — Checklist Update (MANDATORY)

1. Open `{{solution_checklist}}`.
2. Mark `@task-restore-solution` as complete (`- [x]`).
3. In `### Solution Variables`, update:
   - `restore_status → "SUCCEEDED"` if success=true else `"FAILED"`.
4. Preserve all other lines unchanged.
5. Write atomically (replace file only after full validation).

---

## Step 8 — Final Integrity Verification (MANDATORY)

1. Validate that all checkpoints from Steps 1–7 were printed.
2. Validate that the final JSON exists and contains `success` and `exit_code`.
3. If any checkpoint missing → re-run last incomplete step once.

---

## Implementation Notes

- Use **synchronous** command execution; never async/background.  
- Immediately check `$LASTEXITCODE` (PowerShell) or `$?` (Bash).  
- Never request file access for MSBuild flags.  
- Always confirm step completion before proceeding.  
- If output or validation missing → retry step once, then fail cleanly.

---
