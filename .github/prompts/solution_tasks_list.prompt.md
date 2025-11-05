@solution-tasks-list solution_path={{solution_path}}
@task-restore-solution solution_path={{solution_path}}
@task-build-solution solution_path={{solution_path}}
@task-search-knowledge-base solution_path={{solution_path}}
@task-create-knowledge-base solution_path={{solution_path}}
@task-apply-knowledge-base-fix solution_path={{solution_path}}
@task-update-knowledgebase-log knowledgebase_file={{knowledgebase_file}} option={{option}} status={{status}} repo_name={{repo_name}}
---
temperature: 0.1
---

### Available Tasks:
1. @task-restore-solution - Restore NuGet packages for the solution
2. @task-build-solution - Build the solution (Clean + Build)
3. @task-search-knowledge-base - Search for existing KB article matching the error
4. @task-create-knowledge-base - Create new KB article by researching with Microsoft Docs
5. @task-apply-knowledge-base-fix - Apply the fix from KB article to the solution
6. @task-update-knowledgebase-log - Update knowledgebase usage log and statistics

### Solution Variables
(Variables set by tasks for this specific solution)

- {{solution_path}} → path value
- {{solution_name}} → name value
- {{max_build_attempts}} → 3
- {{restore_status}} → SUCCEEDED | FAILED | NOT_EXECUTED
- {{build_status}} → SUCCEEDED | FAILED | NOT_EXECUTED | SKIPPED
- {{kb_search_status}} → COMPLETED | SKIPPED | NOT_FOUND
- {{kb_file_path}} → path or N/A
- {{kb_article_status}} → EXISTS | CREATED | SKIPPED

**Retry Attempt 1:**
- {{fix_applied_attempt_1}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_1}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_1}} → SUCCEEDED | FAILED | SKIPPED

**Retry Attempt 2:**
- {{fix_applied_attempt_2}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_2}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_2}} → SUCCEEDED | FAILED | SKIPPED

**Retry Attempt 3:**
- {{fix_applied_attempt_3}} → APPLIED | NOT_APPLIED | SKIPPED
- {{kb_option_applied_attempt_3}} → 1 | 2 | 3 | null
- {{retry_build_status_attempt_3}} → SUCCEEDED | FAILED | SKIPPED
```

Task name: solution-tasks-list


Output Contract (aggregate pipeline output):
- solution_path: string (absolute path to .sln file)
- solution_name: string (filename without extension)
- pipeline_status: SUCCESS | FAIL (overall workflow outcome)
- total_build_attempts: number (1-3, how many times build was attempted)
- successful_build_attempt: number | null (which attempt succeeded, or null if all failed)
- fixes_applied: array[object] (list of fixes applied during retry loop)
  - Each fix object: {kb_file_path: string, error_code: string, fix_applied: string, changes_made: array[string]}
- restore_status: SUCCESS | FAIL (status of last restore attempt)
- restore_stderr: string (error output from last restore)
- restore_warnings: array[string] (warning codes from restore)
- final_build_status: SUCCESS | FAIL (status of last build attempt)
- build_stderr: string (error output from last build attempt)
- errors: array[string] (error codes from last build: NU1008, MSB3644, etc.)
- warnings: array[string] (warning codes from last build)
- build_time: number (seconds taken for last build)
- kb_search_status: FOUND | NOT_FOUND | null (status of last KB search, null if never searched)
- kb_file_path: string | null (path to KB file if found or created)
- detection_tokens: array[string] (error signatures extracted from build errors)
- error_signature: string | null (filename-safe error signature)
- error_code: string | null (error code like NU1008, MSB3644)
- error_type: string | null (NuGet, MSBuild, Compiler, Platform)
- kb_create_status: SUCCESS | SKIPPED | null (status of KB creation, null if never attempted)
- kb_file_created: boolean (true if new KB file was created)
- microsoft_docs_urls: array[string] (Microsoft Docs URLs referenced in KB creation)
