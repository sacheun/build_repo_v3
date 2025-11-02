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

### Step 11 (MANDATORY)
DEBUG Exit Trace: 
If environment variable DEBUG=1, print:
    `[debug][task-build-solution] END solution='{{solution_name}}' status={{success}} errors={{error_count}} warnings={{warning_count}}`
    This line marks task completion and provides quick status visibility for debugging pipeline execution.

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
