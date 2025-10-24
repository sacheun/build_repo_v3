@generate-repo-task-checklists input=<optional> append=<optional>

Task name: generate-repo-task-checklists

Description:
This task generates task checklists for all repositories in the input file. The checklists allow agents to pick up work or resume when a previous run stops. This is a file generation task that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Reads repository URLs from input file
2. Parses task definitions from repo_tasks_list.md
3. Generates master checklist tracking all repositories
4. Generates individual checklist files for each repository
5. Supports append mode to add new repositories without replacing existing ones

Behavior:
0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-repo-task-checklists] START input='{{input}}' append={{append}}`

1. Input Parameters: You are given input (file path) and append (boolean) from the calling context.
   Defaults:
      input = "repositories.txt"
      append = false
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] using input_file: {{input}}, append_mode: {{append}}`

2. Directory Preparation:
   
   **If append = false (default):**
   - Remove all existing files in ./tasks directory if it exists
   - Create ./tasks directory (if it doesn't exist)
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] cleaned tasks directory (append=false)`
   
   **If append = true:**
   - Keep existing files in ./tasks directory
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] preserving existing tasks (append=true)`

3. Read Input File: Read the input file to get all repository URLs
   - Parse line by line, skip empty lines and comments (lines starting with #)
   - Extract repository URLs
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{count}} repositories in input file`

4. Determine Repositories to Process:
   
   **If append = false:**
   - Process all repositories from input file
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] processing all {{count}} repositories`
   
   **If append = true:**
   - Read existing ./tasks/all_repository_checklist.md (if it exists)
   - Extract list of repositories already tracked in master checklist
   - Compare with repositories from input file
   - Identify new repositories = repositories in input file but NOT in master checklist
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{existing_count}} existing repos, {{new_count}} new repos`
   - Only process these new repositories

5. Parse Task Definitions: Read .copilot/prompts/repo_tasks_list.md to extract:
   - All task directives (e.g., @task-clone-repo, @task-search-readme, etc.)
   - Short descriptions for each task
   - The complete "Variables available:" section content
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] extracted {{task_count}} tasks from repo_tasks_list.md`

6. Generate or Update Master Checklist:
   - File: ./tasks/all_repository_checklist.md
   
   **If append = false:**
   - Create new file with all repositories from input file
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] creating new master checklist`
   - Format:
     ```
     # All Repositories Checklist
     
     Generated: [timestamp]
     Source: [input file path]
     
     ## Repositories
     
     - [ ] repo_name_1 [repo_url_1]
     - [ ] repo_name_2 [repo_url_2]
     - [ ] repo_name_3 [repo_url_3]
     ...
     ```
   
   **If append = true:**
   - If file exists:
     - Read existing content
     - Preserve existing repository entries (keep their checkbox status)
     - Append new repositories to the "## Repositories" section
     - Update "Generated" timestamp
     - If DEBUG=1, print: `[debug][generate-repo-task-checklists] appending {{new_count}} repos to master checklist`
   - If file does not exist:
     - Create new file with new repositories only
     - If DEBUG=1, print: `[debug][generate-repo-task-checklists] creating master checklist (no existing file)`

7. Generate Individual Checklist Files:
   
   For each repository to process:
   - Extract repo_name from URL
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] generating checklist for: {{repo_name}}`
   - File: ./tasks/{repo_name}_repo_checklist.md
   
   **If append = false:**
   - Create checklist for all repositories from input file
   
   **If append = true:**
   - Only create checklists for new repositories (not already in master checklist)
   - Skip creating files for repositories that already have checklist files
   - If DEBUG=1 and skipping, print: `[debug][generate-repo-task-checklists] skipping existing: {{repo_name}}`
   - If a repository is in input file but doesn't have a checklist file, create it
   
   - Format:
     ```
     # Task Checklist: {repo_name}
     
     Repository: {repo_url}
     Generated: [timestamp]
     
     ## Repo Tasks (Sequential Pipeline - Complete in Order)
     
     - [ ] [MANDATORY #1] Clone repository to local directory @task-clone-repo
     - [ ] [MANDATORY #2] Search for README file in repository @task-search-readme
     - [ ] [CONDITIONAL - NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
     - [ ] [CONDITIONAL - NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme
     - [ ] [MANDATORY #3] Find all solution files in repository @task-find-solutions
     - [ ] [MANDATORY #4] Generate solution-specific task sections in checklist @generate-solution-task-checklists
     
     ## For Agents Resuming Work
     
     **Next Action:** 
     1. Check if all [MANDATORY] tasks are completed
     2. If YES and {{readme_content}} is not blank and not "NONE", execute @task-scan-readme
     3. If {{commands_extracted}} is not blank and not "NONE", execute @task-execute-readme
     4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated
     
     **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-clone-repo`) as defined in `repo_tasks_list.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.
     
     **Quick Reference:**
     - [MANDATORY] tasks must be completed in numbered order (#1 → #2 → #3 → #4)
     - [CONDITIONAL - NON-SCRIPTABLE] @task-scan-readme executes when {{readme_content}} is not blank and not "NONE"
     - [CONDITIONAL - NON-SCRIPTABLE] @task-execute-readme executes when {{commands_extracted}} is not blank and not "NONE"
     - Mark completed tasks with [x]
     
     ## Repo Variables Available
     
     [Content dynamically extracted from repo_tasks_list.md "Variables available:" section]
     ```
   - Task classification:
     - MANDATORY (sequential): @task-clone-repo (#1), @task-search-readme (#2), @task-find-solutions (#3), @generate-solution-task-checklists (#4)
     - OPTIONAL: @task-scan-readme, @task-execute-readme
   - **Dynamic Variables Section:** Extract the entire "Variables available:" section from repo_tasks_list.md and include it verbatim in each generated checklist under "## Repo Variables Available" heading

8. Structured Output: Save JSON object to output/generate-repo-task-checklists.json with:
   - input_file: path to input file used
   - append_mode: boolean (true/false)
   - repositories_total: integer (total in input file)
   - repositories_processed: integer (new repos if append=true, all if append=false)
   - repositories_skipped: integer (existing repos if append=true, 0 if append=false)
   - checklists_generated: integer (number of individual checklist files created)
   - master_checklist_path: string (./tasks/all_repository_checklist.md)
   - individual_checklists_path: string (./tasks/)
   - status: SUCCESS if all files generated, FAIL if error occurred
   - timestamp: ISO 8601 format datetime when task completed

9. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][generate-repo-task-checklists] EXIT status={{status}} processed={{repositories_processed}} generated={{checklists_generated}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace of checklist generation process.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][generate-repo-task-checklists] allowing simple grep filtering.
- Entry Message: "[debug][generate-repo-task-checklists] START input='<file>' append=<bool>" emitted before step 1.
- Parameter Messages: "[debug][generate-repo-task-checklists] using input_file: <file>, append_mode: <bool>".
- Directory Messages: "[debug][generate-repo-task-checklists] cleaned tasks directory" or "preserving existing tasks".
- Count Messages: "[debug][generate-repo-task-checklists] found <N> repositories in input file".
- Mode Messages: "[debug][generate-repo-task-checklists] processing all <N> repositories" or "found <E> existing, <N> new repos".
- Task Extraction: "[debug][generate-repo-task-checklists] extracted <N> tasks from repo_tasks_list.md".
- Generation Messages: "[debug][generate-repo-task-checklists] generating checklist for: <repo_name>" for each repository.
- Skip Messages: "[debug][generate-repo-task-checklists] skipping existing: <repo_name>" when append=true.
- Exit Message: "[debug][generate-repo-task-checklists] EXIT status=<SUCCESS|FAIL> processed=<N> generated=<N>" emitted after step 8.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- input_file: string (path to input file with repository URLs)
- append_mode: boolean (whether append mode was used)
- repositories_total: integer (total repositories found in input file)
- repositories_processed: integer (repositories for which checklists were generated)
- repositories_skipped: integer (repositories skipped due to existing checklists in append mode)
- checklists_generated: integer (number of individual checklist files created)
- master_checklist_path: string (path to master checklist file)
- individual_checklists_path: string (directory containing individual checklists)
- status: SUCCESS | FAIL
- timestamp: string (ISO 8601 datetime when task completed)

Variables available:
- {{input_file}} → text file path with repository URLs
- {{append}} → boolean flag to append new repositories instead of replacing all
- {{tasks_dir}} → directory where checklists are saved (./tasks)

Output Contract:
- repositories_total: integer (total in input file)
- repositories_processed: integer (new repos added if append=true, all if append=false)
- repositories_skipped: integer (existing repos if append=true, 0 if append=false)
- append_mode: boolean
- checklists_generated: integer (number of individual checklist files created)
- master_checklist_path: string
- individual_checklists_path: string
- generated_at: timestamp
- status: SUCCESS | FAIL

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task
2. URL Parsing: Extract friendly repo names from URLs (e.g., last segment after final /)
3. Dynamic Task Extraction: Parse .copilot/prompts/repo_tasks_list.md to get task list and variables section
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure
5. Markdown Format: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes
6. Timestamp Format: Use ISO 8601 format (e.g., "2025-10-24T14:30:00")
7. Error Handling: If input file not found, set status=FAIL and return with empty results
8. Append Mode Logic: Compare normalized URLs (trim trailing slashes, case-insensitive), preserve existing entries, only create files for new repos
9. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_task_checklists.py (or .ps1/.sh)
10. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired
