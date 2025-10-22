@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}}
---
temperature: 0.1
model: gpt-4
---

Task name: task-execute-readme

Description:
This tool locates and extracts the README documentation file from a repository's root directory to provide build instructions and project context for downstream workflow steps.

** CRITICAL ** DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK. 

This task MUST be performed using DIRECT TOOL CALLS:
1. Use read_file tool to locate and read README files
2. Use structural reasoning to analyze README content
3. Use run_in_terminal tool to execute individual safe commands
4. Use replace_string_in_file or create_file tools to update progress/results files

** NEVER create a Python/PowerShell/Bash script for this task **
** NEVER wrap this entire task in a single executable script **

The AI agent must perform each step interactively using available tools.

Behavior:
0. DEBUG Entry Trace: If you need to output debug messages, use run_in_terminal with echo/Write-Host commands.

1. Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

2. README Candidate Search: Iterates through prioritized list of common README filenames in exact order:
   - README.md
   - readme.md
   - README.txt
   - README.rst
   - README
   - Readme.md

3. File Discovery: Checks repository root directory for each candidate filename; stops on first match found.
   - If DEBUG=1, print: `[debug][task-execute-readme] checking for: {{candidate_filename}}`
   - On first match, if DEBUG=1, print: `[debug][task-execute-readme] found README file: {{matched_filename}}`

4. Content Extraction: 
   - If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
   - If DEBUG=1, print: `[debug][task-execute-readme] content length: {{content_length}} characters`
   - If no match found, content remains null
   - If DEBUG=1 and no match, print: `[debug][task-execute-readme] no README file found in repository root`

5. **Structural Reasoning and Setup Command Parsing** (only if README found):
   - Use structural reasoning to parse README content for setup/build instructions
   - Look for sections with headings containing (case-insensitive):
     - "Prerequisites"
     - "Before you build"
     - "Setup"
     - "Local dev"
     - "Getting Started"
     - "Installation"
     - "Requirements"
   - Within identified sections, extract commands from:
     - Code blocks (fenced with ``` or indented)
     - Inline code segments (wrapped in backticks)
     - Numbered or bulleted lists containing commands
   - **Command Safety Classification**: Categorize each extracted command as SAFE or UNSAFE:
     - **SAFE (non-destructive, read-only, or standard setup)**:
       - Package manager installs: `npm install`, `pip install`, `dotnet restore`, `nuget restore`
       - Environment checks: `node --version`, `python --version`, `dotnet --version`
       - Configuration reads: `git config --list`, `npm config list`
       - Directory listing: `ls`, `dir`, `tree`
       - Variable assignments: `export VAR=value`, `$env:VAR='value'`
     - **UNSAFE (destructive, modifying, or risky)**:
       - File deletion: `rm`, `del`, `Remove-Item`
       - System modifications: `sudo`, `chmod`, `chown`
       - Network operations: `curl`, `wget`, `Invoke-WebRequest` (downloading executables)
       - Build/compile: `msbuild`, `dotnet build`, `npm run build` (skip, handled by other tasks)
       - Database operations: `DROP`, `DELETE`, `UPDATE`
   - **Execute SAFE commands only**:
     - For each SAFE command, if DEBUG=1, print: `[debug][task-execute-readme] executing safe setup command: {{command}}`
     - Execute command synchronously in the repository directory
     - Capture stdout, stderr, and exit code
     - If DEBUG=1, print: `[debug][task-execute-readme] command exit code: {{exit_code}}`
   - **Skip UNSAFE commands**:
     - If DEBUG=1, print: `[debug][task-execute-readme] skipping unsafe command: {{command}}`
     - Log skipped commands to output for review
   - If DEBUG=1, print summary: `[debug][task-execute-readme] executed {{safe_count}} safe commands, skipped {{unsafe_count}} unsafe commands`

6. Structured Output: Save JSON object to output/{repo_name}_task2_execute-readme.json with:
   - repo_directory: echoed from input
   - readme_content: string if found, null otherwise
   - readme_filename: name of matched file, null if not found
   - setup_commands_executed: array of {command, exit_code, stdout, stderr} for executed commands
   - setup_commands_skipped: array of {command, reason} for skipped commands
   - status: SUCCESS if README found, FAIL if not found

7. Result Tracking:
   - Use create_file or replace_string_in_file to append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Update the progress table:
     - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-execute-readme"
     - Change [ ] to [x] to mark task as completed

8. DEBUG Exit Trace: Use run_in_terminal to emit a final debug message after all processing completes:
   "[debug][task-execute-readme] END repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}} commands_executed={{safe_count}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the execute-readme task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-execute-readme] allowing simple grep filtering.
- Entry Message: "[debug][task-execute-readme] START repo_directory='<path>'" emitted before step 1.
- Search Messages: "[debug][task-execute-readme] checking for: <filename>" for each candidate checked.
- Found Message: "[debug][task-execute-readme] found README file: <filename>" when match is found.
- Content Message: "[debug][task-execute-readme] content length: <N> characters" after reading content.
- Not Found Message: "[debug][task-execute-readme] no README file found in repository root" if no match.
- Setup Command Messages: "[debug][task-execute-readme] executing safe setup command: <command>" for each safe command executed.
- Command Result: "[debug][task-execute-readme] command exit code: <N>" after each command execution.
- Skip Messages: "[debug][task-execute-readme] skipping unsafe command: <command>" for unsafe commands.
- Summary Message: "[debug][task-execute-readme] executed <N> safe commands, skipped <M> unsafe commands" after step 5.
- Exit Message: "[debug][task-execute-readme] END repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null> commands_executed=<N>" emitted after step 7.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_directory: string (absolute path to repository root, echoed from input)
- readme_filename: string | null (name of matched README file, null if not found)
- setup_commands_executed: array of objects (each with: command, exit_code, stdout, stderr)
- setup_commands_skipped: array of objects (each with: command, reason for skipping)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)

Implementation Notes (conceptual):
1. **THIS IS NOT A SCRIPT**: The AI agent performs each step using available tools (read_file, run_in_terminal, replace_string_in_file, create_file)
2. Prioritization: Check filenames in exact order listed; first match wins.
3. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
4. Contract Compliance: Always save JSON output file with all six fields (repo_directory, readme_content, readme_filename, setup_commands_executed, setup_commands_skipped, status) regardless of success/failure.
5. Progress Update: Mark [x] in repo-progress for task-execute-readme on both SUCCESS and FAIL (task completed, even if README not found).
6. Content Handling: Return entire file content; do not truncate or summarize at this stage.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
9. **Command Execution Safety**: Use run_in_terminal tool to execute commands in the repository directory. Each command is run individually, not in a batch script.
10. **Command Parsing**: Use structural reasoning to identify command patterns in markdown (code blocks, inline code, list items starting with $, >, etc.).
11. **Safety First**: When in doubt about command safety, classify as UNSAFE and skip. Better to skip a potentially useful command than execute a destructive one.
12. **Empty Arrays**: If no commands found or README not found, return empty arrays for setup_commands_executed and setup_commands_skipped.
13. **Command Context**: Commands should be executed with appropriate shell (pwsh/bash) based on command syntax detection or system default.
14. **Tool-Based Execution**: Use read_file to read README, run_in_terminal to execute individual commands, create_file to save JSON output, replace_string_in_file to update progress tables.
