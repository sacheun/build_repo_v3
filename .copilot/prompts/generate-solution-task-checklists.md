Task name: generate-solution-task-checklistsTask name: generate-solution-task-checklists@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>````markdown````markdown````markdown@generate-solution-task-checklists repo_name=<required> solutions=<required>



Description:



This task generates solution-specific task checklists in a **separate dedicated file** for each repository. Each repository will have its own `{repo_name}_solution_checklist.md` file containing all solutions discovered in that repository. This is a file generation task that CAN be implemented as a script.Description:



**File Organization:**

- `tasks/{repo_name}_repo_checklist.md` → Repository-level tasks (clone, search, find-solutions, etc.)

- `tasks/{repo_name}_solution_checklist.md` → Solution-level tasks (restore, build, KB workflow, etc.) **← THIS TASK CREATES THIS FILE**This task generates solution-specific task checklists in a **separate dedicated file** for each repository. Each repository will have its own `{repo_name}_solution_checklist.md` file containing all solutions discovered in that repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>



** THIS TASK IS SCRIPTABLE **



---**File Organization:**



temperature: 0.1- `tasks/{repo_name}_repo_checklist.md` → Repository-level tasks (clone, search, find-solutions, etc.)



This task can be implemented as a Python script that:- `tasks/{repo_name}_solution_checklist.md` → Solution-level tasks (restore, build, KB workflow, etc.) **← THIS TASK CREATES THIS FILE**Description:@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>

1. Reads solution data from JSON output file (from @task-find-solutions)

2. Parses variable definitions from solution_tasks_list.md (optional - can use hardcoded template)

3. Generates solution sections with task checklists and variables sections

4. Creates a **new separate file** `tasks/{repo_name}_solution_checklist.md` (NOT appending to repo checklist)** THIS TASK IS SCRIPTABLE **

5. Maintains proper markdown formatting



---

---This task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists

Behavior:



0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`

temperature: 0.1

1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.

   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`This task can be implemented as a Python script that:** THIS TASK IS SCRIPTABLE **@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>---



2. Read Solutions Data: Load solutions from JSON file

   - Read file at solutions_json_path

   - Extract "solutions" array (contains absolute paths to .sln files)1. Reads solution data from JSON output file (from @task-find-solutions)

   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`2. Parses variable definitions from solution_tasks_list.md (optional - can use hardcoded template)



3. Parse Solution Variables: Read .copilot/prompts/solution_tasks_list.md to extract:3. Generates solution sections with task checklists and variables sectionstemperature: 0.1Description:

   - The complete "Variables available:" section content

   - All variable definitions that apply to each solution4. Creates a **new separate file** `tasks/{repo_name}_solution_checklist.md` (NOT appending to repo checklist)

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md`

5. Maintains proper markdown formatting

4. Prepare Solution Checklist File:

   - File: `./tasks/{repo_name}_solution_checklist.md` (separate file from repo checklist)

   - Create new file (will overwrite if exists)

   - **IMPORTANT**: This is a NEW file, NOT appending to `{repo_name}_repo_checklist.md`---This task can be implemented as a Python script that:This task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`



5. Generate Solution Checklist Header:

   - Write file header with repository informationBehavior:

   - Format:

     ```

     # Solution Checklist: {repo_name}

     0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`1. Reads solution data from JSON output file (from @task-find-solutions)

     Repository: {repo_url}

     Generated: [timestamp]

     

     This checklist tracks progress for all solutions discovered in this repository.1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.2. Parses variable definitions from solution_tasks_list.md (optional - can use hardcoded template)

     Each solution has its own section with tasks and variables.

     Use @execute-solution-task to process each solution with the full build workflow.   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

     

     **IMPORTANT EXECUTION RULES:**   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")3. Generates solution sections with task checklists and variables sections** THIS TASK IS SCRIPTABLE **temperature: 0.1

     - Execute ALL MANDATORY tasks (#1-2) for every solution

     - Execute ALL CONDITIONAL tasks (#3-10) when conditions are met (i.e., when build fails)   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

     - Mark completed tasks with [x] in the checklist (e.g., `- [x] [MANDATORY #1] ...`)

     - Update checklist immediately after each task completes4. Creates a new file {repo_name}_solution_checklist.md with all solution sections

     

     ---2. Read Solutions Data: Load solutions from JSON file

     ```

   - Read file at solutions_json_path5. Maintains proper markdown formatting

6. Generate Solution Sections:

      - Extract "solutions" array (contains absolute paths to .sln files)

   For each solution in the solutions array:

   - Extract solution name from path (basename without .sln extension)   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`

   - Format:   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

     ```

     ---This task can be implemented as a Python script that:Description:

     ## Solution: {solution_name}

     3. Parse Solution Variables: Read .copilot/prompts/solution_tasks_list.md to extract:

     Path: {solution_path}

        - The complete "Variables available:" section content

     ### Tasks (Conditional Workflow - See execute-solution-task.md)

        - All variable definitions that apply to each solution

     **IMPORTANT:** Execute BOTH MANDATORY and CONDITIONAL tasks when conditions are met.

     Mark tasks with [x] when completed (e.g., `- [x] [MANDATORY #1] ...`).   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md`Behavior:1. Reads solution data from JSON output file (from @task-find-solutions)

     

     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

     - [ ] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base (execute if build fails)4. Prepare Solution Checklist File:

     - [ ] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base (execute if KB not found)

     - [ ] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix (execute if KB found/created)   - File: `./tasks/{repo_name}_solution_checklist.md` (separate file from repo checklist)

     - [ ] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry

     - [ ] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix (execute if attempt 1 failed)   - Create new file (will overwrite if exists)0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`2. Parses variable definitions from solution_tasks_list.mdThis task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists---

     - [ ] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry

     - [ ] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix (execute if attempt 2 failed)   - **IMPORTANT**: This is a NEW file, NOT appending to `{repo_name}_repo_checklist.md`

     - [ ] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry

        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`

     ### Solution Variables

     (Variables set by tasks for this specific solution)

     - {{solution_path}} → `{solution_path}` (absolute path to .sln file)

     - {{solution_name}} → `{solution_name}` (friendly name without extension)5. Generate Solution Checklist Header:1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.3. Generates solution sections with task checklists and variables sections

     - {{max_build_attempts}} → 3

     - {{restore_status}} → Status of restore operation (output of @task-restore-solution)   - Write file header with repository information

     - {{build_status}} → Status of build operation (output of @task-build-solution)

     - {{kb_search_status}} → KB search result: FOUND | NOT_FOUND (output of @task-search-knowledge-base)   - Format:   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

     - {{kb_file_path}} → Path to KB article if found (output of @task-search-knowledge-base)

     - {{kb_article_status}} → KB creation status (output of @task-create-knowledge-base)     ```

     

     **Retry Attempt 1:**     # Solution Checklist: {repo_name}   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")4. Creates a new file {repo_name}_solution_checklist.md with all solution sections

     - {{fix_applied_attempt_1}} → Fix application status for attempt 1 (output of @task-apply-knowledge-base-fix)

     - {{kb_option_applied_attempt_1}} → KB option number applied in attempt 1 (1, 2, 3, or null)     

     - {{retry_build_status_attempt_1}} → Build status after fix in attempt 1 (output of @task-build-solution-retry)

          Repository: {repo_url}   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

     **Retry Attempt 2:**

     - {{fix_applied_attempt_2}} → Fix application status for attempt 2 (output of @task-apply-knowledge-base-fix)     Generated: [timestamp]

     - {{kb_option_applied_attempt_2}} → KB option number applied in attempt 2 (1, 2, 3, or null)

     - {{retry_build_status_attempt_2}} → Build status after fix in attempt 2 (output of @task-build-solution-retry)     5. Maintains proper markdown formatting

     

     **Retry Attempt 3:**     This checklist tracks progress for all solutions discovered in this repository.

     - {{fix_applied_attempt_3}} → Fix application status for attempt 3 (output of @task-apply-knowledge-base-fix)

     - {{kb_option_applied_attempt_3}} → KB option number applied in attempt 3 (1, 2, 3, or null)     Each solution has its own section with tasks and variables.2. Read Solutions Data: Load solutions from JSON file

     - {{retry_build_status_attempt_3}} → Build status after fix in attempt 3 (output of @task-build-solution-retry)

          Use @execute-solution-task to process each solution with the full build workflow.

     ### For Agents Resuming Work

             - Read file at solutions_json_path** THIS TASK IS SCRIPTABLE **

     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles:     ---

     1. Restore packages

     2. Build solution     ```   - Extract "solutions" array (contains absolute paths to .sln files)

     3. If errors → Search KB → Apply fix if found → Retry

     4. If errors persist → Create KB article for manual resolution

     

     **Quick Reference:**6. Generate Solution Sections:   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}Behavior:

     - [MANDATORY] tasks: Restore (#1) → Build (#2)

     - [CONDITIONAL] tasks execute only when build fails   

     - [RETRY] tasks execute automatically after applying fixes

     - Workflow supports up to 3 build attempts with KB-driven fixes   For each solution in the solutions array:   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

     - **Mark completed tasks with [x]**

        - Extract solution name from path (basename without .sln extension)

     ---

     ```   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`



7. Write Solution Checklist File:   - Format:

   - **Create new file**: `./tasks/{repo_name}_solution_checklist.md` (overwrite if exists)

   - Write header (from step 5) to the new solution checklist file     ```3. Parse Solution Variables: Read .copilot/prompts/solution_tasks_list.md to extract:

   - Write all generated solution sections (from step 6) with their variables sections

   - Add horizontal rule `---` between each solution section for visual clarity     

   - Close file

   - **Do NOT modify** `./tasks/{repo_name}_repo_checklist.md` - that file tracks repository-level tasks only     ## Solution: {solution_name}   - The complete "Variables available:" section content

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`

     

8. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:

   - repo_name: echoed from input     Path: {solution_path}   - All variable definitions that apply to each solution

   - solutions_json_path: echoed from input

   - solutions_total: integer count of solutions processed     

   - checklist_created: boolean (true if file was created)

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)     ### Tasks (Conditional Workflow - See execute-solution-task.md)   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md`1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.This task can be implemented as a Python script that:Description:Description:

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred

   - timestamp: ISO 8601 format datetime when task completed     



8a. Log to Decision Log:     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

   - Append to: results/decision-log.csv

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")

   - The solution_name column (third column) is blank since this is a repository-level task     - [ ] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base4. Prepare Solution Checklist File:   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

   - Status: "SUCCESS" or "FAIL"

     - [ ] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base

9. DEBUG Exit Trace: If DEBUG=1, print:

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"     - [ ] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix   - File: ./tasks/{repo_name}_solution_checklist.md



---     - [ ] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry



Conditional Verbose Output (DEBUG):     - [ ] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix   - Create new file (will overwrite if exists)   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")1. Reads solution data from JSON output file (from @task-find-solutions)

- Purpose: Provide clear trace of solution checklist generation process.

- Activation: Only when DEBUG environment variable equals "1".     - [ ] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.     - [ ] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".     - [ ] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry

- Parse Messages: "[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md".

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".     ### Solution Variables

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 8a.

- Non-Interference: Does not modify success criteria or output contract; purely informational.     5. Generate Solution Checklist Header:



---     (Variables set by tasks for this specific solution)



Output Contract:        - Write file header with repository information2. Parses task definitions from solution_tasks_list.md (optional - can use hardcoded template)This task generates solution-specific task checklists and adds them as sections to an existing repository checklist. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.This prompt generates solution-specific task checklists and adds them as sections to an existing repository checklist.

- repo_name: string (friendly repository name)

- solutions_json_path: string (path to input JSON file)     - {{solution_path}} → `{solution_path}` (absolute path to .sln file)

- solutions_total: integer (number of solutions processed)

- checklist_created: boolean (whether checklist file was successfully created)     - {{solution_name}} → `{solution_name}` (friendly name without extension)   - Format:

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)

