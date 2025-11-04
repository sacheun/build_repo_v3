---
temperature: 0.1
---

@task-execute-readme checklist_path={{checklist_path}}

# Task name: task-execute-readme

## Process Overview
1. Debug Entry Trace
2. Checklist Load & Variable Extraction
3. Prerequisites & Checklist Verification
4. Safety Classification
5. SAFE Command Execution
6. Decision Log per Command
7. Skipped Command Recording
8. Execution Summary
9. Structured Output Assembly
10. Result Tracking
11. Repo Checklist Update
12. Repo Variable Refresh
13. Debug Exit Trace

## Prerequisites
- Repo checklist (at checklist_path) contains variable lines for `{{repo_name}}`, `{{repo_directory}}`, `{{commands_extracted}}`, `{{executed_commands}}`, `{{skipped_commands}}`
- `{{commands_extracted}}` value produced previously by `@task-scan-readme` (may be NONE / SKIPPED / FAIL)
- Writable `output/` and `results/` directories
- DEBUG environment variable optional

## Description
This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and **cannot** be scripted.

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**
This task MUST be performed using **direct tool calls** and **structural reasoning**:

1. Use `read_file` to load the repo checklist (checklist_path) and extract variable values.
2. Use structural reasoning to classify each command listed in `{{commands_extracted}}` as SAFE or UNSAFE.
3. Use `run_in_terminal` tool to execute SAFE commands individually in repo_directory.
4. Use `create_file` tool to save execution results to JSON output.
5. Use `replace_string_in_file` tool to update progress/results files.

**NEVER create a Python script for this task.**
**NEVER batch-execute commands in a single script.**
**EACH command must be evaluated individually for safety.**
The AI agent must use reasoning to determine command safety and execute safe commands one at a time.

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
**DEBUG Entry Trace:**  
If DEBUG=1, print:  
`[debug][task-execute-readme] START checklist_path='{{checklist_path}}'`

### Step 2 (MANDATORY)
**Checklist Load & Variable Extraction:**
- Open the file at `{{checklist_path}}`.
- Extract values (after `→`) for:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
  - `- {{commands_extracted}}` (comma-separated commands or status token)
  - Confirm presence of `- {{executed_commands}}` and `- {{skipped_commands}}` lines (values may be placeholders).
- If any required line missing or value empty where required, set `status=FAIL` and proceed to structured output.
- Interpret `{{commands_extracted}}` value:
  - If value in {NONE, SKIPPED, FAIL, ""}: set `status=SKIPPED` and no execution will occur.
  - Else split by comma into raw_commands list; trim whitespace per item.
- If DEBUG=1, print: `[debug][task-execute-readme] extracted repo_name='{{repo_name}}' repo_directory='{{repo_directory}}' commands_extracted_count={{raw_count}} status={{status}}`
- Base variables (`repo_name`, `repo_directory`) are immutable in this task.

### Step 3 (MANDATORY)
**Prerequisites & Checklist Verification:**
- If status already SKIPPED or FAIL from Step 2, bypass classification and execution.
- Validate repo_directory exists (optional list_dir). If missing, set status=FAIL.
- If DEBUG=1, print: `[debug][task-execute-readme] prerequisites ok, proceeding to safety classification` (only if continuing).

### Step 4 (MANDATORY)
**Structural Reasoning – Safety Classification:**  
For EACH command in commands_extracted array, use AI reasoning to determine if it is SAFE or UNSAFE.

