@solution-tasks-overview
---
description: Source list of solution-level task directives and variables section for generation
---

## Solution Task Directives

### Tasks (Reference Only)
- @task-restore-solution : Restore NuGet packages for the solution.
- @task-build-solution : Initial build (Clean + Build) of the solution.
- @task-search-knowledge-base : Search KB for potential fixes based on build errors.
- @task-create-knowledge-base : Create KB article when missing.
- @task-apply-knowledge-base-fix : Apply selected KB fix attempt.
- @task-build-solution-retry : Retry build after applying a fix.

### Solution Variables
(Variables set by tasks for this specific solution)
- solution_path → <absolute .sln path>
- solution_name → <solution name>
- max_build_attempts → 3
- build_count → 0
- restore_status → NOT_EXECUTED
- build_status → NOT_EXECUTED
- kb_search_status → NOT_EXECUTED
- kb_file_path → N/A
- kb_article_status → NOT_EXECUTED
- fix_applied_attempt_1 → NOT_EXECUTED
- kb_option_applied_attempt_1 → null
- retry_build_status_attempt_1 → NOT_EXECUTED
- fix_applied_attempt_2 → NOT_EXECUTED
- kb_option_applied_attempt_2 → null
- retry_build_status_attempt_2 → NOT_EXECUTED
- fix_applied_attempt_3 → NOT_EXECUTED
- kb_option_applied_attempt_3 → null
- retry_build_status_attempt_3 → NOT_EXECUTED

---
End of file.