- status: SUCCESS | FAIL     - {{max_build_attempts}} → 3

- timestamp: string (ISO 8601 datetime when task completed)

     - {{restore_status}} → Status of restore operation (output of @task-restore-solution)     ```2. Read Solutions Data: Load solutions from JSON file

---

     - {{build_status}} → Status of build operation (output of @task-build-solution)

Variables available:

- {{repo_name}} → Friendly repository name     - {{kb_search_status}} → KB search result: FOUND | NOT_FOUND (output of @task-search-knowledge-base)     # Solution Checklist: {repo_name}

- {{solutions_json_path}} → Path to JSON file containing solutions array

- {{tasks_dir}} → Directory where checklists are saved (./tasks)     - {{kb_file_path}} → Path to KB article if found (output of @task-search-knowledge-base)



---     - {{kb_article_status}} → KB creation status (output of @task-create-knowledge-base)        - Read file at solutions_json_path3. Generates solution sections with task checklists



Task Classification (from solution_tasks_list.md):     

- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)

- CONDITIONAL (execute only on build failure):     **Retry Attempt 1:**     Repository: {repo_url}

  - @task-search-knowledge-base (after build fails)

  - @task-create-knowledge-base (if KB not found)     - {{fix_applied_attempt_1}} → Fix application status for attempt 1 (output of @task-apply-knowledge-base-fix)

  - @task-apply-knowledge-base-fix (if KB found or created)

- RETRY (automatic after fix applied):     - {{kb_option_applied_attempt_1}} → KB option number applied in attempt 1 (1, 2, 3, or null)     Generated: [timestamp]   - Extract "solutions" array (contains absolute paths to .sln files)

  - @task-restore-solution-retry (restore again before retry build)

  - @task-build-solution-retry (build again after fix)     - {{retry_build_status_attempt_1}} → Build status after fix in attempt 1 (output of @task-build-solution-retry)



---          



Implementation Notes:     **Retry Attempt 2:**

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task

2. **Separate File**: Create `{repo_name}_solution_checklist.md` as a NEW file separate from `{repo_name}_repo_checklist.md`     - {{fix_applied_attempt_2}} → Fix application status for attempt 2 (output of @task-apply-knowledge-base-fix)     This checklist tracks progress for all solutions discovered in this repository.   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}4. Creates a new file {repo_name}_solution_checklist.md with all solution sectionsIt allows agents to track progress for each solution within a repository.

3. **File Organization**:

   - `{repo_name}_repo_checklist.md` → Repository-level tasks (clone, search, find-solutions, etc.)     - {{kb_option_applied_attempt_2}} → KB option number applied in attempt 2 (1, 2, 3, or null)

   - `{repo_name}_solution_checklist.md` → Solution-level tasks (restore, build, KB workflow, etc.)

4. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names     - {{retry_build_status_attempt_2}} → Build status after fix in attempt 2 (output of @task-build-solution-retry)     Use @execute-solution-task to process each solution with the full build workflow.

5. Path Parsing: Extract solution name from .sln file path (basename without extension)

6. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)     

7. File Structure: Header + solution sections (each with tasks + variables), separated by `---` horizontal rules

8. **Variables Section**: Each solution gets its own variables section with all solution-level variables from solution_tasks_list.md     **Retry Attempt 3:**        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

9. **KB Option Tracking**: Each retry attempt includes `{{kb_option_applied_attempt_N}}` to track which KB fix option (1, 2, 3) was applied

10. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name) with actual values; leave others as placeholders     - {{fix_applied_attempt_3}} → Fix application status for attempt 3 (output of @task-apply-knowledge-base-fix)

11. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation

12. **Task Completion Marking**: When a task is completed, update the checklist to mark it with [x] (e.g., `- [x] [MANDATORY #1] ...`)     - {{kb_option_applied_attempt_3}} → KB option number applied in attempt 3 (1, 2, 3, or null)     ---

13. Workflow Reference: Point to @execute-solution-task for autonomous execution

14. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output     - {{retry_build_status_attempt_3}} → Build status after fix in attempt 3 (output of @task-build-solution-retry)

15. Contract Compliance: Always save JSON output file with all fields regardless of success/failure

16. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py          ```5. Maintains proper markdown formatting

17. **Programming Language**: All code generated should be written in Python

18. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory     ### For Agents Resuming Work


     

     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

     6. Generate Solution Sections:3. Parse Solution Variables: Read .copilot/prompts/solution_tasks_list.md to extract:

     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles:

     1. Restore packages   

     2. Build solution

     3. If errors → Search KB → Apply fix if found → Retry   For each solution in the solutions array:   - The complete "Variables available:" section content** THIS TASK IS SCRIPTABLE **

     4. If errors persist → Create KB article for manual resolution

        - Extract solution name from path (basename without .sln extension)

     **Quick Reference:**

     - [MANDATORY] tasks: Restore (#1) → Build (#2)   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`   - All variable definitions that apply to each solution

     - [CONDITIONAL] tasks execute only when build fails

     - [RETRY] tasks execute automatically after applying fixes   - Format:

     - Workflow supports up to 3 build attempts with KB-driven fixes

     - Mark completed tasks with [x]     ```   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md`Behavior:

     

     ---     

     ```

     ## Solution: {solution_name}

7. Write Solution Checklist File:

   - **Create new file**: `./tasks/{repo_name}_solution_checklist.md` (overwrite if exists)     

   - Write header (from step 5) to the new solution checklist file

   - Write all generated solution sections (from step 6) with their variables sections     Path: {solution_path}4. Prepare Solution Checklist File:0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`Behavior:

   - Add horizontal rule `---` between each solution section for visual clarity

   - Close file     

   - **Do NOT modify** `./tasks/{repo_name}_repo_checklist.md` - that file tracks repository-level tasks only

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`     ### Tasks (Conditional Workflow - See execute-solution-task.md)   - File: ./tasks/{repo_name}_solution_checklist.md



8. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:     

   - repo_name: echoed from input

   - solutions_json_path: echoed from input     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution   - Create new file (will overwrite if exists)

   - solutions_total: integer count of solutions processed

   - checklist_created: boolean (true if file was created)     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred     - [ ] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`

   - timestamp: ISO 8601 format datetime when task completed

     - [ ] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base

8a. Log to Decision Log:

   - Append to: results/decision-log.csv     - [ ] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.This task can be implemented as a Python script that:1. Parse the required parameters:

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")     - [ ] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry

   - The solution_name column (third column) is blank since this is a repository-level task

   - Status: "SUCCESS" or "FAIL"     - [ ] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix5. Generate Solution Checklist Header:



9. DEBUG Exit Trace: If DEBUG=1, print:     - [ ] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"

     - [ ] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix   - Write file header with repository information   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

---

     - [ ] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry

Conditional Verbose Output (DEBUG):

        - Format:

- Purpose: Provide clear trace of solution checklist generation process.

- Activation: Only when DEBUG environment variable equals "1".     ### Solution Variables

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.          ```   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")1. Reads solution data from JSON output file (from @task-find-solutions)   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".     (Variables set by tasks for this specific solution)

- Parse Messages: "[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md".

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".          # Solution Checklist: {repo_name}

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".     - {{solution_path}} → `{solution_path}` (absolute path to .sln file)

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 8a.

- Non-Interference: Does not modify success criteria or output contract; purely informational.     - {{solution_name}} → `{solution_name}` (friendly name without extension)        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`



---     - {{max_build_attempts}} → 3



Output Contract:     - {{restore_status}} → Status of restore operation (output of @task-restore-solution)     Repository: {repo_url}



- repo_name: string (friendly repository name)     - {{build_status}} → Status of build operation (output of @task-build-solution)

- solutions_json_path: string (path to input JSON file)

- solutions_total: integer (number of solutions processed)     - {{kb_search_status}} → KB search result: FOUND | NOT_FOUND (output of @task-search-knowledge-base)     Generated: [timestamp]2. Parses task definitions from solution_tasks_list.md (optional - can use hardcoded template)   - solutions: Array of solution objects with name and path properties

- checklist_created: boolean (whether checklist file was successfully created)

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)     - {{kb_file_path}} → Path to KB article if found (output of @task-search-knowledge-base)

