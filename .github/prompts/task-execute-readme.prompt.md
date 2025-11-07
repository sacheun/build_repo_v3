---
temperature: 0.1
---

@task-execute-readme checklist_path={{checklist_path}}

# Task name: task-execute-readme

## Description
This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and **cannot** be scripted.

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
This task MUST be performed using **direct tool calls** and **structural reasoning**:
*STRICT MODE ON**
- All steps are **MANDATORY**.

The AI agent must use reasoning to determine command safety and execute safe commands one at a time.

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
**Checklist Load, Variable Extraction & Prerequisite Verification:**
1. Open the file at `{{checklist_path}}`.
2. Extract values (text after a single `→`) for:
  - `- {{repo_name}}`
  - `- {{repo_directory}}`
  - `- {{commands_extracted}}` (comma-separated commands or status token)
  - Confirm presence of lines for `- {{executed_commands}}` and `- {{skipped_commands}}` (values may be placeholders).
3. Validation rules:
  - If any required line missing OR `repo_name`/`repo_directory` empty: `status=FAIL` → jump to Structured Output (skip remaining steps).
  - Validate `repo_directory` exists (may use list_dir). If not: `status=FAIL`.
4. Interpret `{{commands_extracted}}`:
  - If value in {NONE, SKIPPED, FAIL, ""}: set `status=SKIPPED` (no classification/execution later).
  - Else split by comma to build `raw_commands` array; trim whitespace for each.
5. Base variables (`repo_name`, `repo_directory`) are immutable in this task.
6. Outcomes:
  - On FAIL: proceed directly to Step 5 (Structured Output) after checklist update logic (only marking FAIL) is applied.
  - On SKIPPED: still perform checklist update (mark as SKIPPED) then structured output.

### Step 2 (MANDATORY)
**Structural Reasoning – Safety Classification:**  
If `status` from Step 1 is SKIPPED or FAIL, bypass this step (no classification performed).

For EACH command in `raw_commands`, use AI reasoning to determine if it is SAFE or UNSAFE.

**SAFE Commands** (non-destructive, standard setup, low risk):
- **Package Manager Installs** (read-only or controlled installation):
  - `npm install`, `npm ci`, `yarn install`, `yarn`
  - `pip install`, `pip install -r requirements.txt`
  - `dotnet restore`, `nuget restore`
  - `composer install`, `bundle install`
  - `go get`, `cargo build`

- **Version Checks** (read-only, informational):
  - `node --version`, `npm --version`, `python --version`, `pip --version`
  - `dotnet --version`, `git --version`, `java -version`
  - `msbuild -version`, `gcc --version`

- **Configuration Reads** (non-modifying queries):
  - `git config --list`, `git config --get user.name`
  - `npm config list`, `npm config get registry`
  - Environment variable reads: `echo $PATH`, `$env:PATH`

- **Non-Destructive File Operations**:
  - Directory listing: `ls`, `dir`, `tree`
  - Directory navigation: `cd <path>` (safe when used to set context)
  - File reading: `cat`, `type`, `Get-Content` (read-only)

- **Environment Variable Assignment** (local scope):
  - `export VAR=value` (Bash/sh)
  - `$env:VAR='value'` (PowerShell)
  - `set VAR=value` (CMD - local scope)

- **Safe Directory Creation** (non-destructive):
  - `mkdir <name>` (creating directories is generally safe)
  - `New-Item -Type Directory`


**UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):
- **File Deletion/Modification**:
  - `rm`, `del`, `Remove-Item`, `rmdir`
  - `mv`, `move`, `ren`, `rename`
  - `cp -f`, `copy /Y` (overwriting files)
  - Reason: "destructive_file_operation"

- **System/Permission Modifications**:
  - `sudo <anything>`, `su`
  - `chmod`, `chown`, `icacls`
  - `setx` (permanent environment variables)
  - Reason: "system_modification"

- **Network Operations** (downloading executables, security risk):
  - `curl <url> | sh`, `wget <url> | bash`
  - `Invoke-WebRequest <url> -OutFile <exe>`
  - Downloading .exe, .msi, .sh, .bat files
  - Reason: "network_download_execute"

