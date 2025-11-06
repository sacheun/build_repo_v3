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
11. Verification (Post-Refresh)
12. Debug Exit Trace

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
Load Authoritative Variables From Checklist (and self-heal missing README variable lines):
1. Resolve `checklist_path`; ensure file exists. If missing, set status=FAIL, emit JSON immediately, and skip remaining steps.
2. Open the checklist file; locate the `## Repo Variables Available` section. Treat the lines from that heading up to (but not including) the next `## ` heading as the SINGLE authoritative variable block.
3. Parse variable lines beginning with:
   * `- {{repo_directory}}`
   * `- {{repo_name}}`
4. Extract arrow (`→`) values (trim whitespace). These become authoritative `repo_directory` and `repo_name` for all subsequent steps.
5. If `repo_directory` value is blank, set preliminary status=FAIL (cannot attempt README search) but STILL continue with variable normalization (Steps 6–8) so the checklist stays consistent.
6. REQUIRED README variable lines: ensure exactly one line each for:
   * `- {{readme_content}}`
   * `- {{readme_filename}}`
   If either is missing OR present with single braces (e.g. `- {readme_content}`), INSERT/REWRITE them INSIDE the variable block (never after the definitions section) using blank placeholders:
   * `- {{readme_content}} →`
   * `- {{readme_filename}} →`
  Insertion position rule: place them immediately after the line starting with - {{repo_directory}}; if that line is missing, append them at the end of the variable block (just before the next ## heading).
7. Do NOT mark status=FAIL solely because they were missing; self-healing insertion is expected behavior. Failure status is driven only by README discovery or a missing `repo_directory` value.
8. Normalize legacy single-brace variants to the double-brace canonical form (`{{token}}`).
9. If DEBUG=1 print: `[debug][task-search-readme] loaded repo_directory='{repo_directory}' repo_name='{repo_name}' from checklist`.
10. External parameters for repo_directory/repo_name MUST be ignored; checklist is single source of truth.

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
Structured Output:
Generate JSON only (no verification in this step) at: `output/{{repo_name}}_task2_search-readme.json` including required fields below. `verification_errors` is emitted as an array (empty here) and may be populated in Step 11.

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
- Open `{{checklist_path}}`.
- Mark the `@task-search-readme` task with `[x]` ONLY if final status after verification will be SUCCESS. Leave as `[ ]` on failure.
- Do not modify other checklist tasks.
- Never duplicate the directive line.

### Step 10 (MANDATORY)
Repo Variable Refresh (INLINE ONLY – POINTER MODEL):
- Within the SAME variable block, update ONLY:
  * `- {{readme_content}}`
  * `- {{readme_filename}}`
- NEVER move them outside the block or create a second block.
- Do NOT modify `- {{repo_directory}}` or `- {{repo_name}}`.
- POINTER STORAGE POLICY (no embedded README text):
  * On SUCCESS (README found):
    - `{{readme_filename}}` → `<actual filename>` (e.g. `README.md`)
    - `{{readme_content}}` → `output/{{repo_name}}_task2_search-readme.json (field=readme_content)`
  * On FAIL (not found or repo_directory blank):
    - `{{readme_filename}}` → NONE
    - `{{readme_content}}` → NONE
- Always ensure exactly one `→` per line. Replace only the portion after the arrow; preserve leading `- {{token}}` verbatim.
- If the line exists but is missing an arrow or has extra arrows, normalize to the correct single-arrow format.
- If the line was inserted blank earlier (Step 2), overwrite its value here according to status.
**Inline Variable Policy:** Single authoritative block; no duplicates; no multi-line content.

### Step 11 (MANDATORY)
Verification (Post-Refresh):
Perform verification AFTER checklist update (Step 9) and variable refresh (Step 10). Load current checklist state and JSON (from Step 6) then populate `verification_errors` and adjust `status` if needed.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for (case-sensitive tokens):
  - `- {{repo_directory}}` (non-empty unless original status FAIL due to missing directory)
  - `- {{repo_name}}` (non-empty)
  - `- {{readme_content}}` (present; value may be NONE)
  - `- {{readme_filename}}` (present; value may be NONE)
3. Arrow formatting: each variable line uses single `→`.
4. No duplicate variable lines for repo_directory or repo_name.
5. Task directive line `@task-search-readme` appears exactly once.
6. If status=SUCCESS in JSON:
  - JSON `readme_filename` not null/NONE.
  - JSON `readme_content` length > 0.
7. If status=FAIL due to missing repo_directory (detect by empty repo_directory value in checklist and null JSON fields): ensure JSON `readme_filename` and `readme_content` are null.
8. Checklist variable refresh coherence:
  - If README found: checklist `readme_filename` matches JSON `readme_filename`.
  - If README not found: checklist values are NONE.
9. JSON required keys present: repo_directory, repo_name, readme_content, readme_filename, status, timestamp.
10. Results CSV row present and correctly formatted for this task execution (pattern: `{{timestamp}},{{repo_name}},task-search-readme,{{status}},✓|✗`).

Violations recorded as objects: `{ "type": "<code>", "target": "<file|variable|json>", "detail": "<description>" }`.
Recommended codes: file_missing, variable_missing, variable_empty, duplicate_variable, arrow_format_error, mismatch_filename, content_missing, json_missing_key, invalid_status_consistency, results_row_missing.

Status Adjustment:
- Start with existing JSON status.
- If status=SUCCESS and any violations → set status=FAIL (do not alter original success criteria fields).
- If status already FAIL leave unchanged.

Update JSON in-place: overwrite `verification_errors` (sorted by type then target) and `status` (if changed). Preserve original timestamp.

### Step 12 (MANDATORY)
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
6. Content Handling: JSON output stores full README content; checklist stores only a pointer (`output/{{repo_name}}_task2_search-readme.json (field=readme_content)`) not the content itself.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)

## Error Handling
- For a missing checklist file: emit JSON with status=FAIL, a `file_missing` violation, and skip Steps 3–12.
- For missing `repo_directory` value: proceed with variable self-heal; skip README search but still emit JSON, update checklist variables to NONE, and perform verification.
- For README not found: status=FAIL but still update checklist (variables set to NONE) and record decision log + CSV row.
- For file read errors after discovery: treat as status=FAIL, set content to null, still perform Steps 7–11.
- Always append the CSV row and decision log entry regardless of success/failure to maintain audit trail.

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
- When updating checklist variables, ensure pointer format or NONE matches status (never embed or truncate content in checklist).