- status: SUCCESS | FAIL

- timestamp: string (ISO 8601 datetime when task completed)     - {{kb_article_status}} → KB creation status (output of @task-create-knowledge-base)     



---     



Variables available:     **Retry Attempt 1:**     This checklist tracks progress for all solutions discovered in this repository.2. Read Solutions Data: Load solutions from JSON file



- {{repo_name}} → Friendly repository name     - {{fix_applied_attempt_1}} → Fix application status for attempt 1 (output of @task-apply-knowledge-base-fix)

- {{solutions_json_path}} → Path to JSON file containing solutions array

- {{tasks_dir}} → Directory where checklists are saved (./tasks)     - {{kb_option_applied_attempt_1}} → KB option number applied in attempt 1 (1, 2, 3, or null)     Use @execute-solution-task to process each solution with the full build workflow.



---     - {{retry_build_status_attempt_1}} → Build status after fix in attempt 1 (output of @task-build-solution-retry)



Task Classification (from solution_tasks_list.md):             - Read file at solutions_json_path3. Generates solution sections with task checklists     Format: [{"name": "Solution1", "path": "/path/to/solution1.sln"}, ...]



- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)     **Retry Attempt 2:**

- CONDITIONAL (execute only on build failure):

  - @task-search-knowledge-base (after build fails)     - {{fix_applied_attempt_2}} → Fix application status for attempt 2 (output of @task-apply-knowledge-base-fix)     ---

  - @task-create-knowledge-base (if KB not found)

  - @task-apply-knowledge-base-fix (if KB found or created)     - {{kb_option_applied_attempt_2}} → KB option number applied in attempt 2 (1, 2, 3, or null)

