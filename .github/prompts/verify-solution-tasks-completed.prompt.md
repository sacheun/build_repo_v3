@verify-solution-tasks-completed

Task name: verify-solution-tasks-completed

** THIS TASK IS SCRIPTABLE **

## Description:
Verify that all solution-level tasks have been completed successfully.
This checks:
1. All tasks in all *_solutions_checklist.md files are marked with [x]
2. All solution variables under "Solution Variables" sections are properly set (not blank, not "NONE", not "N/A")
3. Each solution's mandatory tasks (#1 and #2) are completed
4. The solution_path for each solution exists

If DEBUG=1, print detailed verification steps.

---

## Behavior (Follow this Step by Step)

1. **Find All Solution Checklists**
   • Search for all files matching `tasks/*_solutions_checklist.md`
   • Extract repository names from filenames
   • Log count if DEBUG=1

2. **Parse Solution Checklists**
   For each solution checklist file:
   • Read the markdown file
   • Parse each solution section (starts with `## Solution N:`)
   • Extract solution metadata:
     - Solution number
     - Solution name
     - Solution path
   • Store solution list per repository
   • Log per-repository solution count if DEBUG=1

3. **Verify Task Completion**
   For each solution in each checklist:
   • Find all task lines (lines containing `- [ ]` or `- [x]`)
   • Count total tasks
   • Count completed tasks (marked with `[x]`)
   • Identify incomplete tasks (marked with `[ ]`)
   • Check if mandatory tasks (#1 and #2) are completed
   • Store results: {repo_name, solution_name, total_tasks, completed_tasks, incomplete_tasks, all_completed: bool, mandatory_completed: bool}
   • Log per-solution status if DEBUG=1

4. **Verify Solution Variables Are Set**
   For each solution in each checklist:
   • Read the "Solution Variables" section for that solution
   • Extract all variable assignments (lines with `- variable_name → value`)
   • For each variable, check if value is properly set:
     - NOT blank/empty
     - NOT "NONE" (case-insensitive)
     - NOT "N/A" (case-insensitive)
     - NOT "NOT_EXECUTED"
     - "SKIPPED" is ACCEPTABLE (indicates intentional skip with context)
     - "SUCCESS" is ACCEPTABLE
     - "FAILED" is ACCEPTABLE (indicates task was executed, even if unsuccessful)
   • Identify unset or invalid variables
   • Store results: {repo_name, solution_name, total_variables, valid_variables, invalid_variables, all_variables_set: bool, invalid_variable_list: []}
   • Log per-solution status if DEBUG=1

5. **Verify Solution Path Exists**
   For each solution:
   • Extract the `solution_path` variable value
   • Check if the .sln file exists at that path
   • Store result: {repo_name, solution_name, solution_path, path_exists: bool}
   • Log status if DEBUG=1

6. **Verify CSV Completeness**
   • Check if `results/solution_result.csv` exists
   • Expected: At least 2 rows per solution (restore + build tasks minimum)
   • Parse CSV file (skip header row)
   • For each solution, verify expected tasks are logged:
     - @task-restore-solution (MANDATORY)
     - @task-build-solution (MANDATORY)
     - @task-search-knowledge-base (CONDITIONAL)
     - @task-create-knowledge-base (CONDITIONAL)
     - @task-apply-knowledge-base-fix (CONDITIONAL, may appear up to 3 times)
     - @task-build-solution-retry (CONDITIONAL, may appear up to 3 times)
   • Group by repository and solution
   • Identify missing mandatory tasks
   • Identify duplicate tasks (same task logged multiple times inappropriately)
   • Store result: {csv_exists, total_solutions, solutions_with_issues, all_mandatory_logged, details: {repo_name: {solution_name: {expected_mandatory_tasks, actual_tasks, missing_mandatory_tasks, has_issues}}}}
   • Log status if DEBUG=1

7. **Generate Verification Report**
   Create summary with:
   • Total repositories verified
   • Total solutions verified
   • Solutions with all tasks complete
   • Solutions with all mandatory tasks complete
   • Solutions with all variables properly set
   • Solutions with missing/invalid paths
   • Overall status: PASS or FAIL
   • Detailed findings per repository and solution

8. **Write Results**
   • Save markdown report to: `results/solution-tasks-verification.md`
   • Save JSON output to: `output/verify-solution-tasks-completed.json`
   • Log completion if DEBUG=1

---

## Output Contract
JSON saved to:  
`output/verify-solution-tasks-completed.json`

| Field | Type | Description |
|-------|------|-------------|
| total_repositories | integer | Number of repositories verified |
| total_solutions | integer | Total number of solutions across all repositories |
| repositories_verified | array | List of repository names checked |
| solutions_by_repository | object | {repo_name: solution_count} |
| task_completion_summary | object | {repo_name: {solution_name: {total_tasks, completed_tasks, incomplete_tasks, all_completed, mandatory_completed}}} |
| variable_validation_summary | object | {repo_name: {solution_name: {total_variables, valid_variables, invalid_variables, all_variables_set, invalid_variable_list}}} |
| solution_path_summary | object | {repo_name: {solution_name: {path, exists}}} |
| csv_completeness | object | {csv_exists, total_solutions, solutions_with_issues, all_mandatory_logged, details} |
| solutions_passing | array | List of solutions (repo:solution_name) passing all checks |
| solutions_failing | array | List of solutions (repo:solution_name) failing any check |
| overall_status | string | PASS or FAIL |
| timestamp | string | ISO8601 timestamp |

---

## Verification Criteria

A solution PASSES if:
- All tasks in the solution section are marked [x]
- Mandatory tasks (#1 Restore and #2 Build) are completed
- All solution variables are properly set (not blank, not "NONE", not "N/A", not "NOT_EXECUTED"). Note: "SKIPPED", "SUCCESS", and "FAILED" are acceptable values.
- The solution_path exists and points to a valid .sln file
- At least the 2 mandatory tasks (@task-restore-solution and @task-build-solution) are logged in solution_result.csv

A solution FAILS if any of the above criteria is not met.

Overall status is PASS only if all solutions in all repositories pass.

---

## Markdown Report Format

```markdown
# Solution Tasks Verification Report

Generated: {timestamp}

## Summary

- Total Repositories: {count}
- Total Solutions: {count}
- Solutions Passing: {count}
- Solutions Failing: {count}
- Overall Status: {PASS/FAIL}

## Solutions by Repository

{For each repository:}
- {repo_name}: {solution_count} solutions

## CSV Completeness Check

- CSV File: {EXISTS/MISSING}
- Total Solutions: {count}
- Solutions with Issues: {count}
- All Mandatory Tasks Logged: {YES/NO}

{If solutions_with_issues:}
**Solutions with CSV Issues:**
- {repo_name} :: {solution_name}:
  - Missing mandatory tasks: {list}

## Detailed Results

### Repository: {repo_name}

#### Solution: {solution_name}
**Status: {PASS/FAIL}**
**Path: {solution_path}**

##### Task Completion
- Total Tasks: {count}
- Completed Tasks: {count}
- Incomplete Tasks: {count}
- All Tasks Complete: {YES/NO}
- Mandatory Tasks Complete: {YES/NO}
{List of incomplete tasks if any}

##### Solution Variables
- Total Variables: {count}
- Valid Variables: {count}
- Invalid Variables: {count}
- All Variables Set: {YES/NO}
{List of invalid variables with their values if any}

##### Solution Path
- Path: {solution_path}
- Exists: {YES/NO}

##### CSV Tracking
- Mandatory Tasks Expected: 2
- Mandatory Tasks in CSV: {count}
- All Mandatory Tasks Logged: {YES/NO}
{If issues:}
- Missing mandatory: {list}

---

{Repeat for each solution in each repository}
```

---

## Debug Logging (DEBUG=1)
Prefix: `[debug][verify-solution-tasks-completed]`

Log messages for:
• START (with search pattern)
• Found solution checklists
• Solutions parsed per repository
• Each solution verification (tasks, variables, path, CSV)
• Summary statistics
• EXIT status

---

## Example Usage

```python
# Execute verification
python verify_solution_tasks_completed.py

# With debug output
DEBUG=1 python verify_solution_tasks_completed.py
```

---

## Notes

- Solution checklists contain multiple solutions per file (one file per repository)
- Each solution has its own task list and variable section
- Mandatory tasks (#1 and #2) must always be completed
- Conditional tasks (#3-#10) only need to be completed if they were executed
- "SKIPPED" variables indicate tasks were intentionally not executed (acceptable)
- "FAILED" variables indicate tasks were attempted but failed (acceptable, shows execution)
- Only "NONE", "N/A", blank/empty, and "NOT_EXECUTED" are invalid variable values


