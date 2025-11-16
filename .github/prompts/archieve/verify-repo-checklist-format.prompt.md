---
temperature: 0.0
---

@verify-repo-checklist-format

Task name: verify-repo-checklist-format

## Description:
This task verifies that a single checklist file (either a repository or solution checklist) follows the canonical structure and formatting rules. It enforces the correct section headers, task syntax, and variable formatting so downstream automation can rely on the content.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Reads the checklist file supplied via CLI argument
2. Detects whether the file is a repository or solution checklist
3. Parses the file line-by-line to validate structure
4. Uses regex and string matching to verify formatting rules per checklist type
5. Generates detailed markdown and JSON reports
6. Returns PASS/FAIL status with specific issues found

## Behavior (Follow this Step by Step)

**Step 1: Identify Checklist Type**
1. Accept a required CLI argument `--checklist <path>` (absolute or relative).
2. Validate that the path exists and points to a `.md` file.
3. Determine checklist type:
  - If filename ends with `_repo_checklist.md` → type = `repo`.
  - If filename ends with `_solution_checklist.md` → type = `solution`.
4. If neither suffix matches, report an error and exit with failure.

**Step 2: Define Expected Format Requirements**

The verification script must enforce the canonical structure while remaining flexible about how many tasks or variables appear. Section expectations depend on the detected checklist type.

### Common Header Requirements

1. **Header block**
  ```markdown
  # Task Checklist: {repo_name}
  Repository: {repo_url}
  Generated: {timestamp}
  ```
  - `Generated` must use ISO-8601 format (e.g., `2025-11-14T23:59:12Z`).
  - Allow optional blank lines between header lines but do not allow other content before the header.

### Repository Checklist Sections (`_repo_checklist.md`)

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

### Solution Checklist Sections (`_solution_checklist.md`)

2. **`## Solution Tasks (Sequential Pipeline - Complete in Order)` section**
  - Task line pattern is identical to repository task validation (checkbox, sequential numbering, `[TAG]` blocks, arrow, `@task-handle`).
  - Task descriptions may differ; do not hardcode names.

3. **`## Solution Variables` section**
  - Each variable line must match `- {{variable_name}} → value`.
  - Variable names must be lowercase snake_case (`[a-z0-9_]+`).
  - Values may be blank; treat `(blank)` or empty strings as valid content.

4. **Optional Sections** — Additional sections after the variables block (e.g., instructions) are permitted but should not disrupt the validated sections above. Record unexpected mandatory sections as warnings, not failures.

**Step 3: Verify Each File Structure**

For the provided checklist file, perform these checks according to its type:

**A. Header Block**
- [ ] File starts with `# Task Checklist:`.
- [ ] `Repository:` line appears before the first blank line after the header.
- [ ] `Generated:` line matches regex `^Generated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.

**B. Tasks Section**
- Repository checklist: Heading must be `## Repo Tasks (Sequential Pipeline - Complete in Order)`.
- Solution checklist: Heading must be `## Solution Tasks (Sequential Pipeline - Complete in Order)`.
- All task lines match the pattern in Step 2.
- Task numbers are sequential (1..N with no gaps or duplicates).
- Task handles are unique within the file.

**C. Variables Section**
- Repository checklist: Heading must be `## Repo Variables Available`.
- Solution checklist: Heading must be `## Solution Variables`.
- Variable lines follow `- {{name}} → value` with valid snake_case names.
- Variable names are unique within the file.

**D. Additional Sections (Repo only)**
- When checklist type is repository, ensure:
  - `## For Agents Resuming Work` exists with at least one ordered list item (`^[0-9]+\.`).
  - `## Execution Notes` exists with at least one bullet line starting with `- `.
- When checklist type is solution, record presence of extra sections but do not fail unless they break ordering/formatting rules.

**Step 4: Cross-File Consistency Check**

If validating multiple files in a single run (optional enhancement), track consistency across files of the same type:

1. **Section Order** — Sections defined above appear once and in the same order across all files of a given type.
2. **Task Formatting** — Task numbering is sequential in every file; tag and handle syntax is valid everywhere.
3. **Variable Formatting** — All variables follow the `- {{name}} → value` pattern. When files share the same set of variable names, enforce identical ordering; otherwise, report mismatches.
4. **Arrow Usage** — Only `→` or `->` arrows are used in task and variable lines.

For single-file verification, record these checks as `PASS`/`N/A` as appropriate.

**Step 5: Generate Verification Report**

Create a detailed report showing (adapt the labels based on checklist type):

```markdown
# Checklist Format Verification Report

Generated: {timestamp}
Files Verified: {count}
Checklist Type: {repo|solution|mixed}

## Summary

- ✅ Total Files Checked: {count}
- ✅ Files Passing All Checks: {pass_count}
- ❌ Files With Issues: {fail_count}
- Overall Status: PASS | FAIL

## Individual File Results

### File: ic3_spool_cosine-dep-spool_repo_checklist.md (repo)
- ✅ Header Section: PASS
- ✅ Repo Tasks Section: PASS (6 tasks found)
- ✅ Repo Variables Section: PASS (10 variables in correct order)
- ✅ For Agents Resuming Work Section: PASS
- ✅ Execution Notes Section: PASS
- **Status: PASS**

### File: sdk_solution.sln_solution_checklist.md (solution)
- ✅ Header Section: PASS
- ❌ Solution Variables Section: FAIL
  - Issue: Variable `solution_path` uses colon instead of arrow
- ✅ Solution Tasks Section: PASS (7 tasks found)
- **Status: FAIL**

## Consistency Check Results

- ✅ Section Order: All files have same section order
- ✅ Task Order: All 6 tasks in correct order across all files
- ❌ Variable Format: Inconsistent formatting detected
  - ic3_spool_cosine-dep-spool_repo_checklist.md: Uses arrows correctly
  - sdk_solution.sln_solution_checklist.md: Found `solution_path: value` format (should be arrow)

## Issues Found

1. **sdk_solution.sln_solution_checklist.md**
   - Line 18: Variable format error - expected `- {{solution_path}} → ...`

## Recommendations

- Fix formatting issues in people_spool_usertokenmanagement_repo_checklist.md
- Re-run verification after fixes
- Consider using template generation to prevent future inconsistencies

## Verification Details

Checked:
- ✅ 3 checklist files (repo + solution)
- ✅ Header structure (5 lines)
- ✅ Required section headers present
- ✅ Task list numbering validated
- ✅ Variable list formatting validated
- ✅ Variable order consistency
- ✅ Section order consistency
```

**Step 6: Output Results**

1. Print verification report to console
2. Save report to: `results/checklist-format-verification.md`
3. Save JSON summary to: `output/verify-checklist-format.json`

JSON Output Contract:
```json
{
  "task": "verify-checklist-format",
  "timestamp": "2025-10-26T03:30:00.000000+00:00",
  "files_checked": 2,
  "files_passed": 1,
  "files_failed": 1,
  "overall_status": "FAIL",
  "files": [
    {
      "filename": "ic3_spool_cosine-dep-spool_repo_checklist.md",
      "type": "repo",
      "status": "PASS",
      "issues": []
    },
    {
      "filename": "sdk_solution.sln_solution_checklist.md",
      "type": "solution",
      "status": "FAIL",
      "issues": [
        {
          "section": "Solution Variables",
          "line": 18,
          "issue": "Expected arrow format",
          "expected": "- {{solution_path}} → ...",
          "actual": "- solution_path: ..."
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

- files_checked: integer (number of checklist files verified)
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
9. **Script Location**: Save generated script to temp-script/ directory with naming pattern: verify_checklist_format.py (or .ps1)
