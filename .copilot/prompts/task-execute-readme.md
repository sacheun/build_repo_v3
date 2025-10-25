---
temperature: 0.1
---

@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}} commands_json_path={{commands_json_path}}

Task name: task-execute-readme

Description:

This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and CANNOT be scripted.

** CRITICAL ** DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK.

This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:

1. Use read_file tool to load commands from the file specified in commands_json_path parameter
2. Use structural reasoning to classify each command as SAFE or UNSAFE
3. Use run_in_terminal tool to execute SAFE commands individually
4. Use create_file tool to save execution results to JSON output
5. Use replace_string_in_file tool to update progress/results files

** NEVER create a Python/PowerShell/Bash script for this task **
** NEVER batch-execute commands in a single script **
** EACH command must be evaluated individually for safety **

The AI agent must use reasoning to determine command safety and execute safe commands one at a time.

Behavior:

0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:
   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}' commands_json_path='{{commands_json_path}}'"

1. Input Parameters:
   - repo_directory: absolute path to repository root
   - repo_name: repository name
   - commands_json_path: path to the JSON file containing extracted commands (from task-scan-readme output)
     Example: "output/{repo_name}_task3_scan-readme.json"

2. Prerequisites Check:
   - Use read_file to load the file specified in commands_json_path parameter
   - Extract the commands_extracted array from the JSON
   - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution
   - If DEBUG=1, print: `[debug][task-execute-readme] loaded {{command_count}} commands from {{commands_json_path}}`
   - If no commands or scan failed, set status=SKIPPED and proceed to output
   - If commands available, proceed with safety classification

3. **Structural Reasoning - Safety Classification**:
   
   For EACH command in commands_extracted array, use AI reasoning to determine if it is SAFE or UNSAFE.
   
   **SAFE Commands** (non-destructive, standard setup, low risk):
   
   a. **Package Manager Installs** (read-only or controlled installation):
      - `npm install`, `npm ci`, `yarn install`, `yarn`
      - `pip install`, `pip install -r requirements.txt`
      - `dotnet restore`, `nuget restore`
      - `composer install`, `bundle install`
      - `go get`, `cargo build`
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`
   
   b. **Version Checks** (read-only, informational):
      - `node --version`, `npm --version`, `python --version`, `pip --version`
      - `dotnet --version`, `git --version`, `java -version`
      - `msbuild -version`, `gcc --version`
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`
   
   c. **Configuration Reads** (non-modifying queries):
      - `git config --list`, `git config --get user.name`
      - `npm config list`, `npm config get registry`
      - Environment variable reads: `echo $PATH`, `$env:PATH`
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`
   
   d. **Non-Destructive File Operations**:
      - Directory listing: `ls`, `dir`, `tree`
      - Directory navigation: `cd <path>` (safe when used to set context)
      - File reading: `cat`, `type`, `Get-Content` (read-only)
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`
   
   e. **Environment Variable Assignment** (local scope):
      - `export VAR=value` (Bash/sh)
      - `$env:VAR='value'` (PowerShell)
      - `set VAR=value` (CMD - local scope)
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`
   
   f. **Safe Directory Creation** (non-destructive):
      - `mkdir <name>` (creating directories is generally safe)
      - `New-Item -Type Directory`
      - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`
   
   **UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):
   
   a. **File Deletion/Modification**:
      - `rm`, `del`, `Remove-Item`, `rmdir`
      - `mv`, `move`, `ren`, `rename`
      - `cp -f`, `copy /Y` (overwriting files)
      - Reason: "destructive_file_operation"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`
   
   b. **System/Permission Modifications**:
      - `sudo <anything>`, `su`
      - `chmod`, `chown`, `icacls`
      - `setx` (permanent environment variables)
      - Reason: "system_modification"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`
   
   c. **Network Operations** (downloading executables, security risk):
      - `curl <url> | sh`, `wget <url> | bash`
      - `Invoke-WebRequest <url> -OutFile <exe>`
      - Downloading .exe, .msi, .sh, .bat files
      - Reason: "network_download_execute"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`
   
   d. **Build/Compile Commands** (handled by other workflow tasks):
      - `msbuild`, `dotnet build`, `dotnet publish`
      - `npm run build`, `npm run start`, `yarn build`
      - `make`, `cmake`, `gradle build`
      - `mvn compile`, `ant build`
      - Reason: "build_command_handled_elsewhere"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`
   
   e. **Database Operations**:
      - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`
      - `mongod`, `mysqld`, database server start commands
      - Reason: "database_operation"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`
   
   f. **Ambiguous/Complex Commands**:
      - Commands with shell redirects that modify files: `> file.txt`
      - Pipes to unknown executables: `| unknown-tool`
      - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)
      - Reason: "ambiguous_safety"
      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`
   
   **Safety Decision Logic**:
   - When in doubt, classify as UNSAFE
   - Consider command category from task-scan-readme output
   - Consider context from README (is it clearly a setup step?)
   - Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`)
   - If command does multiple things (chained with && or ;), evaluate each part

4. **Command Execution** (SAFE commands only):
   
   For each SAFE command:
   
   a. Pre-execution:
      - If DEBUG=1, print: `[debug][task-execute-readme] executing command [{{safety_category}}]: {{command}}`
      - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch
   
   b. Execution:
      - Use run_in_terminal tool to execute command in {{repo_directory}}
      - Execute command synchronously (wait for completion)
      - Capture stdout, stderr, and exit code
      - Set timeout: 5 minutes (to prevent hanging on interactive commands)
   
   c. Post-execution:
      - If DEBUG=1, print: `[debug][task-execute-readme] command exit_code={{exit_code}}`
      - If exit_code != 0 and DEBUG=1, print: `[debug][task-execute-readme] command failed, stderr: {{stderr[:200]}}`
      - Record result in executed_commands array
      - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},,task-execute-readme,{{command}},{{status}}"
        * timestamp: ISO 8601 format (e.g., "2025-10-22T14:30:45Z")
        * solution_name column (third column) is blank since this is a repository-level task
        * command: the actual command that was executed
        * status: "SUCCESS" if exit_code is 0, "FAIL" if exit_code is non-zero, "TIMEOUT" if command timed out, "ERROR" if execution failed
   
   d. Error Handling:
      - If command times out: record as executed with status="TIMEOUT"
      - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)
      - If tool call fails: record as executed with status="ERROR"

5. **Skipped Commands** (UNSAFE commands):
   
   For each UNSAFE command:
   - If DEBUG=1, print: `[debug][task-execute-readme] skipping command [{{safety_category}}]: {{command}}, reason: {{reason}}`
   - Record in skipped_commands array with:
     - command: the command that was skipped
     - reason: why it was classified as UNSAFE
     - category: safety category (destructive, system_mod, network, build, database, ambiguous)
     - source_section: from task-scan-readme output

6. Summary:
   - If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`
   - If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`

7. Structured Output: Save JSON object to output/{repo_name}_task4_execute-readme.json with:
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
     - status: SUCCESS | FAIL | TIMEOUT | ERROR
     - execution_time_seconds: how long it took
   - skipped_commands: array of objects:
     - command: the command that was skipped
     - safety_category: UNSAFE classification reason
     - reason: detailed reason for skipping
     - source_section: which README section it came from
   - status: SUCCESS (if execution completed, even if some commands failed)
   - timestamp: ISO 8601 format datetime

8. Result Tracking:
   - Use create_file or replace_string_in_file to append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-execute-readme | status | symbol
   - Status is SUCCESS if execution completed (even if individual commands failed)

9. Progress Update:
   - Use replace_string_in_file to update results/repo-progress.md
   - Find row for {{repo_name}} and column for "task-execute-readme"
   - Change [ ] to [x] to mark task as completed

10. DEBUG Exit Trace: Use run_in_terminal to emit:
    "[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide detailed trace of safety reasoning and execution
- Activation: Only when DEBUG environment variable equals "1"
- Format: All messages start with [debug][task-execute-readme]
- Entry: "[debug][task-execute-readme] START repo_directory='<path>' commands_json_path='<path>'"
- Load: "[debug][task-execute-readme] loaded <N> commands from <path>"
- Safe Classification: "[debug][task-execute-readme] SAFE [<category>]: <command>"
- Unsafe Classification: "[debug][task-execute-readme] UNSAFE [<category>]: <command>"
- Pre-execution: "[debug][task-execute-readme] executing command [<category>]: <command>"
- Post-execution: "[debug][task-execute-readme] command exit_code=<N>"
- Failure: "[debug][task-execute-readme] command failed, stderr: <text>"
- Skip: "[debug][task-execute-readme] skipping command [<category>]: <command>, reason: <reason>"
- Summary: "[debug][task-execute-readme] execution summary: <N> safe commands executed, <M> unsafe commands skipped"
- Exit: "[debug][task-execute-readme] EXIT repo_directory='<path>' status=<status> executed=<N> skipped=<M>"

Output Contract:
- repo_directory: string
- repo_name: string
- total_commands_scanned: number (from task-scan-readme)
- safe_commands_count: number
- unsafe_commands_count: number
- executed_commands: array of execution result objects
- skipped_commands: array of skipped command objects
- status: SUCCESS | SKIPPED | FAIL
- timestamp: string (ISO 8601)

Implementation Notes (conceptual):
1. **THIS IS NOT A SCRIPT**: Use direct tool calls only
2. **Individual Evaluation**: Each command is evaluated separately for safety
3. **No Batch Execution**: Commands are executed one at a time using run_in_terminal
4. **Safety First**: When uncertain, classify as UNSAFE
5. **Context Awareness**: Use command category and source section to inform safety decision
6. **Failure Tolerance**: If a safe command fails, log it but continue with remaining commands
7. **Tool-Based Execution**:
   - Use read_file to load the file specified in commands_json_path parameter
   - Use AI reasoning to classify each command
   - Use run_in_terminal to execute each SAFE command individually
   - Use create_file to save output/{repo_name}_task4_execute-readme.json
   - Use replace_string_in_file to update progress tables
8. **Timeout Protection**: Set reasonable timeout (5 minutes) to prevent infinite hangs
9. **Output Truncation**: Truncate stdout/stderr to prevent massive JSON files
10. **Shell Selection**: Choose appropriate shell based on command syntax:
    - PowerShell syntax ($env:, Get-*, New-*) → pwsh
    - Unix syntax (export, ls, grep) → bash or sh
    - Windows batch (set, dir, type) → cmd
11. **Working Directory**: All commands execute in {{repo_directory}} context
12. **Error Logging**: Failed commands are logged but don't stop the workflow
13. **Parameter Usage**: The commands_json_path parameter specifies where to load commands - do not hardcode paths

Safety Classification Examples:

**SAFE:**
- `npm install` → package_install (standard, safe)
- `node --version` → version_check (read-only)
- `export PATH=$PATH:/new/path` → env_var (local scope)
- `ls -la` → file_read (read-only)
- `mkdir build` → mkdir (non-destructive)

**UNSAFE:**
- `rm -rf node_modules` → destructive (file deletion)
- `sudo npm install -g` → system_mod (system-wide change)
- `curl https://get.script.sh | sh` → network (download and execute)
- `msbuild solution.sln` → build (handled by task-process-solutions)
- `cmd1 && cmd2 && sudo cmd3` → ambiguous (contains unsafe component)

Execution Examples:

**Example 1: Simple Safe Command**
Command: `npm install`
→ Classify: SAFE [package_install]
→ Execute: run_in_terminal("cd {{repo_directory}}; npm install")
→ Result: exit_code=0, stdout="added 523 packages", status=SUCCESS

**Example 2: Version Check**
Command: `node --version`
→ Classify: SAFE [version_check]
→ Execute: run_in_terminal("node --version")
→ Result: exit_code=0, stdout="v18.17.0", status=SUCCESS

**Example 3: Build Command (Unsafe)**
Command: `dotnet build`
→ Classify: UNSAFE [build]
→ Reason: "build_command_handled_elsewhere"
→ Skip: Add to skipped_commands array
→ No execution

**Example 4: Destructive Command (Unsafe)**
Command: `rm -rf dist`
→ Classify: UNSAFE [destructive]
→ Reason: "destructive_file_operation"
→ Skip: Add to skipped_commands array
→ No execution


   

   **SAFE Commands** (non-destructive, standard setup, low risk):

   Behavior:4. Use create_file tool to save execution results to JSON output

   a. **Package Manager Installs** (read-only or controlled installation):

      - `npm install`, `npm ci`, `yarn install`, `yarn`0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:

      - `pip install`, `pip install -r requirements.txt`

      - `dotnet restore`, `nuget restore`   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}' commands_json_path='{{commands_json_path}}'"5. Use replace_string_in_file tool to update progress/results files** NEVER create a Python/PowerShell/Bash script for this task **

      - `composer install`, `bundle install`

      - `go get`, `cargo build`

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`

   1. Input Parameters:** NEVER batch-execute commands in a single script **

   b. **Version Checks** (read-only, informational):

      - `node --version`, `npm --version`, `python --version`, `pip --version`   - repo_directory: absolute path to repository root

      - `dotnet --version`, `git --version`, `java -version`

      - `msbuild -version`, `gcc --version`   - repo_name: repository name** NEVER create a Python/PowerShell/Bash script for this task **** EACH command must be evaluated individually for safety **

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`

      - commands_json_path: path to the JSON file containing extracted commands (from task-scan-readme output)

   c. **Configuration Reads** (non-modifying queries):

      - `git config --list`, `git config --get user.name`     Example: "output/{repo_name}_task3_scan-readme.json"** NEVER batch-execute commands in a single script **

      - `npm config list`, `npm config get registry`

      - Environment variable reads: `echo $PATH`, `$env:PATH`

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`

   2. Prerequisites Check:** EACH command must be evaluated individually for safety **The AI agent must use reasoning to determine command safety and execute safe commands one at a time.

   d. **Non-Destructive File Operations**:

      - Directory listing: `ls`, `dir`, `tree`   - Use read_file to load the file specified in commands_json_path parameter

      - Directory navigation: `cd <path>` (safe when used to set context)

      - File reading: `cat`, `type`, `Get-Content` (read-only)   - Extract the commands_extracted array from the JSON

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`

      - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution

   e. **Environment Variable Assignment** (local scope):

      - `export VAR=value` (Bash/sh)   - If DEBUG=1, print: `[debug][task-execute-readme] loaded {{command_count}} commands from {{commands_json_path}}`The AI agent must use reasoning to determine command safety and execute safe commands one at a time.Behavior:

      - `$env:VAR='value'` (PowerShell)

      - `set VAR=value` (CMD - local scope)   - If no commands or scan failed, set status=SKIPPED and proceed to output

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`

      - If commands available, proceed with safety classification0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:

   f. **Safe Directory Creation** (non-destructive):

      - `mkdir <name>` (creating directories is generally safe)

      - `New-Item -Type Directory`

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`3. **Structural Reasoning - Safety Classification**:Behavior:   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}'"



   **UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):   

   

   a. **File Deletion/Modification**:   For EACH command in commands_extracted array, use AI reasoning to determine if it is SAFE or UNSAFE.0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:

      - `rm`, `del`, `Remove-Item`, `rmdir`

      - `mv`, `move`, `ren`, `rename`   

      - `cp -f`, `copy /Y` (overwriting files)

      - Reason: "destructive_file_operation"   **SAFE Commands** (non-destructive, standard setup, low risk):   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}'"1. Input Parameters:

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`

      

   b. **System/Permission Modifications**:

      - `sudo <anything>`, `su`   a. **Package Manager Installs** (read-only or controlled installation):   - repo_directory: absolute path to repository root

      - `chmod`, `chown`, `icacls`

      - `setx` (permanent environment variables)      - `npm install`, `npm ci`, `yarn install`, `yarn`

      - Reason: "system_modification"

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`      - `pip install`, `pip install -r requirements.txt`1. Input Parameters:   - repo_name: repository name

   

   c. **Network Operations** (downloading executables, security risk):      - `dotnet restore`, `nuget restore`

      - `curl <url> | sh`, `wget <url> | bash`

      - `Invoke-WebRequest <url> -OutFile <exe>`      - `composer install`, `bundle install`   - repo_directory: absolute path to repository root   - Load commands from: output/{repo_name}_task3_scan-readme.json

      - Downloading .exe, .msi, .sh, .bat files

      - Reason: "network_download_execute"      - `go get`, `cargo build`

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`

         - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`   - repo_name: repository name

   d. **Build/Compile Commands** (handled by other workflow tasks):

      - `msbuild`, `dotnet build`, `dotnet publish`   

      - `npm run build`, `npm run start`, `yarn build`

      - `make`, `cmake`, `gradle build`   b. **Version Checks** (read-only, informational):   - Load commands from: output/{repo_name}_task3_scan-readme.json2. Prerequisites Check:

      - `mvn compile`, `ant build`

      - Reason: "build_command_handled_elsewhere"      - `node --version`, `npm --version`, `python --version`, `pip --version`

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`

         - `dotnet --version`, `git --version`, `java -version`   - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution

   e. **Database Operations**:

      - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`      - `msbuild -version`, `gcc --version`

      - `mongod`, `mysqld`, database server start commands

      - Reason: "database_operation"      - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`2. Prerequisites Check:   - If DEBUG=1, print: `[debug][task-execute-readme] no commands to execute (scan status: {{scan_status}})`

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`

      

   f. **Ambiguous/Complex Commands**:

      - Commands with shell redirects that modify files: `> file.txt`   c. **Configuration Reads** (non-modifying queries):   - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution   - Set status=SKIPPED and proceed to output

      - Pipes to unknown executables: `| unknown-tool`

      - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)      - `git config --list`, `git config --get user.name`

      - Reason: "ambiguous_safety"

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`      - `npm config list`, `npm config get registry`   - If DEBUG=1, print: `[debug][task-execute-readme] no commands to execute (scan status: {{scan_status}})`   - If commands available, proceed with safety classification



   **Safety Decision Logic**:      - Environment variable reads: `echo $PATH`, `$env:PATH`

   - When in doubt, classify as UNSAFE

   - Consider command category from task-scan-readme output      - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`   - Set status=SKIPPED and proceed to output

   - Consider context from README (is it clearly a setup step?)

   - Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`)   

   - If command does multiple things (chained with && or ;), evaluate each part

   d. **Non-Destructive File Operations**:   - If commands available, proceed with safety classification3. **Structural Reasoning - Safety Classification**:

4. **Command Execution** (SAFE commands only):

         - Directory listing: `ls`, `dir`, `tree`

   For each SAFE command:

         - Directory navigation: `cd <path>` (safe when used to set context)   - Use structural reasoning to parse README content for setup/build instructions

   a. Pre-execution:

      - If DEBUG=1, print: `[debug][task-execute-readme] executing command [{{safety_category}}]: {{command}}`      - File reading: `cat`, `type`, `Get-Content` (read-only)

      - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch

         - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`3. **Structural Reasoning - Safety Classification**:   - Look for sections with headings containing (case-insensitive):

   b. Execution:

      - Use run_in_terminal tool to execute command in {{repo_directory}}   

      - Execute command synchronously (wait for completion)

      - Capture stdout, stderr, and exit code   e. **Environment Variable Assignment** (local scope):   For EACH command in commands_extracted array, use AI reasoning to determine if it is SAFE or UNSAFE.     - "Prerequisites"

      - Set timeout: 5 minutes (to prevent hanging on interactive commands)

         - `export VAR=value` (Bash/sh)

   c. Post-execution:

      - If DEBUG=1, print: `[debug][task-execute-readme] command exit_code={{exit_code}}`      - `$env:VAR='value'` (PowerShell)        - "Before you build"

      - If exit_code != 0 and DEBUG=1, print: `[debug][task-execute-readme] command failed, stderr: {{stderr[:200]}}`

      - Record result in executed_commands array      - `set VAR=value` (CMD - local scope)

      - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},,task-execute-readme,{{command}},{{status}}"

        * timestamp: ISO 8601 format (e.g., "2025-10-22T14:30:45Z")      - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`   **SAFE Commands** (non-destructive, standard setup, low risk):     - "Setup"

        * solution_name column (third column) is blank since this is a repository-level task

        * command: the actual command that was executed   

        * status: "SUCCESS" if exit_code is 0, "FAIL" if exit_code is non-zero, "TIMEOUT" if command timed out, "ERROR" if execution failed

      f. **Safe Directory Creation** (non-destructive):        - "Local dev"

   d. Error Handling:

      - If command times out: record as executed with status="TIMEOUT"      - `mkdir <name>` (creating directories is generally safe)

      - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)

      - If tool call fails: record as executed with status="ERROR"      - `New-Item -Type Directory`   a. **Package Manager Installs** (read-only or controlled installation):     - "Getting Started"



5. **Skipped Commands** (UNSAFE commands):      - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`

   

   For each UNSAFE command:         - `npm install`, `npm ci`, `yarn install`, `yarn`     - "Installation"

   - If DEBUG=1, print: `[debug][task-execute-readme] skipping command [{{safety_category}}]: {{command}}, reason: {{reason}}`

   - Record in skipped_commands array with:   **UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):

     - command: the command that was skipped

     - reason: why it was classified as UNSAFE         - `pip install`, `pip install -r requirements.txt`     - "Requirements"

     - category: safety category (destructive, system_mod, network, build, database, ambiguous)

     - source_section: from task-scan-readme output   a. **File Deletion/Modification**:



6. Summary:      - `rm`, `del`, `Remove-Item`, `rmdir`      - `dotnet restore`, `nuget restore`   - Within identified sections, extract commands from:

   - If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`

   - If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`      - `mv`, `move`, `ren`, `rename`



7. Structured Output: Save JSON object to output/{repo_name}_task4_execute-readme.json with:      - `cp -f`, `copy /Y` (overwriting files)      - `composer install`, `bundle install`     - Code blocks (fenced with ``` or indented)

   - repo_directory: echoed from input

   - repo_name: echoed from input      - Reason: "destructive_file_operation"

   - total_commands_scanned: from task-scan-readme

   - safe_commands_count: number of SAFE commands      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`      - `go get`, `cargo build`     - Inline code segments (wrapped in backticks)

   - unsafe_commands_count: number of UNSAFE commands

   - executed_commands: array of objects:   

     - command: the command executed

     - safety_category: SAFE classification reason   b. **System/Permission Modifications**:      - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`     - Numbered or bulleted lists containing commands

     - exit_code: exit code from execution

     - stdout: captured stdout (truncate to 1000 chars if longer)      - `sudo <anything>`, `su`

     - stderr: captured stderr (truncate to 1000 chars if longer)

     - status: SUCCESS | FAIL | TIMEOUT | ERROR      - `chmod`, `chown`, `icacls`      - **Command Safety Classification**: Categorize each extracted command as SAFE or UNSAFE:

     - execution_time_seconds: how long it took

   - skipped_commands: array of objects:      - `setx` (permanent environment variables)

     - command: the command that was skipped

     - safety_category: UNSAFE classification reason      - Reason: "system_modification"   b. **Version Checks** (read-only, informational):     - **SAFE (non-destructive, read-only, or standard setup)**:

     - reason: detailed reason for skipping

     - source_section: which README section it came from      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`

   - status: SUCCESS (if execution completed, even if some commands failed)

   - timestamp: ISO 8601 format datetime         - `node --version`, `npm --version`, `python --version`, `pip --version`       - Package manager installs: `npm install`, `pip install`, `dotnet restore`, `nuget restore`



8. Result Tracking:   c. **Network Operations** (downloading executables, security risk):

   - Use create_file or replace_string_in_file to append the result to:

     - results/repo-results.md (Markdown table row)      - `curl <url> | sh`, `wget <url> | bash`      - `dotnet --version`, `git --version`, `java -version`       - Environment checks: `node --version`, `python --version`, `dotnet --version`

     - results/repo-results.csv (CSV row)

   - Row format: timestamp | repo_name | task-execute-readme | status | symbol      - `Invoke-WebRequest <url> -OutFile <exe>`

   - Status is SUCCESS if execution completed (even if individual commands failed)

      - Downloading .exe, .msi, .sh, .bat files      - `msbuild -version`, `gcc --version`       - Configuration reads: `git config --list`, `npm config list`

9. Progress Update:

   - Use replace_string_in_file to update results/repo-progress.md      - Reason: "network_download_execute"

   - Find row for {{repo_name}} and column for "task-execute-readme"

   - Change [ ] to [x] to mark task as completed      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`      - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`       - Directory listing: `ls`, `dir`, `tree`



10. DEBUG Exit Trace: Use run_in_terminal to emit:   

    "[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}"

   d. **Build/Compile Commands** (handled by other workflow tasks):          - Variable assignments: `export VAR=value`, `$env:VAR='value'`

Conditional Verbose Output (DEBUG):

- Purpose: Provide detailed trace of safety reasoning and execution      - `msbuild`, `dotnet build`, `dotnet publish`

- Activation: Only when DEBUG environment variable equals "1"

- Format: All messages start with [debug][task-execute-readme]      - `npm run build`, `npm run start`, `yarn build`   c. **Configuration Reads** (non-modifying queries):     - **UNSAFE (destructive, modifying, or risky)**:

- Entry: "[debug][task-execute-readme] START repo_directory='<path>' commands_json_path='<path>'"

- Load: "[debug][task-execute-readme] loaded <N> commands from <path>"      - `make`, `cmake`, `gradle build`

- Safe Classification: "[debug][task-execute-readme] SAFE [<category>]: <command>"

- Unsafe Classification: "[debug][task-execute-readme] UNSAFE [<category>]: <command>"      - `mvn compile`, `ant build`      - `git config --list`, `git config --get user.name`       - File deletion: `rm`, `del`, `Remove-Item`

- Pre-execution: "[debug][task-execute-readme] executing command [<category>]: <command>"

- Post-execution: "[debug][task-execute-readme] command exit_code=<N>"      - Reason: "build_command_handled_elsewhere"

- Failure: "[debug][task-execute-readme] command failed, stderr: <text>"

- Skip: "[debug][task-execute-readme] skipping command [<category>]: <command>, reason: <reason>"      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`      - `npm config list`, `npm config get registry`       - System modifications: `sudo`, `chmod`, `chown`

- Summary: "[debug][task-execute-readme] execution summary: <N> safe commands executed, <M> unsafe commands skipped"

- Exit: "[debug][task-execute-readme] EXIT repo_directory='<path>' status=<status> executed=<N> skipped=<M>"   



Output Contract:   e. **Database Operations**:      - Environment variable reads: `echo $PATH`, `$env:PATH`       - Network operations: `curl`, `wget`, `Invoke-WebRequest` (downloading executables)

- repo_directory: string

- repo_name: string      - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`

- total_commands_scanned: number (from task-scan-readme)

- safe_commands_count: number      - `mongod`, `mysqld`, database server start commands      - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`       - Build/compile: `msbuild`, `dotnet build`, `npm run build` (skip, handled by other tasks)

- unsafe_commands_count: number

- executed_commands: array of execution result objects      - Reason: "database_operation"

- skipped_commands: array of skipped command objects

- status: SUCCESS | SKIPPED | FAIL      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`          - Database operations: `DROP`, `DELETE`, `UPDATE`

- timestamp: string (ISO 8601)

   

Implementation Notes (conceptual):

1. **THIS IS NOT A SCRIPT**: Use direct tool calls only   f. **Ambiguous/Complex Commands**:   d. **Non-Destructive File Operations**:   - **Execute SAFE commands only**:

2. **Individual Evaluation**: Each command is evaluated separately for safety

3. **No Batch Execution**: Commands are executed one at a time using run_in_terminal      - Commands with shell redirects that modify files: `> file.txt`

4. **Safety First**: When uncertain, classify as UNSAFE

5. **Context Awareness**: Use command category and source section to inform safety decision      - Pipes to unknown executables: `| unknown-tool`      - Directory listing: `ls`, `dir`, `tree`     - For each SAFE command, if DEBUG=1, print: `[debug][task-execute-readme] executing safe setup command: {{command}}`

6. **Failure Tolerance**: If a safe command fails, log it but continue with remaining commands

7. **Tool-Based Execution**:      - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)

   - Use read_file to load the file specified in commands_json_path parameter

   - Use AI reasoning to classify each command      - Reason: "ambiguous_safety"      - Directory navigation: `cd <path>` (safe when used to set context)     - Execute command synchronously in the repository directory

   - Use run_in_terminal to execute each SAFE command individually

   - Use create_file to save output/{repo_name}_task4_execute-readme.json      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`

   - Use replace_string_in_file to update progress tables

8. **Timeout Protection**: Set reasonable timeout (5 minutes) to prevent infinite hangs         - File reading: `cat`, `type`, `Get-Content` (read-only)     - Capture stdout, stderr, and exit code

9. **Output Truncation**: Truncate stdout/stderr to prevent massive JSON files

10. **Shell Selection**: Choose appropriate shell based on command syntax:   **Safety Decision Logic**:

    - PowerShell syntax ($env:, Get-*, New-*) → pwsh

    - Unix syntax (export, ls, grep) → bash or sh   - When in doubt, classify as UNSAFE      - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`     - If DEBUG=1, print: `[debug][task-execute-readme] command exit code: {{exit_code}}`

    - Windows batch (set, dir, type) → cmd

