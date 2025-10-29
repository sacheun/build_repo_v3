 @task-build-solution solution_path={{solution_path}}
---
temperature: 0.1
---

Task name: task-build-solution

## Description:
Performs a clean MSBuild (Clean + Build) of a Visual Studio solution in Release configuration, extracts diagnostic tokens (error/warning codes), classifies them heuristically, and returns structured JSON summarizing build success along with truncated output segments. Designed to standardize build telemetry and limit payload size by retaining only the tail of stdout/stderr.

** CRITICAL INSTRUCTION FOR AI AGENTS **: When executing MSBuild commands in this task, parameters that start with `--` or `-` (such as `--target:Clean,Build`, `--property:Configuration=Release`, `--maxcpucount`, `--verbosity:quiet`, `-noLogo`) are COMMAND-LINE FLAGS for the msbuild.exe executable. These are NOT file paths or directories. DO NOT request file system access or check directory permissions for these parameters. Only the solution_path parameter refers to an actual file.

** Important **: Do not deviate from the command list provided. Always use the exact same commands each time you run this prompt.

** THIS TASK IS SCRIPTABLE **

## Behavior (Follow this Step by Step)
0. DEBUG Entry Trace: If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   "[debug][task-build-solution] START solution='{{solution_name}}' path='{{solution_path}}'"
   This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

1. Input Validation:
   - Ensure {{solution_path}} is provided and exists.
   - Must end with .sln; otherwise treat as contract failure.
   - Derive solution_name from file name (e.g., Foo.sln → Foo).

2. Build Invocation:
   - Command: `msbuild "{{solution_path}}" --target:Clean,Build --property:Configuration=Release --maxcpucount --verbosity:quiet -noLogo`
   - **CRITICAL - DO NOT REQUEST FILE ACCESS**: The strings `--target:Clean,Build`, `--property:Configuration=Release`, `--maxcpucount`, `--verbosity:quiet`, and `-noLogo` (and any other arguments that begin with `--` or `-`) are **command-line flags** for `msbuild.exe`. They are **not** directories that require access approval. Copilot (or any orchestrator) must never trigger a directory-access prompt for these values. If the runtime surfaces such a prompt, treat it as a false positive and continue without granting access; ignore or dismiss the prompt and run the command unchanged. Only `{{solution_path}}` represents a real filesystem path that needs validation.
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to the msbuild executable, NOT file system paths
   - If DEBUG=1, print to console: `[debug][task-build-solution] executing: msbuild "{{solution_path}}" --target:Clean,Build --property:Configuration=Release --maxcpucount --verbosity:quiet -noLogo`
   - Multi-processor build enabled via `--maxcpucount`.
   - Assumes packages already restored by @task-restore-solution.
   - Capture full stdout and stderr streams.

3. Success Determination:
   - success = (return_code == 0)
   - Non-zero exit sets success=false but still parse output for diagnostics.

3a. Log to Decision Log:
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

4. Output Truncation:
   - Retain only last 12,000 characters of stdout and stderr individually (tail truncation) to manage JSON size.
   - Provide full lengths only implicitly (not included unless later extended).

5. Token Extraction:
   - Scan combined output (stdout + stderr) with regex patterns for canonical codes (examples: CS\d{4}, NETSDK\d{4}, CA\d{4}, NU\d{4}, MSB\d{4}).
   - Produce distinct set of tokens (no duplicates).

6. Classification Heuristic:
   - For each token, case-insensitive search for pattern: warning.*<token> within combined output.
   - If match found → categorize as warning; else → error.
   - Edge cases: token appearing outside typical format may misclassify.

7. Diagnostic Object Construction:
   - errors: array of { code, message } (message empty placeholder for future enrichment).
   - warnings: array of { code, message } same structure.
   - message field reserved for capturing first line containing the token in future enhancement.

8. Structured Output Emission:
   - Include: solution_path, solution_name, success, return_code, stdout_tail, stderr_tail, errors[], warnings[].
   - Maintain JSON Contract regardless of success state.
   - Writes to stdout for workflow consumption.
   - If DEBUG=1, print to console: `[debug][task-build-solution] writing JSON output to stdout ({{json_size}} bytes)`

9. Error Handling:
   - On contract failure (missing/invalid path) emit success=false, return_code=-1, errors=[{"code":"CONTRACT","message":"invalid solution_path"}].
   - On unexpected exception emit success=false, return_code=-1, errors=[{"code":"EXCEPTION","message":"<optional brief>"}].
   - Always emit warnings array (empty if none).

10. DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), emit a final line to stdout (or terminal) after all processing completes:
    "[debug][task-build-solution] END solution='{{solution_name}}' status={{success}} errors={{error_count}} warnings={{warning_count}}"
    This line marks task completion and provides quick status visibility for debugging pipeline execution.

Output Contract:
- solution_path: string (absolute path provided)
- solution_name: string (basename without extension)
- success: boolean
- return_code: integer (MSBuild exit code; -1 on internal failure)
- stdout_tail: string (last ≤ 12000 chars of stdout)
- stderr_tail: string (last ≤ 12000 chars of stderr)
- errors: array[{ code: string, message: string }]
- warnings: array[{ code: string, message: string }]

Implementation Notes (conceptual):
1. Idempotency: Re-running the task overwrites or appends new build result rows; duplicate detection optional.
2. Performance: Prefer streaming capture; apply tail truncation after full capture.
3. Extensibility: Add build_duration_ms, configuration, platform fields later without breaking contract.
4. Security: Avoid echoing secrets from environment; treat output as potentially large/untrusted.
5. Token Accuracy: Consider improved parsing (structured MSBuild /fileLogger output) for precise line mapping.
6. Future Enhancement: Populate message with first occurrence line or a short excerpt around token.
7. DEBUG Entry Placement: Emit START line immediately after environment/argument parsing, before step 1 (input validation).
8. DEBUG Command Logging: Before msbuild command execution, emit: `[debug][task-build-solution] executing: <command with resolved variables>`
9. **Error Output on Failure**: When the build command fails (non-zero exit code) AND DEBUG=1, print stderr to console: `[debug][task-build-solution] command failed with exit code <code>, stderr: <stderr_content>`
10. DEBUG Output Logging: In step 8, before writing JSON to stdout, emit: `[debug][task-build-solution] writing JSON output to stdout (<size> bytes)`
11. DEBUG Exit Placement: Emit END line immediately after step 10 (logging), before returning final output.
12. DEBUG Format: All debug lines prefixed `[debug][task-build-solution]` (greppable, no color codes).
13. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--target:Clean,Build`, `--property:Configuration=Release`, `--maxcpucount`, `--verbosity:quiet`, or `-noLogo`.

Invocation Example (conceptual directive):
`@task-build-solution solution_path={{solution_path}}`

Relation to Pipelines:
- Insert into `solution_tasks_list.md` below restore task to perform build after successful restore.
- Downstream tasks (e.g., test) can inspect success, errors, warnings for gating decisions.

Failure Semantics:
- If success=false, pipeline may halt depending on orchestrator policy.
- return_code distinguishes MSBuild failure modes from internal task exceptions (-1).

No embedded executable code; a runner must implement the steps above.