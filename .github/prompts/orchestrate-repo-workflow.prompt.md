````prompt
---
temperature: 0.1
---

@orchestrate-repo-workflow append=<optional>

Task name: orchestrate-repo-workflow

## Description:
This task orchestrates the complete repository workflow by:
1. Generating repository checklists from repositories_small.txt
2. Finding all incomplete repository checklists
3. Executing tasks for each repository sequentially until all are complete

This is a workflow orchestration task that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Optionally cleans results/tasks/output directories (if append=false)
2. Calls copilot to generate repository checklists
3. Discovers all *_repo_checklist.md files
4. Filters for repositories with incomplete tasks
5. Executes tasks for each repository one by one
6. Waits for each execution to complete before proceeding to next

## Behavior (Follow this Step by Step)

0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][orchestrate-repo-workflow] START append={{append}}`

1. Input Parameters: You are given append (boolean) from the calling context.
   Defaults:
      append = false
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] using append_mode: {{append}}`

2. Clean Directories (if append=false):
   
   **If append = false:**
   - Remove all files in ./results directory (keep directory)
   - Remove all files in ./tasks directory (keep directory)
   - Remove all files in ./output directory (keep directory)
   - Remove all files in ./temp-script directory (keep directory)
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] cleaned results, tasks, output, temp-script directories`
   
   **If append = true:**
   - Skip cleaning, preserve all existing files
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] preserving existing files (append=true)`

3. Generate Repository Checklists:
   - Build command: `copilot --prompt "@generate-repo-task-checklists input=\"repositories_small.txt\" append={{append}}" --allow-all-tools`
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] executing: copilot --prompt "@generate-repo-task-checklists input=\"repositories_small.txt\" append={{append}}" --allow-all-tools`
   - Execute the command
   - Wait for completion
   - Capture exit code
   - If exit code != 0:
     - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] ERROR: generate-repo-task-checklists failed with exit code {{exit_code}}`
     - Set status=FAIL
     - Return error result
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] generate-repo-task-checklists completed successfully`

4. Discover Repository Checklists:
   - Search for all files matching pattern: `./tasks/*_repo_checklist.md`
   - Exclude: `all_repository_checklist.md`
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] found {{count}} repository checklist files`

5. Filter for Incomplete Repositories:
   - For each checklist file found:
     - Read the file content
     - Find all task lines in "## Repo Tasks" section
     - Check if any tasks are marked with `- [ ]` (incomplete)
     - If any incomplete tasks found, add to processing list
   - Create list of repositories with incomplete tasks
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] found {{count}} repositories with incomplete tasks`

6. Print Incomplete Repository List (if DEBUG=1):
   - If DEBUG=1:
     - Print: `[debug][orchestrate-repo-workflow] repositories to process:`
     - For each repository in list:
       - Print: `[debug][orchestrate-repo-workflow]   - {{repo_checklist_path}}`

7. Process Each Repository Sequentially:
   - For each repository checklist in the incomplete list:
     
     a. Extract repository name from checklist filename
        - Pattern: `./tasks/{repo_name}_repo_checklist.md`
        - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] processing repository: {{repo_name}}`
     
     b. Build execute command:
        - Command: `copilot --prompt "@execute-repo-task repo_checklist=\"{{checklist_path}}\" clone=\"./clone_repos\"" --allow-all-tools`
        - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] executing: {{command}}`
     
     c. Execute the command:
        - Run command and wait for completion
        - Capture stdout, stderr, and exit code
        - If DEBUG=1 and exit code != 0, print: `[debug][orchestrate-repo-workflow] ERROR: execute-repo-task failed for {{repo_name}} with exit code {{exit_code}}`
        - If DEBUG=1 and exit code == 0, print: `[debug][orchestrate-repo-workflow] execute-repo-task completed for {{repo_name}}`
     
     d. Handle execution result:
        - If exit code == 0:
          - Increment success counter
          - Continue to next repository
        - If exit code != 0:
          - Increment failure counter
          - Log error details
          - **Decision: Continue to next repository OR stop workflow**
          - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] continuing to next repository despite failure`
     
     e. Update master checklist:
        - Build command: `copilot --prompt "@task-update-all-repo-checklist repo_name=\"{{repo_name}}\"" --allow-all-tools`
        - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] updating master checklist for {{repo_name}}`
        - Execute the command
        - Wait for completion
        - If DEBUG=1 and exit code == 0, print: `[debug][orchestrate-repo-workflow] master checklist updated for {{repo_name}}`

8. Generate Summary Report:
   - Total repositories processed: {{count}}
   - Successful: {{success_count}}
   - Failed: {{failure_count}}
   - Processing time: {{duration}}
   - If DEBUG=1, print full summary

9. Print Script Location:
   - If DEBUG=1, print: `[debug][orchestrate-repo-workflow] script saved to: ./temp-script/orchestrate_repo_workflow.py`
   - Always print: `Script generated: ./temp-script/orchestrate_repo_workflow.py`

10. Structured Output: Save JSON object to output/orchestrate-repo-workflow.json with:
   - append_mode: boolean (value of append parameter)
   - total_repositories: integer (total repositories found)
   - incomplete_repositories: integer (repositories with incomplete tasks)
   - processed_repositories: integer (repositories processed)
   - successful_repositories: integer (successfully completed)
   - failed_repositories: integer (failed executions)
   - repository_details: array of objects:
     - repo_name: string
     - checklist_path: string
     - execution_status: "SUCCESS" | "FAIL" | "SKIPPED"
     - exit_code: integer
     - error_message: string | null
   - workflow_status: "SUCCESS" | "PARTIAL_SUCCESS" | "FAIL"
   - start_time: ISO 8601 timestamp
   - end_time: ISO 8601 timestamp
   - duration_seconds: float
   - status: SUCCESS | FAIL

9a. Log to Decision Log:
   - Call @task-update-decision-log to log workflow execution:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="ALL" 
     solution_name="" 
     task="orchestrate-repo-workflow" 
     message="{{message}}" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp
   - Message format: "Processed {{processed_count}} repositories: {{success_count}} successful, {{failure_count}} failed"
   - Status: "SUCCESS" if all successful, "PARTIAL_SUCCESS" if some failed, "FAIL" if all failed

11. DEBUG Exit Trace: If DEBUG=1, print:
    "[debug][orchestrate-repo-workflow] EXIT status={{workflow_status}} processed={{processed_count}} successful={{success_count}} failed={{failure_count}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace of workflow orchestration steps and progress
- Activation: Only when DEBUG environment variable equals "1"
- Format Guarantees: Always starts with prefix [debug][orchestrate-repo-workflow]
- Entry Message: "[debug][orchestrate-repo-workflow] START append=<value>" before step 1
- Append Mode: "[debug][orchestrate-repo-workflow] using append_mode: <value>"
- Directory Cleaning: "[debug][orchestrate-repo-workflow] cleaned results, tasks, output, temp-script directories" or "preserving existing files"
- Command Execution: "[debug][orchestrate-repo-workflow] executing: <command>" before each copilot call
- Checklist Discovery: "[debug][orchestrate-repo-workflow] found <count> repository checklist files"
- Incomplete Filter: "[debug][orchestrate-repo-workflow] found <count> repositories with incomplete tasks"
- Repository List: "[debug][orchestrate-repo-workflow] repositories to process:" followed by each checklist path
- Repository Processing: "[debug][orchestrate-repo-workflow] processing repository: <repo_name>"
- Success/Failure: "[debug][orchestrate-repo-workflow] execute-repo-task completed/failed for <repo_name>"
- Master Checklist: "[debug][orchestrate-repo-workflow] updating master checklist for <repo_name>"
- Script Location: "[debug][orchestrate-repo-workflow] script saved to: ./temp-script/orchestrate_repo_workflow.py"
- Exit Message: "[debug][orchestrate-repo-workflow] EXIT status=<STATUS> processed=<count> successful=<count> failed=<count>"

Variables available:
- {{append}} → Append mode flag (from append= parameter, default: false)
- {{tasks_dir}} → Directory where checklists are stored (./tasks)
- {{output_dir}} → Directory where outputs are stored (./output)
- {{results_dir}} → Directory where results are stored (./results)
- {{temp_script_dir}} → Directory where generated scripts are stored (./temp-script)
- {{clone_path}} → Directory where repositories are cloned (./clone_repos)

Output Contract:
- append_mode: boolean
- total_repositories: integer
- incomplete_repositories: integer
- processed_repositories: integer
- successful_repositories: integer
- failed_repositories: integer
- repository_details: array of objects
  - repo_name: string
  - checklist_path: string
  - execution_status: "SUCCESS" | "FAIL" | "SKIPPED"
  - exit_code: integer
  - error_message: string | null
- workflow_status: "SUCCESS" | "PARTIAL_SUCCESS" | "FAIL"
- start_time: string (ISO 8601)
- end_time: string (ISO 8601)
- duration_seconds: float
- status: "SUCCESS" | "FAIL"

Special Cases:

**Case 1: No repositories found**
- Set workflow_status="SUCCESS"
- Set processed_repositories=0
- Log message: "No repositories found to process"

**Case 2: All repositories already complete**
- Set workflow_status="SUCCESS"
- Set incomplete_repositories=0
- Log message: "All repositories already complete"

**Case 3: Some repositories fail**
- Continue processing remaining repositories
- Set workflow_status="PARTIAL_SUCCESS"
- Log each failure with details

**Case 4: Generate checklists command fails**
- Set workflow_status="FAIL"
- Return immediately with error details
- Do not proceed to repository processing

**Case 5: All repositories fail**
- Set workflow_status="FAIL"
- Log all failures
- Return summary with all error details

Implementation Notes:
1. **Sequential Processing**: Process one repository at a time to avoid resource conflicts
2. **Wait for Completion**: Each copilot command must complete before starting the next
3. **Error Handling**: Individual repository failures should not stop the entire workflow
4. **Master Checklist Updates**: Update master checklist after each repository completes
5. **Idempotent**: Can be re-run - will only process repositories with incomplete tasks
6. **Progress Tracking**: Detailed logging for monitoring long-running workflows
7. **Programming Language**: All code generated should be written in Python
8. **Script Location**: Save generated script to ./temp-script/orchestrate_repo_workflow.py
9. **Subprocess Execution**: Use subprocess.run() to execute copilot commands
10. **Exit Code Checking**: Validate exit codes for all subprocess calls

Example Usage:
```python
# Fresh start - clean all directories and process all repositories
DEBUG=1 python orchestrate_repo_workflow.py

# Append mode - preserve existing work and process only new/incomplete repositories
DEBUG=1 python orchestrate_repo_workflow.py --append

# Via copilot prompt
copilot --prompt "@orchestrate-repo-workflow append=false" --allow-all-tools
copilot --prompt "@orchestrate-repo-workflow append=true" --allow-all-tools
```

Expected Output (Success):
```json
{
  "append_mode": false,
  "total_repositories": 3,
  "incomplete_repositories": 3,
  "processed_repositories": 3,
  "successful_repositories": 3,
  "failed_repositories": 0,
  "repository_details": [
    {
      "repo_name": "ic3_spool_cosine-dep-spool",
      "checklist_path": "./tasks/ic3_spool_cosine-dep-spool_repo_checklist.md",
      "execution_status": "SUCCESS",
      "exit_code": 0,
      "error_message": null
    },
    {
      "repo_name": "people_spool_usertokenmanagement",
      "checklist_path": "./tasks/people_spool_usertokenmanagement_repo_checklist.md",
      "execution_status": "SUCCESS",
      "exit_code": 0,
      "error_message": null
    },
    {
      "repo_name": "sync_calling_concore-conversation",
      "checklist_path": "./tasks/sync_calling_concore-conversation_repo_checklist.md",
      "execution_status": "SUCCESS",
      "exit_code": 0,
      "error_message": null
    }
  ],
  "workflow_status": "SUCCESS",
  "start_time": "2025-10-28T14:30:00Z",
  "end_time": "2025-10-28T15:45:30Z",
  "duration_seconds": 4530.5,
  "status": "SUCCESS"
}
```

Expected Output (Partial Success):
```json
{
  "append_mode": true,
  "total_repositories": 3,
  "incomplete_repositories": 2,
  "processed_repositories": 2,
  "successful_repositories": 1,
  "failed_repositories": 1,
  "repository_details": [
    {
      "repo_name": "people_spool_usertokenmanagement",
      "checklist_path": "./tasks/people_spool_usertokenmanagement_repo_checklist.md",
      "execution_status": "SUCCESS",
      "exit_code": 0,
      "error_message": null
    },
    {
      "repo_name": "sync_calling_concore-conversation",
      "checklist_path": "./tasks/sync_calling_concore-conversation_repo_checklist.md",
      "execution_status": "FAIL",
      "exit_code": 1,
      "error_message": "execute-repo-task failed with exit code 1"
    }
  ],
  "workflow_status": "PARTIAL_SUCCESS",
  "start_time": "2025-10-28T16:00:00Z",
  "end_time": "2025-10-28T17:30:15Z",
  "duration_seconds": 5415.2,
  "status": "SUCCESS"
}
```

Workflow Sequence:
```
1. [Optional] Clean directories (if append=false)
2. Generate repository checklists
3. Discover all *_repo_checklist.md files
4. Filter for repositories with [ ] tasks
5. For each incomplete repository:
   a. Execute @execute-repo-task
   b. Wait for completion
   c. Update master checklist with @task-update-all-repo-checklist
   d. Move to next repository
6. Generate summary report
7. Log to decision log
```

This orchestrator enables fully autonomous, sequential repository processing with complete traceability and error handling.
````