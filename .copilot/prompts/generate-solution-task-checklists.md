------

temperature: 0.1temperature: 0.1

------



@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>@generate-solution-task-checklists repo_name=<required> solutions_json_path=<required>



Task name: generate-solution-task-checklistsTask name: generate-solution-task-checklists



Description:Description:

This task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.

This task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists

** THIS TASK IS SCRIPTABLE **

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:

1. Reads solution data from JSON output file (from @task-find-solutions)

2. Generates solution sections with 10-task checklists (matching execute-solution-task.md format)This task can be implemented as a Python script that:Description:

3. Creates variables sections with retry attempt tracking

4. Creates a new file {repo_name}_solution_checklist.md with all solution sections1. Reads solution data from JSON output file (from @task-find-solutions)

5. Maintains proper markdown formatting

2. Parses variable definitions from solution_tasks_list.mdThis task generates solution-specific task checklists in a separate file for each repository. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.Task name: generate-solution-task-checklists---

Behavior:

3. Generates solution sections with task checklists and variables sections

0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`

4. Creates a new file {repo_name}_solution_checklist.md with all solution sections

1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.

   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")5. Maintains proper markdown formatting

   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`** THIS TASK IS SCRIPTABLE **



2. Read Solutions Data: Load solutions from JSON fileBehavior:

   - Read file at solutions_json_path

   - Extract "solutions" array (contains absolute paths to .sln files)0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`

   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`



3. Prepare Solution Checklist File:1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.This task can be implemented as a Python script that:Description:Description:

   - File: ./tasks/{repo_name}_solution_checklist.md

   - Create new file (will overwrite if exists)   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`

   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")1. Reads solution data from JSON output file (from @task-find-solutions)

4. Generate Solution Checklist Header:

   - Write file header with repository information   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

   - Format:

     ```2. Parses task definitions from solution_tasks_list.md (optional - can use hardcoded template)This task generates solution-specific task checklists and adds them as sections to an existing repository checklist. The checklists allow agents to track progress for each solution within a repository. This is a file generation task that CAN be implemented as a script.This prompt generates solution-specific task checklists and adds them as sections to an existing repository checklist.

     # Solution Checklist: {repo_name}

     2. Read Solutions Data: Load solutions from JSON file

     Repository: {repo_url}

     Generated: [timestamp]   - Read file at solutions_json_path3. Generates solution sections with task checklists

     

     ---   - Extract "solutions" array (contains absolute paths to .sln files)

     

     ```   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}4. Creates a new file {repo_name}_solution_checklist.md with all solution sectionsIt allows agents to track progress for each solution within a repository.



5. Generate Solution Sections:   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

   

   For each solution in the solutions array:5. Maintains proper markdown formatting

   - Extract solution name from path (basename without .sln extension)

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`3. Parse Solution Variables: Read .copilot/prompts/solution_tasks_list.md to extract:

   - Format:

     ```   - The complete "Variables available:" section content** THIS TASK IS SCRIPTABLE **

     

     ## Solution: {solution_name}   - All variable definitions that apply to each solution

     

     Path: `{solution_path}`   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] extracted variables from solution_tasks_list.md`Behavior:

     

     ### Tasks

     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution4. Prepare Solution Checklist File:0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`Behavior:

     - [ ] [CONDITIONAL #3] Search knowledge base for error fix @task-search-knowledge-base

     - [ ] [CONDITIONAL #4] Create knowledge base article @task-create-knowledge-base   - File: ./tasks/{repo_name}_solution_checklist.md

     - [ ] [CONDITIONAL #5 - Attempt 1] Apply fix from KB @task-apply-knowledge-base-fix

     - [ ] [CONDITIONAL #6 - Attempt 1] Retry build after fix @task-build-solution-retry   - Create new file (will overwrite if exists)

     - [ ] [CONDITIONAL #7 - Attempt 2] Apply fix from KB @task-apply-knowledge-base-fix

     - [ ] [CONDITIONAL #8 - Attempt 2] Retry build after fix @task-build-solution-retry   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`

     - [ ] [CONDITIONAL #9 - Attempt 3] Apply fix from KB @task-apply-knowledge-base-fix

     - [ ] [CONDITIONAL #10 - Attempt 3] Retry build after fix @task-build-solution-retry1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.This task can be implemented as a Python script that:1. Parse the required parameters:

     

     ### Solution Variables5. Generate Solution Checklist Header:

     

     (Variables set by tasks for this specific solution)   - Write file header with repository information   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

     

     - solution_path → {solution_path}   - Format:

     - solution_name → {solution_name}

     - max_build_attempts → 3     ```   - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")1. Reads solution data from JSON output file (from @task-find-solutions)   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")

     - restore_status → NOT_EXECUTED

     - build_status → NOT_EXECUTED     # Solution Checklist: {repo_name}

     - kb_search_status → NOT_EXECUTED

     - kb_file_path → N/A        - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

     - kb_article_status → NOT_EXECUTED

          Repository: {repo_url}

     **Retry Attempt 1:**

     - fix_applied_attempt_1 → NOT_EXECUTED     Generated: [timestamp]2. Parses task definitions from solution_tasks_list.md (optional - can use hardcoded template)   - solutions: Array of solution objects with name and path properties

     - kb_option_applied_attempt_1 → null

     - retry_build_status_attempt_1 → NOT_EXECUTED     

     

     **Retry Attempt 2:**     This checklist tracks progress for all solutions discovered in this repository.2. Read Solutions Data: Load solutions from JSON file

     - fix_applied_attempt_2 → NOT_EXECUTED

     - kb_option_applied_attempt_2 → null     Use @execute-solution-task to process each solution with the full build workflow.

     - retry_build_status_attempt_2 → NOT_EXECUTED

             - Read file at solutions_json_path3. Generates solution sections with task checklists     Format: [{"name": "Solution1", "path": "/path/to/solution1.sln"}, ...]

     **Retry Attempt 3:**

     - fix_applied_attempt_3 → NOT_EXECUTED     ---

     - kb_option_applied_attempt_3 → null

     - retry_build_status_attempt_3 → NOT_EXECUTED     ```   - Extract "solutions" array (contains absolute paths to .sln files)

     

     ---

     

     ```6. Generate Solution Sections:   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}4. Appends solution sections to existing repository checklist



6. Write Solution Checklist File:   

   - Write header (from step 4) to ./tasks/{repo_name}_solution_checklist.md

   - Write all generated solution sections (from step 5) with their variables sections   For each solution in the solutions array:   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] loaded {{solution_count}} solutions from JSON`

   - Add horizontal rule `---` between each solution section for visual clarity

   - Close file   - Extract solution name from path (basename without .sln extension)

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] wrote {{solution_count}} solution sections to file`

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`5. Maintains proper markdown formatting and preserves existing content2. Locate the existing repository checklist:

7. Structured Output: Save JSON object to output/{repo_name}_task6_generate-solution-checklists.json with:

   - repo_name: echoed from input   - Format:

   - solutions_json_path: echoed from input

   - solutions_total: integer count of solutions processed     ```3. Prepare Solution Checklist File:

   - checklist_created: boolean (true if file was created)

   - checklist_path: string (./tasks/{repo_name}_solution_checklist.md)     

   - status: SUCCESS if all sections generated and file created, FAIL if error occurred

   - timestamp: ISO 8601 format datetime when task completed     ## Solution: {solution_name}   - File: ./tasks/{repo_name}_solution_checklist.md   - File: ./tasks/{repo_name}_checklist.md



8. Log to Decision Log:     

   - Append to: results/decision-log.csv

   - Append row with: "{{timestamp}},{{repo_name}},,generate-solution-task-checklists,Generated solution checklist with {{solutions_total}} solutions,{{status}}"     Path: {solution_path}   - Create new file (will overwrite if exists)

   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")

   - The solution_name column (third column) is blank since this is a repository-level task     

   - Status: "SUCCESS" or "FAIL"

     ### Tasks (Conditional Workflow - See execute-solution-task.md)   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/{repo_name}_solution_checklist.md`Behavior:   - If file does not exist, return FAIL status

9. DEBUG Exit Trace: If DEBUG=1, print:

   "[debug][generate-solution-task-checklists] EXIT repo_name='{{repo_name}}' status={{status}} solutions_total={{solutions_total}}"     



Conditional Verbose Output (DEBUG):     - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution

- Purpose: Provide clear trace of solution checklist generation process.

- Activation: Only when DEBUG environment variable equals "1".     - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution

- Format Guarantees: Always starts with prefix [debug][generate-solution-task-checklists] allowing simple grep filtering.

- Entry Message: "[debug][generate-solution-task-checklists] START repo_name='<name>' solutions_json_path='<path>'" emitted before step 1.     - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base4. Generate Solution Checklist Header:0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-solution-task-checklists] START repo_name='{{repo_name}}' solutions_json_path='{{solutions_json_path}}'`

- Parameter Messages: "[debug][generate-solution-task-checklists] repo_name: <name>, solutions_json_path: <path>".

- Load Messages: "[debug][generate-solution-task-checklists] loaded <N> solutions from JSON".     - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base

- File Messages: "[debug][generate-solution-task-checklists] creating solution checklist: ./tasks/<name>_solution_checklist.md".

- Generation Messages: "[debug][generate-solution-task-checklists] generating section for: <solution_name>" for each solution.     - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix   - Write file header with repository information

- Write Messages: "[debug][generate-solution-task-checklists] wrote <N> solution sections to file".

- Exit Message: "[debug][generate-solution-task-checklists] EXIT repo_name='<name>' status=<SUCCESS|FAIL> solutions_total=<N>" emitted after step 8.     - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry

- Non-Interference: Does not modify success criteria or output contract; purely informational.

     - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry   - Format:3. Parse solution_tasks_list.md to extract ALL solution task directives:

Output Contract:

- repo_name: string (friendly repository name)     

- solutions_json_path: string (path to input JSON file)

- solutions_total: integer (number of solutions processed)     ### Solution Variables     ```

- checklist_created: boolean (whether checklist file was successfully created)

- checklist_path: string (path to created solution checklist file: ./tasks/{repo_name}_solution_checklist.md)     

- status: SUCCESS | FAIL

- timestamp: string (ISO 8601 datetime when task completed)     (Variables set by tasks for this specific solution)     # Solution Checklist: {repo_name}1. Input Parameters: You are given repo_name and solutions_json_path from the calling context.   - Extract task names (e.g., @task-restore-solution, @task-build-solution, etc.)



Variables available:     

- {{repo_name}} → Friendly repository name

- {{solutions_json_path}} → Path to JSON file containing solutions array     - {{solution_path}} → `{solution_path}` (absolute path to .sln file)     

- {{tasks_dir}} → Directory where checklists are saved (./tasks)

     - {{solution_name}} → `{solution_name}` (friendly name without extension)

Task Numbering and Format:

Tasks are numbered #1-10 with specific attempt numbers for retry tasks:     - {{build_attempt}} → Current build attempt number (1-3)     Repository: {repo_url}   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")   - Extract short descriptions for each task

- [MANDATORY #1] Restore NuGet packages

- [MANDATORY #2] Build solution (Clean + Build)     - {{max_build_attempts}} → Maximum allowed build attempts (3)

- [CONDITIONAL #3] Search knowledge base for error fix

- [CONDITIONAL #4] Create knowledge base article     - {{restore_status}} → Status of restore operation (output of @task-restore-solution)     Generated: [timestamp]

- [CONDITIONAL #5 - Attempt 1] Apply fix from KB

- [CONDITIONAL #6 - Attempt 1] Retry build after fix     - {{build_status}} → Status of build operation (output of @task-build-solution)

- [CONDITIONAL #7 - Attempt 2] Apply fix from KB

- [CONDITIONAL #8 - Attempt 2] Retry build after fix     - {{kb_search_status}} → KB search result: FOUND | NOT_FOUND (output of @task-search-knowledge-base)        - solutions_json_path: Path to JSON file from @task-find-solutions (e.g., "output/{repo_name}_task5_find-solutions.json")   - Identify which tasks are mandatory vs optional based on the conditional workflow

- [CONDITIONAL #9 - Attempt 3] Apply fix from KB

- [CONDITIONAL #10 - Attempt 3] Retry build after fix     - {{kb_file_path}} → Path to KB article if found (output of @task-search-knowledge-base)



Implementation Notes:     - {{kb_create_status}} → KB creation status (output of @task-create-knowledge-base)     This checklist tracks progress for all solutions discovered in this repository.

1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task

2. Solutions Array: Read from JSON file at solutions_json_path, extract basename for solution names     - {{fix_applied}} → Whether fix was applied (output of @task-apply-knowledge-base-fix)

3. Path Parsing: Extract solution name from .sln file path (basename without extension)

4. File Creation: Create new file ./tasks/{repo_name}_solution_checklist.md (overwrite if exists)     - {{retry_restore_status}} → Restore status after fix (output of @task-restore-solution-retry)     Use @execute-solution-task to process each solution with the full build workflow.   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] repo_name: {{repo_name}}, solutions_json_path: {{solutions_json_path}}`

5. File Structure: Header + solution sections (each with 10 tasks + variables), separated by `---` horizontal rules

6. **Variables Section**: Each solution gets its own variables section with:     - {{retry_build_status}} → Build status after fix (output of @task-build-solution-retry)

   - Base variables: solution_path, solution_name, max_build_attempts, restore_status, build_status, kb_search_status, kb_file_path, kb_article_status

   - Retry Attempt 1 variables: fix_applied_attempt_1, kb_option_applied_attempt_1, retry_build_status_attempt_1          

   - Retry Attempt 2 variables: fix_applied_attempt_2, kb_option_applied_attempt_2, retry_build_status_attempt_2

   - Retry Attempt 3 variables: fix_applied_attempt_3, kb_option_applied_attempt_3, retry_build_status_attempt_3     ### For Agents Resuming Work

7. Variable Initialization: Initialize solution-specific variables (solution_path, solution_name, max_build_attempts=3) with actual values; set others to NOT_EXECUTED or N/A

8. Markdown Format: Use `- [ ]` for unchecked tasks, maintain consistent indentation          ---4. For each solution in the solutions array:

9. Workflow Reference: Point to @execute-solution-task for autonomous execution

10. Error Handling: If JSON file not found or invalid, set status=FAIL and save error to JSON output     **Next Action:** Use `@execute-solution-task` to execute the full conditional workflow with automatic retry logic.

11. Contract Compliance: Always save JSON output file with all fields regardless of success/failure

12. Script Location: Save generated script to temp-script/ directory with naming pattern: task6_generate_solution_checklists_{repo_name}.py          ```

13. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired

     **How to Execute:** Invoke `@execute-solution-task solution_path="{solution_path}"` which handles restore → build → KB workflow → retry logic.

     2. Read Solutions Data: Load solutions from JSON file   - Create a new section in the repository checklist

     **Quick Reference:**

     - [MANDATORY] tasks: Restore (#1) → Build (#2)5. Generate Solution Sections:

     - [CONDITIONAL] tasks execute only when build fails

     - [RETRY] tasks execute automatically after applying fixes      - Read file at solutions_json_path   - Section title: ## Solution: {solution_name}

     - Workflow supports up to 3 build attempts with KB-driven fixes

     - Mark completed tasks with [x]   For each solution in the solutions array:

     

     ---   - Extract solution name from path (basename without .sln extension)   - Extract "solutions" array (contains absolute paths to .sln files)   - Add solution path as metadata

     ```

   - If DEBUG=1, print: `[debug][generate-solution-task-checklists] generating section for: {{solution_name}}`

7. Write Solution Checklist File:

   - Write header (from step 5) to ./tasks/{repo_name}_solution_checklist.md   - Format:   - Convert paths to solution objects: {"name": basename without extension, "path": absolute path}   - Generate task checklist using same format as repo tasks

   - Write all generated solution sections (from step 6) with their variables sections

   - Add horizontal rule `---` between each solution section for visual clarity     ```

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