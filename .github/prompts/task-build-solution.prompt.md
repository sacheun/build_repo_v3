 @task-build-solution solution_path={{solution_path}}
---
temperature: 0.0
---

Task name: task-build-solution

## Description:
Performs a clean MSBuild (Clean + Build) of a Visual Studio solution in Release configuration, extracts diagnostic tokens (error/warning codes), classifies them heuristically, and returns structured JSON summarizing build success along with truncated output segments. Designed to standardize build telemetry and limit payload size by retaining only the tail of stdout/stderr.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**
**Do not deviate from the command list provided. Always use the exact same commands each time you run this prompt.**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
DEBUG Entry Trace:
 If environment variable DEBUG=1 (string comparison), print:
   `[debug][task-build-solution] START solution='{{solution_name}}' path='{{solution_path}}'`

### Step 2 (MANDATORY)
Input Validation:
   - Ensure {{solution_path}} is provided and exists.
   - Must end with .sln; otherwise treat as contract failure.
   - Derive solution_name from file name (e.g., Foo.sln → Foo).

### Step 3 (MANDATORY)
Build Invocation:
   - Command: `msbuild "{{solution_path}}" --target:Clean,Build --property:Configuration=Release   --verbosity:quiet -noLogo`
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to the msbuild executable, NOT file system paths
   - If DEBUG=1, print to console: `[debug][task-build-solution] executing: msbuild "{{solution_path}}" --target:Clean,Build`--property:Configuration=Release --verbosity:quiet -noLogo`
   - Assumes packages already restored by @task-restore-solution.
   - Capture full stdout and stderr streams.

### Step 4 (MANDATORY)
Success Determination:
   - success = (return_code == 0)
   - Non-zero exit sets success=false but still parse output for diagnostics.

### Step 5 (MANDATORY)
Log to Decision Log:
   - Call @task-update-decision-log to log task execution:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="{{repo_name}}" 
     solution_name="{{solution_name}}" 
     task="task-build-solution" 
       message="msbuild \"{{solution_path}}\" --target:Clean,Build --property:Configuration=Release --maxcpucount --verbosity:quiet -noLogo" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - Status: "SUCCESS" if return_code is 0, "FAIL" if non-zero

### Step 6 (MANDATORY)
   Retain only last 12,000 characters of stdout and stderr individually (tail truncation) to manage JSON size.
   - Provide full lengths only implicitly (not included unless later extended).

### Step 7 (MANDATORY)
Token Extraction:
   - Scan combined output (stdout + stderr) with regex patterns for canonical codes (examples: CS\d{4}, NETSDK\d{4}, CA\d{4}, NU\d{4}, MSB\d{4}).
   - Produce distinct set of tokens (no duplicates).

### Step 8 (MANDATORY)
Classification Heuristic:
   - For each token, case-insensitive search for pattern: warning.*<token> within combined output.
   - If match found → categorize as warning; else → error.
   - Edge cases: token appearing outside typical format may misclassify.

### Step 9 (MANDATORY)
Diagnostic Object Construction:
   - errors: array of { code, message } (message empty placeholder for future enrichment).
   - warnings: array of { code, message } same structure.
   - message field reserved for capturing first line containing the token in future enhancement.

### Step 10 (MANDATORY)
Structured Output Emission:
   - Include: solution_path, solution_name, success, return_code, stdout_tail, stderr_tail, errors[], warnings[].
   - Maintain JSON Contract regardless of success state.
   - Writes to stdout for workflow consumption.
   - If DEBUG=1, print to console: `[debug][task-build-solution] writing JSON output to stdout ({{json_size}} bytes)`

 Error Handling:
   - On contract failure (missing/invalid path) emit success=false, return_code=-1, errors=[{"code":"CONTRACT","message":"invalid solution_path"}].
   - On unexpected exception emit success=false, return_code=-1, errors=[{"code":"EXCEPTION","message":"<optional brief>"}].
   - Always emit warnings array (empty if none).

### Step 7 (MANDATORY)
Result Tracking: Append to solution-results.csv
1. **Prepare CSV entry:**
   - timestamp: Current UTC timestamp in ISO 8601 format (e.g., "2025-10-26T12:00:00Z")
   - repo_name: {{repo_name}}
   - solution_name: {{solution_name}}
   - task_name: "@task-build-solution"
   - status: "SUCCESS" if success=true, "FAIL" if success=false
   - symbol: "✓" if status="SUCCESS", "✗" if status="FAIL"

2. **Append to results/solution-results.csv using comma (`,`) as the separator:**
   - Format: `{{timestamp}},{{repo_name}},{{solution_name}},@task-build-solution,{{status}},{{symbol}}`
   - Use PowerShell: `Add-Content -Path ".\results\solution-results.csv" -Value "{{csv_row}}"`
   - Ensure directory exists: `.\results\`
   - If file doesn't exist, create with headers: `timestamp,repo_name,solution_name,task_name,status,symbol`

### Step 8 (MANDATORY)
Repo Checklist Update: Mark EXACTLY ONE build-related task line based on the PRE-INCREMENT build_count and then increment build_count by exactly 1.

Canonical Increment Requirement:
   - The `build_count` variable MUST be treated as authoritative. Do NOT derive or recompute its value from previously marked task lines.
   - On every invocation: new_build_count = old_build_count + 1 (always +1, no skipping, no collapsing, no recomputation).
   - Persist the new value by overwriting ONLY the single `- build_count → <value>` variable line.

Add & Use Variable:
   - A solution variable `build_count` (integer) MUST exist in `### Solution Variables` (initialize to 0 if missing).
   - Each invocation increments `build_count` AFTER marking exactly one applicable task line.