**SAFE Commands** (non-destructive, standard setup, low risk):
- **Package Manager Installs** (read-only or controlled installation):
  - `npm install`, `npm ci`, `yarn install`, `yarn`
  - `pip install`, `pip install -r requirements.txt`
  - `dotnet restore`, `nuget restore`
  - `composer install`, `bundle install`
  - `go get`, `cargo build`
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`
- **Version Checks** (read-only, informational):
  - `node --version`, `npm --version`, `python --version`, `pip --version`
  - `dotnet --version`, `git --version`, `java -version`
  - `msbuild -version`, `gcc --version`
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`
- **Configuration Reads** (non-modifying queries):
  - `git config --list`, `git config --get user.name`
  - `npm config list`, `npm config get registry`
  - Environment variable reads: `echo $PATH`, `$env:PATH`
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`
- **Non-Destructive File Operations**:
  - Directory listing: `ls`, `dir`, `tree`
  - Directory navigation: `cd <path>` (safe when used to set context)
  - File reading: `cat`, `type`, `Get-Content` (read-only)
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`
- **Environment Variable Assignment** (local scope):
  - `export VAR=value` (Bash/sh)
  - `$env:VAR='value'` (PowerShell)
  - `set VAR=value` (CMD - local scope)
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`
- **Safe Directory Creation** (non-destructive):
  - `mkdir <name>` (creating directories is generally safe)
  - `New-Item -Type Directory`
  - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`

**UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):
- **File Deletion/Modification**:
  - `rm`, `del`, `Remove-Item`, `rmdir`
  - `mv`, `move`, `ren`, `rename`
  - `cp -f`, `copy /Y` (overwriting files)
  - Reason: "destructive_file_operation"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`
- **System/Permission Modifications**:
  - `sudo <anything>`, `su`
  - `chmod`, `chown`, `icacls`
  - `setx` (permanent environment variables)
  - Reason: "system_modification"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`
- **Network Operations** (downloading executables, security risk):
  - `curl <url> | sh`, `wget <url> | bash`
  - `Invoke-WebRequest <url> -OutFile <exe>`
  - Downloading .exe, .msi, .sh, .bat files
  - Reason: "network_download_execute"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`
- **Build/Compile Commands** (handled by other workflow tasks):
  - `msbuild`, `dotnet build`, `dotnet publish`
  - `npm run build`, `npm run start`, `yarn build`
  - `make`, `cmake`, `gradle build`
  - `mvn compile`, `ant build`
  - Reason: "build_command_handled_elsewhere"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`
- **Database Operations**:
  - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`
  - `mongod`, `mysqld`, database server start commands
  - Reason: "database_operation"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`
- **Ambiguous/Complex Commands**:
  - Commands with shell redirects that modify files: `> file.txt`
  - Pipes to unknown executables: `| unknown-tool`
  - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)
  - Reason: "ambiguous_safety"
  - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`

**Safety Decision Logic:**
- When in doubt, classify as UNSAFE.
- Consider command category from task-scan-readme output.
- Consider context from README (is it clearly a setup step?).
- Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`).
- If command does multiple things (chained with && or ;), evaluate each part.

### Step 5 (MANDATORY)
**Command Execution (SAFE commands only):**  
For each SAFE command:
a. Pre-execution:
   - If DEBUG=1, print: `[debug][task-execute-readme] executing command [{{safety_category}}]: {{command}}`
   - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch
b. Execution:
   - Use `run_in_terminal` tool to execute command in {{repo_directory}}
   - Execute command synchronously (wait for completion)
   - Capture stdout, stderr, and exit code
   - Set timeout: 5 minutes (to prevent hanging on interactive commands)
c. Post-execution:
   - If DEBUG=1, print: `[debug][task-execute-readme] command exit_code={{exit_code}}`
   - If exit_code != 0 and DEBUG=1, print: `[debug][task-execute-readme] command failed, stderr: {{stderr[:200]}}`
   - Record result in executed_commands array
d. Log Command Execution:
   - Call @task-update-decision-log to log each command execution:
     ```
     @task-update-decision-log
     timestamp="{{timestamp}}"
     repo_name="{{repo_name}}"
     solution_name=""
     task="task-execute-readme"
     message="{{command}}"
     status="{{status}}"
     ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - solution_name is blank since this is a repository-level task
   - message: the actual command that was executed
   - status: "SUCCESS" if exit_code is 0, "FAIL" if exit_code is non-zero, "TIMEOUT" if command timed out, "ERROR" if execution failed
e. Error Handling:
   - If command times out: record as executed with status="TIMEOUT"
   - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)
   - If tool call fails: record as executed with status="ERROR"

**Skipped Commands (UNSAFE commands):**  
For each UNSAFE command:
- If DEBUG=1, print: `[debug][task-execute-readme] skipping command [{{safety_category}}]: {{command}}, reason: {{reason}}`
- Record in skipped_commands array with:
  - command: the command that was skipped
  - reason: why it was classified as UNSAFE
  - category: safety category (destructive, system_mod, network, build, database, ambiguous)
  - source_section: from task-scan-readme output

### Step 6 (MANDATORY)
- If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`
- If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`

### Step 7 (MANDATORY)
**Verification & Structured Output:**
Run verification BEFORE writing JSON. Any violation sets status=FAIL unless already SKIPPED/FAIL.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for:
   - `- {{repo_name}}` (non-empty)
   - `- {{repo_directory}}` (non-empty if not SKIPPED)
   - `- {{commands_extracted}}` (present; value may be NONE/SKIPPED/FAIL)
   - `- {{executed_commands}}` (present)
   - `- {{skipped_commands}}` (present)
3. If status=SUCCESS:
   - `safe_commands_count + unsafe_commands_count == total_commands_scanned`.
   - `len(executed_commands) == safe_commands_count`.
   - `len(skipped_commands) == unsafe_commands_count`.
4. If status=SKIPPED: executed_commands and skipped_commands arrays SHOULD be empty.
5. Each executed command object has mandatory keys: command, status, exit_code (except TIMEOUT/ERROR may omit exit_code), safety_category.
6. Each skipped command object has command, reason, safety_category.
7. No duplicate command strings across executed vs skipped sets.
8. Task directive line `@task-execute-readme` appears exactly once.
9. Arrow formatting: each variable line uses `- {{token}} → value`.
10. Base variables (`repo_name`, `repo_directory`) unchanged.

Record each failure as: `{ "type": "<code>", "target": "<file|repo>", "detail": "<description>" }` in `verification_errors`.
If DEBUG=1 emit: `[debug][task-execute-readme][verification] FAIL code=<code> detail="<description>"`.

Structured Output JSON (output/{{repo_name}}_task4_execute-readme.json) MUST include:
- repo_directory
- repo_name
- total_commands_scanned
- safe_commands_count
- unsafe_commands_count
- executed_commands (array)
- skipped_commands (array)
- status (SUCCESS|SKIPPED|FAIL)
- timestamp (ISO 8601 UTC seconds)
- verification_errors (array, empty if none)
- debug (optional array when DEBUG=1)

### Step 8 (MANDATORY)
**Result Tracking:**  
- Use `create_file` or `replace_string_in_file` to append the result to:
  - results/repo-results.csv (CSV row)
  - Row format: timestamp, repo_name, task-execute-readme, status, symbol (✓ or ✗)
  - Status is SUCCESS if execution completed (even if individual commands failed)

### Step 9 (MANDATORY)
**Repo Checklist Update:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-execute-readme` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 10 (MANDATORY)
**Repo Variable Refresh (INLINE ONLY):**
- Open `tasks/{{repo_name}}_repo_checklist.md`.
- Locate lines beginning with:
  * `- {{executed_commands}}`
  * `- {{skipped_commands}}`
- Replace ONLY the text after `→` with summary values:
  * `{{executed_commands}}` → `<count> executed: cmd1; cmd2; cmd3 ...` (list up to 5 commands, then `...` if more)
  * `{{skipped_commands}}` → `<count> skipped: cmdA; cmdB ...` (same truncation rule)
