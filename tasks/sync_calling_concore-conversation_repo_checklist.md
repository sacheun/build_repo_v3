# Task Checklist: sync_calling_concore-conversation
Repository: https://skype.visualstudio.com/SCC/_git/sync_calling_concore-conversation
Generated: 2025-11-07T04:57:49Z

## Repo Tasks (Sequential Pipeline - Complete in Order)
- [ ] [MANDATORY] [SCRIPTABLE] Clone repository to local directory @task-clone-repo (1)
- [ ] [MANDATORY] [SCRIPTABLE] Find all solution files in repository @task-find-solutions (2)
- [ ] [MANDATORY] [SCRIPTABLE] Generate per-solution checklist files (no inline sections) @generate-solution-task-checklists (3)
- [ ] [MANDATORY] [SCRIPTABLE] Search for README file in repository @task-search-readme (4)
- [ ] [CONDITIONAL] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
- [ ] [CONDITIONAL] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme

## For Agents Resuming Work
**Next Action:**
1. Check if all [MANDATORY] tasks are completed
2. If YES and {readme_content} is not blank and not "NONE", execute @task-scan-readme
3. If {commands_extracted} is not blank and not "NONE", execute @task-execute-readme
4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

**How to Execute:** Invoke the corresponding task prompt.

**Quick Reference:**
- [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4)
- [CONDITIONAL] @task-scan-readme runs when {readme_content} not blank and not "NONE"
- [CONDITIONAL] @task-execute-readme runs when {commands_extracted} not blank and not "NONE"
- [SCRIPTABLE] tasks: clone, search-readme, find-solutions, generate-solution-task-checklists
- [NON-SCRIPTABLE] tasks: scan-readme, execute-readme
- Mark completed tasks with [x]

## Repo Variables Available
- {repo_url} → https://skype.visualstudio.com/SCC/_git/sync_calling_concore-conversation
- {repo_name} → sync_calling_concore-conversation
- {solutions_json} →
- {solutions} →
- {clone_path} →
- {repo_directory} →
- {readme_content} →
- {readme_filename} →
- {commands_extracted} →
- {executed_commands} →
- {skipped_commands} →

## Variable Definitions (Reference Only – DO NOT PARSE FOR VALUES)
- repo_url: Original repository URL provided to the workflow.
- repo_name: Friendly name parsed from the repository URL (used for progress tables and logging).
- clone_path: Root folder where repositories are cloned (populated later by task-clone-repo).
- repo_directory: Absolute path to the cloned repository (populated later by task-clone-repo).
- readme_content: README file content (output of @task-search-readme).
- readme_filename: README filename (output of @task-search-readme).
- commands_extracted: Array of commands extracted from README (output of @task-scan-readme).
- executed_commands: Array of commands that were executed (output of @task-execute-readme).
- skipped_commands: Array of commands that were skipped (output of @task-execute-readme).
- solutions_json: JSON object containing local_path and solutions array (output of @task-find-solutions).
- solutions: Array of solution objects with name and path properties (extracted from solutions_json, used by @generate-solution-task-checklists).