- RETRY (automatic after fix applied):

  - @task-restore-solution-retry (restore again before retry build)     - {{retry_build_status_attempt_2}} → Build status after fix in attempt 2 (output of @task-build-solution-retry)     ```   - Extract "solutions" array (contains absolute paths to .sln files)

  - @task-build-solution-retry (build again after fix)

     

---

     **Retry Attempt 3:**

Implementation Notes:

     - {{fix_applied_attempt_3}} → Fix application status for attempt 3 (output of @task-apply-knowledge-base-fix)

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task

2. **Separate File**: Create `{repo_name}_solution_checklist.md` as a NEW file separate from `{repo_name}_repo_checklist.md`     - {{kb_option_applied_attempt_3}} → KB option number applied in attempt 3 (1, 2, 3, or null)6. Generate Solution Sections:   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}4. Appends solution sections to existing repository checklist

3. **File Organization**:

   - `{repo_name}_repo_checklist.md` → Repository-level tasks (clone, search, find-solutions, etc.)     - {{retry_build_status_attempt_3}} → Build status after fix in attempt 3 (output of @task-build-solution-retry)

   - `{repo_name}_solution_checklist.md` → Solution-level tasks (restore, build, KB workflow, etc.)

4. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names        

5. Path Parsing: Extract solution name from .sln file path (basename without extension)

6. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)     ### For Agents Resuming Work

7. File Structure: Header + solution sections (each with tasks + variables), separated by `---` horizontal rules

8. **Variables Section**: Each solution gets its own variables section with all solution-level variables from solution_tasks_list.md        For each solution in the solutions array:   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

9. **KB Option Tracking**: Each retry attempt includes `{{kb_option_applied_attempt_N}}` to track which KB fix option (1, 2, 3) was applied

10. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name) with actual values; leave others as placeholders     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

11. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation

12. Workflow Reference: Point to @execute-solution-task for autonomous execution        - Extract solution name from path (basename without .sln extension)

13. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output

14. Contract Compliance: Always save JSON output file with all fields regardless of success/failure     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles:

15. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py

16. **Programming Language**: All code generated should be written in Python     1. Restore packages   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`5. Maintains proper markdown formatting and preserves existing content2. Locate the existing repository checklist:

17. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

     2. Build solution

     3. If errors → Search KB → Apply fix if found → Retry   - Format:

     4. If errors persist → Create KB article for manual resolution

          ```3. Prepare Solution Checklist File:

     **Quick Reference:**

     - [MANDATORY] tasks: Restore (#1) → Build (#2)     

     - [CONDITIONAL] tasks execute only when build fails

     - [RETRY] tasks execute automatically after applying fixes     ## Solution: {solution_name}   - File: ./tasks/{repo_name}_solution_checklist.md   - File: ./tasks/{repo_name}_checklist.md

     - Workflow supports up to 3 build attempts with KB-driven fixes

     - Mark completed tasks with [x]     

     

     ---     Path: {solution_path}   - Create new file (will overwrite if exists)

     ```

     

7. Write Solution Checklist File:

   - Write header (from step 5) to ./tasks/{repo_name}_solution_checklist.md     ### Tasks (Conditional Workflow - See execute-solution-task.md)   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`Behavior:   - If file does not exist, return FAIL status

   - Write all generated solution sections (from step 6) with their variables sections

   - Add horizontal rule `---` between each solution section for visual clarity     

   - Close file

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution



8. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

   - repo_name: echoed from input

   - solutions_json_path: echoed from input     - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base4. Generate Solution Checklist Header:0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`

   - solutions_total: integer count of solutions processed

   - checklist_created: boolean (true if file was created)     - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred     - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix   - Write file header with repository information

   - timestamp: ISO 8601 format datetime when task completed

     - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry

8a. Log to Decision Log:

   - Append to: results/decision-log.csv     - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry   - Format:3. Parse solution_tasks_list.md to extract ALL solution task directives:

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")     

   - The solution_name column (third column) is blank since this is a repository-level task

   - Status: "SUCCESS" or "FAIL"     ### Solution Variables     ```



9. DEBUG Exit Trace: If DEBUG=1, print:     

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"

     (Variables set by tasks for this specific solution)     # Solution Checklist: {repo_name}1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.   - Extract task names (e.g., @task-restore-solution, @task-build-solution, etc.)

---

     

Conditional Verbose Output (DEBUG):

     - {{solution_path}} → `{solution_path}` (absolute path to .sln file)     

- Purpose: Provide clear trace of solution checklist generation process.

- Activation: Only when DEBUG environment variable equals "1".     - {{solution_name}} → `{solution_name}` (friendly name without extension)

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.     - {{build_attempt}} → Current build attempt number (1-3)     Repository: {repo_url}   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")   - Extract short descriptions for each task

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".     - {{max_build_attempts}} → Maximum allowed build attempts (3)

