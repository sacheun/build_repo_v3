@task-execute-readme repo_directory={{repo_directory}} repo_name={{repo_name}}

Task name: task-execute-readme

Description:
This tool locates and extracts the README documentation file from a repository's root directory to provide build instructions and project context for downstream workflow steps.

Behavior:
0. DEBUG Entry Trace: If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   "[debug][task-execute-readme] START repo_directory='{{repo_directory}}'"
   This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

1. Input Validation: Reads JSON input expecting repo_directory field (absolute path to repository root); raises ContractError if missing or if path does not exist on filesystem.

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

5. Structured Output: Returns JSON object with:
   - repo_directory: echoed from input
   - readme_content: string if found, null otherwise
   - readme_filename: name of matched file, null if not found
   - status: SUCCESS if README found, FAIL if not found

6. Result Tracking:
   - Append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Update the progress table:
     - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-execute-readme"
     - Change [ ] to [x] to mark task as completed

7. DEBUG Exit Trace: If environment variable DEBUG=1 (string comparison), emit a final line to stdout (or terminal) after all processing completes:
   "[debug][task-execute-readme] END repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}"
   This line marks task completion and provides quick status visibility for debugging pipeline execution.

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the execute-readme task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-execute-readme] allowing simple grep filtering.
- Entry Message: "[debug][task-execute-readme] START repo_directory='<path>'" emitted before step 1.
- Search Messages: "[debug][task-execute-readme] checking for: <filename>" for each candidate checked.
- Found Message: "[debug][task-execute-readme] found README file: <filename>" when match is found.
- Content Message: "[debug][task-execute-readme] content length: <N> characters" after reading content.
- Not Found Message: "[debug][task-execute-readme] no README file found in repository root" if no match.
- Exit Message: "[debug][task-execute-readme] END repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null>" emitted after step 6.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_directory: string (absolute path to repository root, echoed from input)
- readme_content: string | null (full text content of README file if found, null otherwise)
- readme_filename: string | null (name of matched README file, null if not found)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)

Implementation Notes (conceptual):
1. Detection: In PowerShell: `if($env:DEBUG -eq '1') { Write-Host "[debug][task-execute-readme] START repo_directory='$repoDirectory'" }`
2. Prioritization: Check filenames in exact order listed; first match wins.
3. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
4. Contract Compliance: Always return all four fields (repo_directory, readme_content, readme_filename, status) regardless of success/failure.
5. Progress Update: Mark [x] in repo-progress for task-execute-readme on both SUCCESS and FAIL (task completed, even if README not found).
6. Content Handling: Return entire file content; do not truncate or summarize at this stage.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
