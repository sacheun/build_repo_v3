@task-validate-all-solution-tasks-completed repo_name={{repo_name}}
---
temperature: 0.1
---

Task name: task-validate-all-solution-tasks-completed repo_path={{repo_path}} checked={{checked}}
---
temperature: 0.1
---

Description:
Validates that all mandatory solution tasks are in the expected state (checked or unchecked) for a repository by checking solution-progress.md. Can validate both:
1. checked=false (default): Ensures all cells are EMPTY [ ] (for pre-processing validation)
2. checked=true: Ensures all cells are COMPLETED [x] (for post-processing validation)

If any solutions have tasks in the wrong state and checked=true, re-executes task-process-solutions to complete them.

Inputs:
- repo_name: string (repository name, e.g., "ic3_spool_cosine-dep-spool")
- repo_path: string (absolute path to repository directory)
- checked: boolean (default: false)
  - false = Validate cells are EMPTY [ ] (pre-processing check)
  - true = Validate cells are COMPLETED [x] (post-processing check)

Outputs:
- validation_status: string (SUCCESS | INCOMPLETE | ERROR)
  - SUCCESS: All solutions have tasks in the expected state (all [ ] if checked=false, all [x] if checked=true)
  - INCOMPLETE: Some solutions have tasks in wrong state and reprocessing was triggered (only when checked=true)
  - ERROR: Could not complete validation (only when checked=true)
- total_solutions: number (total number of solutions in repository)
- completed_solutions: number (solutions with all tasks in expected state)
- incomplete_solutions: array[object] (solutions with tasks in wrong state)
  - solution_name: string
  - wrong_state_tasks: array[string] (list of tasks not in expected state)
- reprocessing_triggered: boolean (true if task-process-solutions was re-executed, only when checked=true)

Behavior:
When checked=false (pre-processing validation):
- Validates all mandatory task cells are EMPTY [ ] for all solutions in the repository
- Returns SUCCESS if all cells are [ ], otherwise lists solutions with wrong state
- Does NOT trigger reprocessing (only reports validation status)

When checked=true (post-processing validation):
- Validates all mandatory task cells are COMPLETED [x] or FAILED [!] for all solutions in the repository
- If any solutions have incomplete tasks (still [ ]), automatically re-runs task-process-solutions to complete them
- Returns SUCCESS if all tasks complete, INCOMPLETE if reprocessing triggered, ERROR if failed

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
  "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Starting validation with checked={checked} (validates cells are {checked ? '[x] or [!]' : '[ ]'}),INFO"
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

**Step 5: Validate Task State Based on 'checked' Parameter**

**When checked=false (pre-processing validation):**
- For each solution in the repository:
  - Check if restore-solution is marked [ ] (empty/unchecked)
  - Check if build-solution is marked [ ] (empty/unchecked)
  - If either is [x] (already checked), add solution to incomplete_solutions array with wrong_state_tasks = ["restore-solution"] or ["build-solution"]
- Goal: Ensure ALL cells are empty [ ] before processing begins
- **Do NOT trigger reprocessing** in this mode (only report validation status)

**When checked=true (post-processing validation):**
- For each solution in the repository:
  - Check if restore-solution is marked [x] or [!]
  - Check if build-solution is marked [x] or [!]
  - These two tasks are ALWAYS mandatory
  - If either is [ ], add solution to incomplete_solutions array with wrong_state_tasks = ["restore-solution"] or ["build-solution"]
- KB tasks (search/apply/create) are conditional:
  - If build-solution is [x] (success), KB tasks are NOT required (can be [ ])
  - If build-solution is [!] (fail), at least one KB task should be [x] (attempted to fix)
  - For validation, we primarily check restore and build completion
- **Will trigger reprocessing** for incomplete solutions (see Step 7)

**Step 6: Calculate Completion Status**

**When checked=false (pre-processing validation):**
- completed_solutions = count of solutions where restore-solution [ ] AND build-solution [ ] (all cells empty)
- If completed_solutions == total_solutions:
  - Set validation_status = SUCCESS
  - Set reprocessing_triggered = false
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Validation with checked=false SUCCESS: All {total_solutions} solutions have empty cells [ ],SUCCESS"
    ```
  - Return success message
  - **EXIT** (do not proceed to Step 7)
- If completed_solutions < total_solutions:
  - Set validation_status = INCOMPLETE
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Validation with checked=false FAIL: Solutions with non-empty cells: {comma-separated list},FAIL"
    ```
  - Example message: "Solutions with non-empty cells: MySolution1 (has: restore-solution [x]), MySolution2 (has: build-solution [x])"
  - **Do NOT proceed to Step 7** (no reprocessing in pre-validation mode)
  - **EXIT** with status INCOMPLETE

**When checked=true (post-processing validation):**
- completed_solutions = count of solutions where restore-solution [x] AND build-solution [x] OR [!]
- If completed_solutions == total_solutions:
  - Set validation_status = SUCCESS
  - Set reprocessing_triggered = false
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Validation with checked=true SUCCESS: All {completed_solutions}/{total_solutions} solutions complete,SUCCESS"
    ```
  - Return success message
  - **EXIT** (do not proceed to Step 7)
- If completed_solutions < total_solutions:
  - Set validation_status = INCOMPLETE
  - **Log to Decision Log:**
    ```
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Validation with checked=true FAIL: Incomplete solutions: {comma-separated list of solution names with missing tasks},FAIL"
    ```
  - Example message: "Incomplete solutions: MySolution1 (missing: build-solution), MySolution2 (missing: restore-solution build-solution)"
  - Continue to Step 7 (trigger reprocessing)

**Step 7: Re-execute task-process-solutions for Incomplete Solutions (checked=true ONLY)**
- **Note: This step is ONLY executed when checked=true. When checked=false, exit at Step 6.**
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
    "{{timestamp}},{{repo_name}},,task-validate-all-solution-tasks-completed,Re-processing solution {solution_name} due to incomplete tasks: {wrong_state_tasks},REPROCESSING"
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
  [VALIDATION] Mode: {checked ? "post-processing (checked=true)" : "pre-processing (checked=false)"}
  [VALIDATION] Total Solutions: {total_solutions}
  [VALIDATION] Completed Solutions: {completed_solutions}
  [VALIDATION] Incomplete Solutions: {len(incomplete_solutions)}
  [VALIDATION] Reprocessing Triggered: {reprocessing_triggered}
  [VALIDATION] Status: {validation_status}
  ```
- Return JSON output with all fields from Outputs section

Usage Examples:

**Example 1: Pre-processing validation (checked=false)**
```
@task-validate-all-solution-tasks-completed repo_name=ic3_spool_cosine-dep-spool repo_path=C:\repos\ic3_spool_cosine-dep-spool checked=false
```
Expected: All cells should be [ ] (empty). Returns SUCCESS if all empty, INCOMPLETE if any cells have [x].
Use case: Run BEFORE processing solutions to ensure clean state.

**Example 2: Post-processing validation (checked=true, default behavior)**
```
@task-validate-all-solution-tasks-completed repo_name=ic3_spool_cosine-dep-spool repo_path=C:\repos\ic3_spool_cosine-dep-spool checked=true
```
Expected: All cells should be [x] or [!] (completed/failed). Returns SUCCESS if all complete, triggers reprocessing if any [ ].
Use case: Run AFTER processing solutions to ensure all tasks completed.

Behavior:

1. **Validation Modes:**
   - **checked=false (pre-processing)**: Validates all cells are EMPTY [ ] before processing begins
     * Returns SUCCESS if all cells [ ], INCOMPLETE if any cells have [x] or [!]
     * Does NOT trigger reprocessing (only reports status)
     * Use case: Ensure clean state before starting workflow
   - **checked=true (post-processing)**: Validates all cells are COMPLETED [x] or FAILED [!] after processing
     * Returns SUCCESS if all cells [x] or [!], INCOMPLETE if any cells [ ]
     * Triggers reprocessing for incomplete solutions
     * Use case: Ensure all tasks completed after workflow execution

2. **Validation Logic:**
   - ALWAYS required tasks: restore-solution [x], build-solution [x]
   - Conditionally required tasks: KB tasks (only if build failed)
   - Solution is "complete" if restore [x] AND build [x] OR [!]
   - Solution is "incomplete" if restore [ ] OR build [ ]

3. **Re-processing Logic (checked=true ONLY):**
   - If any solution is incomplete, automatically re-execute task-process-solutions
   - Re-processing runs the full conditional workflow:
     * Restore → Build → (KB workflow if build fails) → Retry build
   - After re-processing, re-validate to confirm completion

4. **Error Handling:**
   - If solution-progress.md missing → ERROR (repository not processed)
   - If no solutions found for repo → ERROR (data integrity issue)
   - If re-processing fails → ERROR (persistent build failures)

5. **Idempotency:**
   - Safe to run multiple times
   - Only re-processes solutions that are actually incomplete (when checked=true)
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
