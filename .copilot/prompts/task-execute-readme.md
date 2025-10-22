@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}}@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}}



Task name: task-execute-readmeTask name: task-execute-readme



Description:Description:

This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and CANNOT be scripted.This task takes the commands extracted by task-scan-readme, determines which commands are safe to execute, and executes them in the repository directory. This task requires AI structural reasoning for safety classification and CANNOT be scripted.



** CRITICAL ** DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK.This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:

1. Use read_file tool to load commands from task-scan-readme output JSON

This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:2. Use structural reasoning to classify each command as SAFE or UNSAFE

1. Use read_file tool to load commands from task-scan-readme output JSON3. Use run_in_terminal tool to execute SAFE commands individually

2. Use structural reasoning to classify each command as SAFE or UNSAFE4. Use create_file tool to save execution results to JSON output

3. Use run_in_terminal tool to execute SAFE commands individually5. Use replace_string_in_file tool to update progress/results files

4. Use create_file tool to save execution results to JSON output

5. Use replace_string_in_file tool to update progress/results files** NEVER create a Python/PowerShell/Bash script for this task **

** NEVER batch-execute commands in a single script **

** NEVER create a Python/PowerShell/Bash script for this task **** EACH command must be evaluated individually for safety **

** NEVER batch-execute commands in a single script **

** EACH command must be evaluated individually for safety **The AI agent must use reasoning to determine command safety and execute safe commands one at a time.



The AI agent must use reasoning to determine command safety and execute safe commands one at a time.Behavior:

0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:

Behavior:   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}'"

0. DEBUG Entry Trace: Use run_in_terminal with echo/Write-Host:

   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}'"1. Input Parameters:

   - repo_directory: absolute path to repository root

1. Input Parameters:   - repo_name: repository name

   - repo_directory: absolute path to repository root   - Load commands from: output/{repo_name}_task3_scan-readme.json

   - repo_name: repository name

   - Load commands from: output/{repo_name}_task3_scan-readme.json2. Prerequisites Check:

   - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution

2. Prerequisites Check:   - If DEBUG=1, print: `[debug][task-execute-readme] no commands to execute (scan status: {{scan_status}})`

   - If task-scan-readme was SKIPPED (no README) or FAIL, skip execution   - Set status=SKIPPED and proceed to output

   - If DEBUG=1, print: `[debug][task-execute-readme] no commands to execute (scan status: {{scan_status}})`   - If commands available, proceed with safety classification

   - Set status=SKIPPED and proceed to output

   - If commands available, proceed with safety classification3. **Structural Reasoning - Safety Classification**:

   - Use structural reasoning to parse README content for setup/build instructions

3. **Structural Reasoning - Safety Classification**:   - Look for sections with headings containing (case-insensitive):

   For EACH command in commands_extracted array, use AI reasoning to determine if it is SAFE or UNSAFE.     - "Prerequisites"

        - "Before you build"

   **SAFE Commands** (non-destructive, standard setup, low risk):     - "Setup"

        - "Local dev"

   a. **Package Manager Installs** (read-only or controlled installation):     - "Getting Started"

      - `npm install`, `npm ci`, `yarn install`, `yarn`     - "Installation"

      - `pip install`, `pip install -r requirements.txt`     - "Requirements"

      - `dotnet restore`, `nuget restore`   - Within identified sections, extract commands from:

      - `composer install`, `bundle install`     - Code blocks (fenced with ``` or indented)

      - `go get`, `cargo build`     - Inline code segments (wrapped in backticks)

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [package_install]: {{command}}`     - Numbered or bulleted lists containing commands

      - **Command Safety Classification**: Categorize each extracted command as SAFE or UNSAFE:

   b. **Version Checks** (read-only, informational):     - **SAFE (non-destructive, read-only, or standard setup)**:

      - `node --version`, `npm --version`, `python --version`, `pip --version`       - Package manager installs: `npm install`, `pip install`, `dotnet restore`, `nuget restore`

      - `dotnet --version`, `git --version`, `java -version`       - Environment checks: `node --version`, `python --version`, `dotnet --version`

      - `msbuild -version`, `gcc --version`       - Configuration reads: `git config --list`, `npm config list`

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [version_check]: {{command}}`       - Directory listing: `ls`, `dir`, `tree`

          - Variable assignments: `export VAR=value`, `$env:VAR='value'`

   c. **Configuration Reads** (non-modifying queries):     - **UNSAFE (destructive, modifying, or risky)**:

      - `git config --list`, `git config --get user.name`       - File deletion: `rm`, `del`, `Remove-Item`

      - `npm config list`, `npm config get registry`       - System modifications: `sudo`, `chmod`, `chown`

      - Environment variable reads: `echo $PATH`, `$env:PATH`       - Network operations: `curl`, `wget`, `Invoke-WebRequest` (downloading executables)

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [config_read]: {{command}}`       - Build/compile: `msbuild`, `dotnet build`, `npm run build` (skip, handled by other tasks)

          - Database operations: `DROP`, `DELETE`, `UPDATE`

   d. **Non-Destructive File Operations**:   - **Execute SAFE commands only**:

      - Directory listing: `ls`, `dir`, `tree`     - For each SAFE command, if DEBUG=1, print: `[debug][task-execute-readme] executing safe setup command: {{command}}`

      - Directory navigation: `cd <path>` (safe when used to set context)     - Execute command synchronously in the repository directory

      - File reading: `cat`, `type`, `Get-Content` (read-only)     - Capture stdout, stderr, and exit code

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [file_read]: {{command}}`     - If DEBUG=1, print: `[debug][task-execute-readme] command exit code: {{exit_code}}`

      - **Skip UNSAFE commands**:

   e. **Environment Variable Assignment** (local scope):     - If DEBUG=1, print: `[debug][task-execute-readme] skipping unsafe command: {{command}}`

      - `export VAR=value` (Bash/sh)     - Log skipped commands to output for review

      - `$env:VAR='value'` (PowerShell)   - If DEBUG=1, print summary: `[debug][task-execute-readme] executed {{safe_count}} safe commands, skipped {{unsafe_count}} unsafe commands`

      - `set VAR=value` (CMD - local scope)

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [env_var]: {{command}}`6. Structured Output: Save JSON object to output/{repo_name}_task2_execute-readme.json with:

      - repo_directory: echoed from input

   f. **Safe Directory Creation** (non-destructive):   - readme_content: string if found, null otherwise

      - `mkdir <name>` (creating directories is generally safe)   - readme_filename: name of matched file, null if not found

      - `New-Item -Type Directory`   - setup_commands_executed: array of {command, exit_code, stdout, stderr} for executed commands

      - If DEBUG=1: `[debug][task-execute-readme] SAFE [mkdir]: {{command}}`   - setup_commands_skipped: array of {command, reason} for skipped commands

      - status: SUCCESS if README found, FAIL if not found

   **UNSAFE Commands** (destructive, modifying, risky, or out-of-scope):

   7. Result Tracking:

   a. **File Deletion/Modification**:   - Use create_file or replace_string_in_file to append the result to:

      - `rm`, `del`, `Remove-Item`, `rmdir`     - results/repo-results.md (Markdown table row)

      - `mv`, `move`, `ren`, `rename`     - results/repo-results.csv (CSV row)

      - `cp -f`, `copy /Y` (overwriting files)   - Update the progress table:

      - Reason: "destructive_file_operation"     - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-execute-readme"

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [destructive]: {{command}}`     - Change [ ] to [x] to mark task as completed

   

   b. **System/Permission Modifications**:8. DEBUG Exit Trace: Use run_in_terminal to emit a final debug message after all processing completes:

      - `sudo <anything>`, `su`   "[debug][task-execute-readme] END repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}} commands_executed={{safe_count}}"

      - `chmod`, `chown`, `icacls`

      - `setx` (permanent environment variables)Conditional Verbose Output (DEBUG):

      - Reason: "system_modification"- Purpose: Provide clear trace that the execute-readme task was called and for which repository, plus completion status.

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [system_mod]: {{command}}`- Activation: Only when DEBUG environment variable equals "1".

   - Format Guarantees: Always starts with prefix [debug][task-execute-readme] allowing simple grep filtering.

   c. **Network Operations** (downloading executables, security risk):- Entry Message: "[debug][task-execute-readme] START repo_directory='<path>'" emitted before step 1.

      - `curl <url> | sh`, `wget <url> | bash`- Search Messages: "[debug][task-execute-readme] checking for: <filename>" for each candidate checked.

      - `Invoke-WebRequest <url> -OutFile <exe>`- Found Message: "[debug][task-execute-readme] found README file: <filename>" when match is found.

      - Downloading .exe, .msi, .sh, .bat files- Content Message: "[debug][task-execute-readme] content length: <N> characters" after reading content.

      - Reason: "network_download_execute"- Not Found Message: "[debug][task-execute-readme] no README file found in repository root" if no match.

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [network]: {{command}}`- Setup Command Messages: "[debug][task-execute-readme] executing safe setup command: <command>" for each safe command executed.

   - Command Result: "[debug][task-execute-readme] command exit code: <N>" after each command execution.

   d. **Build/Compile Commands** (handled by other workflow tasks):- Skip Messages: "[debug][task-execute-readme] skipping unsafe command: <command>" for unsafe commands.

      - `msbuild`, `dotnet build`, `dotnet publish`- Summary Message: "[debug][task-execute-readme] executed <N> safe commands, skipped <M> unsafe commands" after step 5.

      - `npm run build`, `npm run start`, `yarn build`- Exit Message: "[debug][task-execute-readme] END repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null> commands_executed=<N>" emitted after step 7.

      - `make`, `cmake`, `gradle build`- Non-Interference: Does not modify success criteria or output contract; purely informational.

      - `mvn compile`, `ant build`

      - Reason: "build_command_handled_elsewhere"Output Contract:

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [build]: {{command}}`- repo_directory: string (absolute path to repository root, echoed from input)

   - readme_filename: string | null (name of matched README file, null if not found)

   e. **Database Operations**:- setup_commands_executed: array of objects (each with: command, exit_code, stdout, stderr)

      - `DROP`, `DELETE`, `UPDATE`, `TRUNCATE`- setup_commands_skipped: array of objects (each with: command, reason for skipping)

      - `mongod`, `mysqld`, database server start commands- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)

      - Reason: "database_operation"

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [database]: {{command}}`Implementation Notes (conceptual):

   1. **THIS IS NOT A SCRIPT**: The AI agent performs each step using available tools (read_file, run_in_terminal, replace_string_in_file, create_file)

   f. **Ambiguous/Complex Commands**:2. Prioritization: Check filenames in exact order listed; first match wins.

      - Commands with shell redirects that modify files: `> file.txt`3. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.

      - Pipes to unknown executables: `| unknown-tool`4. Contract Compliance: Always save JSON output file with all six fields (repo_directory, readme_content, readme_filename, setup_commands_executed, setup_commands_skipped, status) regardless of success/failure.

      - Complex chained commands: `cmd1 && cmd2 && cmd3` (evaluate each separately)5. Progress Update: Mark [x] in repo-progress for task-execute-readme on both SUCCESS and FAIL (task completed, even if README not found).

      - Reason: "ambiguous_safety"6. Content Handling: Return entire file content; do not truncate or summarize at this stage.

      - If DEBUG=1: `[debug][task-execute-readme] UNSAFE [ambiguous]: {{command}}`7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.

   8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.

   **Safety Decision Logic**:9. **Command Execution Safety**: Use run_in_terminal tool to execute commands in the repository directory. Each command is run individually, not in a batch script.

   - When in doubt, classify as UNSAFE10. **Command Parsing**: Use structural reasoning to identify command patterns in markdown (code blocks, inline code, list items starting with $, >, etc.).

   - Consider command category from task-scan-readme output11. **Safety First**: When in doubt about command safety, classify as UNSAFE and skip. Better to skip a potentially useful command than execute a destructive one.

   - Consider context from README (is it clearly a setup step?)12. **Empty Arrays**: If no commands found or README not found, return empty arrays for setup_commands_executed and setup_commands_skipped.

   - Check for command flags that change behavior (e.g., `rm -rf` vs `ls -l`)13. **Command Context**: Commands should be executed with appropriate shell (pwsh/bash) based on command syntax detection or system default.

   - If command does multiple things (chained with && or ;), evaluate each part14. **Tool-Based Execution**: Use read_file to read README, run_in_terminal to execute individual commands, create_file to save JSON output, replace_string_in_file to update progress tables.


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
