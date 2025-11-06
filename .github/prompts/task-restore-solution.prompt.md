@task-restore-solution solution_checklist={{solution_checklist}}
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
Input & Checklist Validation:
1. Expect input parameter: `solution_checklist` (path to `tasks/<repo_name>_<solution_name>_solution_checklist.md`).
2. Validate file exists; if missing → status=FAIL; emit JSON with success=false; abort subsequent restore attempts.
3. Read file content UTF-8; locate `### Solution Variables` section.
4. Parse the line beginning with `- solution_path →` (exact arrow U+2192) and extract the value (strip surrounding backticks if present).
5. If solution_path line missing or value blank → status=FAIL; record error code `variable_missing` and abort.
6. Validate extracted solution_path ends with `.sln` and file exists on disk; if not, status=FAIL (error code `sln_missing`).
7. Derive `solution_name` from solution_path (basename without extension) ignoring any differing name in checklist filename.
8. If DEBUG=1, print: `[debug][task-restore-solution] parsed solution_path='{{solution_path}}' solution_name='{{solution_name}}' from checklist='{{solution_checklist}}'`.
9. All subsequent steps MUST use the extracted solution_path; do NOT trust any external parameter or alternate source.

### Step 3 (MANDATORY)
Primary Restore Attempt: 
   - Command: `msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **CRITICAL - DO NOT REQUEST FILE ACCESS**: The strings `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, and `-noLogo` are MSBuild command-line FLAGS, NOT file paths or directories. Do NOT check for file access or directory permissions for these parameters.
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to the msbuild executable, NOT file system paths
   - If DEBUG=1, print to console: `[debug][task-restore-solution] executing: msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **Execute the command synchronously and wait for process completion** before proceeding.
   - **CRITICAL**: After process completes, capture the exit code (e.g., `$LASTEXITCODE` in PowerShell, `$?` in Bash).
   - Captures stdout/stderr without throwing exceptions.
   - If DEBUG=1 and dotnet fallback triggered, print to console: `[debug][task-restore-solution] executing: dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **Execute the dotnet msbuild fallback command synchronously and wait for process completion**, then **capture its exit code** before proceeding.

### Step 4 (MANDATORY)
NuGet Fallback (executed when step 3 MSBuild fails with ANY non-zero exit code): 
   - **Trigger Condition**: If the exit code from step 2 (msbuild or dotnet msbuild) is non-zero (any failure, not just command-not-found).
   - **Action**: Invoke `nuget restore "{{solution_path}}"` in the solution's parent directory.
   - If DEBUG=1, print: `[debug][task-restore-solution] NuGet fallback triggered (msbuild exitCode={exitCode})`
   - If DEBUG=1, print: `[debug][task-restore-solution] executing: nuget restore "{{solution_path}}"`
   - **Execute the nuget command synchronously and wait for process completion**, then **capture its exit code** before proceeding.
     * status: "SUCCESS" if exit code is 0, "FAIL" if non-zero
   - **Check NuGet exit code**: If NuGet succeeds (return code 0), re-runs the original MSBuild restore command once (with DEBUG command print if enabled), 
   - **wait for completion and capture exit code**, then aggregates all outputs (NuGet + retry) with labeled sections (=== NuGet Restore Output ===, etc.).
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
Result Tracking: Append to solution-results.csv
1. **Prepare CSV entry:**
   - timestamp: Current UTC timestamp in ISO 8601 format (e.g., "2025-10-26T12:00:00Z")
   - repo_name: {{repo_name}}
   - solution_name: {{solution_name}}
   - task_name: "@task-restore-solution"
   - status: "SUCCESS" if success=true, "FAIL" if success=false
   - symbol: "✓" if status="SUCCESS", "✗" if status="FAIL"

2. **Append to results/solution-results.csv using comma (`,`) as the separator:**
   - Format: `{{timestamp}},{{repo_name}},{{solution_name}},@task-restore-solution,{{status}},{{symbol}}`
   - Use PowerShell: `Add-Content -Path ".\results\solution-results.csv" -Value "{{csv_row}}"`
   - Ensure directory exists: `.\results\`
   - If file doesn't exist, create with headers: `timestamp,repo_name,solution_name,task_name,status,symbol`

### Step 10 (MANDATORY)
Repo Checklist Update: Mark current task complete
1. **Open checklist file:**
   - Path: `{{solution_checklist}}`

2. **Find and update ONLY the current task entry:**
   - Locate the unchecked restore task line containing the directive @task-restore-solution.
   - Change its leading unchecked marker "- [ ]" to "- [x]" without altering the remainder of the line.
   - Do NOT modify any other task entries
   - Do NOT update other solution checklists

3. **Write updated content back to file**

### Step 11 (MANDATORY)
Repo Variable Refresh: Update solution variables
1. **Open checklist file:**
   - Path: `{{solution_checklist}}`

2. **Find the Solution Variables section**

3. **Update the following variables based on task execution:**
   - `restore_status` → "SUCCEEDED" if success=true, "FAILED" if success=false

4. **Maintain all other existing variables unchanged:**
   - solution_path, solution_name, max_build_attempts, build_status, kb_search_status, kb_file_path, kb_article_status
   - fix_applied_attempt_1, retry_build_status_attempt_1
   - fix_applied_attempt_2, retry_build_status_attempt_2
   - fix_applied_attempt_3, retry_build_status_attempt_3

5. **Write updated variables back to checklist file**

### Step 12 (MANDATORY)
Verification (Post-Variable Refresh)
Perform a verification pass AFTER Step 11 has updated the checklist and variables. This step validates correctness and records any violations. It MUST run even if the restore failed. It does NOT re-run restore commands.

Scope of Verification:
1. Checklist File Presence: `tasks/{{repo_name}}_{{solution_name}}_solution_checklist.md` exists and is readable.
2. Task Marking:
   - If success=true: the `@task-restore-solution` line MUST be marked `- [x]`.
   - If success=false: the line MUST still be marked `- [x]` (task executed) but restore_status MUST reflect FAILED.
3. Directive Uniqueness: Exactly one line contains `@task-restore-solution`.
4. Value Consistency:
   - `restore_status` matches success flag (SUCCEEDED when success=true, FAILED when success=false).
   - `solution_path` ends with `.sln` and points to existing file.
5. JSON Output Integrity:
   - The structured JSON emitted in Step 7 MUST contain keys: success, stdout, stderr, errors, warnings.
   - If a file `output/{{repo_name}}_{{solution_name}}_task-restore-solution.json` was also written (optional enhancement), it MUST include those keys.
6. No Duplicate Variables: Each required variable appears exactly once.

Success Criteria for Step 12: Verification JSON written (either updated original or separate file) reflecting accurate error list and final status.

### Step 13 (MANDATORY)
DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), print:
   `[debug][task-restore-solution] END solution='{{solution_name}}' status={{success}} final_status={{status}} verification_errors={{verification_errors_count}}`

## Implementation Notes:
1. **Command Execution**: Use synchronous execution (NOT background jobs). In PowerShell: `msbuild ... ; $exitCode = $LASTEXITCODE`. In Bash: `msbuild ... ; exitCode=$?`. Do NOT proceed until the command completes.
2. **Exit Code Checking**: Immediately after each command completes, check the exit code to determine success/failure. Store this value for use in step 4 (Success Determination).
3. **Error Output on Failure**: When a command fails (non-zero exit code) AND DEBUG=1, print stderr to console: `[debug][task-restore-solution] command failed with exit code <code>, stderr: <stderr_content>`
4. Output Logging: In step 7, before writing JSON to stdout, emit: `[debug][task-restore-solution] writing JSON output to stdout (<size> bytes)`
5. Exit Placement: Emit immediately after step 8 (logging), before returning final output.
6. Idempotency: Two debug lines per task invocation (START + END) plus one per command executed (variable count based on fallback path) plus one for JSON output.
7. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, or `-noLogo`.
