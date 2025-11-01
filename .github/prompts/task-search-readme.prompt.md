---
temperature: 0.0
---

@task-search-readme repo_directory={{repo_directory}} repo_name={{repo_name}}

Task name: task-search-readme

## Description:
This task searches for and reads the README documentation file from a repository's root directory. This is a simple file location and content extraction task that CAN be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-search-readme] START repo_directory='{{repo_directory}}'`

### Step 2 (MANDATORY)
Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

README Candidate Search: Performs case-insensitive search for README files in the repository root directory.
   - Search patterns to match (case-insensitive): README.md, README.txt, README.rst, README
   - On Windows: File system is case-insensitive by default
   - On Linux/Mac: Use case-insensitive file matching (e.g., glob with IGNORECASE or list all files and compare lowercased names)
   - Priority order if multiple matches found: .md > .txt > .rst > (no extension)

Pre-flight Checklist Verification:
    - Open `tasks/{{repo_name}}_repo_checklist.md`
    - Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
     * `{{readme_content}}`
     * `{{readme_filename}}`
    - If any token is missing or altered, restore it prior to continuing

### Step 3 (MANDATORY)
File Discovery: Searches repository root directory using case-insensitive matching; stops on first match found.
   - If DEBUG=1, print: `[debug][task-search-readme] searching for README files (case-insensitive)`
   - On first match, if DEBUG=1, print: `[debug][task-search-readme] found README file: {{matched_filename}}`

### Step 4 (MANDATORY)
Content Extraction: 
   - If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
   - If DEBUG=1, print: `[debug][task-search-readme] content length: {{content_length}} characters`
   - If no match found, content remains null
   - If DEBUG=1 and no match, print: `[debug][task-search-readme] no README file found in repository root`

### Step 5 (MANDATORY)
Structured Output: Save JSON object to output/{repo_name}_task2_search-readme.json with:
   - repo_directory: echoed from input
   - repo_name: echoed from input
   - readme_content: string if found, null otherwise
   - readme_filename: name of matched file, null if not found
   - status: SUCCESS if README found, FAIL if not found
   - timestamp: ISO 8601 format datetime when task completed

### Step 6 (MANDATORY)
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

### Step 7 (MANDATORY)
Result Tracking:
   - Append the result to:
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-search-readme | status | symbol (✓ or ✗)

### Step 8 (MANDATORY)
Repo Checklist Update:
   - Open `tasks/{{repo_name}}_repo_checklist.md`
   - Set `[x]` only on the `@task-search-readme` entry for the current repository
   - Do not modify other checklist items or other repositories' files

### Step 9 (MANDATORY)
Repo Variable Refresh:
   - Open `tasks/{{repo_name}}_repo_checklist.md` file
   - Confirm the `## Repo Variables Available` section still contains the expected templated tokens exactly as shown below:
     * `{{readme_content}}`
     * `{{readme_filename}}`
   - Update the following variables with the latest values produced by this task:
     * `{{readme_content}}`
     * `{{readme_filename}}`
   - Ensure each variable reflects the refresh results before saving the file

### Step 10 (MANDATORY)
DEBUG Exit Trace: If DEBUG=1, print:
   `[debug][task-search-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}`

## Output Contract:
- repo_directory: string (absolute path to repository root, echoed from input)
- repo_name: string (repository name, echoed from input)
- readme_content: string | null (full content of README file, null if not found)
- readme_filename: string | null (name of matched README file, null if not found)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)
- timestamp: string (ISO 8601 datetime when task completed)

## Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. **Case-Insensitive Search**: Use case-insensitive file matching to find README files (e.g., README.md, readme.md, Readme.MD all match)
3. Prioritization: If multiple README files found, prioritize by extension: .md > .txt > .rst > (no extension)
4. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
5. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
6. Content Handling: Return entire file content; do not truncate or summarize at this stage.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)
