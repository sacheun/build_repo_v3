---
temperature: 0.0
---

@task-search-readme repo_directory={{repo_directory}} repo_name={{repo_name}}

# Task name: task-search-readme

## Process Overview
1. Debug Entry Trace
2. Input Parameter Extraction & Checklist Verification
3. README Candidate Search
4. File Discovery
5. Content Extraction
6. Structured Output
7. Log to Decision Log
8. Result Tracking
9. Repo Checklist Update
10. Repo Variable Refresh
11. Debug Exit Trace

## Prerequisites
- Python 3.x installed (if scripting)
- Directory permissions for repo_directory
- Required input parameters: repo_directory (absolute path), repo_name

## Description
This task searches for and reads the README documentation file from a repository's root directory. This is a simple file location and content extraction task that CAN be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**  
**DO NOT SKIP OR SUMMARIZE.**  
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
DEBUG Entry Trace:  
If DEBUG=1, print:  
`[debug][task-search-readme] START repo_directory='{{repo_directory}}'`

### Step 2 (MANDATORY)
Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

Pre-flight Checklist Verification:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  * `{{readme_content}}`
  * `{{readme_filename}}`
- If any token is missing or altered, restore it prior to continuing

### Step 3 (MANDATORY)
README Candidate Search:
- Performs case-insensitive search for README files in the repository root directory.
  - Search patterns to match (case-insensitive): README.md, README.txt, README.rst, README
  - On Windows: File system is case-insensitive by default
  - On Linux/Mac: Use case-insensitive file matching (e.g., glob with IGNORECASE or list all files and compare lowercased names)
  - Priority order if multiple matches found: .md > .txt > .rst > (no extension)

### Step 4 (MANDATORY)
File Discovery:
- Searches repository root directory using case-insensitive matching; stops on first match found.
- If DEBUG=1, print: `[debug][task-search-readme] searching for README files (case-insensitive)`
- On first match, if DEBUG=1, print: `[debug][task-search-readme] found README file: {{matched_filename}}`

### Step 5 (MANDATORY)
Content Extraction:
- If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
- If DEBUG=1, print: `[debug][task-search-readme] content length: {{content_length}} characters`
- If no match found, content remains null
- If DEBUG=1 and no match, print: `[debug][task-search-readme] no README file found in repository root`

### Step 6 (MANDATORY)
Structured Output:
- Save JSON object to output/{{repo_name}}_task2_search-readme.json with:
  - repo_directory: echoed from input
  - repo_name: echoed from input
  - readme_content: string if found, null otherwise
  - readme_filename: name of matched file, null if not found
  - status: SUCCESS if README found, FAIL if not found
  - timestamp: ISO 8601 format datetime when task completed

#### Example Output
```json
{
  "repo_directory": "/home/user/repos/repo",
  "repo_name": "repo",
  "readme_content": "# Project Title

This is the README.",
  "readme_filename": "README.md",
  "status": "SUCCESS",
  "timestamp": "2025-11-02T21:35:48Z"
}
```

### Step 7 (MANDATORY)
Log to Decision Log:
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

### Step 8 (MANDATORY)
Result Tracking:
- Append the result to:
  - results/repo-results.csv (CSV row)
- Row format: timestamp, repo_name, task-search-readme, status, symbol (✓ or ✗)

#### Example CSV Row
```
2025-11-02T21:35:48Z,repo,task-search-readme,SUCCESS,✓
```

### Step 9 (MANDATORY)
Repo Checklist Update:
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-search-readme` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 10 (MANDATORY)
Repo Variable Refresh (INLINE ONLY):
- Open `tasks/{{repo_name}}_repo_checklist.md`.
- Locate lines under `## Repo Variables Available` beginning with:
  * `- {{readme_content}}`
  * `- {{readme_filename}}`
- Do NOT create a new section or duplicate these tokens; you must update inline only.
- Replace ONLY the text after the arrow `→` on each line with the concrete value from this task's output JSON. If the line has no arrow, append one: `- {{token}} → <value>`.
- Large README content: store either the first 200 characters + `...` suffix or the literal string `EMPTY` if no README found (never null). This prevents checklist bloat.
- If README was not found (status=FAIL), set:
  * `{{readme_content}}` → NONE
  * `{{readme_filename}}` → NONE
- Example transformation:
  * `- {{readme_filename}} → README.md` (previous placeholder replaced)
  * `- {{readme_content}} → # Project Title...` (truncated preview)
- Preserve the leading `- {{token}}` portion exactly for future tasks.
**Inline Variable Policy:** Never add a secondary "refreshed" block; all updates must occur on the original lines.

### Step 11 (MANDATORY)
DEBUG Exit Trace:  
If DEBUG=1, print:  
`[debug][task-search-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}`

## Output Contract
- repo_directory: string (absolute path to repository root, echoed from input)
- repo_name: string (repository name, echoed from input)
- readme_content: string | null (full content of README file, null if not found)
- readme_filename: string | null (name of matched README file, null if not found)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)
- timestamp: string (ISO 8601 datetime when task completed)

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. **Case-Insensitive Search**: Use case-insensitive file matching to find README files (e.g., README.md, readme.md, Readme.MD all match)
3. Prioritization: If multiple README files found, prioritize by extension: .md > .txt > .rst > (no extension)
4. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
5. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
6. Content Handling: Return entire file content; do not truncate or summarize at this stage.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)

## Error Handling
- For any step that fails:
  - Log the error with details (stdout, stderr, exception message)
  - Abort further steps if critical (e.g., file read fails)
  - Do not update checklist or results CSV on failure

## Consistency Checks
- After updating files (checklist, results CSV, output JSON), verify that the changes were written successfully.
- If verification fails, log an error and abort.

## Cross-References
- Always reference the latest values produced in earlier steps (never reuse stale cached values).
- Variables involved in this task:
  - repo_directory (absolute path to repository root)
  - repo_name (derived or provided repository name)
  - readme_content (full README text or null)
  - readme_filename (discovered README filename or null)
  - timestamp (ISO 8601 time when task completed)
- When updating checklist variables, ensure the written values match the output JSON exactly.
