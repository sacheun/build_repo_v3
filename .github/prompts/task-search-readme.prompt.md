---
temperature: 0.0
---

@task-search-readme checklist_path={{checklist_path}}

# Task name: task-search-readme

## Description
This task searches for and reads the README documentation file from a repository's root directory. This is a simple file location and content extraction task that CAN be implemented as a script.

## Execution Policy
**STRICT MODE ON**
- All steps are **MANDATORY**.
- **Verification (Step 7)** must **always** execute.
- If Step 7 fails, **re-run Steps 1–7** automatically (up to `max_verification_retries`).
- Never summarize or skip steps.
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
Load Variables From Checklist:
1. Resolve `checklist_path`; ensure file exists. If missing, set status=FAIL, emit JSON immediately, and skip remaining steps.
2. Open the checklist file; locate the `## Repo Variables Available` section.
3. Parse variable lines beginning with:
   * `- {{repo_directory}}`
   * `- {{repo_name}}`
4. Extract arrow (`→`) values (trim whitespace). These become authoritative `repo_directory` and `repo_name` for all subsequent steps.
5. If `repo_directory` value is blank, set preliminary status=FAIL (cannot attempt README search) but STILL continue with variable normalization (Steps 6–8) so the checklist stays consistent.

### Step 2 (MANDATORY)
README Candidate Search (conditional):
- If Step 2 produced status=FAIL due to missing repo_directory value: skip search, proceed with empty results (readme_filename/readme_content later set to NONE).
- Otherwise perform case-insensitive search in the authoritative repo_directory for README files.
  - Patterns: README.md, README.txt, README.rst, README (case-insensitive)
  - Priority order: .md > .txt > .rst > (no extension)

### Step 3 (MANDATORY)
File Discovery:
- Searches repository root directory using case-insensitive matching; stops on first match found.
- If DEBUG=1, print: `[debug][task-search-readme] searching for README files (case-insensitive)`
- On first match, if DEBUG=1, print: `[debug][task-search-readme] found README file: {{matched_filename}}`

### Step 4 (MANDATORY)
Content Extraction:
- If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
- If DEBUG=1, print: `[debug][task-search-readme] content length: {{content_length}} characters`
- If no match found, content remains null
- If DEBUG=1 and no match, print: `[debug][task-search-readme] no README file found in repository root`

### Step 5 (MANDATORY)
Structured Output:
Generate JSON only (no verification in this step) at: `./output/{{repo_name}}_task2_search-readme.json` including required fields below. `verification_errors` is emitted as an array (empty here) and may be populated in Step 7.

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

### Step 6 (MANDATORY)
Checklist Update & Variable Refresh (INLINE ONLY – POINTER MODEL):
1. Open `{{checklist_path}}`.
2. Mark the `@task-search-readme` task with `[x]` ONLY if final status after verification will be SUCCESS. Leave as `[ ]` on failure.
3. Within the SAME `## Repo Variables Available` block, update ONLY:
   * `- {{readme_content}}`
   * `- {{readme_filename}}`
4. NEVER move them outside the block or create a second block.
5. Do NOT modify `- {{repo_directory}}` or `- {{repo_name}}`.
6. POINTER STORAGE POLICY (no embedded README text):
   * On SUCCESS (README found):
     - `{{readme_filename}}` → `<actual filename>` (e.g. `README.md`)
     - `{{readme_content}}` → `output/{{repo_name}}_task2_search-readme.json (field=readme_content)`
   * On FAIL (not found or repo_directory blank):
     - `{{readme_filename}}` → NONE
     - `{{readme_content}}` → NONE
7. Always ensure exactly one `→` per line. Replace only the portion after the arrow; preserve leading `- {{token}}` verbatim.
8. If the line exists but is missing an arrow or has extra arrows, normalize to the correct single-arrow format.
9. If the line was inserted blank earlier (Step 2), overwrite its value here according to status.
10. **Inline Variable Policy:** Single authoritative block; no duplicates; no multi-line content.
11. If DEBUG=1, after updates print: `[debug][task-search-readme] checklist & pointer variables updated`.

### Step 7 (MANDATORY)
Verification (Post-Refresh):
Perform verification AFTER combined checklist update & variable refresh (Step 6). Load current checklist state and JSON (from Step 5) then populate `verification_errors` and adjust `status` if needed.

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

### Step 8 (MANDATORY)
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
4. Content Handling: JSON output stores full README content; checklist stores only a pointer (`output/{{repo_name}}_task2_search-readme.json (field=readme_content)`) not the content itself.
5. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
6. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
7. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)

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
