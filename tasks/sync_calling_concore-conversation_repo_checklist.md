# Task Checklist: sync_calling_concore-conversation

Repository: https://skype.visualstudio.com/SCC/_git/sync_calling_concore-conversation
Generated: 2025-11-04T02:01:48.502724

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
:
- {{repo_url}} → Original repository URL provided to the workflow.
- {{clone_path}} → Root folder where repositories are cloned.
- {{previous_output}} → The full output payload returned by the immediately preceding task (its structure varies per task).
- {{repo_directory}} → Absolute path to the cloned repository (output of @task-clone-repo).
- {{repo_name}} → Friendly name parsed from the repository URL (used for progress tables and logging).
- {{readme_content}} → README file content (output of @task-search-readme).
- {{readme_filename}} → README filename (output of @task-search-readme).
- {{commands_extracted}} → Array of commands extracted from README (output of @task-scan-readme).
- {{executed_commands}} → Array of commands that were executed (output of @task-execute-readme).
- {{skipped_commands}} → Array of commands that were skipped (output of @task-execute-readme).
- {{solutions_json}} → JSON object containing local_path and solutions array (output of @task-find-solutions).
- {{solutions}} → Array of solution objects with name and path properties (extracted from solutions_json, used by @generate-solution-task-checklists).

Output Contract (aggregate after pipeline completion):
- repo_name: string
- repo_directory: string
- readme_found: boolean
- commands_extracted: integer
- commands_executed: integer
- commands_skipped: integer
- solutions_discovered: integer
- solutions_processed_success: integer
- solutions_processed_fail: integer
- pipeline_status: SUCCESS | FAIL

## Parsed Task Directives
- @task-clone-repo ⇒ 1. @task-clone-repo
- @task-search-readme ⇒ 2. @task-search-readme
- @task-scan-readme ⇒ 3. @task-scan-readme
- @task-execute-readme ⇒ 4. @task-execute-readme
- @task-find-solutions ⇒ 5. @task-find-solutions
- @task-clone-repo ⇒ - {{repo_directory}} → Absolute path to the cloned repository (output of @task-clone-repo).
- @task-search-readme ⇒ - {{readme_content}} → README file content (output of @task-search-readme).
- @task-search-readme ⇒ - {{readme_filename}} → README filename (output of @task-search-readme).
- @task-scan-readme ⇒ - {{commands_extracted}} → Array of commands extracted from README (output of @task-scan-readme).
- @task-execute-readme ⇒ - {{executed_commands}} → Array of commands that were executed (output of @task-execute-readme).
- @task-execute-readme ⇒ - {{skipped_commands}} → Array of commands that were skipped (output of @task-execute-readme).
- @task-find-solutions ⇒ - {{solutions_json}} → JSON object containing local_path and solutions array (output of @task-find-solutions).
