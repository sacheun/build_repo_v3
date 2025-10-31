---
temperature: 0.0
---

@task-search-readme repo_directory={{repo_directory}} repo_name={{repo_name}}

Task name: task-search-readme

## Description:
This task searches for and reads the README documentation file from a repository's root directory. This is a simple file location and content extraction task that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python/PowerShell/Bash script that:
1. Searches for README files in the repository root
2. Reads the content of the first match found
3. Saves the result to JSON output
4. Updates progress and results files

## Behavior (Follow this Step by Step)
0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-search-readme] START repo_directory='{{repo_directory}}'`

1. Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

2. README Candidate Search: Performs case-insensitive search for README files in the repository root directory.
   - Search patterns to match (case-insensitive): README.md, README.txt, README.rst, README
   - On Windows: File system is case-insensitive by default
   - On Linux/Mac: Use case-insensitive file matching (e.g., glob with IGNORECASE or list all files and compare lowercased names)
   - Priority order if multiple matches found: .md > .txt > .rst > (no extension)

3. File Discovery: Searches repository root directory using case-insensitive matching; stops on first match found.
   - If DEBUG=1, print: `[debug][task-search-readme] searching for README files (case-insensitive)`
   - On first match, if DEBUG=1, print: `[debug][task-search-readme] found README file: {{matched_filename}}`

4. Content Extraction: 
   - If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
   - If DEBUG=1, print: `[debug][task-search-readme] content length: {{content_length}} characters`
   - If no match found, content remains null
   - If DEBUG=1 and no match, print: `[debug][task-search-readme] no README file found in repository root`

5. Structured Output: Save JSON object to output/{repo_name}_task2_search-readme.json with:
   - repo_directory: echoed from input
   - repo_name: echoed from input
   - readme_content: string if found, null otherwise
   - readme_filename: name of matched file, null if not found
   - status: SUCCESS if README found, FAIL if not found
   - timestamp: ISO 8601 format datetime when task completed

5a. Log to Decision Log:
   - Call @task-update-decision-log to log task execution:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="{{repo_name}}" 
     solution_name="" 
     task="task-search-readme" 
     message="{{message}}" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - The solution_name is blank since this is a repository-level task
   - Message format:
     * If README found: "Found README: {{readme_filename}}" (e.g., "Found README: README.md")
     * If README not found: "No README file found"
   - Status: "SUCCESS" if README found, "FAIL" if not found

6. Result Tracking:
   - Append the result to:
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-search-readme | status | symbol (✓ or ✗)

7. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][task-search-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the search-readme task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-search-readme] allowing simple grep filtering.
- Entry Message: "[debug][task-search-readme] START repo_directory='<path>'" emitted before step 1.
- Search Messages: "[debug][task-search-readme] checking for: <filename>" for each candidate checked.
- Found Message: "[debug][task-search-readme] found README file: <filename>" when match is found.
- Content Message: "[debug][task-search-readme] content length: <N> characters" after reading content.
- Not Found Message: "[debug][task-search-readme] no README file found in repository root" if no match.
- Exit Message: "[debug][task-search-readme] EXIT repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null>" emitted after step 7.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_directory: string (absolute path to repository root, echoed from input)
- repo_name: string (repository name, echoed from input)
- readme_content: string | null (full content of README file, null if not found)
- readme_filename: string | null (name of matched README file, null if not found)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)
- timestamp: string (ISO 8601 datetime when task completed)

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task
2. **Case-Insensitive Search**: Use case-insensitive file matching to find README files (e.g., README.md, readme.md, Readme.MD all match)
3. Prioritization: If multiple README files found, prioritize by extension: .md > .txt > .rst > (no extension)
4. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
5. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
6. Progress Update: Mark [x] in repo-progress for task-search-readme on both SUCCESS and FAIL (task completed, even if README not found).
7. Content Handling: Return entire file content; do not truncate or summarize at this stage.
8. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
9. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
10. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)
11. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired.