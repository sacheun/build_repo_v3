@task-validate-all-solution-tasks-completed repo_name={{repo_name}} repo_path={{repo_path}}
---
temperature: 0.1
model: gpt-5
---

Description:
Validates that all mandatory solution tasks have been completed for a repository by checking solution-progress.md against the mandatory tasks defined in solution_tasks_list.md. If any solutions have incomplete tasks, re-executes task-process-solutions to complete them.

Inputs:
- repo_name: string (repository name, e.g., "ic3_spool_cosine-dep-spool")
- repo_path: string (absolute path to repository directory)

Outputs:
- validation_status: string (SUCCESS | INCOMPLETE | ERROR)
- total_solutions: number (total number of solutions in repository)
- completed_solutions: number (solutions with all mandatory tasks completed)
- incomplete_solutions: array[object] (solutions missing tasks)
  - solution_name: string
  - missing_tasks: array[string] (list of incomplete mandatory task names)
- reprocessing_triggered: boolean (true if task-process-solutions was re-executed)

Task name: task-validate-all-solution-tasks-completed

Steps:

**Step 1: Identify Mandatory Tasks**
- Read solution_tasks_list.md from .copilot/prompts/solution_tasks_list.md
- Extract the list of mandatory tasks referenced in the workflow
- Mandatory tasks are:
  1. restore-solution (always required)
  2. build-solution (always required)
  3. search-knowledge-base (required if build fails)
  4. apply-knowledge-base-fix (required if KB found and build failed)
  5. create-knowledge-base (required if KB not found and build failed)
