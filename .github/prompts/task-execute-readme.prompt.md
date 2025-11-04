---
temperature: 0.1
---

@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}} commands_json_path={{commands_json_path}}

# Task name: task-execute-readme

## Description
This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and **cannot** be scripted.

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**
This task MUST be performed using **direct tool calls** and **structural reasoning**:

1. Use `read_file` tool to load commands from the file specified in commands_json_path parameter.
2. Use structural reasoning to classify each command as SAFE or UNSAFE.
3. Use `run_in_terminal` tool to execute SAFE commands individually.
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
`[debug][task-execute-readme] START repo_directory='{{repo_directory}}' commands_json_path='{{commands_json_path}}'`

### Step 2 (MANDATORY)
**Input Parameters:**  
- repo_directory: absolute path to repository root  
- repo_name: repository name  
- commands_json_path: path to the JSON file containing extracted commands (from task-scan-readme output)  
  Example: `output/{{repo_name}}_task3_scan-readme.json`

**Prerequisites Check:**  
- Use `read_file` to load the file specified in commands_json_path parameter.
- Extract the commands_extracted array from the JSON.
- If @task-scan-readme was SKIPPED (no README) or FAIL, skip execution.
- If DEBUG=1, print: `[debug][task-execute-readme] loaded {{command_count}} commands from {{commands_json_path}}`
- If no commands or scan failed, set status=SKIPPED and proceed to output.
- If commands available, proceed with safety classification.

**Pre-flight Checklist Verification:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  - `{{executed_commands}}`
  - `{{skipped_commands}}`
- If any token is missing or altered, restore it prior to continuing.

### Step 3 (MANDATORY)
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

### Step 4 (MANDATORY)
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

### Step 5 (MANDATORY)
- If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`
- If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`

### Step 6 (MANDATORY)
**Structured Output:**  
Save JSON object to `output/{{repo_name}}_task4_execute-readme.json` with:
- repo_directory: echoed from input
- repo_name: echoed from input
- total_commands_scanned: from task-scan-readme
- safe_commands_count: number of SAFE commands
- unsafe_commands_count: number of UNSAFE commands
- executed_commands: array of objects:
  - command: the command executed
  - safety_category: SAFE classification reason
  - exit_code: exit code from execution
  - stdout: captured stdout (truncate to 1000 chars if longer)
  - stderr: captured stderr (truncate to 1000 chars if longer)
  - status: SUCCESS / FAIL / TIMEOUT / ERROR
  - execution_time_seconds: how long it took
- skipped_commands: array of objects:
  - command: the command that was skipped
  - safety_category: UNSAFE classification reason
  - reason: detailed reason for skipping
  - source_section: which README section it came from
- status: SUCCESS / SKIPPED / FAIL
- timestamp: ISO 8601 format datetime

### Step 7 (MANDATORY)
**Result Tracking:**  
- Use `create_file` or `replace_string_in_file` to append the result to:
  - results/repo-results.csv (CSV row)
  - Row format: timestamp, repo_name, task-execute-readme, status, symbol (✓ or ✗)
  - Status is SUCCESS if execution completed (even if individual commands failed)

### Step 8 (MANDATORY)
**Repo Checklist Update:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-execute-readme` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 9 (MANDATORY)
**Repo Variable Refresh:**  
- Open `tasks/{{repo_name}}_repo_checklist.md` file
- Confirm the `## Repo Variables Available` section still contains the expected templated tokens exactly as shown below:
  - `{{executed_commands}}`
  - `{{skipped_commands}}`
- Update the following variables with the latest values produced by this task:
  - `{{executed_commands}}`
  - `{{skipped_commands}}`
- Ensure each variable reflects the refresh results before saving the file

### Step 10 (MANDATORY)
**DEBUG Exit Trace:**  
If DEBUG=1, print:  
`[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}`

## Output Contract
- repo_directory: string
- repo_name: string
- total_commands_scanned: number (from task-scan-readme)
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