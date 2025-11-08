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
Entry Context:
Print a single line indicating start:
   `[task-restore-solution] START checklist='{{solution_checklist}}'`

### Step 2 (MANDATORY)
Input & Checklist Validation:
1. Expect input parameter: `solution_checklist` (path to `tasks/<repo_name>_<solution_name>_solution_checklist.md`).
2. Validate file exists; if missing → status=FAIL; emit JSON with success=false; abort subsequent restore attempts.
3. Read file content UTF-8; locate `### Solution Variables` section.
4. Parse the line beginning with `- solution_path →` (exact arrow U+2192) and extract the value (strip surrounding backticks if present).
5. If solution_path line missing or value blank → status=FAIL; record error code `variable_missing` and abort.
6. Validate extracted solution_path ends with `.sln` and file exists on disk; if not, status=FAIL (error code `sln_missing`).
7. Derive `solution_name` from solution_path (basename without extension) ignoring any differing name in checklist filename.
8. Print: `[task-restore-solution] parsed solution_path='{{solution_path}}' solution_name='{{solution_name}}'`
9. All subsequent steps MUST use the extracted solution_path; do NOT trust any external parameter or alternate source.

### Step 3 (MANDATORY)
Primary Restore Attempt: 
   - Command: `msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo`
   - **CRITICAL - DO NOT REQUEST FILE ACCESS**: The strings `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, and `-noLogo` are MSBuild command-line FLAGS, NOT file paths or directories.
   - **IMPORTANT**: All parameters starting with `--` or `-` are command arguments to the msbuild executable, NOT file system paths.
   - Print the exact command line prior to execution: `[task-restore-solution] executing msbuild restore`.
   - Execute synchronously and capture exit code.
   - If msbuild unavailable fall back to: `dotnet msbuild "{{solution_path}}" --restore --property:Configuration=Release --verbosity:quiet -noLogo` and print `[task-restore-solution] executing dotnet msbuild restore`.

### Step 4 (MANDATORY)
NuGet Fallback (executed when step 3 restore fails with non-zero exit code): 
   - Invoke: `nuget restore "{{solution_path}}"`
   - Print: `[task-restore-solution] nuget fallback invoked exit_code={{exitCode}}`
   - If NuGet succeeds, re-run the msbuild restore once and print `[task-restore-solution] msbuild retry after nuget`.
   - Aggregate outputs with labeled sections.

### Step 5 (MANDATORY)
Success Determination: **Sets success=true only if the final MSBuild exit code is 0** (after NuGet retry if applicable). The success flag is based on the actual exit code, not assumed.

Error/Warning Extraction: Parses combined stdout and stderr line-by-line for case-insensitive substring matches (" warning ", "warning ", " error ", "error "); collects matching lines into separate arrays, capping at 50 entries each to prevent overflow.

### Step 6 (MANDATORY)
Output Truncation: Trims stdout and stderr to last 8000 characters each before returning to avoid excessive JSON payload size.

### Step 7 (MANDATORY)
Structured Output: 
   - Return JSON with: success (boolean), stdout (last 8KB), stderr (last 8KB), errors (≤50), warnings (≤50).
   - Write to stdout and print one informational line: `[task-restore-solution] JSON emitted size={{json_size}} bytes`.

### Step 8 (MANDATORY)
Repo Checklist Update: Mark current task complete
1. **Open checklist file:**
   - Path: `{{solution_checklist}}`

2. **Find and update ONLY the current task entry:**
   - Locate the unchecked restore task line containing the directive @task-restore-solution.
   - Change its leading unchecked marker "- [ ]" to "- [x]" without altering the remainder of the line.
   - Do NOT modify any other task entries
   - Do NOT update other solution checklists

3. **Write updated content back to file**

### Step 9 (MANDATORY)
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

### End of steps

## Implementation Notes:
1. **Command Execution**: Use synchronous execution (NOT background jobs). In PowerShell: `msbuild ... ; $exitCode = $LASTEXITCODE`. In Bash: `msbuild ... ; exitCode=$?`. Do NOT proceed until the command completes.
2. **Exit Code Checking**: Immediately after each command completes, check the exit code to determine success/failure. Store this value for use in step 4 (Success Determination).
3. **Command Line Arguments**: MSBuild flags (starting with `--` or `-`) are command arguments, not file paths. Do not request directory access for parameters like `--restore`, `--property:Configuration=Release`, `--verbosity:quiet`, or `-noLogo`.