- Parse Messages: "[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md".

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".     - {{restore_status}} → Status of restore operation (output of @task-restore-solution)     Generated: [timestamp]

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".     - {{build_status}} → Status of build operation (output of @task-build-solution)

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 8a.

- Non-Interference: Does not modify success criteria or output contract; purely informational.     - {{kb_search_status}} → KB search result: FOUND | NOT_FOUND (output of @task-search-knowledge-base)        - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")   - Identify which tasks are mandatory vs optional based on the conditional workflow



---     - {{kb_file_path}} → Path to KB article if found (output of @task-search-knowledge-base)



Output Contract:     - {{kb_create_status}} → KB creation status (output of @task-create-knowledge-base)     This checklist tracks progress for all solutions discovered in this repository.



- repo_name: string (friendly repository name)     - {{fix_applied}} → Whether fix was applied (output of @task-apply-knowledge-base-fix)

- solutions_json_path: string (path to input JSON file)

- solutions_total: integer (number of solutions processed)     - {{retry_restore_status}} → Restore status after fix (output of @task-restore-solution-retry)     Use @execute-solution-task to process each solution with the full build workflow.   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

- checklist_created: boolean (whether checklist file was successfully created)

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)     - {{retry_build_status}} → Build status after fix (output of @task-build-solution-retry)

- status: SUCCESS | FAIL

- timestamp: string (ISO 8601 datetime when task completed)          



---     ### For Agents Resuming Work



Variables available:          ---4. For each solution in the solutions array:



- {{repo_name}} → Friendly repository name     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

- {{solutions_json_path}} → Path to JSON file containing solutions array

- {{tasks_dir}} → Directory where checklists are saved (./tasks)          ```



---     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles restore → build → KB workflow → retry logic.



Task Classification (from solution_tasks_list.md):     2. Read Solutions Data: Load solutions from JSON file   - Create a new section in the repository checklist



- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)     **Quick Reference:**

- CONDITIONAL (execute only on build failure):

  - @task-search-knowledge-base (after build fails)     - [MANDATORY] tasks: Restore (#1) → Build (#2)5. Generate Solution Sections:

  - @task-create-knowledge-base (if KB not found)

  - @task-apply-knowledge-base-fix (if KB found or created)     - [CONDITIONAL] tasks execute only when build fails

- RETRY (automatic after fix applied):

  - @task-restore-solution-retry (restore again before retry build)     - [RETRY] tasks execute automatically after applying fixes      - Read file at solutions_json_path   - Section title: ## Solution: {solution_name}

  - @task-build-solution-retry (build again after fix)

     - Workflow supports up to 3 build attempts with KB-driven fixes

---

     - Mark completed tasks with [x]   For each solution in the solutions array:

Implementation Notes:

     

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task

2. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names     ---   - Extract solution name from path (basename without .sln extension)   - Extract "solutions" array (contains absolute paths to .sln files)   - Add solution path as metadata

3. Path Parsing: Extract solution name from .sln file path (basename without extension)

4. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)     ```

5. File Structure: Header + solution sections (each with tasks + variables), separated by `---` horizontal rules

6. **Variables Section**: Each solution gets its own variables section with all solution-level variables from solution_tasks_list.md   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`

7. **KB Option Tracking**: Each retry attempt now includes `{{kb_option_applied_attempt_N}}` to track which KB fix option (1, 2, 3) was applied, integrating with the enhanced @task-apply-knowledge-base-fix prompt

8. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name) with actual values; leave others as placeholders7. Write Solution Checklist File:

9. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation

10. Workflow Reference: Point to @execute-solution-task for autonomous execution   - Write header (from step 5) to ./tasks/{repo_name}_solution_checklist.md   - Format:   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}   - Generate task checklist using same format as repo tasks

11. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output

12. Contract Compliance: Always save JSON output file with all fields regardless of success/failure   - Write all generated solution sections (from step 6) with their variables sections

13. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py

14. **Programming Language**: All code generated should be written in Python   - Add horizontal rule `---` between each solution section for visual clarity     ```

15. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

   - Close file

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`



8. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:     ## Solution: {solution_name}

   - repo_name: echoed from input

   - solutions_json_path: echoed from input     5. Append all solution sections to the repository checklist file:

   - solutions_total: integer count of solutions processed

   - checklist_created: boolean (true if file was created)     Path: {solution_path}

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred     3. Locate Repository Checklist:   - Preserve existing content (repo tasks section)

   - timestamp: ISO 8601 format datetime when task completed

     ### Tasks (Conditional Workflow - See execute-solution-task.md)

8a. Log to Decision Log:

   - Append to: results/decision-log.csv        - File: ./tasks/{repo_name}_repo_checklist.md   - Add solution sections after repo tasks

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

   - The solution_name column (third column) is blank since this is a repository-level task

   - Status: "SUCCESS" or "FAIL"     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution   - Verify file exists   - Maintain proper markdown formatting



9. DEBUG Exit Trace: If DEBUG=1, print:     - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"

     - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base   - If file does not exist, set status=FAIL and exit

Conditional Verbose Output (DEBUG):

- Purpose: Provide clear trace of solution checklist generation process.     - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix

- Activation: Only when DEBUG environment variable equals "1".

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.     - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry   - If DEBUG=1 and file exists, print: `[debug][generate-solution-task-checklists] found checklist: ./tasks/{repo_name}_repo_checklist.md`6. Solution task checklist format (per solution):

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".     - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".

- Parse Messages: "[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md".        - If DEBUG=1 and file not found, print: `[debug][generate-solution-task-checklists] ERROR: checklist not found`   ```

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.     ### For Agents Resuming Work

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 8a.        ## Solution: {solution_name}

