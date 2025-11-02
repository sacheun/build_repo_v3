---
temperature: 0.0
---

@generate-repo-task-checklists input=<optional> append=<optional>

Task name: generate-repo-task-checklists

## Description:
This task generates task checklists for all repositories in the input file. The checklists allow agents to pick up work or resume when a previous run stops. This is a file generation task that CAN be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-repo-task-checklists] START input='{{input}}' append={{append}}`

### Step 2 (MANDATORY)
Input Parameters: You are given input (file path) and append (boolean) from the calling context.
   Defaults:
      input = "repositories.txt"
      append = false
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] using input_file: {{input}}, append_mode: {{append}}`

Directory Preparation:   
   **If append = false (default):**
   - **Remove the entire ./tasks directory if it exists** (including all files and subdirectories)
   - **Remove the entire ./output directory if it exists** (including all output JSON files)
   - **Remove the entire ./temp-script directory if it exists** (including all generated scripts)
   - Create fresh ./tasks, ./output, and ./temp-script directories
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] removed and recreated tasks, output, and temp-script directories (append=false)`
   - **WARNING**: This will delete all existing checklists, solution checklists, output files, and generated scripts
   
   **If append = true:**
   - Keep existing ./tasks directory and all its contents
   - Keep existing ./output directory and all its contents
   - Keep existing ./temp-script directory and all its contents
   - Create ./tasks, ./output, and ./temp-script directories if they don't exist
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] preserving existing tasks, output, and temp-script (append=true)`

### Step 3 (MANDATORY)
Read Input File: Read the input file to get all repository URLs
   - Parse line by line, skip empty lines and comments (lines starting with #)
   - Extract repository URLs
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{count}} repositories in input file`

### Step 4 (MANDATORY)
Determine Repositories to Process:
   
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

### Step 5 (MANDATORY)
Parse Task Definitions: Read .github\prompts\repo_tasks_list.prompt.md to extract:
   - All task directives (e.g., @task-clone-repo, @task-search-readme, etc.)
   - Short descriptions for each task
   - The complete "Variables available:" section content
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] extracted {{task_count}} tasks from .github\prompts\repo_tasks_list.prompt.md`

### Step 6 (MANDATORY)
Generate or Update Master Checklist:
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

### Step 8 (MANDATORY)
Generate Individual Checklist Files:
   
   For each repository to process:
   - Extract repo_name from URL
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] generating checklist for: {{repo_name}}`
   **Important** Always name the checklist exactly `./tasks/{repo_name}_repo_checklist.md` (no alternate paths or filenames).
   
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
     
     - [ ] [MANDATORY #1] [SCRIPTABLE] Clone repository to local directory @task-clone-repo
     - [ ] [MANDATORY #2] [SCRIPTABLE] Search for README file in repository @task-search-readme
     - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
     - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme
     - [ ] [MANDATORY #3] [SCRIPTABLE] Find all solution files in repository @task-find-solutions
     - [ ] [MANDATORY #4] [SCRIPTABLE] Generate solution-specific task sections in checklist @generate-solution-task-checklists
     
     ## For Agents Resuming Work
     
     **Next Action:** 
     1. Check if all [MANDATORY] tasks are completed
     2. If YES and {{readme_content}} is not blank and not "NONE", execute @task-scan-readme
     3. If {{commands_extracted}} is not blank and not "NONE", execute @task-execute-readme
     4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

     **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-clone-repo`) as defined in `.github\prompts\repo_tasks_list.prompt.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.

     **Quick Reference:**
     - [MANDATORY] tasks must be completed in numbered order (#1 → #2 → #3 → #4)
     - [CONDITIONAL] [NON-SCRIPTABLE] @task-scan-readme executes when {{readme_content}} is not blank and not "NONE"
     - [CONDITIONAL] [NON-SCRIPTABLE] @task-execute-readme executes when {{commands_extracted}} is not blank and not "NONE"
     - [SCRIPTABLE] tasks can be automated with scripts
     - [NON-SCRIPTABLE] tasks require AI reasoning and direct tool calls
     - Mark completed tasks with [x]
     
     ## Repo Variables Available
     
     ### Variables available:
     [Content dynamically extracted from .github\prompts\repo_tasks_list.prompt.md "Variables available:" section]
     
     ```
   - Task classification:
     - MANDATORY (sequential): @task-clone-repo (#1), @task-search-readme (#2), @task-find-solutions (#3), @generate-solution-task-checklists (#4)
     - CONDITIONAL: @task-scan-readme, @task-execute-readme
     - SCRIPTABLE: @task-clone-repo, @task-search-readme, @task-find-solutions, @generate-solution-task-checklists
     - NON-SCRIPTABLE: @task-scan-readme, @task-execute-readme
   - **Dynamic Variables Section:** Extract the entire "### Variables available:" section from .github\prompts\repo_tasks_list.prompt.md and include it verbatim in each generated checklist under "## Repo Variables Available" heading

### Step 8 (MANDATORY)
Structured Output: Save JSON object to output/generate-repo-task-checklists.json with:
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

### Step 9 (MANDATORY)
DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][generate-repo-task-checklists] EXIT status={{status}} processed={{repositories_processed}} generated={{checklists_generated}}"

## Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. URL Parsing: Extract friendly repo names from URLs (e.g., last segment after final /)
3. Dynamic Task Extraction: Parse .github\prompts\repo_tasks_list.prompt.md to get task list and variables section
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure
5. Markdown Format: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes
6. Timestamp Format: Use ISO 8601 format (e.g., "2025-10-24T14:30:00")
7. Error Handling: If input file not found, set status=FAIL and return with empty results
8. Append Mode Logic: Compare normalized URLs (trim trailing slashes, case-insensitive), preserve existing entries, only create files for new repos
9. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_task_checklists.py (or .ps1/.sh)