Mapping Logic (choose ONE line to flip from `- [ ]` to `- [x]` using old_build_count BEFORE increment):
         - If old_build_count == 0: mark the mandatory build line containing @task-build-solution
         - If old_build_count == 1: mark the first retry build line containing @task-build-solution-retry
         - If old_build_count == 2: mark the second retry build line containing @task-build-solution-retry
         - If old_build_count == 3: mark the third retry build line containing @task-build-solution-retry
   - If old_build_count >= 4: do NOT mark any additional lines (attempt limit reached) but still increment build_count by 1 (showing additional invocations) and proceed with variable refresh & verification.

Rules:
   - Never convert more than one `[ ]` to `[x]` per run.
   - Do NOT unmark or modify already marked lines.
   - Do NOT add, duplicate, or delete task lines.
   - Preserve original text of the line except the leading `- [ ]` → `- [x]` change.
   - Do NOT attempt to “correct” build_count based on observed markings; always trust and increment the stored value.

Procedure:
   1. Load checklist file: `tasks/{{repo_name}}_{{solution_name}}_solution_checklist.md`.
   2. Read current `build_count` integer (default 0 if missing).
   3. Select target task line per mapping using old_build_count; if eligible and unchecked, mark it.
   4. Compute new_build_count = old_build_count + 1.
   5. Overwrite the `- build_count → <old>` line with `- build_count → <new_build_count>` (insert after `- max_build_attempts →` if absent).
   6. Write updated file content.

Verification Note (enforced in Step 12): A violation MUST be recorded if the difference between successive runs is not exactly +1 or if build_count appears more than once.

### Step 9 (MANDATORY)
Repo Variable Refresh (STRICT ISOLATED UPDATE): Use the PRE-INCREMENT build_count (cached BEFORE Step 8 wrote the new value) to update EXACTLY ONE status variable and NO OTHER VARIABLES. Then rely on the already-performed increment from Step 8 (DO NOT re-increment or recompute).

Procedure:
1. Open the same checklist file.
2. Locate `### Solution Variables` section.
3. Read cached old_build_count (value prior to Step 8). Never derive from task markings. Never read the newly incremented value for mapping.
4. Apply EXACT ONE mapping based on old_build_count:
   - If old_build_count == 0: ONLY set `build_status` to SUCCEEDED or FAILED. Do not modify any other variable lines.
   - If old_build_count == 1: ONLY set `retry_build_status_attempt_1` to SUCCEEDED or FAILED. Do not modify any other variable lines.
   - If old_build_count == 2: ONLY set `retry_build_status_attempt_2` to SUCCEEDED or FAILED. Do not modify any other variable lines.
   - If old_build_count == 3: ONLY set `retry_build_status_attempt_3` to SUCCEEDED or FAILED. Do not modify any other variable lines.
   - If old_build_count >= 4: Do NOT change ANY status variables.
5. Never alter previously written statuses from earlier attempts.
6. (Updated) `retry_build_status_attempt_3` MUST be modified ONLY when old_build_count == 3 per the mapping above; never at other counts.
7. Do NOT touch restore_status, kb_search_status, kb_file_path, kb_article_status, fix_applied_attempt_* or any other variables.
8. Ensure there remains EXACTLY ONE `- build_count → <value>` line (already updated in Step 8). Do not rewrite or duplicate it here.
9. Write the updated file with only the single permitted change.

Validation Focus for Step 9:
 - A run modifying more than the single allowed status variable MUST be considered a violation in Step 12 (`variable_mismatch`).
 - Failure to update the required single status variable when old_build_count ∈ {0,1,2,3} MUST also be a violation (`variable_missing`).

### Step 11 (MANDATORY)
DEBUG Exit Trace: 
If environment variable DEBUG=1, print:
    `[debug][task-build-solution] END solution='{{solution_name}}' status={{success}} errors={{error_count}} warnings={{warning_count}}`
    This line marks task completion and provides quick status visibility for debugging pipeline execution.