- Non-Interference: Does not modify success criteria or output contract; purely informational.

     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

Output Contract:

- repo_name: string (friendly repository name)     4. Generate Solution Sections:   

- solutions_json_path: string (path to input JSON file)

- solutions_total: integer (number of solutions processed)     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles restore → build → KB workflow → retry logic.

- checklist_created: boolean (whether checklist file was successfully created)

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)           Path: {solution_path}

- status: SUCCESS | FAIL

- timestamp: string (ISO 8601 datetime when task completed)     **Quick Reference:**



Variables available:     - [MANDATORY] tasks: Restore (#1) → Build (#2)   For each solution in the solutions array:   

- {{repo_name}} → Friendly repository name

- {{solutions_json_path}} → Path to JSON file containing solutions array     - [CONDITIONAL] tasks execute only when build fails

- {{tasks_dir}} → Directory where checklists are saved (./tasks)

     - [RETRY] tasks execute automatically after applying fixes   - Extract solution name from path (basename without .sln extension)   ### Tasks (Conditional Workflow - See solution_tasks_list.md)

Task Classification (from solution_tasks_list.md):

- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)     - Workflow supports up to 3 build attempts with KB-driven fixes

- CONDITIONAL (execute only on build failure):

  - @task-search-knowledge-base (after build fails)     - Mark completed tasks with [x]   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`   

  - @task-create-knowledge-base (if KB not found)

  - @task-apply-knowledge-base-fix (if KB found or created)     

- RETRY (automatic after fix applied):

  - @task-restore-solution-retry (restore again before retry build)     ---   - Format:   - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

  - @task-build-solution-retry (build again after fix)

     ```

Implementation Notes:

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task     ```   - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

2. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names

3. Path Parsing: Extract solution name from .sln file path (basename without extension)6. Write Solution Checklist File:

4. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)

5. File Structure: Header + solution sections (each with tasks + variables), separated by `---` horizontal rules   - Write header (from step 4) to ./tasks/{repo_name}_solution_checklist.md     ---   - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base

6. **Variables Section**: Each solution gets its own variables section with all solution-level variables from solution_tasks_list.md

7. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name) with actual values; leave others as placeholders   - Write all generated solution sections (from step 5)

8. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation

9. Workflow Reference: Point to @execute-solution-task for autonomous execution   - Add horizontal rule `---` between each solution section for visual clarity        - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base

10. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output

11. Contract Compliance: Always save JSON output file with all fields regardless of success/failure   - Close file

12. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`     ## Solution: {solution_name}   - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix

````


7. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:        - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry

   - repo_name: echoed from input

   - solutions_json_path: echoed from input     Path: {solution_path}   - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry

   - solutions_total: integer count of solutions processed

   - checklist_created: boolean (true if file was created)        

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred     ### Tasks (Conditional Workflow - See execute-solution-task.md)   ### For Agents Resuming Work

   - timestamp: ISO 8601 format datetime when task completed

        

