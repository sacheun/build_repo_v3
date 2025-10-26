@solution-tasks-list solution_path={{solution_path}}
@task-restore-solution solution_path={{solution_path}}
@task-build-solution solution_path={{solution_path}}
@task-search-knowledge-base solution_path={{solution_path}}
@task-apply-knowledge-base-fix solution_path={{solution_path}}
@task-create-knowledge-base solution_path={{solution_path}}
---
temperature: 0.1
---

### Available Tasks:
1. @task-restore-solution - Restore NuGet packages for the solution
2. @task-build-solution - Build the solution (Clean + Build)
3. @task-search-knowledge-base - Search for existing KB article matching the error
4. @task-apply-knowledge-base-fix - Apply the fix from KB article to the solution
5. @task-create-knowledge-base - Create new KB article by researching with Microsoft Docs

### Variables available:
- {{solution_path}} → Absolute path to the .sln file being processed
- {{solution_name}} → Friendly solution name derived from the file name without extension
- {{build_attempt}} → Current build attempt number (1-3)
- {{max_build_attempts}} → Maximum allowed build attempts (3)

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
