@generate-task-checklists input=<optional> append=<optional>
---
temperature: 0.1
---

Description:
This prompt generates task checklists for all repositories in the input file.
The checklists allow agents to pick up work or resume when a previous run stops.

Behavior:
1. If the user provides `input=` and `append=` when invoking this prompt, use them.
   Defaults:
      input = "repositories.txt"
      append = false

2. Clean and prepare the tasks directory:
   
   **If append = false (default):**
   - Remove all existing files in ./tasks directory if it exists
   - Create ./tasks directory (if it doesn't exist)
   
   **If append = true:**
   - Keep existing files in ./tasks directory
   - Create ./tasks directory if it doesn't exist
   - Read existing all_repository_checklist.md to get list of already tracked repositories
   - Read input file to get list of all repositories
   - Compare the two lists to identify new repositories (in input but not in master checklist)
   - Only process the new repositories (skip repositories already in master checklist)

3. Read the input file to get all repository URLs

4. Determine repositories to process:
   
   **If append = false:**
   - Process all repositories from input file
   
   **If append = true:**
   - Read existing ./tasks/all_repository_checklist.md (if it exists)
   - Extract list of repositories already tracked in master checklist
   - Compare with repositories from input file
   - Identify new repositories = repositories in input file but NOT in master checklist
   - Only process these new repositories

5. Parse repo_tasks_list.md to extract ALL task directives:
   - Extract task names (e.g., @task-clone-repo, @task-execute-readme, etc.)
   - Extract short descriptions for each task

6. Generate or update the master checklist file:
   - File: ./tasks/all_repository_checklist.md
   
   **If append = false:**
   - Create new file with all repositories from input file
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
     - Append new repositories to the "## Repositories" section
     - Update "Generated" timestamp
     - Preserve existing repository entries (keep their checkbox status)
   - If file does not exist:
     - Create new file with new repositories only

7. For each repository to process, generate an individual checklist file:
   - File: ./tasks/{repo_name}_checklist.md
   
   **If append = false:**
   - Create checklist for all repositories from input file
   
   **If append = true:**
   - Only create checklists for new repositories (not already in master checklist)
   - Skip creating files for repositories that already have checklist files
   - If a repository is in input file but doesn't have a checklist file, create it
   
   - Format:
     ```
     # Task Checklist: {repo_name}
     
     Repository: {repo_url}
     Generated: [timestamp]
     
     ## Tasks (Sequential Pipeline - Complete in Order)
     
     - [ ] [MANDATORY #1] Clone repository to local directory @task-clone-repo
     - [ ] [MANDATORY #2] Search for README file in repository @task-search-readme
     - [ ] [OPTIONAL] Scan README and extract setup commands @task-scan-readme
     - [ ] [OPTIONAL] Execute safe commands from README @task-execute-readme
     - [ ] [MANDATORY #3] Find all solution files in repository @task-find-solutions
     - [ ] [MANDATORY #4] Process and build each solution @task-process-solutions
     
     ## For Agents Resuming Work
     
     **Next Action:** Find the first uncompleted [MANDATORY #N] task above.
     
     **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-clone-repo`) as defined in `repo_tasks_list.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.
     
     **Quick Reference:**
     - [MANDATORY] tasks must be completed in numbered order (#1 → #2 → #3 → #4)
     - [OPTIONAL] tasks can be skipped if not applicable
     - Mark completed tasks with [x]
     ```
   - Task classification:
     - MANDATORY (sequential): @task-clone-repo (#1), @task-search-readme (#2), @task-find-solutions (#3), @task-process-solutions (#4)
     - OPTIONAL: @task-scan-readme, @task-execute-readme

8. Return a summary message with:
   - Total repositories found in input file
   - Total repositories processed (new repositories if append=true, all if append=false)
   - Total repositories skipped (if append=true)
   - Location of generated checklist files

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
1. Extract friendly repo names from URLs (e.g., "owner/repo" from GitHub URLs)
2. Parse repo_tasks_list.md to get task names and descriptions dynamically
3. Generate all checklist files in the ./tasks directory
4. Use Markdown checkbox format: `- [ ]` for unchecked, `- [x]` for checked
5. Include timestamps for tracking when checklists were generated
6. Ensure all files are created even if some repositories have issues
7. **Append Mode Logic:**
   - Parse existing all_repository_checklist.md to extract repository URLs
   - Compare URLs (normalize for comparison, e.g., trim trailing slashes)
   - Only process repositories that don't exist in master checklist
   - Append new repository entries to master checklist (preserve existing entries)
   - Only create individual checklist files for new repositories
8. **Programming Language**: All code generated should be written in Python
9. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory
