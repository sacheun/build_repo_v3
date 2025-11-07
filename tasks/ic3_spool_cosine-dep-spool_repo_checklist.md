# Task Checklist: ic3_spool_cosine-dep-spool
Repository: https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool
Generated: 2025-11-07T05:14:02Z

## Repo Tasks (Sequential Pipeline - Complete in Order)
- [x] [MANDATORY] [SCRIPTABLE] Clone repository to local directory @task-clone-repo (1)
- [x] [MANDATORY] [SCRIPTABLE] Find all solution files in repository @task-find-solutions (2)
- [x] [MANDATORY] [SCRIPTABLE] Generate per-solution checklist files (no inline sections) @generate-solution-task-checklists (3)
- [x] [MANDATORY] [SCRIPTABLE] Search for README file in repository @task-search-readme (4)
- [x] [CONDITIONAL] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
- [x] [CONDITIONAL] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme (No commands to run)

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
- {repo_url} → https://skype.visualstudio.com/SCC/_git/ic3_spool_cosine-dep-spool
- {repo_name} → ic3_spool_cosine-dep-spool
- {solutions_json} → {"local_path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool", "solutions": [{"name": "ResourceProvider.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\src\\ResourceProvider.sln"}, {"name": "codereview.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\tools\\codereview\\codereview.sln"}, {"name": "RPClientSampleService.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\tools\\testing\\RPClientSampleService\\RPClientSampleService.sln"}, {"name": "Microsoft.Azure.Communication.Email.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\src\\Email\\Microsoft.Azure.Communication.Email.sln"}, {"name": "MigrateCosmosDb.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\src\\Management\\Deployment\\Tools\\MigrateCosmosDb\\MigrateCosmosDb.sln"}, {"name": "LinkDomains.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\src\\Email\\tools\\azure-cli\\LinkDomains\\LinkDomains.sln"}, {"name": "SDKTestApp.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\samples\\External\\samples\\SDKTestApp\\SDKTestApp.sln"}, {"name": "AcsAdminConsoleApp.sln", "path": "D:\\build_repo_v3\\clone_repos\\ic3_spool_cosine-dep-spool\\samples\\External\\samples\\TurnWebRTCApps\\AcsAdminConsoleApp.sln"}]}
- {solutions} → ResourceProvider.sln, codereview.sln, RPClientSampleService.sln, Microsoft.Azure.Communication.Email.sln, MigrateCosmosDb.sln, LinkDomains.sln, SDKTestApp.sln, AcsAdminConsoleApp.sln
- {clone_path} →
- {repo_directory} →
- {readme_content} → (ROOT README.md) Azure Communication Services (ACS) is a collection of micro-services that allows you to easily add real-time communications features to your applications.
- {readme_filename} → README.md
- {commands_extracted} → NONE
- {executed_commands} → NONE
- {skipped_commands} → NONE

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
