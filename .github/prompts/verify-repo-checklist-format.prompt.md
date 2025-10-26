---
temperature: 0.1
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

ALL {repo_name}_repo_checklist.md files MUST have this exact structure:

```markdown
# Task Checklist: {repo_name}

Repository: {repo_url}
Generated: {timestamp}

## Repo Tasks (Sequential Pipeline - Complete in Order)

- [ ] [MANDATORY #1] Clone repository to local directory @task-clone-repo
- [ ] [MANDATORY #2] Search for README file in repository @task-search-readme
- [ ] [CONDITIONAL - NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
- [ ] [CONDITIONAL - NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme
- [ ] [MANDATORY #3] Find all solution files in repository @task-find-solutions
- [ ] [MANDATORY #4] Generate solution-specific task sections in checklist @generate-solution-task-checklists

## Task Variables

Variables set by completed tasks:
- `repo_url`: {value}
- `clone_path`: {value}
- `repo_directory`: {value}
- `repo_name`: {value}
- `readme_content`: {value}
- `readme_filename`: {value}
- `commands_extracted`: {value}
- `executed_commands`: {value}
- `skipped_commands`: {value}
- `solutions_json`: {value}

## For Agents Resuming Work

**Next Action:** 
1. Check if all [MANDATORY] tasks are completed
2. If YES and {{readme_content}} is not blank and not NONE, execute @task-scan-readme
3. If {{commands_extracted}} is not blank and not NONE, execute @task-execute-readme
4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

**How to Execute:** Invoke the corresponding task prompt as defined in repo_tasks_list.md.

**Quick Reference:**
- [MANDATORY] tasks must be completed in numbered order
- [CONDITIONAL - NON-SCRIPTABLE] @task-scan-readme executes when readme_content is not blank and not NONE
- [CONDITIONAL - NON-SCRIPTABLE] @task-execute-readme executes when commands_extracted is not blank and not NONE
- Mark completed tasks with [x]

## Repo Variables Available

Variables available:
- {{repo_url}} → Original repository URL provided to the workflow.
- {{clone_path}} → Root folder where repositories are cloned.
...
```

**Step 3: Verify Each File Structure**

For each repo checklist file, verify:

**A. Header Section:**
- [ ] Line 1: Starts with `# Task Checklist: {repo_name}`
- [ ] Line 2: Empty line
- [ ] Line 3: Starts with `Repository: `
- [ ] Line 4: Starts with `Generated: ` (ISO 8601 timestamp)
- [ ] Line 5: Empty line

**B. Repo Tasks Section:**
- [ ] Section header: `## Repo Tasks (Sequential Pipeline - Complete in Order)`
- [ ] Empty line before section
- [ ] Empty line after section header
- [ ] Exactly 6 tasks listed in correct order:
  1. `- [ ] [MANDATORY #1] Clone repository to local directory @task-clone-repo`
  2. `- [ ] [MANDATORY #2] Search for README file in repository @task-search-readme`
  3. `- [ ] [CONDITIONAL - NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme`
  4. `- [ ] [CONDITIONAL - NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme`
  5. `- [ ] [MANDATORY #3] Find all solution files in repository @task-find-solutions`
  6. `- [ ] [MANDATORY #4] Generate solution-specific task sections in checklist @generate-solution-task-checklists`
- [ ] Empty line after tasks
- [ ] Tasks may be checked `[x]` or unchecked `[ ]`

**C. Task Variables Section:**
- [ ] Section header: `## Task Variables` (exact match)
- [ ] Empty line before section
- [ ] Empty line after section header
- [ ] Subheading: `Variables set by completed tasks:` (exact match)
- [ ] All 10 variables present in this exact order:
  1. `` `repo_url`: {value} ``
  2. `` `clone_path`: {value} ``
  3. `` `repo_directory`: {value} ``
  4. `` `repo_name`: {value} ``
  5. `` `readme_content`: {value} ``
  6. `` `readme_filename`: {value} ``
  7. `` `commands_extracted`: {value} ``
  8. `` `executed_commands`: {value} ``
  9. `` `skipped_commands`: {value} ``
  10. `` `solutions_json`: {value} ``
- [ ] Variable format: Backticks around variable name, colon separator, space, value
- [ ] Empty line after variables

**D. For Agents Resuming Work Section:**
- [ ] Section header: `## For Agents Resuming Work` (exact match)
- [ ] Empty line before section
- [ ] Empty line after section header
- [ ] Contains `**Next Action:**` subsection
- [ ] Contains `**How to Execute:**` subsection
- [ ] Contains `**Quick Reference:**` subsection
- [ ] Empty line after section

**E. Repo Variables Available Section:**
- [ ] Section header: `## Repo Variables Available` (exact match)
- [ ] Empty line before section
- [ ] Empty line after section header
- [ ] Contains variables documentation from repo_tasks_list.md
- [ ] Variables use `{{variable_name}}` format with double curly braces

**Step 4: Cross-File Consistency Check**

Compare all repo checklist files to ensure:

1. **Section Order Consistency:**
   - All files have sections in same order
   - No extra sections
   - No missing sections

2. **Task Variables Order:**
   - All 10 variables in exact same order across all files
   - Same variable naming (no typos)
   - Same format (backticks, colon, space)

3. **Task List Consistency:**
   - All 6 tasks in exact same order
   - Same task numbering (#1, #2, #3, #4)
   - Same labels (MANDATORY, CONDITIONAL - NON-SCRIPTABLE)
   - Same task directive names (@task-clone-repo, etc.)

4. **Formatting Consistency:**
   - Same number of empty lines between sections
   - Same markdown heading levels (##)
   - Same list formatting (- [ ] or - [x])
   - Same code formatting (backticks for variables)

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
