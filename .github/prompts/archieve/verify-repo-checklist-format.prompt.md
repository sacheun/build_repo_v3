---
temperature: 0.0
---

@verify-repo-checklist-format

Task name: verify-repo-checklist-format

## Description:
This task verifies that all {repo_name}_repo_checklist.md files in the tasks/ directory follow the exact same format and structure. It checks for consistency in section headers, variable formatting, and overall structure to ensure LLM can reliably parse all checklist files during autonomous execution.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Reads all *_repo_checklist.md files from tasks/ directory
2. Parses each file line-by-line to validate structure
3. Uses regex and string matching to verify formatting
4. Compares files to check cross-file consistency
5. Generates detailed markdown and JSON reports
6. Returns PASS/FAIL status with specific issues found

## Behavior (Follow this Step by Step)

**Step 1: Discover All Repo Checklist Files**
1. Search the tasks/ directory for all files matching pattern: *_repo_checklist.md
2. Exclude the master checklist: all_repository_checklist.md
3. List all found repository checklist files
4. If no files found, report error and exit

**Step 2: Define Expected Format Requirements**

The verification script must enforce the canonical structure while remaining flexible about how many tasks or variables appear. All `{repo_name}_repo_checklist.md` files must include the following sections in this order:

1. **Header block**
  ```markdown
  # Task Checklist: {repo_name}
  Repository: {repo_url}
  Generated: {timestamp}
  ```
  - `Generated` must use ISO-8601 format (e.g., `2025-11-14T23:59:12Z`).
  - Allow optional blank lines between header lines but do not allow other content before the header.

2. **`## Repo Tasks (Sequential Pipeline - Complete in Order)` section**
  - Each task line must match the pattern:
    ```text
    - [x] (N) [TAG] ... → @task-handle
    - [ ] (N) [TAG] ... → @task-handle
    ```
    Requirements:
     * Checkbox is either `[ ]` or `[x]`.
     * `(N)` is a positive integer. Numbers must begin at 1 and increment by 1 without gaps.
     * One or more `[TAG]` blocks may appear; tags are uppercase words separated by spaces (e.g., `[MANDATORY] [SCRIPTABLE]`).
     * Description text is freeform but must precede the arrow.
     * Arrow may be Unicode `→` or ASCII `->`.
     * Task handle must match `@task-[a-z0-9\-]+`.
  - Additional tasks are allowed; do not hardcode specific descriptions.

3. **`## Repo Variables Available` section**
  - Each variable line must match `- {{variable_name}} → value`.
  - Variable names must be lowercase snake_case (`[a-z0-9_]+`).
  - Values may be blank; treat `(blank)` or empty strings as valid content.

4. **`## For Agents Resuming Work` section**
  - Section must contain at least one ordered list item (line starting with `1.`).
  - Additional paragraphs or bullet points allowed.

5. **`## Execution Notes` section**
  - Section must contain at least one bullet line starting with `- `.
  - Bullet text should mention which tasks are SCRIPTABLE vs NON-SCRIPTABLE.

No other sections should appear unless future templates require them; flag unexpected sections.

**Step 3: Verify Each File Structure**

For each repo checklist file, perform these checks:

**A. Header Block**
- [ ] File starts with `# Task Checklist:`.
- [ ] `Repository:` line appears before the first blank line after the header.
- [ ] `Generated:` line matches regex `^Generated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.

**B. Repo Tasks Section**
- [ ] Section heading exactly equals `## Repo Tasks (Sequential Pipeline - Complete in Order)`.
- [ ] All task lines match the pattern in Step 2.
- [ ] Task numbers are sequential (1..N with no gaps or duplicates).
- [ ] Task handles are unique within the file.

**C. Repo Variables Section**
- [ ] Section heading exactly equals `## Repo Variables Available`.
- [ ] Variable lines follow `- {{name}} → value` with valid snake_case names.
- [ ] Variable names are unique within the file.

**D. For Agents Resuming Work Section**
- [ ] Section heading exactly equals `## For Agents Resuming Work`.
- [ ] Section contains at least one ordered list item (`^[0-9]+\.`).

**E. Execution Notes Section**
- [ ] Section heading exactly equals `## Execution Notes`.
- [ ] Section contains at least one bullet line starting with `- `.

**Step 4: Cross-File Consistency Check**

Compare all repo checklist files to ensure:

1. **Section Order** — Sections defined above appear once and in the same order across files.
2. **Task Formatting** — Task numbering is sequential in every file; tag and handle syntax is valid everywhere.
3. **Variable Formatting** — All variables follow the `- {{name}} → value` pattern. When files share the same set of variable names, enforce identical ordering; otherwise, report mismatches.
4. **Arrow Usage** — Only `→` or `->` arrows are used in task and variable lines.