### Step 12 (MANDATORY)
Verification (Post-Variable Refresh)
Perform a verification pass AFTER Step 9 variable refresh and AFTER checklist marking (Step 8). This validates correctness and records violations. Runs regardless of build success.

Scope of Verification:
1. Checklist File Presence: `tasks/{{repo_name}}_{{solution_name}}_solution_checklist.md` exists.
2. Task Marking:
   - Regardless of success, the `@task-build-solution` line MUST be marked `- [x]` (task executed).
3. Directive Uniqueness: Exactly one occurrence of `@task-build-solution` in the checklist file.
4. Solution Variables Section Integrity:
   - Header `### Solution Variables` present.
   - Parenthetical `(Variables set by tasks for this specific solution)` present.
   - All required variable lines present in arrow format `variable_name → value` (U+2192):
   * solution_path
     * solution_name
     * max_build_attempts
   * build_count
     * restore_status
     * build_status
     * kb_search_status
     * kb_file_path
     * kb_article_status
     * fix_applied_attempt_1
     * retry_build_status_attempt_1
     * fix_applied_attempt_2
     * retry_build_status_attempt_2
     * fix_applied_attempt_3
     * retry_build_status_attempt_3
5. Arrow Formatting: Record violation if any required variable line missing arrow or using `->` instead of `→`.
6. Value Consistency:
   - `build_status` matches success flag (SUCCEEDED when success=true, FAILED when success=false).
   - `solution_path` ends with `.sln` and file exists.
7. JSON Output Integrity:
   - The structured JSON emitted in Step 10 MUST contain keys: solution_path, solution_name, success, return_code, stdout_tail, stderr_tail, errors, warnings.
   - If an optional file `output/{{repo_name}}_{{solution_name}}_task-build-solution.json` is written, ensure those keys exist.
8. No Duplicate Variables: Each required variable appears exactly once.
9. build_count Monotonicity: build_count MUST increase by exactly 1 compared to its value on the previous invocation; if tooling can detect previous value, record violation `variable_mismatch` when delta != 1.

Violation Recording:
- Append each violation as `{ "type": "<code>", "target": "<file|variable|line>", "detail": "<human readable>" }` to `verification_errors`.
- Recommended codes: file_missing, directive_duplicate, checklist_mark_incorrect, variable_missing, variable_mismatch, arrow_format_error, sln_missing, json_missing_key.
- If DEBUG=1 emit: `[debug][task-build-solution][verification] FAIL code=<code> target=<target> detail="<description>"` per violation.

Status Adjustment Logic:
- Start `status = SUCCESS` if success=true else `status = FAIL`.
- If success=true but any violations exist → set `status = FAIL` (build succeeded but checklist invalid).
- If success=false keep `status = FAIL`.

Output Update:
1. If a JSON file was created (optional enhancement) update/add:
   - `verification_errors` (sorted by type then target)
   - `status` (adjusted) without altering original `success`.
2. If JSON only emitted via stdout, ALSO create a separate verification file: `output/{{repo_name}}_{{solution_name}}_task-build-solution_verification.json` containing:
```json
{
  "repo_name": "{{repo_name}}",
  "solution_name": "{{solution_name}}",
  "success": <bool>,
  "status": "SUCCESS"|"FAIL",
  "verification_errors": [ ... ]
}
```
3. Ensure deterministic ordering (sort errors by type then target).

Success Criteria for Step 12: Verification JSON written reflecting accurate error list and final status.

## Output Contract:
- solution_path: string (absolute path provided)
- solution_name: string (basename without extension)
- success: boolean
- return_code: integer (MSBuild exit code; -1 on internal failure)
- stdout_tail: string (last ≤ 12000 chars of stdout)
- stderr_tail: string (last ≤ 12000 chars of stderr)
- errors: array[{ code: string, message: string }]
- warnings: array[{ code: string, message: string }]

## Implementation Notes:
1. Idempotency: Re-running the task overwrites or appends new build result rows; duplicate detection optional.
2. Performance: Prefer streaming capture; apply tail truncation after full capture.
3. Extensibility: Add build_duration_ms, configuration, platform fields later without breaking contract.
4. Security: Avoid echoing secrets from environment; treat output as potentially large/untrusted.
5. Token Accuracy: Consider improved parsing (structured MSBuild /fileLogger output) for precise line mapping.
6. **Error Output on Failure**: When the build command fails (non-zero exit code) AND DEBUG=1, print stderr to console: `[debug][task-build-solution] command failed with exit code <code>, stderr: <stderr_content>`
7. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--target:Clean,Build`, `--property:Configuration=Release`, `--maxcpucount`, `--verbosity:quiet`, or `-noLogo`.
