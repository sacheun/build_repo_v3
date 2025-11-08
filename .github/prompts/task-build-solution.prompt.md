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
Entry Context:
 Print a single line to indicate start:
    `[task-build-solution] START solution='{{solution_name}}' path='{{solution_path}}'`

### Step 2 (MANDATORY)
Input Validation:
   - Ensure {{solution_path}} is provided and exists.
   - Must end with .sln; otherwise treat as contract failure.
   - Derive solution_name from file name (e.g., Foo.sln → Foo).

### Step 3 (MANDATORY)
Build Invocation:
   - Command: `msbuild "{{solution_path}}" --target:Clean,Build --property:Configuration=Release --maxcpucount --verbosity:quiet -noLogo`
   - The flag `--maxcpucount` is included for parallel build consistency (matches decision log message).
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to msbuild, NOT file paths.
   - Print the exact command line prior to execution for transparency.
   - Assumes packages already restored by @task-restore-solution.
   - Capture full stdout and stderr streams.

### Step 4 (MANDATORY)
Success Determination:
   - success = (return_code == 0)
   - Non-zero exit sets success=false but still parse output for diagnostics.


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
   - Write JSON to stdout for workflow consumption and print a single informational line:
     `[task-build-solution] JSON emitted (size={{json_size}} bytes)`

 Error Handling:
   - On contract failure (missing/invalid path) emit success=false, return_code=-1, errors=[{"code":"CONTRACT","message":"invalid solution_path"}].
   - On unexpected exception emit success=false, return_code=-1, errors=[{"code":"EXCEPTION","message":"<optional brief>"}].
   - Always emit warnings array (empty if none).

### Step 12 (MANDATORY)
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

### Step 13 (MANDATORY)
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

### Step 14 (MANDATORY)
Unconditional Exit Summary:
 Print exactly one line on completion (always):
    `[task-build-solution] EXIT success={{success}} errors={{error_count}} warnings={{warning_count}}`
 This line marks task completion and provides quick status visibility for pipeline execution.

### Step 16 (MANDATORY)
Count-Suffixed Artifact Capture & Variable Update:
   - BEFORE incrementing build_count, write secondary JSON: `output/{{repo_name}}_{{solution_name}}_task-build-solution_buildcount-{{old_build_count}}.json` containing identical payload to base JSON.
   - Update exactly one stderr artifact variable (per mapping above) to point to that count-suffixed file.
   - Do NOT modify more than one stderr artifact variable per run.
   - Arrow format MUST use U+2192.

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
6. **Error Output on Failure**: When the build command fails (non-zero exit code) print stderr to console: `[task-build-solution] command failed exit_code=<code>` followed by a truncated snippet.
7. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--target:Clean,Build`, `--property:Configuration=Release`, `--maxcpucount`, `--verbosity:quiet`, or `-noLogo`.
8. **Retry Directive Naming**: Use `@task-build-solution-retry` for retry attempt task lines to avoid uniqueness conflicts with the mandatory directive.
9. **Artifact Suffix Logic**: The suffix uses PRE-INCREMENT build_count value (old_build_count). After writing suffixed file and updating variable, increment build_count.