**Step 5: Generate Verification Report**

Create a detailed report showing:

```markdown
# Repo Checklist Format Verification Report

Generated: {timestamp}
Files Verified: {count}

## Summary

- ✅ Total Files Checked: {count}
- ✅ Files Passing All Checks: {pass_count}
- ❌ Files With Issues: {fail_count}
- Overall Status: PASS | FAIL

## Individual File Results

### File: ic3_spool_cosine-dep-spool_repo_checklist.md
- ✅ Header Section: PASS
- ✅ Repo Tasks Section: PASS (6 tasks found)
- ✅ Task Variables Section: PASS (10 variables in correct order)
- ✅ For Agents Resuming Work Section: PASS
- ✅ Repo Variables Available Section: PASS
- **Status: PASS**

### File: people_spool_usertokenmanagement_repo_checklist.md
- ✅ Header Section: PASS
- ❌ Task Variables Section: FAIL
  - Issue: Variable 'repo_url' missing backticks
  - Issue: Variable order incorrect (clone_path before repo_url)
- ✅ For Agents Resuming Work Section: PASS
- ✅ Repo Variables Available Section: PASS
- **Status: FAIL**

## Consistency Check Results

- ✅ Section Order: All files have same section order
- ✅ Task Order: All 6 tasks in correct order across all files
- ❌ Variable Format: Inconsistent formatting detected
  - ic3_spool_cosine-dep-spool: Uses backticks correctly
  - people_spool_usertokenmanagement: Missing backticks on 2 variables
  - sync_calling_concore-conversation: Uses backticks correctly

## Issues Found

1. **people_spool_usertokenmanagement_repo_checklist.md**
   - Line 23: Variable format error - missing backticks around `repo_url`
   - Line 24: Variable order error - clone_path should come before repo_url

## Recommendations

- Fix formatting issues in people_spool_usertokenmanagement_repo_checklist.md
- Re-run verification after fixes
- Consider using template generation to prevent future inconsistencies

## Verification Details

Checked:
- ✅ 3 repository checklist files
- ✅ Header structure (5 lines)
- ✅ Section headers (5 required sections)
- ✅ Task list (6 tasks expected)
- ✅ Variable list (10 variables expected)
- ✅ Variable formatting (backticks + colon)
- ✅ Variable order consistency
- ✅ Section order consistency
```

**Step 6: Output Results**

1. Print verification report to console
2. Save report to: `results/repo-checklist-format-verification.md`
3. Save JSON summary to: `output/verify-repo-checklist-format.json`

JSON Output Contract:
```json
{
  "task": "verify-repo-checklist-format",
  "timestamp": "2025-10-26T03:30:00.000000+00:00",
  "files_checked": 3,
  "files_passed": 2,
  "files_failed": 1,
  "overall_status": "FAIL",
  "files": [
    {
      "filename": "ic3_spool_cosine-dep-spool_repo_checklist.md",
      "status": "PASS",
      "issues": []
    },
    {
      "filename": "people_spool_usertokenmanagement_repo_checklist.md",
      "status": "FAIL",
      "issues": [
        {
          "section": "Task Variables",
          "line": 23,
          "issue": "Missing backticks around variable name",
          "expected": "`repo_url`",
          "actual": "repo_url"
        }
      ]
    }
  ],
  "consistency_checks": {
    "section_order": "PASS",
    "task_order": "PASS",
    "variable_order": "PASS",
    "variable_format": "FAIL"
  }
}
```

**Step 7: Return Status**

- If all files pass all checks: Return SUCCESS
- If any file has issues: Return FAIL with details
- Include count of issues found
- Include list of files needing fixes

## Output Contract:

- files_checked: integer (number of repo checklist files verified)
- files_passed: integer (files with no issues)
- files_failed: integer (files with format issues)
- overall_status: PASS | FAIL
- issues_found: array of issue objects with file, section, line, description
- consistency_status: object with boolean checks (section_order, task_order, variable_order, variable_format)
- report_path: string (path to markdown report)
- timestamp: string (ISO 8601 datetime)

## Implementation Notes:

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell script to execute this task
2. **Line-by-Line Analysis**: Read files and check exact line numbers and content
3. **String Matching**: Use exact string matching for section headers and variable names
4. **Regex for Patterns**: Use regex to validate format patterns (e.g., `` `variable`: value ``)
5. **Diff Comparison**: Compare files to find inconsistencies using data structures
6. **Detailed Reporting**: Provide line numbers and exact issues for easy fixing
7. **Idempotent**: Can be run multiple times to verify fixes
8. **No Modifications**: This task only reads and reports, never modifies files
9. **Script Location**: Save generated script to temp-script/ directory with naming pattern: verify_repo_checklist_format.py (or .ps1)