- If no executed commands: `0 executed` (no trailing colon list).
- If no skipped commands: `0 skipped`.
- On SKIPPED status (no execution attempted): set both to SKIPPED.
- On FAIL: retain existing values but append ` (FAIL)` unless already marked.
- If a line lacks an arrow, append one then the value: `- {{token}} → <value>`.
**Inline Variable Policy:** Never create separate refreshed blocks; modify original lines only.

### Step 11 (MANDATORY)
**DEBUG Exit Trace:**  
If DEBUG=1, print:  
`[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}`

## Output Contract
- repo_directory: string (from checklist)
- repo_name: string (from checklist)
- total_commands_scanned: number (raw_commands length before safety classification; 0 if SKIPPED)
- safe_commands_count: number
- unsafe_commands_count: number
- executed_commands: array of execution result objects
- skipped_commands: array of skipped command objects
- status: SUCCESS / SKIPPED / FAIL
- timestamp: string (ISO 8601)

## Implementation Notes
1. **THIS IS NOT A SCRIPT**: Use direct tool calls only.
2. **Individual Evaluation**: Each command is evaluated separately for safety.
3. **No Batch Execution**: Commands are executed one at a time using run_in_terminal.
4. **Safety First**: When uncertain, classify as UNSAFE.
5. **Context Awareness**: Use command category and source section to inform safety decision.
6. **Failure Tolerance**: If a safe command fails, log it but continue with remaining commands.
7. **Tool-Based Execution**:
   - Use read_file to load the file specified in commands_json_path parameter.
   - Use AI reasoning to classify each command.
   - Use run_in_terminal to execute each SAFE command individually.
   - Use create_file to save output/{{repo_name}}_task4_execute-readme.json.
   - Use replace_string_in_file to update progress tables.
8. **Timeout Protection**: Set reasonable timeout (5 minutes) to prevent infinite hangs.
9. **Output Truncation**: Truncate stdout/stderr to prevent massive JSON files.
10. **Shell Selection**: Choose appropriate shell based on command syntax:
    - PowerShell syntax ($env:, Get-*, New-*) → pwsh
    - Unix syntax (export, ls, grep) → bash or sh
    - Windows batch (set, dir, type) → cmd
11. **Working Directory**: All commands execute in {{repo_directory}} context.
12. **Error Logging**: Failed commands are logged but don't stop the workflow.
13. **Parameter Usage**: The commands_json_path parameter specifies where to load commands – do not hardcode paths.
14. **Result Integrity**: Ensure executed_commands + skipped_commands counts align with total_commands_scanned.

## Error Handling
- For any step that fails:
  - Log error details (exception type, message, failing command if applicable)
  - If loading commands_json_path fails, set status=FAIL and abort further execution steps
  - Do not update checklist or results CSV on critical failure
  - Individual SAFE command failures do not abort the task; record status=FAIL for that command and continue

## Consistency Checks
- After writing `output/{{repo_name}}_task4_execute-readme.json`, verify file exists and contains keys: `executed_commands`, `skipped_commands`, `status`.
- Verify counts: `safe_commands_count == len(executed_commands)` and `unsafe_commands_count == len(skipped_commands)`.
- After updating checklist, confirm `@task-execute-readme` checkbox only set when status is SUCCESS or SKIPPED (not FAIL).
- If any verification fails, log an error and do not mark checklist.

## Cross-References
- Reference the most recent values obtained in earlier steps; never reuse outdated variable snapshots.
- Variables in scope for this task:
  - repo_directory (execution working directory)
  - repo_name (repository identifier)
  - commands_json_path (input path from scan-readme)
  - total_commands_scanned (from scan JSON)
  - safe_commands_count / unsafe_commands_count
  - executed_commands (array of execution results)
  - skipped_commands (array of skipped command descriptors)
  - status (SUCCESS | SKIPPED | FAIL)
  - timestamp (ISO 8601)
- Ensure checklist variables `{{executed_commands}}`, `{{skipped_commands}}` reflect final JSON values.