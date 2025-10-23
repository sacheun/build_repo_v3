@solution-tasks-list solution_path={{solution_path}}
@task-restore-solution solution_path={{solution_path}}
@task-build-solution solution_path={{solution_path}}
@task-search-knowledge-base solution_path={{solution_path}}
@task-apply-knowledge-base-fix solution_path={{solution_path}}
@task-create-knowledge-base solution_path={{solution_path}}
---
temperature: 0.1
model: gpt-5
---

** ⚠️ CRITICAL - CONDITIONAL WORKFLOW WITH RETRY LOGIC ⚠️ **

This is NOT a simple linear pipeline. Tasks execute conditionally based on build results.

** ⚠️ MANDATORY CHECKLIST - DO NOT SKIP ANY STEP ⚠️ **

When a build FAILS and KB is FOUND or CREATED, you MUST:
1. ✅ Execute @task-apply-knowledge-base-fix (MANDATORY - never skip)
2. ✅ Retry RESTORE + BUILD after applying fix (MANDATORY - loop back to Step 1)
   - ⚠️ RESTORE happens FIRST (Step 1), then BUILD (Step 2)
3. ✅ DO NOT move to next solution/repository until retry RESTORE + BUILD is complete

Note: Each build attempt includes BOTH restore and build steps (restore FIRST, then build).

WORKFLOW OVERVIEW:
1. Restore solution (restore NuGet packages)
2. Build solution (attempt 1 of max 3)
3. If Build SUCCESS → Done
4. If Build FAIL → Search Knowledge Base for fix
5. If Knowledge Base FOUND → **APPLY FIX in Knowledge Base** (MANDATORY) → **RETRY RESTORE + BUILD** (MANDATORY - attempt 2)
6. If Knowledge Base NOT FOUND → Create Knowledge Base → Search Knowledge Base → **APPLY FIX in Knowledge Base** (MANDATORY) → **RETRY RESTORE + BUILD** (MANDATORY)
7. Maximum 3 build attempts total (each with restore)

** ⚠️ CRITICAL - YOU MUST USE CONDITIONAL LOGIC - NOT LINEAR EXECUTION ⚠️ **
** ⚠️ AFTER CREATING KB, YOU MUST APPLY THE FIX AND RETRY THE BUILD  ⚠️ **

Description:
This prompt executes a conditional workflow for a single solution file (.sln) with automatic retry logic. Build failures trigger KB search, fix application, and rebuild - up to 3 times maximum.

Environment Initialization:
- Before executing any task directives set environment variable DEBUG=1.
- This enables verbose logging or additional diagnostics for all subsequent task prompts.

Available Tasks:
1. @task-restore-solution - Restore NuGet packages for the solution
2. @task-build-solution - Build the solution (Clean + Build)
3. @task-search-knowledge-base - Search for existing KB article matching the error
4. @task-apply-knowledge-base-fix - Apply the fix from KB article to the solution
5. @task-create-knowledge-base - Create new KB article by researching with Microsoft Docs

Behavior:

** CONDITIONAL WORKFLOW - NOT LINEAR PIPELINE **

Initialize counters:
- build_attempt = 0
- max_build_attempts = 3
- fixes_applied = []

**MAIN LOOP (repeat until success or max attempts reached):**

**Step 1: Restore Solution**
   - DEBUG: Log "[WORKFLOW-DEBUG] Restore attempt for build {build_attempt} of {max_build_attempts}"
   - Execute: @task-restore-solution solution_path={{solution_path}}
   - Input: solution_path
   - Scriptable: Generate a Python script
   - Output: restore_status (SUCCESS | FAIL), restore_stderr, restore_warnings[]
   - Tracking: Update solution-progress.md, solution-results.md
   - Note: Restore failures are logged but do NOT stop the workflow (build will attempt)

**Step 2: Build Solution**
   - Increment build_attempt counter
   - DEBUG: Log "[WORKFLOW-DEBUG] Build attempt {build_attempt} of {max_build_attempts}"
   - Execute: @task-build-solution solution_path={{solution_path}}
   - Input: solution_path
   - Scriptable: Generate a Python script
   - Output: build_status (SUCCESS | FAIL), build_stderr, errors[], warnings[]
   - Tracking: Update solution-progress.md, solution-results.md
   
   **Branch based on build_status:**
   
   **If build_status == SUCCESS:**
   - DEBUG: Log "[WORKFLOW-DEBUG] Build succeeded on attempt {build_attempt}"
   - Set pipeline_status = SUCCESS
   - Record: successful_build_attempt = build_attempt
   - **EXIT LOOP** → Go to Final Output (Step 7)
   
   **If build_status == FAIL:**
   - DEBUG: Log "[WORKFLOW-DEBUG] Build failed on attempt {build_attempt}"
   - Check: if build_attempt >= max_build_attempts:
     - DEBUG: Log "[WORKFLOW-DEBUG] Max build attempts reached, workflow failed"
     - Set pipeline_status = FAIL
     - **EXIT LOOP** → Go to Step 6 (Final KB Tasks)
   - Otherwise: Continue to Step 3

**Step 3: Search Knowledge Base**
   - DEBUG: Log "[WORKFLOW-DEBUG] Searching KB for error fix (build attempt {build_attempt})"
   - Execute: @task-search-knowledge-base solution_path={{solution_path}} solution_name={{solution_name}} build_status={{build_status}} build_stderr={{build_stderr}} errors={{errors}} warnings={{warnings}}
   - Input: solution_path, solution_name, build_status, build_stderr, errors (from build task), warnings (from build task)
   - Output: kb_search_status (FOUND | NOT_FOUND), kb_file_path, detection_tokens, error_signature, error_code, error_type
   - Scriptable: Generate a Python script
   - Tracking: Update solution-progress.md, solution-results.md
   - Note: Receives errors[] and warnings[] arrays from Step 2 (Build Solution)
   
   **Branch based on kb_search_status:**
   
   **If kb_search_status == FOUND:**
   - DEBUG: Log "[WORKFLOW-DEBUG] KB article found: {kb_file_path}"
   - Continue to Step 4 (Apply Fix)
   
   **If kb_search_status == NOT_FOUND:**
   - DEBUG: Log "[WORKFLOW-DEBUG] No KB article found, creating new KB"
   - Continue to Step 5 (Create KB)

**Step 4: Apply KB Fix** (only when kb_search_status == FOUND)
   - ⚠️ **CRITICAL: THIS STEP IS MANDATORY - NEVER SKIP IT**
   - DEBUG: Log "[WORKFLOW-DEBUG] Applying fix from KB: {kb_file_path}"
   - Execute: @task-apply-knowledge-base-fix solution_path={{solution_path}} kb_file_path={{kb_file_path}} error_code={{error_code}}
   - Input: solution_path, kb_file_path (from search-knowledge-base), error_code (from search-knowledge-base)
   - Output: fix_status (SUCCESS | FAIL | SKIPPED), fix_applied, changes_made[]
   - Tracking: Update solution-progress.md, solution-results.md
   - Record: Append fix to fixes_applied array
   - Non-scriptable: Uses AI reasoning to classify command from the fix is safe and execute safe commands individually
   - Note: kb_file_path is provided by task-search-knowledge-base output
   - ⚠️ **YOU MUST EXECUTE @task-apply-knowledge-base-fix - DO NOT JUST DISPLAY THE KB CONTENT**
   
   **Branch based on fix_status:**
   
   **If fix_status == SUCCESS:**
   - DEBUG: Log "[WORKFLOW-DEBUG] Fix applied successfully, retrying restore + build"
   - ⚠️ **MANDATORY: LOOP BACK to Step 1** (RESTORE solution first, then retry build with fix applied)
   - **DO NOT MOVE TO NEXT REPOSITORY UNTIL RESTORE + BUILD IS RETRIED**
   
   **If fix_status == FAIL or SKIPPED:**
   - DEBUG: Log "[WORKFLOW-DEBUG] Fix could not be applied, marking workflow as failed"
   - Set pipeline_status = FAIL
   - **EXIT LOOP** → Go to Step 6 (Final KB Tasks)

**Step 5: Create KB** (only when kb_search_status == NOT_FOUND)
   - DEBUG: Log "[WORKFLOW-DEBUG] Creating new KB article for error: {error_signature}"
   - Execute: @task-create-knowledge-base solution_path={{solution_path}} solution_name={{solution_name}} kb_search_status=NOT_FOUND detection_tokens={{detection_tokens}} error_signature={{error_signature}} error_code={{error_code}} error_type={{error_type}} build_stderr={{build_stderr}} errors={{errors}} warnings={{warnings}}
   - Input: solution_path, solution_name, kb_search_status, detection_tokens, error_signature, error_code, error_type, build_stderr, errors (from build task), warnings (from build task)
   - Output: kb_create_status (SUCCESS | SKIPPED), kb_file_path, kb_file_created, microsoft_docs_urls[]
   - Non-scriptable: Leverage AI reasoning to execute an MCP query for resolve this issue.
   - Tracking: Update solution-progress.md, solution-results.md
   - Note: Receives errors[] and warnings[] arrays from Step 2 (Build Solution) for additional context
   
   **After KB creation:**
   - ⚠️ **CRITICAL: THESE STEPS ARE MANDATORY AFTER KB CREATION**
   - DEBUG: Log "[WORKFLOW-DEBUG] KB created: {kb_file_path}, searching again"
   - **MANDATORY STEP A: Execute @task-search-knowledge-base again** to find the newly created KB
   - Input: Pass same build errors for consistency
   - Output: kb_search_status should now be FOUND, kb_file_path will point to newly created KB
   - If kb_search_status == FOUND:
     - Use kb_file_path from search result
     - ⚠️ **MANDATORY STEP B: Continue to Step 4** (Apply the fix from newly created KB)
     - ⚠️ **YOU MUST EXECUTE @task-apply-knowledge-base-fix - DO NOT SKIP THIS**
     - ⚠️ **YOU MUST RETRY RESTORE + BUILD AFTER APPLYING THE FIX**
   - If kb_search_status == NOT_FOUND (should not happen):
     - DEBUG: Log "[WORKFLOW-DEBUG] ERROR: Created KB but search failed, marking workflow as failed"
     - Set pipeline_status = FAIL
     - **EXIT LOOP**

**Step 6: Final KB Tasks** (when max attempts reached or fix failed)
   - If kb_search_status was never run (edge case):
     - Execute: @task-search-knowledge-base with build errors to document the final error
   - If kb_search_status == NOT_FOUND:
     - Execute: @task-create-knowledge-base with build errors to create KB for the error
   - DEBUG: Log "[WORKFLOW-DEBUG] Final KB tasks complete, workflow ending with FAIL status"

**Step 7: Final Output**
   - DEBUG: Log "[WORKFLOW-DEBUG] Workflow complete: pipeline_status={pipeline_status}, build_attempts={build_attempt}, fixes_applied={len(fixes_applied)}"
   - Return aggregate output (see Output Contract below)

**TASK EXECUTION DETAILS:**

   1. **Restore Task (@task-restore-solution):**
      - Input: solution_path (absolute path to .sln)
      - Action: Restore NuGet packages (msbuild /t:restore)
      - Output: restore_status (SUCCESS | FAIL), restore_stderr, restore_warnings[]
      - Tracking: Update solution-results.md with restore outcome
      - Note: Restore failures are logged but do NOT prevent build from attempting

   2. **Build Task (@task-build-solution):**
      - Input: solution_path (absolute path to .sln)
      - Action: MSBuild Clean + Build (msbuild /t:Clean,Build)
      - Output: build_status (SUCCESS | FAIL), build_stderr, errors[], warnings[], build_time
      - Tracking: Update solution-results.md with build outcome
      - Note: Can be called up to 3 times in retry loop

   3. **Knowledge Base Search Task (@task-search-knowledge-base):**
      - Prerequisite: Runs ONLY after build failures (not after success)
      - Input: build_status=FAIL, build_stderr (error output from build task), errors[] (diagnostic error codes), warnings[] (diagnostic warning codes)
      - Action: Extract detection tokens from build errors, search existing knowledge base markdown files
      - Output: kb_search_status (FOUND | NOT_FOUND), kb_file_path (absolute path to KB .md file), detection_tokens, error_signature, error_code, error_type
      - Tracking: Logs search results but does not create files
      - Note: **kb_file_path output is CRITICAL** - it's passed to apply-knowledge-base-fix task
      - Behavior:
        a. Receive errors[] array from build task containing diagnostic codes (NU1008, MSB3644, CS0234, etc.)
        b. Extract "Detection Tokens" from stderr and errors[] using AI reasoning
        c. Search existing .md files in ./knowledge_base_markdown/ for matching tokens
        d. If match found, return kb_search_status=FOUND with **kb_file_path** (absolute path to matched KB file)
        e. If no match found, return kb_search_status=NOT_FOUND with detection_tokens

   4. **Apply Fix Task (@task-apply-knowledge-base-fix):**
      - Prerequisite: Runs ONLY when kb_search_status == FOUND
      - Input: solution_path, kb_file_path (from search-knowledge-base output), error_code (from search-knowledge-base output)
      - Action: Parse KB article, apply fix instructions to solution files (modify .csproj, Directory.Build.props, etc.)
      - Output: fix_status (SUCCESS | FAIL | SKIPPED), fix_applied (string description), changes_made[]
      - Tracking: Update solution-results.md with fix details
      - Note: **Receives kb_file_path from task-search-knowledge-base** - this is the absolute path to the KB markdown file
      - Behavior:
        a. Read KB article from kb_file_path to extract fix instructions
        b. Identify target files to modify (e.g., .csproj, props files)
        c. Apply changes using file editing tools
        d. Validate changes were applied correctly
        e. If successful, return fix_status=SUCCESS (triggers rebuild)
        f. If unable to apply, return fix_status=FAIL (exits workflow)

   5. **Knowledge Base Creation Task (@task-create-knowledge-base):**
      - Prerequisite: Runs ONLY when kb_search_status == NOT_FOUND
      - Input: kb_search_status=NOT_FOUND, detection_tokens, error_signature, error_code, error_type, build_stderr, errors[] (diagnostic error codes), warnings[] (diagnostic warning codes)
      - Action: Research error using Microsoft Docs MCP server, synthesize fix instructions, create new KB article
      - Output: kb_create_status (SUCCESS | SKIPPED), kb_file_path (if created), kb_file_created (boolean), microsoft_docs_urls[]
      - Tracking: Creates new markdown files in ./knowledge_base_markdown/ directory
      - Behavior:
        a. Receive errors[] and warnings[] arrays from build task for comprehensive error analysis
        b. Research error using mcp_microsoftdocs_microsoft_docs_search
        c. Find code examples using mcp_microsoftdocs_microsoft_code_sample_search
        d. Fetch comprehensive docs if needed using mcp_microsoftdocs_microsoft_docs_fetch
        e. Synthesize diagnostic hints from Microsoft Docs understanding
        f. Draft fix instructions (Option 1: Recommended, Option 2: Alternative, Option 3: Workaround)
        g. Create safety guidance based on fix impact
        h. Generate KB article file with real content (no placeholders)
        i. Save to ./knowledge_base_markdown/ with error_signature as filename
        j. After creation, workflow automatically re-runs search-knowledge-base to find the new article

Variables available:
- {{solution_path}} → Absolute path to the .sln file being processed
- {{solution_name}} → Friendly solution name derived from the file name without extension
- {{build_attempt}} → Current build attempt number (1-3)
- {{max_build_attempts}} → Maximum allowed build attempts (3)

Task name: solution-tasks-list

Directive Format:
- Each task directive appears as: `@task-<task-name> key=value key2=value2`
- Placeholders like `{{solution_path}}`, `{{solution_name}}` are substituted before execution

Execution Semantics:

** THIS IS A CONDITIONAL RETRY WORKFLOW - NOT A LINEAR PIPELINE **

0. **Initialization:**
   - Set DEBUG=1 in the execution environment ($env:DEBUG="1" or export DEBUG=1)
   - Set build_attempt = 0
   - Set max_build_attempts = 3
   - Set fixes_applied = []
   - Set pipeline_status = PENDING

1. **Main Retry Loop** (repeat until SUCCESS or max attempts):
   
   a. **Build Attempt:**
      - Increment build_attempt counter
      - DEBUG log: "[WORKFLOW-DEBUG] Build attempt {build_attempt} of {max_build_attempts}"
      - Execute @task-build-solution
      - Record: build_status, build_stderr, errors[], warnings[]
      - **If build_status == SUCCESS:**
        - Set pipeline_status = SUCCESS
        - DEBUG log: "[WORKFLOW-DEBUG] Build succeeded on attempt {build_attempt}"
        - **EXIT LOOP** → Go to Step 3 (Final Output)
      - **If build_status == FAIL and build_attempt >= max_build_attempts:**
        - Set pipeline_status = FAIL
        - DEBUG log: "[WORKFLOW-DEBUG] Max build attempts reached"
        - **EXIT LOOP** → Go to Step 2 (Final KB Documentation)
      - **If build_status == FAIL and build_attempt < max_build_attempts:**
        - Continue to KB Search
   
   b. **KB Search:**
      - DEBUG log: "[WORKFLOW-DEBUG] Searching KB for error fix"
      - Execute @task-search-knowledge-base with build_status=FAIL, build_stderr, errors, warnings
      - Input: Receives errors[] and warnings[] arrays from build task
      - Record: kb_search_status, kb_file_path, detection_tokens, error_signature, error_code, error_type
      - **If kb_search_status == FOUND:**
        - Continue to Apply Fix
      - **If kb_search_status == NOT_FOUND:**
        - Continue to Create KB
   
   c. **Apply Fix** (when kb_search_status == FOUND):
      - DEBUG log: "[WORKFLOW-DEBUG] Applying fix from KB: {kb_file_path}"
      - Execute @task-apply-knowledge-base-fix with solution_path, kb_file_path, error_code
      - Record: fix_status, fix_applied, changes_made[]
      - **If fix_status == SUCCESS:**
        - Append fix to fixes_applied array
        - DEBUG log: "[WORKFLOW-DEBUG] Fix applied successfully, retrying build"
        - **LOOP BACK to Build Attempt** (step 1a)
      - **If fix_status == FAIL or SKIPPED:**
        - Set pipeline_status = FAIL
        - DEBUG log: "[WORKFLOW-DEBUG] Fix could not be applied"
        - **EXIT LOOP** → Go to Step 2 (Final KB Documentation)
   
   d. **Create KB** (when kb_search_status == NOT_FOUND):
      - DEBUG log: "[WORKFLOW-DEBUG] Creating new KB article for error: {error_signature}"
      - Execute @task-create-knowledge-base with kb_search_status=NOT_FOUND, detection_tokens, error_signature, error_code, error_type, build_stderr, errors, warnings
      - Input: Receives errors[] and warnings[] arrays from build task
      - Record: kb_create_status, kb_file_path, kb_file_created, microsoft_docs_urls[]
      - **After KB creation:**
        - DEBUG log: "[WORKFLOW-DEBUG] KB created: {kb_file_path}, searching again"
        - Re-execute @task-search-knowledge-base to find newly created KB
        - **If kb_search_status == FOUND:**
          - Continue to Apply Fix (step 1c)
        - **If kb_search_status == NOT_FOUND (error condition):**
          - Set pipeline_status = FAIL
          - DEBUG log: "[WORKFLOW-DEBUG] ERROR: Created KB but search failed"
          - **EXIT LOOP**

2. **Final KB Documentation** (when exiting with FAIL):
   - If no KB search was performed (edge case), execute @task-search-knowledge-base with build errors to document error
   - If kb_search_status == NOT_FOUND, execute @task-create-knowledge-base with build errors to create KB for error
   - Ensure errors[] and warnings[] from last build attempt are passed for comprehensive documentation
   - DEBUG log: "[WORKFLOW-DEBUG] Final KB tasks complete"

3. **Final Output:**
   - DEBUG log: "[WORKFLOW-DEBUG] Workflow complete: pipeline_status={pipeline_status}, build_attempts={build_attempt}, fixes_applied={len(fixes_applied)}"
   - Return aggregate JSON output (see Output Contract below)

4. **Critical Rules:**
   - Maximum 3 build attempts (initial + 2 retries)
   - Each failed build triggers KB search
   - Each KB found triggers fix application and rebuild
   - Each KB not found triggers KB creation → search → fix → rebuild
   - Loop continues until: (a) build succeeds, (b) fix fails, or (c) max attempts reached
   - All failures must be documented in KB (ensures learning from errors)

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

Implementation Notes:
1. **Retry Loop is the Core Logic:** Unlike linear pipelines, this workflow LOOPS back to build after applying fixes
2. **Maximum 3 Build Attempts:** Initial build + up to 2 retries after fixes applied
3. **Conditional Execution:** Tasks only run when needed:
   - search-kb: ONLY after build failures
   - apply-kb-fix: ONLY when KB found
   - create-kb: ONLY when KB not found
4. **Fix Application Triggers Rebuild:** After successful fix, workflow automatically retries build
5. **KB Creation Triggers Search:** After creating KB, workflow automatically searches for it, then applies fix
6. **Exit Conditions:**
   - SUCCESS: Build succeeds on any attempt (1-3)
   - FAIL: Max attempts reached OR fix application fails
7. **Final KB Documentation:** If workflow fails, always ensure error is documented in KB
8. **Debug Logging:** All workflow decisions logged with [WORKFLOW-DEBUG] prefix for transparency
9. **Idempotency:** Each task avoids duplicate actions (e.g., don't create KB if already exists)
10. **Error Propagation:** Individual task failures logged but workflow continues to final KB documentation
11. **Tracking:** fixes_applied array maintains complete history of all fixes attempted
12. **Performance:** Workflow stops as soon as build succeeds (no unnecessary tasks)

Extensibility Guidelines:
- To add new fix strategies: Create new task like @task-apply-custom-fix
- To add new build validation: Add task after successful build before exiting
- To add new error research sources: Enhance @task-create-kb with additional MCP servers
- Maintain loop structure: New tasks should integrate into retry loop or final documentation phase
