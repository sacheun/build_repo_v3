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

### Step 4 (MANDATORY)
Content Extraction:
- If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)

### Step 5 (MANDATORY)
Structured Output JSON:
Generate JSON at: `output/{{repo_name}}_task2_search-readme.json` including required fields below.

Structured Output JSON at `(output/{{repo_name}}_task2_search-readme.json)` MUST include:
- repo_directory
- repo_name
- readme_content (string|null)
- readme_filename (string|null)
- status (SUCCESS|FAIL)
- timestamp (ISO 8601 UTC seconds precision)

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

### End of Steps

## Output Contract
- `repo_directory`: string (absolute path to repository root loaded from checklist)
- `repo_name`: string (repository name loaded from checklist)
- `readme_content`: string | null (full content of README file, null if not found or `repo_directory` missing)
- `readme_filename`: string | null (name of matched README file, null if not found or `repo_directory` missing)
- `status`: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found or `repo_directory` missing)
- `timestamp`: string (ISO 8601 datetime when task completed)

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. **Case-Insensitive Search**: Use case-insensitive file matching to find README files (e.g., README.md, readme.md, Readme.MD all match)
3. Prioritization: If multiple README files found, prioritize by extension: .md > .txt > .rst > (no extension)
4. Content Handling: JSON output stores full README content; checklist stores only a pointer (`output/{{repo_name}}_task2_search-readme.json (field=readme_content)`) not the content itself.
5. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
6. Script Location: Save generated script to `temp-script/` directory with naming pattern: `step{N}_repo{M}_task2_search-readme.py` (or .ps1/.sh)