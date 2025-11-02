@task-restore-solution solution_path={{solution_path}}
---
temperature: 0.0
---

Task name: task-restore-solution

## Description:
This tasks performs NuGet package restore for a Visual Studio solution file using MSBuild with automatic fallback strategies. It attempts `msbuild --restore` first, optionally falls back to `dotnet msbuild --restore` if MSBuild is unavailable, and executes `nuget restore` as a last resort for legacy solutions requiring classic NuGet CLI. Returns structured JSON indicating success status, captured output, and parsed error/warning messages.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**
**Do not deviate from the command list provided. Always use the exact same commands each time you run this prompt.**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
DEBUG Entry Trace:
If environment variable DEBUG=1, print
   `[debug][task-restore-solution] START solution='{{solution_name}}' path='{{solution_path}}'`

### Step 2 (MANDATORY)
Input Validation:
Reads JSON from stdin expecting solution_path (absolute path to .sln file); raises ContractError if missing or nonexistent.

### Step 3 (MANDATORY)
Primary Restore Attempt: 
   - Command: `msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **CRITICAL - DO NOT REQUEST FILE ACCESS**: The strings `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, and `-noLogo` are MSBuild command-line FLAGS, NOT file paths or directories. Do NOT check for file access or directory permissions for these parameters.
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to the msbuild executable, NOT file system paths
   - If DEBUG=1, print to console: `[debug][task-restore-solution] executing: msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **Execute the command synchronously and wait for process completion** before proceeding.
   - **CRITICAL**: After process completes, capture the exit code (e.g., `$LASTEXITCODE` in PowerShell, `$?` in Bash).
   - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},{{solution_name}},task-restore-solution,msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo,{{status}}"
     * timestamp: ISO 8601 format (e.g., "2025-10-22T14:30:45Z")
     * status: "SUCCESS" if exit code is 0, "FAIL" if non-zero
   - Captures stdout/stderr without throwing exceptions.
   - **Special Case - MSBuild Not Found**: If command fails with error code 9009 (Windows "command not found") or stderr contains "not recognized", switches to `dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - If DEBUG=1 and dotnet fallback triggered, print to console: `[debug][task-restore-solution] executing: dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **Execute the dotnet msbuild fallback command synchronously and wait for process completion**, then **capture its exit code** before proceeding.
   - **Log to Decision Log**: If dotnet msbuild was executed,  Call @task-update-decision-log to log task execution:, append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},{{solution_name}},task-restore-solution,dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo,{{status}}"
   - **IMPORTANT**: Proceed to step 4 (NuGet fallback) if the final MSBuild exit code (msbuild or dotnet msbuild) is non-zero, regardless of the specific error code.

### Step 4 (MANDATORY)
NuGet Fallback (executed when step 3 MSBuild fails with ANY non-zero exit code): 
   - **Trigger Condition**: If the exit code from step 2 (msbuild or dotnet msbuild) is non-zero (any failure, not just command-not-found).
   - **Action**: Invoke `nuget restore "{{solution_path}}"` in the solution's parent directory.
   - If DEBUG=1, print: `[debug][task-restore-solution] NuGet fallback triggered (msbuild exitCode={exitCode})`
   - If DEBUG=1, print: `[debug][task-restore-solution] executing: nuget restore "{{solution_path}}"`
   - **Execute the nuget command synchronously and wait for process completion**, then **capture its exit code** before proceeding.
   - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},{{solution_name}},task-restore-solution,nuget restore "{{solution_path}}",{{status}}"
     * timestamp: ISO 8601 format
     * status: "SUCCESS" if exit code is 0, "FAIL" if non-zero
   - **Check NuGet exit code**: If NuGet succeeds (return code 0), re-runs the original MSBuild restore command once (with DEBUG command print if enabled), 
   - **wait for completion and capture exit code**, then aggregates all outputs (NuGet + retry) with labeled sections (=== NuGet Restore Output ===, etc.).
   - **Log MSBuild Retry to Decision Log**: If MSBuild retry was executed after successful NuGet, append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},{{solution_name}},task-restore-solution,msbuild "{{solution_path}}" --restore (retry after nuget),{{status}}"
   - If NuGet fails (non-zero exit code), appends its output but skips MSBuild retry.
   - If DEBUG=1 and NuGet failed, print to console: `[debug][task-restore-solution] NuGet restore failed with exitCode={nugetExitCode}, skipping MSBuild retry`

### Step 5 (MANDATORY)
Success Determination: **Sets success=true only if the final MSBuild exit code is 0** (after NuGet retry if applicable). The success flag is based on the actual exit code, not assumed.

Error/Warning Extraction: Parses combined stdout and stderr line-by-line for case-insensitive substring matches (" warning ", "warning ", " error ", "error "); collects matching lines into separate arrays, capping at 50 entries each to prevent overflow.

### Step 6 (MANDATORY)
Output Truncation: Trims stdout and stderr to last 8000 characters each before returning to avoid excessive JSON payload size.

### Step 7 (MANDATORY)
Structured Output: 
   - Returns JSON object with fields: success (boolean), stdout (string, last 8KB), stderr (string, last 8KB), errors (array of strings, max 50), warnings (array of strings, max 50).
   - Writes to stdout for workflow consumption.
   - If DEBUG=1, print to console: `[debug][task-restore-solution] writing JSON output to stdout ({{json_size}} bytes)`

### Step 8 (MANDATORY)
Log to Decision Log:
   - Call @task-update-decision-log to log task completion:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="{{repo_name}}" 
     solution_name="{{solution_name}}" 
     task="task-restore-solution" 
     message="{{message}}" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - Message format:
     * If success=true: "NuGet packages restored successfully"
     * If success=false: "NuGet restore failed - {{error_count}} errors, {{warning_count}} warnings"
   - Status: "SUCCESS" if success=true, "FAIL" if success=false

### Step 9 (MANDATORY)
DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), print:
   `[debug][task-restore-solution] END solution='{{solution_name}}' status={{success}}`

## Implementation Notes:
1. **Command Execution**: Use synchronous execution (NOT background jobs). In PowerShell: `msbuild ... ; $exitCode = $LASTEXITCODE`. In Bash: `msbuild ... ; exitCode=$?`. Do NOT proceed until the command completes.
2. **Exit Code Checking**: Immediately after each command completes, check the exit code to determine success/failure. Store this value for use in step 4 (Success Determination).
3. **Error Output on Failure**: When a command fails (non-zero exit code) AND DEBUG=1, print stderr to console: `[debug][task-restore-solution] command failed with exit code <code>, stderr: <stderr_content>`
4. Output Logging: In step 7, before writing JSON to stdout, emit: `[debug][task-restore-solution] writing JSON output to stdout (<size> bytes)`
5. Exit Placement: Emit immediately after step 8 (logging), before returning final output.
6. Idempotency: Two debug lines per task invocation (START + END) plus one per command executed (variable count based on fallback path) plus one for JSON output.
7. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, or `-noLogo`.
