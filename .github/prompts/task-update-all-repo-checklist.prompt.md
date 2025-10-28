````prompt
---
temperature: 0.1
---

@task-update-all-repo-checklist repo_name={{repo_name}}

Task name: task-update-all-repo-checklist

## Description:
This task marks a repository as complete [x] in the all repository checklist (all_repository_checklist.md) after all repository-level tasks have been successfully completed. This is a simple file update operation that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Reads the master checklist file (tasks/all_repository_checklist.md)
2. Finds the line containing the specified repository name
3. Updates the checkbox from [ ] to [x]
4. Writes the updated content back to the file
5. Saves the result to JSON output

## Behavior (Follow this Step by Step)

0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-update-all-repo-checklist] START repo_name='{{repo_name}}'`

1. Input Parameters: You are given repo_name from the calling context.
   - Validate that repo_name is not empty
   - If DEBUG=1, print: `[debug][task-update-all-repo-checklist] validating repo_name='{{repo_name}}'`

2. Read All Repository Checklist: Read the file tasks/all_repository_checklist.md
   - If file does not exist, set status=FAIL with error: "All repository checklist file not found"
   - If DEBUG=1 and file exists, print: `[debug][task-update-all-repo-checklist] all repository checklist file found`
   - If DEBUG=1 and file not found, print: `[debug][task-update-all-repo-checklist] ERROR: all repository checklist file not found`

3. Find Repository Line: Search for the repository in the "## Repositories" section
   - Look for a line matching pattern: `- [ ] {{repo_name}} [` or `- [x] {{repo_name}} [`
   - This matches lines like: `- [ ] ic3_spool_cosine-dep-spool [https://...]`
   - If DEBUG=1 and found, print: `[debug][task-update-all-repo-checklist] found repository line for '{{repo_name}}'`
   - If DEBUG=1 and not found, print: `[debug][task-update-all-repo-checklist] ERROR: repository '{{repo_name}}' not found in all repository checklist`

4. Check Current Status:
   - Determine if repository is already marked complete [x] or incomplete [ ]
   - If already marked [x]:
     - If DEBUG=1, print: `[debug][task-update-all-repo-checklist] repository already marked complete, no update needed`
     - Set operation_performed="NO_UPDATE_NEEDED"
   - If marked [ ]:
     - If DEBUG=1, print: `[debug][task-update-all-repo-checklist] repository marked incomplete, will update to complete`
     - Set operation_performed="UPDATED"

5. Update Checkbox: If repository is currently marked [ ], update it to [x]
   - Replace the line: `- [ ] {{repo_name}} [{{repo_url}}]`
   - With: `- [x] {{repo_name}} [{{repo_url}}]`
   - If DEBUG=1, print: `[debug][task-update-all-repo-checklist] updated checkbox from [ ] to [x]`

6. Write Updated Content: Save the modified content back to tasks/all_repository_checklist.md
   - Preserve all other content exactly as-is
   - Only modify the specific repository line
   - If DEBUG=1, print: `[debug][task-update-all-repo-checklist] all repository checklist file updated successfully`

7. Structured Output: Save JSON object to output/{{repo_name}}_task_update-all-repo-checklist.json with:
   - repo_name: echoed from input
   - all_repo_checklist_path: "tasks/all_repository_checklist.md"
   - operation_performed: "UPDATED" | "NO_UPDATE_NEEDED" | "NOT_FOUND" | "FILE_NOT_FOUND"
   - previous_status: "INCOMPLETE" | "COMPLETE" | "NOT_FOUND" | null
   - new_status: "COMPLETE" | "COMPLETE" | null | null
   - status: SUCCESS if operation completed, FAIL if repository not found or file error
   - timestamp: ISO 8601 format datetime when task completed
   - error_message: string if status=FAIL, null otherwise

7a. Log to Decision Log:
   - Call @task-update-decision-log to log task execution:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="{{repo_name}}" 
     solution_name="" 
     task="task-update-all-repo-checklist" 
     message="{{message}}" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-28T14:30:45Z")
   - The solution_name is blank since this is a repository-level task
   - Message format:
     * If UPDATED: "Marked repository as complete [x] in all repository checklist"
     * If NO_UPDATE_NEEDED: "Repository already marked complete [x]"
     * If NOT_FOUND: "Repository '{{repo_name}}' not found in all repository checklist"
     * If FILE_NOT_FOUND: "All repository checklist file not found"
   - Status: "SUCCESS" or "FAIL"

8. Result Tracking:
   - Append the result to:
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-update-all-repo-checklist | status | symbol (✓ or ✗)

9. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][task-update-all-repo-checklist] EXIT repo_name='{{repo_name}}' status={{status}} operation={{operation_performed}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the update-all-repo-checklist task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-update-all-repo-checklist] allowing simple grep filtering.
- Entry Message: "[debug][task-update-all-repo-checklist] START repo_name='<name>'" emitted before step 1.
- Validation: "[debug][task-update-all-repo-checklist] validating repo_name='<name>'" after parameter check.
- File Check: "[debug][task-update-all-repo-checklist] all repository checklist file found" or "ERROR: all repository checklist file not found".
- Search Result: "[debug][task-update-all-repo-checklist] found repository line for '<name>'" or "ERROR: repository '<name>' not found in all repository checklist".
- Status Check: "[debug][task-update-all-repo-checklist] repository already marked complete, no update needed" or "repository marked incomplete, will update to complete".
- Update Action: "[debug][task-update-all-repo-checklist] updated checkbox from [ ] to [x]" when update is performed.
- Write Success: "[debug][task-update-all-repo-checklist] all repository checklist file updated successfully" after file write.
- Exit Message: "[debug][task-update-all-repo-checklist] EXIT repo_name='<name>' status=<STATUS> operation=<OPERATION>".

Variables available:
- {{repo_name}} → Name of the repository to mark as complete (from repo_name= parameter - required)
- {{all_repo_checklist_path}} → Path to all repository checklist file (./tasks/all_repository_checklist.md)
- {{output_dir}} → Directory where task output is saved (./output)
- {{results_dir}} → Directory where results and logs are saved (./results)

Output Contract:
- repo_name: string (repository name)
- all_repo_checklist_path: string (path to all repository checklist file)
- operation_performed: "UPDATED" | "NO_UPDATE_NEEDED" | "NOT_FOUND" | "FILE_NOT_FOUND"
- previous_status: "INCOMPLETE" | "COMPLETE" | "NOT_FOUND" | null
- new_status: "COMPLETE" | "COMPLETE" | null | null
- status: "SUCCESS" | "FAIL"
- timestamp: string (ISO 8601 format)
- error_message: string | null

Special Cases:

**Case 1: Repository not found in all repository checklist**
- Set status=FAIL
- Set operation_performed="NOT_FOUND"
- Set error_message="Repository '{{repo_name}}' not found in all repository checklist"
- Do not modify any files
- Log to decision log with status FAIL

**Case 2: All repository checklist file does not exist**
- Set status=FAIL
- Set operation_performed="FILE_NOT_FOUND"
- Set error_message="All repository checklist file not found at tasks/all_repository_checklist.md"
- Log to decision log with status FAIL

**Case 3: Repository already marked complete [x]**
- Set status=SUCCESS
- Set operation_performed="NO_UPDATE_NEEDED"
- Set previous_status="COMPLETE"
- Set new_status="COMPLETE"
- Do not modify the file
- Log to decision log with status SUCCESS

**Case 4: Successful update from [ ] to [x]**
- Set status=SUCCESS
- Set operation_performed="UPDATED"
- Set previous_status="INCOMPLETE"
- Set new_status="COMPLETE"
- Update the file
- Log to decision log with status SUCCESS

Implementation Notes:
1. **Simple File Update**: This task performs a straightforward text replacement
2. **Idempotent Operation**: Can be run multiple times safely - will not re-update if already complete
3. **Error Handling**: Validates file existence and repository presence before attempting update
4. **Minimal Changes**: Only modifies the specific repository line, preserves all other content
5. **Checkpoint Integration**: Designed to be called after all repository tasks complete
6. **Programming Language**: All code generated should be written in Python
7. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory

Example Usage:
```
# Mark repository as complete in all repository checklist
@task-update-all-repo-checklist repo_name="ic3_spool_cosine-dep-spool"

# With debug output
DEBUG=1 @task-update-all-repo-checklist repo_name="ic3_spool_cosine-dep-spool"
```

Expected Output (Success):
```json
{
  "repo_name": "ic3_spool_cosine-dep-spool",
  "all_repo_checklist_path": "tasks/all_repository_checklist.md",
  "operation_performed": "UPDATED",
  "previous_status": "INCOMPLETE",
  "new_status": "COMPLETE",
  "status": "SUCCESS",
  "timestamp": "2025-10-28T14:30:45Z",
  "error_message": null
}
```

Expected Output (Already Complete):
```json
{
  "repo_name": "ic3_spool_cosine-dep-spool",
  "all_repo_checklist_path": "tasks/all_repository_checklist.md",
  "operation_performed": "NO_UPDATE_NEEDED",
  "previous_status": "COMPLETE",
  "new_status": "COMPLETE",
  "status": "SUCCESS",
  "timestamp": "2025-10-28T14:30:45Z",
  "error_message": null
}
```

Expected Output (Not Found):
```json
{
  "repo_name": "nonexistent_repo",
  "all_repo_checklist_path": "tasks/all_repository_checklist.md",
  "operation_performed": "NOT_FOUND",
  "previous_status": "NOT_FOUND",
  "new_status": null,
  "status": "FAIL",
  "timestamp": "2025-10-28T14:30:45Z",
  "error_message": "Repository 'nonexistent_repo' not found in all repository checklist"
}
```
````