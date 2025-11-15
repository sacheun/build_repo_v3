---
temperature: 0.0
---

@verify-repo-tasks-completed

Task name: verify-repo-tasks-completed

** THIS TASK IS SCRIPTABLE **

## Description:
Verify that all repository-level tasks have been completed successfully.
This checks:
1. All tasks in all *_repo_checklist.md files are marked with [x]
2. All task variables under "Variables set by completed tasks:" are properly set (not blank, not "NONE", not "N/A")
3. Each repository has a corresponding *_solution_checklist.md file
4. The repo_directory for each repository is not empty (directory exists and contains files)

If DEBUG=1, print detailed verification steps.

---

## Behavior (Follow this Step by Step)

1. **Find All Repository Checklists**
   • Search for all files matching `tasks/*_repo_checklist.md`
   • Extract repository names from filenames
   • Log count if DEBUG=1

2. **Verify Task Completion**
   For each repository checklist:
   • Read the markdown file
   • Find all task lines (lines containing `- [ ]` or `- [x]`)
   • Count total tasks
   • Count completed tasks (marked with `[x]`)
   • Identify any incomplete tasks (marked with `[ ]`)
   • Store results: {repo_name, total_tasks, completed_tasks, incomplete_tasks, all_completed: bool}
   • Log per-repo status if DEBUG=1

3. **Verify Task Variables Are Set**
   For each repository checklist:
   • Read the "Variables set by completed tasks:" section
   • Extract all variable assignments (lines with `- variable_name: value`)
   • For each variable, check if value is properly set:
     - NOT blank/empty
     - NOT "NONE" (case-insensitive)
     - NOT "N/A" (case-insensitive)
     - NOT "NOT_EXECUTED"
     - "SKIPPED" is ACCEPTABLE (indicates intentional skip with context)
   • Identify unset or invalid variables
   • Store results: {repo_name, total_variables, valid_variables, invalid_variables, all_variables_set: bool, invalid_variable_list: []}
   • Log per-repo status if DEBUG=1

4. **Verify Solution Checklist Exists**
   For each repository:
   • Check if file `tasks/{repo_name}_solution_checklist.md` exists
   • Store result: {repo_name, solution_checklist_exists: bool, solution_checklist_path}
   • Log status if DEBUG=1

5. **Verify Repository Directory**
   For each repository:
   • Read the repo checklist to extract `repo_directory` variable
   • Check if the directory exists
   • If exists, count files/subdirectories (non-empty check)
   • Store result: {repo_name, repo_directory, directory_exists: bool, is_empty: bool, file_count}
   • Log status if DEBUG=1

6. **Verify CSV Completeness**
   • Check if `results/repo_result.csv` exists
   • Expected: Exactly 1 row per task per repository (6 tasks per repo)
   • Parse CSV file (skip header row)
   • For each repository, verify all expected tasks are logged:
     - @task-clone-repo
     - @task-search-readme
     - @task-scan-readme
     - @task-execute-readme
     - @task-find-solutions
     - @generate-solution-task-checklists
   • Identify missing tasks (expected but not in CSV)
   • Identify duplicate tasks (same task logged multiple times)
   • Identify unexpected tasks (in CSV but not in expected list, check for naming issues like missing @ prefix)
   • Store result: {csv_exists, total_expected_rows, total_actual_rows, missing_rows, duplicate_rows, repositories_with_issues, all_rows_present, details: {repo_name: {expected_tasks, actual_tasks, missing_tasks, duplicate_tasks, unexpected_tasks, has_issues}}}
   • Log status if DEBUG=1

7. **Generate Verification Report**
   Create summary with:
   • Total repositories verified
   • Repositories with all tasks complete
   • Repositories with all variables set
   • Repositories missing solution checklists
   • Repositories with empty/missing directories
   • Overall status: PASS or FAIL
   • Detailed findings per repository

8. **Write Results**
   • Save markdown report to: `results/repo-tasks-verification.md`
   • Save JSON output to: `output/verify-repo-tasks-completed.json`
   • Log completion if DEBUG=1

---

## Output Contract
JSON saved to:  
`output/verify-repo-tasks-completed.json`

| Field | Type | Description |
|-------|------|-------------|
| total_repositories | integer | Number of repositories verified |
| repositories_verified | array | List of repository names checked |
| task_completion_summary | object | {repo_name: {total_tasks, completed_tasks, incomplete_tasks, all_completed}} |
| variable_validation_summary | object | {repo_name: {total_variables, valid_variables, invalid_variables, all_variables_set, invalid_variable_list}} |
| solution_checklist_summary | object | {repo_name: {exists, path}} |
| directory_summary | object | {repo_name: {directory, exists, is_empty, file_count}} |
| csv_completeness | object | {csv_exists, total_expected_rows, total_actual_rows, missing_rows, duplicate_rows, repositories_with_issues, all_rows_present, details} |
| repositories_passing | array | List of repos passing all checks |
| repositories_failing | array | List of repos failing any check |
| overall_status | string | PASS or FAIL |
| timestamp | string | ISO8601 timestamp |

---

## Verification Criteria

A repository PASSES if:
- All tasks in *_repo_checklist.md are marked [x]
- All task variables under "Variables set by completed tasks:" are properly set (not blank, not "NONE", not "N/A", not "NOT_EXECUTED"). Note: "SKIPPED" is acceptable as it indicates an intentional skip with context.
- A *_solution_checklist.md file exists
- The repo_directory exists and is not empty (contains at least 1 file/directory)
- All 6 expected tasks are logged in repo_result.csv with correct naming (@ prefix)

A repository FAILS if any of the above criteria is not met.

Overall status is PASS only if all repositories pass.

---

## Markdown Report Format

```markdown
# Repository Tasks Verification Report

Generated: {timestamp}

## Summary

- Total Repositories: {count}
- Repositories Passing: {count}
- Repositories Failing: {count}
- Overall Status: {PASS/FAIL}

## CSV Completeness Check

- CSV File: {EXISTS/MISSING}
- Expected Rows (6 tasks × {repo_count} repos): {count}
- Actual Rows: {count}
- Missing Rows: {count}
- Duplicate Rows: {count}
- All Rows Present: {YES/NO}

{If repositories_with_issues:}
**Repositories with CSV Issues:**
- {repo_name}:
  - Missing tasks: {list}
  - Duplicate tasks: {list}
  - Unexpected tasks: {list}

## Detailed Results

### Repository: {repo_name}
**Status: {PASS/FAIL}**

#### Task Completion
- Total Tasks: {count}
- Completed Tasks: {count}
- Incomplete Tasks: {count}
- All Tasks Complete: {YES/NO}
{List of incomplete tasks if any}

#### Task Variables
- Total Variables: {count}
- Valid Variables: {count}
- Invalid Variables: {count}
- All Variables Set: {YES/NO}
{List of invalid variables with their values if any}

#### Solution Checklist
- Exists: {YES/NO}
- Path: {path or N/A}

#### Repository Directory
- Path: {repo_directory}
- Exists: {YES/NO}
- Empty: {YES/NO}
- File Count: {count}

#### CSV Tracking
- Expected Tasks: 6
- Actual Tasks in CSV: {count}
- All Tasks Logged: {YES/NO}
{If issues:}
- Missing: {list}
- Duplicates: {list}
- Unexpected: {list}

---

{Repeat for each repository}
```

---

## Debug Logging (DEBUG=1)
Prefix: `[debug][verify-repo-tasks-completed]`

Log messages for:
• START (with search pattern)
• Found repository checklists
• Each repository verification (tasks, variables, solution checklist, directory)
• Summary statistics
• EXIT status

---

## Example Usage

```python
# Execute verification
python verify_repo_tasks_completed.py

# With debug output
DEBUG=1 python verify_repo_tasks_completed.py
```
