---
temperature: 0.0
---

@task-search-readme checklist_path={{checklist_path}}

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
- Required input parameters: checklist_path (absolute or relative path to `tasks/<repo_name>_repo_checklist.md`)
- Directory permissions for the resolved repo_directory (loaded from checklist)
- Authoritative values for repo_directory and repo_name are READ from variable lines inside the checklist file (`## Repo Variables Available`).

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
`[debug][task-search-readme] START checklist_path='{{checklist_path}}'`

### Step 2 (MANDATORY)
Load Authoritative Variables From Checklist:
1. Resolve `checklist_path`; ensure file exists. If missing, set status=FAIL and abort.
2. Open the checklist file; locate the `## Repo Variables Available` section.
3. Parse variable lines beginning with:
  * `- {{repo_directory}}`
  * `- {{repo_name}}`
4. Extract arrow (`→`) values (trim whitespace). These become authoritative `repo_directory` and `repo_name` for all subsequent steps.
5. If `repo_directory` value is blank, set status=FAIL (cannot continue) but still produce JSON output; do not attempt README search.
6. Ensure presence (may be blank) of lines for:
  * `- {{readme_content}}`
  * `- {{readme_filename}}`
  Insert blank (`- {{token}} →`) if missing; mark status=FAIL unless corrected later.
7. If DEBUG=1 print: `[debug][task-search-readme] loaded repo_directory='{repo_directory}' repo_name='{repo_name}' from checklist`.
8. External parameters for repo_directory/repo_name MUST be ignored; checklist is single source of truth.

### Step 3 (MANDATORY)
README Candidate Search (conditional):
- If Step 2 produced status=FAIL due to missing repo_directory value: skip search, proceed with empty results (readme_filename/readme_content later set to NONE).
- Otherwise perform case-insensitive search in the authoritative repo_directory for README files.
  - Patterns: README.md, README.txt, README.rst, README (case-insensitive)
  - Priority order: .md > .txt > .rst > (no extension)

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
Verification & Structured Output:
Run verification BEFORE writing JSON. Any violation sets status=FAIL unless already FAIL.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for:
  - `- {{repo_directory}}` (non-empty if status not FAIL)
  - `- {{repo_name}}` (non-empty)
3. Mutable variable lines exist (may be blank prior to refresh):
  - `- {{readme_content}}`
  - `- {{readme_filename}}`
4. If status=SUCCESS (README found):
  - `readme_filename` not null and not NONE.
  - `readme_content` length > 0.
5. If status=FAIL due to missing repo_directory: ensure `readme_filename` and `readme_content` will be null in JSON.
6. No duplicate variable lines for repo_directory or repo_name (case-insensitive).
7. Task directive line `@task-search-readme` appears exactly once.
8. Arrow formatting correct: each variable line uses `- {{token}} → value` (report if arrow missing).

Record each failure as object: `{ "type": "<code>", "target": "<file|repo>", "detail": "<description>" }` in `verification_errors`.
If DEBUG=1 emit: `[debug][task-search-readme][verification] FAIL code=<code> detail="<description>"` per violation.

Structured Output JSON (output/{{repo_name}}_task2_search-readme.json) MUST include:
- repo_directory
- repo_name
- readme_content (string|null)
- readme_filename (string|null)
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 UTC seconds precision)
- verification_errors (array, empty if none)
- debug (optional array when DEBUG=1)

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
- Open `{{checklist_path}}`
- Set `[x]` only on the `@task-search-readme` entry for this repository
- Do not modify other checklist items or other repositories' files

### Step 10 (MANDATORY)
Repo Variable Refresh (INLINE ONLY):
- Open checklist file at `{{checklist_path}}`.
- Locate lines under `## Repo Variables Available` beginning with:
  * `- {{readme_content}}`
  * `- {{readme_filename}}`
- Do NOT modify lines for `- {{repo_directory}}` or `- {{repo_name}}` (immutable for this task).
- Replace ONLY the text after the arrow `→` on each mutable line with the concrete value from this task's output JSON. If the line has no arrow, append one: `- {{token}} → <value>`.
- Large README content: store either the first 200 characters + `...` suffix OR the literal string `EMPTY` if no README found (never null in JSON but reflected as NONE in checklist if not found).
- If README was not found (status=FAIL) OR repo_directory missing:
  * `{{readme_content}}` → NONE
  * `{{readme_filename}}` → NONE
- Example transformation:
  * `- {{readme_filename}} → README.md`
  * `- {{readme_content}} → # Project Title...`
- Preserve leading `- {{token}}` exactly.
**Inline Variable Policy:** Never add a secondary "refreshed" block; all updates must occur on original lines.

### Step 11 (MANDATORY)
DEBUG Exit Trace:  
If DEBUG=1, print:  
`[debug][task-search-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}`

## Output Contract
- repo_directory: string (absolute path to repository root loaded from checklist)
- repo_name: string (repository name loaded from checklist)
- readme_content: string | null (full content of README file, null if not found or repo_directory missing)
- readme_filename: string | null (name of matched README file, null if not found or repo_directory missing)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found or repo_directory missing)
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
- Always reference the latest values loaded from the checklist (Step 2); do not use stale external parameters.
- Variables involved in this task:
  - repo_directory (absolute path loaded from checklist)
  - repo_name (loaded from checklist variable line)
  - readme_content (full README text or null)
  - readme_filename (discovered README filename or null)
  - timestamp (ISO 8601 time when task completed)
- When updating checklist variables, ensure written values match output JSON (with truncation rules for readme_content).