11. **Working Directory**: All commands execute in {{repo_directory}} context   - Consider command category from task-scan-readme output

12. **Error Logging**: Failed commands are logged but don't stop the workflow

13. **Parameter Usage**: The commands_json_path parameter specifies where to load commands - do not hardcode paths   - Consider context from README (is it clearly a setup step?)      - **Skip UNSAFE commands**:



Safety Classification Examples:   - Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`)



**SAFE:**   - If command does multiple things (chained with && or ;), evaluate each part   e. **Environment Variable Assignment** (local scope):     - If DEBUG=1, print: `[debug][task-execute-readme] skipping unsafe command: {{command}}`

- `npm install` → package_install (standard, safe)

- `node --version` → version_check (read-only)

- `export PATH=$PATH:/new/path` → env_var (local scope)

- `ls -la` → file_read (read-only)4. **Command Execution** (SAFE commands only):      - `export VAR=value` (Bash/sh)     - Log skipped commands to output for review

- `mkdir build` → mkdir (non-destructive)

   

**UNSAFE:**

- `rm -rf node_modules` → destructive (file deletion)   For each SAFE command:      - `$env:VAR='value'` (PowerShell)   - If DEBUG=1, print summary: `[debug][task-execute-readme] executed {{safe_count}} safe commands, skipped {{unsafe_count}} unsafe commands`

- `sudo npm install -g` → system_mod (system-wide change)

- `curl https://get.script.sh | sh` → network (download and execute)   

- `msbuild solution.sln` → build (handled by task-process-solutions)

- `cmd1 && cmd2 && sudo cmd3` → ambiguous (contains unsafe component)   a. Pre-execution:      - `set VAR=value` (CMD - local scope)



Execution Examples:      - If DEBUG=1, print: `[debug][task-execute-readme] executing command [{{safety_category}}]: {{command}}`



**Example 1: Simple Safe Command**      - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch      - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`6. Structured Output: Save JSON object to output/{repo_name}_task2_execute-readme.json with:

Command: `npm install`

→ Classify: SAFE [package_install]   

→ Execute: run_in_terminal("cd {{repo_directory}}; npm install")

→ Result: exit_code=0, stdout="added 523 packages", status=SUCCESS   b. Execution:      - repo_directory: echoed from input



**Example 2: Version Check**      - Use run_in_terminal tool to execute command in {{repo_directory}}

Command: `node --version`

→ Classify: SAFE [version_check]      - Execute command synchronously (wait for completion)   f. **Safe Directory Creation** (non-destructive):   - readme_content: string if found, null otherwise

→ Execute: run_in_terminal("node --version")

→ Result: exit_code=0, stdout="v18.17.0", status=SUCCESS      - Capture stdout, stderr, and exit code



**Example 3: Build Command (Unsafe)**      - Set timeout: 5 minutes (to prevent hanging on interactive commands)      - `mkdir <name>` (creating directories is generally safe)   - readme_filename: name of matched file, null if not found

Command: `dotnet build`

→ Classify: UNSAFE [build]   

→ Reason: "build_command_handled_elsewhere"

→ Skip: Add to skipped_commands array   c. Post-execution:      - `New-Item -Type Directory`   - setup_commands_executed: array of {command, exit_code, stdout, stderr} for executed commands

→ No execution

      - If DEBUG=1, print: `[debug][task-execute-readme] command exit_code={{exit_code}}`

**Example 4: Destructive Command (Unsafe)**

Command: `rm -rf dist`      - If exit_code != 0 and DEBUG=1, print: `[debug][task-execute-readme] command failed, stderr: {{stderr[:200]}}`      - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`   - setup_commands_skipped: array of {command, reason} for skipped commands

→ Classify: UNSAFE [destructive]

→ Reason: "destructive_file_operation"      - Record result in executed_commands array

→ Skip: Add to skipped_commands array