- Note: For validation purposes, we check that restore-solution and build-solution are always [x]
- KB-related tasks may be [ ] if build succeeded (meaning they weren't needed)
- **Log to Decision Log:**
  ```
  "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Mandatory tasks: restore-solution build-solution,INFO"
  ```

**Step 2: Verify solution-progress.md Exists**
- Check if file exists at: ./results/solution-progress.md
- If file does not exist:
  - Set validation_status = ERROR
  - Return error message: "solution-progress.md not found. Repository may not have been processed yet."
  - Do NOT proceed to next steps
- If file exists, continue to Step 3

**Step 3: Load solution-progress.md Content**
- Read ./results/solution-progress.md
- Parse the markdown table to extract:
  - Repository name (from table header or rows)
  - List of all solutions in the repository
  - For each solution, the status of each task column:
    * restore-solution: [x] or [ ]
    * build-solution: [x] or [ ]
    * search-knowledge-base: [x] or [ ]
    * apply-knowledge-base-fix: [x] or [ ]
    * create-knowledge-base: [x] or [ ]
- Expected table format:
  ```markdown
  | Repository | Solution | Restore | Build | Collect KB |
  |------------|----------|---------|-------|------------|
  | repo_name  | sol1     | [x]     | [x]   | [x]        |
  | repo_name  | sol2     | [x]     | [ ]   | [ ]        |
  ```
- Note: Table may use different column headers but should map to:
  * "Restore" → restore-solution
  * "Build" → build-solution
  * "Collect KB" or "KB" → encompasses search/apply/create KB tasks

**Step 4: Filter Solutions for Current Repository**
- From the parsed table, filter rows where Repository column matches {{repo_name}}
- Count total_solutions = number of matching rows
- If total_solutions == 0:
  - Set validation_status = ERROR
  - Return error message: "No solutions found for repository '{{repo_name}}' in solution-progress.md"
  - Do NOT proceed to next steps

**Step 5: Validate Mandatory Task Completion**
- For each solution in the repository:
  - Check if restore-solution is marked [x]
  - Check if build-solution is marked [x]
  - These two tasks are ALWAYS mandatory
  - If either is [ ], add solution to incomplete_solutions array with missing_tasks = ["restore-solution"] or ["build-solution"]
- KB tasks (search/apply/create) are conditional:
  - If build-solution is [x] (success), KB tasks are NOT required (can be [ ])
  - If build-solution is [ ] (fail), at least one KB task should be [x] (attempted to fix)
  - For validation, we primarily check restore and build completion

**Step 6: Calculate Completion Status**
- completed_solutions = count of solutions where restore-solution [x] AND build-solution [x]
- If completed_solutions == total_solutions:
  - Set validation_status = SUCCESS
  - Set reprocessing_triggered = false
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,All solutions complete: {completed_solutions}/{total_solutions},SUCCESS"
    ```
  - Return success message
  - **EXIT** (do not proceed to Step 7)
- If completed_solutions < total_solutions:
  - Set validation_status = INCOMPLETE
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Incomplete solutions: {comma-separated list of solution names with missing tasks},INCOMPLETE"
    ```
  - Example message: "Incomplete solutions: MySolution1 (missing: build-solution), MySolution2 (missing: restore-solution build-solution)"
  - Continue to Step 7

**Step 7: Re-execute task-process-solutions for Incomplete Solutions**
- For each solution in incomplete_solutions array:
  - Log: "Re-processing incomplete solution: {solution_name}"
  - Find solution file path in repo_path:
    * Search for *.sln files recursively in {{repo_path}}
    * Match solution file name with solution_name
  - Execute: @task-process-solutions solution_path={{solution_path}}
  - This will re-run the full solution workflow (restore → build → KB if needed)
  - Update solution-progress.md with new task statuses
  - **Log to Decision Log (per solution re-processed):**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Re-processing solution {solution_name} due to incomplete tasks: {missing_tasks},REPROCESSING"
    ```
    - Example: "Re-processing solution ResourceProvider due to incomplete tasks: restore-solution build-solution"
    - Note: Solution name is in the message, but solution_name column is blank (repository-level task)
- Set reprocessing_triggered = true
- After re-processing all incomplete solutions, return to Step 3 to re-validate
- If validation still fails after re-processing, set validation_status = ERROR

**Step 8: Return Final Output**
- Log validation summary:
  ```
  [VALIDATION] Repository: {{repo_name}}
  [VALIDATION] Total Solutions: {total_solutions}
  [VALIDATION] Completed Solutions: {completed_solutions}
  [VALIDATION] Incomplete Solutions: {len(incomplete_solutions)}
  [VALIDATION] Reprocessing Triggered: {reprocessing_triggered}
  [VALIDATION] Status: {validation_status}
  ```
- Return JSON output with all fields from Outputs section

Behavior:

1. **Validation Logic:**
   - ALWAYS required tasks: restore-solution [x], build-solution [x]
   - Conditionally required tasks: KB tasks (only if build failed)
   - Solution is "complete" if restore [x] AND build [x]
   - Solution is "incomplete" if restore [ ] OR build [ ]

2. **Re-processing Logic:**
   - If any solution is incomplete, automatically re-execute task-process-solutions
   - Re-processing runs the full conditional workflow:
     * Restore → Build → (KB workflow if build fails) → Retry build
   - After re-processing, re-validate to confirm completion

3. **Error Handling:**
   - If solution-progress.md missing → ERROR (repository not processed)
   - If no solutions found for repo → ERROR (data integrity issue)
   - If re-processing fails → ERROR (persistent build failures)

4. **Idempotency:**
   - Safe to run multiple times
   - Only re-processes solutions that are actually incomplete
   - Does not re-process solutions that are already complete

5. **Tracking:**
   - Logs validation results to console with [VALIDATION] prefix
   - Updates solution-progress.md as solutions are re-processed
   - Does NOT create new tracking files (uses existing solution-progress.md)

Example Validation Scenarios:

**Scenario 1: All Tasks Complete**
- solution-progress.md shows all solutions with [x] for restore and build
- validation_status = SUCCESS
- completed_solutions = total_solutions
- incomplete_solutions = []
- reprocessing_triggered = false

**Scenario 2: Some Tasks Incomplete**
- solution-progress.md shows 3 solutions: 2 complete, 1 with build [ ]
- validation_status = INCOMPLETE
- completed_solutions = 2
- total_solutions = 3
- incomplete_solutions = [{solution_name: "MySolution", missing_tasks: ["build-solution"]}]
- Re-execute task-process-solutions for "MySolution"
- reprocessing_triggered = true
- After re-processing, re-validate and update status

**Scenario 3: Missing solution-progress.md**
- File does not exist
- validation_status = ERROR
- Return error immediately without attempting validation

Implementation Notes:

1. **Parsing solution-progress.md:**
   - Use regex or markdown parser to extract table rows
   - Map column headers to task names (may vary slightly)
   - Handle different table formats gracefully

2. **Finding Solution Files:**
   - Use file_search tool with pattern: **/*.sln
   - Match solution file names against solution_name from table
   - Handle cases where multiple .sln files have similar names

3. **Re-processing:**
   - Call task-process-solutions with same inputs as original processing
   - Allow workflow to run fully (restore, build, KB, retry)
   - Do not interrupt or skip steps

4. **Validation Loop:**
   - After re-processing, re-run validation (Steps 3-6)
   - Ensures re-processing actually completed the tasks
   - Prevents infinite loops by limiting to 1 re-processing attempt

5. **Output Format:**
   - Return structured JSON for programmatic consumption
   - Log human-readable summary to console
   - Include all incomplete solution details for debugging