- **Build/Compile Commands** (handled by other workflow tasks):
  - `msbuild`, `dotnet build`, `dotnet publish`
  - `npm run build`, `npm run start`, `yarn build`
  - `make`, `cmake`, `gradle build`
  - `mvn compile`, `ant build`
  - Reason: "build_command_handled_elsewhere"

- **Database Operations**:
  - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`
  - `mongod`, `mysqld`, database server start commands
  - Reason: "database_operation"

- **Ambiguous/Complex Commands**:
  - Commands with shell redirects that modify files: `> file.txt`
  - Pipes to unknown executables: `| unknown-tool`
  - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)
  - Reason: "ambiguous_safety"


**Safety Decision Logic:**
- When in doubt, classify as UNSAFE.
- Consider command category from task-scan-readme output.
- Consider context from README (is it clearly a setup step?).
- Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`).
- If command does multiple things (chained with && or ;), evaluate each part.

### Step 3 (MANDATORY)
**Command Execution (SAFE commands only):**  
For each SAFE command:
a. Pre-execution:
  - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch
b. Execution:
   - Use `run_in_terminal` tool to execute command in {{repo_directory}}
   - Execute command synchronously (wait for completion)
   - Capture stdout, stderr, and exit code
   - Set timeout: 5 minutes (to prevent hanging on interactive commands)
c. Post-execution:
  - Record result in executed_commands array
e. Error Handling:
   - If command times out: record as executed with status="TIMEOUT"
   - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)
   - If tool call fails: record as executed with status="ERROR"

**Skipped Commands (UNSAFE commands):**  
For each UNSAFE command:
  (No debug output.)
- Record in skipped_commands array with:
  - command: the command that was skipped
  - reason: why it was classified as UNSAFE
  - category: safety category (destructive, system_mod, network, build, database, ambiguous)
  - source_section: from task-scan-readme output

### Step 4 (MANDATORY)
**Checklist Update & Variable Refresh (INLINE ONLY):**
1. Open `tasks/{{repo_name}}_repo_checklist.md`.
2. Set `[x]` only on the `@task-execute-readme` entry if status in {SUCCESS, SKIPPED}. Leave `[ ]` on FAIL.
3. Locate lines beginning with:
  * `- {{executed_commands}}`
  * `- {{skipped_commands}}`
4. Replace ONLY the text after `→` with summary values:
  * `{{executed_commands}}` → `<count> executed: cmd1; cmd2; cmd3 ...` (list up to 5 commands, then `...` if more)
  * `{{skipped_commands}}` → `<count> skipped: cmdA; cmdB ...` (same truncation rule)
5. If no executed commands: `0 executed` (no trailing colon list).
6. If no skipped commands: `0 skipped`.
7. On SKIPPED status (no execution attempted): set both to `SKIPPED`.
8. On FAIL: retain existing values but append ` (FAIL)` unless already marked.
9. Always ensure exactly one `→` per line.
10. **Inline Variable Policy:** Never create separate refreshed blocks; modify original lines only.
11. Do not modify other checklist tasks or repository entries.

### Step 5 (MANDATORY)
Structured Output Assembly:
Generate JSON  at `./output/{{repo_name}}_task4_execute-readme.json`.

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

### End of Steps

## Output Contract
- `repo_directory`: string (from checklist)
- `repo_name`: string (from checklist)
- `total_commands_scanned`: number (raw_commands length before safety classification; 0 if SKIPPED)
- `safe_commands_count`: number
- `unsafe_commands_count`: number
- `executed_commands`: array of execution result objects
- `skipped_commands`: array of skipped command objects
- `status`: SUCCESS / SKIPPED / FAIL
- `timestamp`: string (ISO 8601)

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
    - Windows batch (set, dir, type) → cmd
11. **Working Directory**: All commands execute in {{repo_directory}} context.
12. **Error Logging**: Failed commands are logged but don't stop the workflow.
13. **Parameter Usage**: The commands_json_path parameter specifies where to load commands – do not hardcode paths.
14. **Result Integrity**: Ensure executed_commands + skipped_commands counts align with total_commands_scanned.