7a. Log to Decision Log:

   - Append to: results/decision-log.csv     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution   **Next Action:** Find the first uncompleted [MANDATORY #N] task above. If build fails, follow conditional workflow.

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution   

   - The solution_name column (third column) is blank since this is a repository-level task

   - Status: "SUCCESS" or "FAIL"     - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base   **How to Execute:** Invoke `@solution-tasks-list solution_path={solution_path}` which executes the full conditional workflow with automatic retry logic. See `solution_tasks_list.md` for complete workflow details.



8. DEBUG Exit Trace: If DEBUG=1, print:     - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base   

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"

     - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix   **Quick Reference:**

Conditional Verbose Output (DEBUG):

- Purpose: Provide clear trace of solution checklist generation process.     - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry   - [MANDATORY] tasks: Restore (#1) → Build (#2) 

- Activation: Only when DEBUG environment variable equals "1".

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.     - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry   - [CONDITIONAL] tasks execute only when build fails

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".        - [RETRY] tasks execute automatically after applying fixes

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".     ### For Agents Resuming Work   - Workflow supports up to 3 build attempts with KB-driven fixes

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".        - Mark completed tasks with [x]

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 7a.

- Non-Interference: Does not modify success criteria or output contract; purely informational.     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.   



Output Contract:        ---

- repo_name: string (friendly repository name)

- solutions_json_path: string (path to input JSON file)     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles restore → build → KB workflow → retry logic.   ```

- solutions_total: integer (number of solutions processed)

- checklist_created: boolean (whether checklist file was successfully created)     

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)

- status: SUCCESS | FAIL     **Quick Reference:**7. Return a summary message with:

- timestamp: string (ISO 8601 datetime when task completed)

     - [MANDATORY] tasks: Restore (#1) → Build (#2)   - Repository name

Variables available:

- {{repo_name}} → Friendly repository name     - [CONDITIONAL] tasks execute only when build fails   - Total solutions processed

- {{solutions_json_path}} → Path to JSON file containing solutions array

- {{tasks_dir}} → Directory where checklists are saved (./tasks)     - [RETRY] tasks execute automatically after applying fixes   - Checklist file updated



Task Classification (from solution_tasks_list.md):     - Workflow supports up to 3 build attempts with KB-driven fixes   - Location of updated file

- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)

- CONDITIONAL (execute only on build failure):     - Mark completed tasks with [x]

  - @task-search-knowledge-base (after build fails)

  - @task-create-knowledge-base (if KB not found)     ```Variables available:

  - @task-apply-knowledge-base-fix (if KB found or created)

- RETRY (automatic after fix applied):- {{repo_name}} → Friendly repository name

  - @task-restore-solution-retry (restore again before retry build)

  - @task-build-solution-retry (build again after fix)5. Append Solution Sections to Repository Checklist:- {{solutions}} → Array of solution objects



Implementation Notes:   - Open ./tasks/{repo_name}_repo_checklist.md in append mode- {{tasks_dir}} → Directory where checklists are saved (./tasks)

1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task

2. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names   - Write all generated solution sections

3. Path Parsing: Extract solution name from .sln file path (basename without extension)

4. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)   - Preserve all existing content (repo tasks section)Output Contract:

5. File Structure: Header + solution sections, separated by `---` horizontal rules

6. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation   - Add solution sections after repo tasks- repo_name: string

7. Workflow Reference: Point to @execute-solution-task for autonomous execution

8. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output   - Maintain proper markdown formatting- solutions_total: integer

9. Contract Compliance: Always save JSON output file with all fields regardless of success/failure

10. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] appended {{solution_count}} solution sections`- checklist_updated: boolean



````- checklist_path: string

6. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:- generated_at: timestamp

   - repo_name: echoed from input- status: SUCCESS | FAIL

   - solutions_json_path: echoed from input

   - solutions_total: integer count of solutions processedTask Classification (from solution_tasks_list.md):

   - checklist_updated: boolean (true if file was updated)- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)

   - checklist_path: string (./tasks/{repo_name}_repo_checklist.md)- CONDITIONAL (execute only on build failure):

   - status: SUCCESS if all sections generated and appended, FAIL if error occurred  - @task-search-knowledge-base (after build fails)

   - timestamp: ISO 8601 format datetime when task completed  - @task-create-knowledge-base (if KB not found)

  - @task-apply-knowledge-base-fix (if KB found or created)

6a. Log to Decision Log:- RETRY (automatic after fix applied):

   - Append to: results/decision-log.csv  - @task-restore-solution-retry (restore again before retry build)

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated task sections for {{solutions_total}} solutions,{{status}}"  - @task-build-solution-retry (build again after fix)

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")

   - The solution_name column (third column) is blank since this is a repository-level taskImplementation Notes:

   - Status: "SUCCESS" or "FAIL"1. Solutions array must contain objects with "name" and "path" properties

2. Repository checklist must already exist (created by @generate-task-checklists)

7. DEBUG Exit Trace: If DEBUG=1, print:3. Solution sections are appended to existing checklist (not replaced)

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"4. Task numbering for mandatory tasks: #1 (Restore), #2 (Build)

5. Conditional tasks do not have numbers (they execute based on build results)

Conditional Verbose Output (DEBUG):6. Workflow is non-linear with retry loops (not a simple sequential pipeline)

- Purpose: Provide clear trace of solution checklist generation process.7. **Programming Language**: All code generated should be written in Python

- Activation: Only when DEBUG environment variable equals "1".8. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.9. Re-running this prompt will replace existing solution sections with updated content

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.
- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".
- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".
- File Messages: "[debug][generate-solution-task-checklists] found checklist: ./tasks/<name>_repo_checklist.md" or "ERROR: checklist not found".
- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.
- Append Messages: "[debug][generate-solution-task-checklists] appended <N> solution sections".
- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 6a.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_name: string (friendly repository name)
- solutions_json_path: string (path to input JSON file)
- solutions_total: integer (number of solutions processed)
- checklist_created: boolean (whether checklist file was successfully created)
- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)
- status: SUCCESS | FAIL
- timestamp: string (ISO 8601 datetime when task completed)

Variables available:
- {{repo_name}} → Friendly repository name
- {{solutions_json_path}} → Path to JSON file containing solutions array
- {{tasks_dir}} → Directory where checklists are saved (./tasks)

Task Classification (from solution_tasks_list.md):
- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)
- CONDITIONAL (execute only on build failure):
  - @task-search-knowledge-base (after build fails)
  - @task-create-knowledge-base (if KB not found)
  - @task-apply-knowledge-base-fix (if KB found or created)
- RETRY (automatic after fix applied):
  - @task-restore-solution-retry (restore again before retry build)
  - @task-build-solution-retry (build again after fix)

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task
2. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names
3. Path Parsing: Extract solution name from .sln file path (basename without extension)
4. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)
5. File Structure: Header + solution sections (each with tasks + variables), separated by `---` horizontal rules
6. **Variables Section**: Each solution gets its own variables section with all solution-level variables from solution_tasks_list.md
7. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name) with actual values; leave others as placeholders
8. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation
9. Workflow Reference: Point to @execute-solution-task for autonomous execution
10. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output
11. Contract Compliance: Always save JSON output file with all fields regardless of success/failure
12. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_solution_checklists_{repo_name}.py

````