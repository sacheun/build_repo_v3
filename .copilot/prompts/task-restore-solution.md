@task-restore-solution solution_path={{solution_path}}

Task name: task-restore-solution

Description:
This tasks performs NuGet package restore for a Visual Studio solution file using MSBuild with automatic fallback strategies. It attempts msbuild /restore first, optionally falls back to dotnet msbuild if MSBuild is unavailable, and executes nuget restore as a last resort for legacy solutions requiring classic NuGet CLI. Returns structured JSON indicating success status, captured output, and parsed error/warning messages.

Behavior:
0. DEBUG Entry Trace: If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   "[debug][task-restore-solution] START solution='{{solution_name}}' path='{{solution_path}}'"
   This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

1. Input Validation: Reads JSON from stdin expecting solution_path (absolute path to .sln file); raises ContractError if missing or nonexistent.

2. Primary Restore Attempt: 
   - Command: `msbuild {{solution_path}} /restore /p:Configuration=Release /nologo`
   - If DEBUG=1, print to console: `[debug][task-restore-solution] executing: msbuild {{solution_path}} /restore /p:Configuration=Release /nologo`
   - **Execute the command synchronously and wait for process completion** before proceeding.
   - **CRITICAL**: After process completes, capture the exit code (e.g., `$LASTEXITCODE` in PowerShell, `$?` in Bash).
   - Captures stdout/stderr without throwing exceptions.
   - **Special Case - MSBuild Not Found**: If command fails with error code 9009 (Windows "command not found") or stderr contains "not recognized", switches to `dotnet msbuild {{solution_path}} /restore /p:Configuration=Release /nologo`
   - If DEBUG=1 and dotnet fallback triggered, print to console: `[debug][task-restore-solution] executing: dotnet msbuild {{solution_path}} /restore /p:Configuration=Release /nologo`
   - **Execute the dotnet msbuild fallback command synchronously and wait for process completion**, then **capture its exit code** before proceeding.
   - **IMPORTANT**: Proceed to step 3 (NuGet fallback) if the final MSBuild exit code (msbuild or dotnet msbuild) is non-zero, regardless of the specific error code.

3. NuGet Fallback (executed when step 2 MSBuild fails with ANY non-zero exit code): 
   - **Trigger Condition**: If the exit code from step 2 (msbuild or dotnet msbuild) is non-zero (any failure, not just command-not-found).
   - **Action**: Invoke `nuget restore {{solution_path}}` in the solution's parent directory.
   - If DEBUG=1, print to console: `[debug][task-restore-solution] NuGet fallback triggered (msbuild exitCode={exitCode})`
   - If DEBUG=1, print to console: `[debug][task-restore-solution] executing: nuget restore {{solution_path}}`
   - **Execute the nuget command synchronously and wait for process completion**, then **capture its exit code** before proceeding.
   - **Check NuGet exit code**: If NuGet succeeds (return code 0), re-runs the original MSBuild restore command once (with DEBUG command print if enabled), **wait for completion and capture exit code**, then aggregates all outputs (NuGet + retry) with labeled sections (=== NuGet Restore Output ===, etc.).
   - If NuGet fails (non-zero exit code), appends its output but skips MSBuild retry.
   - If DEBUG=1 and NuGet failed, print to console: `[debug][task-restore-solution] NuGet restore failed with exitCode={nugetExitCode}, skipping MSBuild retry`

4. Success Determination: **Sets success=true only if the final MSBuild exit code is 0** (after NuGet retry if applicable). The success flag is based on the actual exit code, not assumed.

5. Error/Warning Extraction: Parses combined stdout and stderr line-by-line for case-insensitive substring matches (" warning ", "warning ", " error ", "error "); collects matching lines into separate arrays, capping at 50 entries each to prevent overflow.

6. Output Truncation: Trims stdout and stderr to last 8000 characters each before returning to avoid excessive JSON payload size.

7. Structured Output: 
   - Returns JSON object with fields: success (boolean), stdout (string, last 8KB), stderr (string, last 8KB), errors (array of strings, max 50), warnings (array of strings, max 50).
   - Writes to stdout for workflow consumption.
   - If DEBUG=1, print to console: `[debug][task-restore-solution] writing JSON output to stdout ({{json_size}} bytes)`

8. Logging: Emits debug messages showing input payload, fallback decisions, NuGet invocation details, and final result summary (success flag, counts of errors/warnings).

9. DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), emit a final line to stdout (or terminal) after all processing completes:
   "[debug][task-restore-solution] END solution='{{solution_name}}' status={{success}}"
   This line marks task completion and provides quick status visibility for debugging pipeline execution.

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the restore task was called and for which solution, plus completion status and exact commands executed.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-restore-solution] allowing simple grep filtering.
- Entry Message: "[debug][task-restore-solution] START solution='<name>' path='<path>'" emitted before step 1.
- Command Messages: "[debug][task-restore-solution] executing: <full command>" emitted immediately before each external command invocation (msbuild, dotnet msbuild, nuget restore).
- Output Message: "[debug][task-restore-solution] writing JSON output to stdout (<N> bytes)" emitted in step 7 before writing JSON.
- Exit Message: "[debug][task-restore-solution] END solution='<name>' status=<true|false>" emitted after step 8.
- Non-Interference: Does not modify success criteria or parsed diagnostics arrays; excluded from error/warning extraction logic.

Implementation Notes (conceptual additions for DEBUG handling):
1. Detection: In PowerShell: `if($env:DEBUG -eq '1') { Write-Host "[debug][task-restore-solution] START solution='$solutionName' path='$solutionPath'" }`
2. In Bash: `if [ "$DEBUG" = "1" ]; then echo "[debug][task-restore-solution] START solution='$solutionName' path='$solutionPath'"; fi`
3. Entry Placement: Emit immediately after environment/argument parsing, before step 1 (input validation).
4. Command Logging: Before each external command execution (msbuild, dotnet msbuild, nuget), emit: `[debug][task-restore-solution] executing: <command with resolved variables>`
5. **Command Execution**: Use synchronous execution (NOT background jobs). In PowerShell: `msbuild ... ; $exitCode = $LASTEXITCODE`. In Bash: `msbuild ... ; exitCode=$?`. Do NOT proceed until the command completes.
6. **Exit Code Checking**: Immediately after each command completes, check the exit code to determine success/failure. Store this value for use in step 4 (Success Determination).
7. **Error Output on Failure**: When a command fails (non-zero exit code) AND DEBUG=1, print stderr to console: `[debug][task-restore-solution] command failed with exit code <code>, stderr: <stderr_content>`
8. Output Logging: In step 7, before writing JSON to stdout, emit: `[debug][task-restore-solution] writing JSON output to stdout (<size> bytes)`
9. Exit Placement: Emit immediately after step 8 (logging), before returning final output.
10. Idempotency: Two debug lines per task invocation (START + END) plus one per command executed (variable count based on fallback path) plus one for JSON output.
11. Security: Avoid printing secrets or expanded environment beyond solution identity and status flag.