→ No execution      - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},,task-execute-readme,{{command}},{{status}}"      - status: SUCCESS if README found, FAIL if not found


        * timestamp: ISO 8601 format (e.g., "2025-10-22T14:30:45Z")

        * solution_name column (third column) is blank since this is a repository-level task   **UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):

        * command: the actual command that was executed

        * status: "SUCCESS" if exit_code is 0, "FAIL" if exit_code is non-zero, "TIMEOUT" if command timed out, "ERROR" if execution failed   7. Result Tracking:

   

   d. Error Handling:   a. **File Deletion/Modification**:   - Use create_file or replace_string_in_file to append the result to:

      - If command times out: record as executed with status="TIMEOUT"

      - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)      - `rm`, `del`, `Remove-Item`, `rmdir`     - results/repo-results.md (Markdown table row)

      - If tool call fails: record as executed with status="ERROR"

      - `mv`, `move`, `ren`, `rename`     - results/repo-results.csv (CSV row)

5. **Skipped Commands** (UNSAFE commands):

         - `cp -f`, `copy /Y` (overwriting files)   - Update the progress table:

   For each UNSAFE command:

   - If DEBUG=1, print: `[debug][task-execute-readme] skipping command [{{safety_category}}]: {{command}}, reason: {{reason}}`      - Reason: "destructive_file_operation"     - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-execute-readme"

   - Record in skipped_commands array with:

     - command: the command that was skipped      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`     - Change [ ] to [x] to mark task as completed

     - reason: why it was classified as UNSAFE

     - category: safety category (destructive, system_mod, network, build, database, ambiguous)   

     - source_section: from task-scan-readme output

   b. **System/Permission Modifications**:8. DEBUG Exit Trace: Use run_in_terminal to emit a final debug message after all processing completes:

6. Summary:

   - If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`      - `sudo <anything>`, `su`   "[debug][task-execute-readme] END repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}} commands_executed={{safe_count}}"

   - If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`

      - `chmod`, `chown`, `icacls`

7. Structured Output: Save JSON object to output/{repo_name}_task4_execute-readme.json with:

   - repo_directory: echoed from input      - `setx` (permanent environment variables)Conditional Verbose Output (DEBUG):

   - repo_name: echoed from input

   - total_commands_scanned: from task-scan-readme      - Reason: "system_modification"- Purpose: Provide clear trace that the execute-readme task was called and for which repository, plus completion status.

   - safe_commands_count: number of SAFE commands

   - unsafe_commands_count: number of UNSAFE commands      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`- Activation: Only when DEBUG environment variable equals "1".

   - executed_commands: array of objects:

     - command: the command executed   - Format Guarantees: Always starts with prefix [debug][task-execute-readme] allowing simple grep filtering.

     - safety_category: SAFE classification reason

     - exit_code: exit code from execution   c. **Network Operations** (downloading executables, security risk):- Entry Message: "[debug][task-execute-readme] START repo_directory='<path>'" emitted before step 1.

     - stdout: captured stdout (truncate to 1000 chars if longer)

     - stderr: captured stderr (truncate to 1000 chars if longer)      - `curl <url> | sh`, `wget <url> | bash`- Search Messages: "[debug][task-execute-readme] checking for: <filename>" for each candidate checked.

     - status: SUCCESS | FAIL | TIMEOUT | ERROR

     - execution_time_seconds: how long it took      - `Invoke-WebRequest <url> -OutFile <exe>`- Found Message: "[debug][task-execute-readme] found README file: <filename>" when match is found.

   - skipped_commands: array of objects:

     - command: the command that was skipped      - Downloading .exe, .msi, .sh, .bat files- Content Message: "[debug][task-execute-readme] content length: <N> characters" after reading content.

     - safety_category: UNSAFE classification reason

     - reason: detailed reason for skipping      - Reason: "network_download_execute"- Not Found Message: "[debug][task-execute-readme] no README file found in repository root" if no match.

     - source_section: which README section it came from

   - status: SUCCESS (if execution completed, even if some commands failed)      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`- Setup Command Messages: "[debug][task-execute-readme] executing safe setup command: <command>" for each safe command executed.

   - timestamp: ISO 8601 format datetime

   - Command Result: "[debug][task-execute-readme] command exit code: <N>" after each command execution.

8. Result Tracking:

   - Use create_file or replace_string_in_file to append the result to:   d. **Build/Compile Commands** (handled by other workflow tasks):- Skip Messages: "[debug][task-execute-readme] skipping unsafe command: <command>" for unsafe commands.

     - results/repo-results.md (Markdown table row)

     - results/repo-results.csv (CSV row)      - `msbuild`, `dotnet build`, `dotnet publish`- Summary Message: "[debug][task-execute-readme] executed <N> safe commands, skipped <M> unsafe commands" after step 5.

   - Row format: timestamp | repo_name | task-execute-readme | status | symbol

   - Status is SUCCESS if execution completed (even if individual commands failed)      - `npm run build`, `npm run start`, `yarn build`- Exit Message: "[debug][task-execute-readme] END repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null> commands_executed=<N>" emitted after step 7.



9. Progress Update:      - `make`, `cmake`, `gradle build`- Non-Interference: Does not modify success criteria or output contract; purely informational.

   - Use replace_string_in_file to update results/repo-progress.md

   - Find row for {{repo_name}} and column for "task-execute-readme"      - `mvn compile`, `ant build`

   - Change [ ] to [x] to mark task as completed

      - Reason: "build_command_handled_elsewhere"Output Contract:

10. DEBUG Exit Trace: Use run_in_terminal to emit:

    "[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}"      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`- repo_directory: string (absolute path to repository root, echoed from input)



Conditional Verbose Output (DEBUG):   - readme_filename: string | null (name of matched README file, null if not found)

- Purpose: Provide detailed trace of safety reasoning and execution

- Activation: Only when DEBUG environment variable equals "1"   e. **Database Operations**:- setup_commands_executed: array of objects (each with: command, exit_code, stdout, stderr)

- Format: All messages start with [debug][task-execute-readme]

- Entry: "[debug][task-execute-readme] START repo_directory='<path>' commands_json_path='<path>'"      - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`- setup_commands_skipped: array of objects (each with: command, reason for skipping)

- Load: "[debug][task-execute-readme] loaded <N> commands from <path>"

- Safe Classification: "[debug][task-execute-readme] SAFE [<category>]: <command>"      - `mongod`, `mysqld`, database server start commands- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)

- Unsafe Classification: "[debug][task-execute-readme] UNSAFE [<category>]: <command>"

- Pre-execution: "[debug][task-execute-readme] executing command [<category>]: <command>"      - Reason: "database_operation"

- Post-execution: "[debug][task-execute-readme] command exit_code=<N>"

- Failure: "[debug][task-execute-readme] command failed, stderr: <text>"      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`Implementation Notes (conceptual):

- Skip: "[debug][task-execute-readme] skipping command [<category>]: <command>, reason: <reason>"

- Summary: "[debug][task-execute-readme] execution summary: <N> safe commands executed, <M> unsafe commands skipped"   1. **THIS IS NOT A SCRIPT**: The AI agent performs each step using available tools (read_file, run_in_terminal, replace_string_in_file, create_file)

- Exit: "[debug][task-execute-readme] EXIT repo_directory='<path>' status=<status> executed=<N> skipped=<M>"

   f. **Ambiguous/Complex Commands**:2. Prioritization: Check filenames in exact order listed; first match wins.

Output Contract:

- repo_directory: string      - Commands with shell redirects that modify files: `> file.txt`3. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.

- repo_name: string

- total_commands_scanned: number (from task-scan-readme)      - Pipes to unknown executables: `| unknown-tool`4. Contract Compliance: Always save JSON output file with all six fields (repo_directory, readme_content, readme_filename, setup_commands_executed, setup_commands_skipped, status) regardless of success/failure.

- safe_commands_count: number

- unsafe_commands_count: number      - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)5. Progress Update: Mark [x] in repo-progress for task-execute-readme on both SUCCESS and FAIL (task completed, even if README not found).

- executed_commands: array of execution result objects

- skipped_commands: array of skipped command objects      - Reason: "ambiguous_safety"6. Content Handling: Return entire file content; do not truncate or summarize at this stage.

- status: SUCCESS | SKIPPED | FAIL

- timestamp: string (ISO 8601)      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.



Implementation Notes (conceptual):   8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.

1. **THIS IS NOT A SCRIPT**: Use direct tool calls only

2. **Individual Evaluation**: Each command is evaluated separately for safety   **Safety Decision Logic**:9. **Command Execution Safety**: Use run_in_terminal tool to execute commands in the repository directory. Each command is run individually, not in a batch script.

3. **No Batch Execution**: Commands are executed one at a time using run_in_terminal

4. **Safety First**: When uncertain, classify as UNSAFE   - When in doubt, classify as UNSAFE10. **Command Parsing**: Use structural reasoning to identify command patterns in markdown (code blocks, inline code, list items starting with $, >, etc.).

5. **Context Awareness**: Use command category and source section to inform safety decision

6. **Failure Tolerance**: If a safe command fails, log it but continue with remaining commands   - Consider command category from task-scan-readme output11. **Safety First**: When in doubt about command safety, classify as UNSAFE and skip. Better to skip a potentially useful command than execute a destructive one.

7. **Tool-Based Execution**:

   - Use read_file to load the file specified in commands_json_path parameter   - Consider context from README (is it clearly a setup step?)12. **Empty Arrays**: If no commands found or README not found, return empty arrays for setup_commands_executed and setup_commands_skipped.

   - Use AI reasoning to classify each command

   - Use run_in_terminal to execute each SAFE command individually   - Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`)13. **Command Context**: Commands should be executed with appropriate shell (pwsh/bash) based on command syntax detection or system default.

   - Use create_file to save output/{repo_name}_task4_execute-readme.json

   - Use replace_string_in_file to update progress tables   - If command does multiple things (chained with && or ;), evaluate each part14. **Tool-Based Execution**: Use read_file to read README, run_in_terminal to execute individual commands, create_file to save JSON output, replace_string_in_file to update progress tables.

8. **Timeout Protection**: Set reasonable timeout (5 minutes) to prevent infinite hangs

9. **Output Truncation**: Truncate stdout/stderr to prevent massive JSON files

10. **Shell Selection**: Choose appropriate shell based on command syntax:4. **Command Execution** (SAFE commands only):

    - PowerShell syntax ($env:, Get-*, New-*) → pwsh   

    - Unix syntax (export, ls, grep) → bash or sh   For each SAFE command:

    - Windows batch (set, dir, type) → cmd   

11. **Working Directory**: All commands execute in {{repo_directory}} context   a. Pre-execution:

12. **Error Logging**: Failed commands are logged but don't stop the workflow      - If DEBUG=1, print: `[debug][task-execute-readme] executing command [{{safety_category}}]: {{command}}`

13. **Parameter Usage**: The commands_json_path parameter specifies where to load commands - do not hardcode paths      - Determine appropriate shell: PowerShell (pwsh) for PowerShell syntax, bash/sh for Unix syntax, cmd for Windows batch

   

Safety Classification Examples:   b. Execution:

      - Use run_in_terminal tool to execute command in {{repo_directory}}

**SAFE:**      - Execute command synchronously (wait for completion)

- `npm install` → package_install (standard, safe)      - Capture stdout, stderr, and exit code

- `node --version` → version_check (read-only)      - Set timeout: 5 minutes (to prevent hanging on interactive commands)

- `export PATH=$PATH:/new/path` → env_var (local scope)   

- `ls -la` → file_read (read-only)   c. Post-execution:

- `mkdir build` → mkdir (non-destructive)      - If DEBUG=1, print: `[debug][task-execute-readme] command exit_code={{exit_code}}`

      - If exit_code != 0 and DEBUG=1, print: `[debug][task-execute-readme] command failed, stderr: {{stderr[:200]}}`

**UNSAFE:**      - Record result in executed_commands array

- `rm -rf node_modules` → destructive (file deletion)      - **Log to Decision Log**: Append to results/decision-log.csv with: "{{timestamp}},{{repo_name}},,task-execute-readme,{{command}},{{status}}"

- `sudo npm install -g` → system_mod (system-wide change)        * timestamp: ISO 8601 format (e.g., "2025-10-22T14:30:45Z")

- `curl https://get.script.sh | sh` → network (download and execute)        * solution_name column (third column) is blank since this is a repository-level task

- `msbuild solution.sln` → build (handled by task-process-solutions)        * command: the actual command that was executed

- `cmd1 && cmd2 && sudo cmd3` → ambiguous (contains unsafe component)        * status: "SUCCESS" if exit_code is 0, "FAIL" if exit_code is non-zero, "TIMEOUT" if command timed out, "ERROR" if execution failed

   

Execution Examples:   d. Error Handling:

      - If command times out: record as executed with status="TIMEOUT"

**Example 1: Simple Safe Command**      - If command fails (exit_code != 0): record as executed with status="FAIL" (don't stop, continue with other commands)

Command: `npm install`      - If tool call fails: record as executed with status="ERROR"

→ Classify: SAFE [package_install]

→ Execute: run_in_terminal("cd {{repo_directory}}; npm install")5. **Skipped Commands** (UNSAFE commands):

→ Result: exit_code=0, stdout="added 523 packages", status=SUCCESS   

   For each UNSAFE command:

**Example 2: Version Check**   - If DEBUG=1, print: `[debug][task-execute-readme] skipping command [{{safety_category}}]: {{command}}, reason: {{reason}}`

Command: `node --version`   - Record in skipped_commands array with:

→ Classify: SAFE [version_check]     - command: the command that was skipped

→ Execute: run_in_terminal("node --version")     - reason: why it was classified as UNSAFE

→ Result: exit_code=0, stdout="v18.17.0", status=SUCCESS     - category: safety category (destructive, system_mod, network, build, database, ambiguous)

     - source_section: from task-scan-readme output

**Example 3: Build Command (Unsafe)**

Command: `dotnet build`6. Summary:

→ Classify: UNSAFE [build]   - If DEBUG=1, print: `[debug][task-execute-readme] execution summary: {{safe_count}} safe commands executed, {{unsafe_count}} unsafe commands skipped`

→ Reason: "build_command_handled_elsewhere"   - If DEBUG=1 and any failures, print: `[debug][task-execute-readme] {{failed_count}} commands failed during execution`

→ Skip: Add to skipped_commands array

→ No execution7. Structured Output: Save JSON object to output/{repo_name}_task4_execute-readme.json with:

   - repo_directory: echoed from input

**Example 4: Destructive Command (Unsafe)**   - repo_name: echoed from input

Command: `rm -rf dist`   - total_commands_scanned: from task-scan-readme

→ Classify: UNSAFE [destructive]   - safe_commands_count: number of SAFE commands

→ Reason: "destructive_file_operation"   - unsafe_commands_count: number of UNSAFE commands

→ Skip: Add to skipped_commands array   - executed_commands: array of objects:

→ No execution     - command: the command executed

     - safety_category: SAFE classification reason
     - exit_code: exit code from execution
     - stdout: captured stdout (truncate to 1000 chars if longer)
     - stderr: captured stderr (truncate to 1000 chars if longer)
     - status: SUCCESS | FAIL | TIMEOUT | ERROR
     - execution_time_seconds: how long it took
   - skipped_commands: array of objects:
     - command: the command that was skipped
     - safety_category: UNSAFE classification reason
     - reason: detailed reason for skipping
     - source_section: which README section it came from
   - status: SUCCESS (if execution completed, even if some commands failed)
   - timestamp: ISO 8601 format datetime

8. Result Tracking:
   - Use create_file or replace_string_in_file to append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-execute-readme | status | symbol
   - Status is SUCCESS if execution completed (even if individual commands failed)

9. Progress Update:
   - Use replace_string_in_file to update results/repo-progress.md
   - Find row for {{repo_name}} and column for "task-execute-readme"
   - Change [ ] to [x] to mark task as completed

10. DEBUG Exit Trace: Use run_in_terminal to emit:
    "[debug][task-execute-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} executed={{safe_count}} skipped={{unsafe_count}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide detailed trace of safety reasoning and execution
- Activation: Only when DEBUG environment variable equals "1"
- Format: All messages start with [debug][task-execute-readme]
- Entry: "[debug][task-execute-readme] START repo_directory='<path>'"
- Safe Classification: "[debug][task-execute-readme] SAFE [<category>]: <command>"
- Unsafe Classification: "[debug][task-execute-readme] UNSAFE [<category>]: <command>"
- Pre-execution: "[debug][task-execute-readme] executing command [<category>]: <command>"
- Post-execution: "[debug][task-execute-readme] command exit_code=<N>"
- Failure: "[debug][task-execute-readme] command failed, stderr: <text>"
- Skip: "[debug][task-execute-readme] skipping command [<category>]: <command>, reason: <reason>"
- Summary: "[debug][task-execute-readme] execution summary: <N> safe commands executed, <M> unsafe commands skipped"
- Exit: "[debug][task-execute-readme] EXIT repo_directory='<path>' status=<status> executed=<N> skipped=<M>"

Output Contract:
- repo_directory: string
- repo_name: string
- total_commands_scanned: number (from task-scan-readme)
- safe_commands_count: number
- unsafe_commands_count: number
- executed_commands: array of execution result objects
- skipped_commands: array of skipped command objects
- status: SUCCESS | SKIPPED | FAIL
- timestamp: string (ISO 8601)

Implementation Notes (conceptual):
1. **THIS IS NOT A SCRIPT**: Use direct tool calls only
2. **Individual Evaluation**: Each command is evaluated separately for safety
3. **No Batch Execution**: Commands are executed one at a time using run_in_terminal
4. **Safety First**: When uncertain, classify as UNSAFE
5. **Context Awareness**: Use command category and source section to inform safety decision
6. **Failure Tolerance**: If a safe command fails, log it but continue with remaining commands
7. **Tool-Based Execution**:
   - Use read_file to load output/{repo_name}_task3_scan-readme.json
   - Use AI reasoning to classify each command
   - Use run_in_terminal to execute each SAFE command individually
   - Use create_file to save output/{repo_name}_task4_execute-readme.json
   - Use replace_string_in_file to update progress tables
8. **Timeout Protection**: Set reasonable timeout (5 minutes) to prevent infinite hangs
9. **Output Truncation**: Truncate stdout/stderr to prevent massive JSON files
10. **Shell Selection**: Choose appropriate shell based on command syntax:
    - PowerShell syntax ($env:, Get-*, New-*) → pwsh
    - Unix syntax (export, ls, grep) → bash or sh
    - Windows batch (set, dir, type) → cmd
11. **Working Directory**: All commands execute in {{repo_directory}} context
12. **Error Logging**: Failed commands are logged but don't stop the workflow

Safety Classification Examples:

**SAFE:**
- `npm install` → package_install (standard, safe)
- `node --version` → version_check (read-only)
- `export PATH=$PATH:/new/path` → env_var (local scope)
- `ls -la` → file_read (read-only)
- `mkdir build` → mkdir (non-destructive)

**UNSAFE:**
- `rm -rf node_modules` → destructive (file deletion)
- `sudo npm install -g` → system_mod (system-wide change)
- `curl https://get.script.sh | sh` → network (download and execute)
- `msbuild solution.sln` → build (handled by task-process-solutions)
- `cmd1 && cmd2 && sudo cmd3` → ambiguous (contains unsafe component)

Execution Examples:

**Example 1: Simple Safe Command**
Command: `npm install`
→ Classify: SAFE [package_install]
→ Execute: run_in_terminal("cd {{repo_directory}}; npm install")
→ Result: exit_code=0, stdout="added 523 packages", status=SUCCESS

**Example 2: Version Check**
Command: `node --version`
→ Classify: SAFE [version_check]
→ Execute: run_in_terminal("node --version")
→ Result: exit_code=0, stdout="v18.17.0", status=SUCCESS

**Example 3: Build Command (Unsafe)**
Command: `dotnet build`
→ Classify: UNSAFE [build]
→ Reason: "build_command_handled_elsewhere"
→ Skip: Add to skipped_commands array
→ No execution

**Example 4: Destructive Command (Unsafe)**
Command: `rm -rf dist`
→ Classify: UNSAFE [destructive]
→ Reason: "destructive_file_operation"
→ Skip: Add to skipped_commands array
→ No execution
