@task-update-decision-log timestamp={{timestamp}} repo_name={{repo_name}} solution_name={{solution_name}} task={{task}} message={{message}} status={{status}}

---
temperature: 0.0
---

Task name: task-update-decision-log

## Description:
This task updates the decision log by appending a new entry. It maintains a CSV file that tracks all task executions across repositories and solutions.

The decision log file: **results/decision-log.csv**


## Execution Policy
** THIS TASK IS SCRIPTABLE **
This task can be fully automated as it follows deterministic file operations.

WHY SCRIPTABLE:
✓ File existence check is a simple conditional operation
✓ CSV file creation follows a fixed header format
✓ Appending rows to CSV is a standard file operation
✓ No AI reasoning or structural decisions required

YOU MUST USE DIRECT TOOL CALLS:
✓ Use read_file to check file existence and read content
✓ Use create_file to create new CSV file with headers
✓ Use run_in_terminal to append rows using PowerShell

DO NOT:
✗ Make manual edits to CSV file
✗ Skip file existence check
✗ Create file in wrong directory

** END WARNING **

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
DEBUG Entry Trace:
   - If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   - `[debug][task-update-decision-log] START task='{{task}}' status='{{status}}' repo='{{repo_name}}'`
   - This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

### Step 2 (MANDATORY)
Ensure Log File Exists

1. **Check if decision-log.csv exists:**
   - Path: `./results/decision-log.csv`
   - Use read_file or file existence check

2. **If file does NOT exist, create it:**
   - Create directory if needed: `./results/`
   - Create file with headers using comma (`,`) as the separator:
   ```csv
   timestamp,repo_name,solution_name,task,message,status
   ```
   - DEBUG: Log "[DECISION-LOG-DEBUG] Created new decision-log.csv with headers"

3. **If file exists:**
   - DEBUG: Log "[DECISION-LOG-DEBUG] decision-log.csv already exists"

### Step 3 (MANDATORY) 
Prepare Log Entry
1. **Prepare log entry with provided values:**
   - timestamp: {{timestamp}} (should be in ISO 8601 format, e.g., "2025-10-26T12:00:00Z")
   - repo_name: {{repo_name}} (e.g., "ic3_spool_cosine-dep-spool", or empty string if not applicable)
   - solution_name: {{solution_name}} (e.g., "ResourceProvider", or empty string if not applicable)
   - task: {{task}} (e.g., "@task-restore-solution", "@task-build-solution")
   - message: {{message}} (e.g., "Restore completed successfully", "Build failed with 3 errors")
   - status: {{status}} (e.g., "SUCCESS", "FAIL", "SKIPPED", "BLOCKED")

2. **Format CSV row using comma (`,`) as the separator:**
   - Handle empty values (use empty string for repo_name or solution_name if not provided)
   - Handle special characters in message (escape commas, quotes if needed)
   - Format: `{{timestamp}},{{repo_name}},{{solution_name}},{{task}},{{message}},{{status}}`

3. **Validate required fields:**
   - timestamp must not be empty
   - task must not be empty
   - status must not be empty
   - If validation fails, return error status
   - DEBUG: Log "[DECISION-LOG-DEBUG] Prepared log entry: {{timestamp}},{{repo_name}},{{solution_name}},{{task}},{{message}},{{status}}"

### Step 4 (MANDATORY)
Append Log Entry

1. **Append row to decision-log.csv:**
   - Use PowerShell to append:
   ```powershell
   Add-Content -Path ".\results\decision-log.csv" -Value "{{timestamp}},{{repo_name}},{{solution_name}},{{task}},{{message}},{{status}}"
   ```
   - DEBUG: Log "[DECISION-LOG-DEBUG] Appending log entry to decision-log.csv"

2. **Verify append succeeded:**
   - If append fails, return error status
   - DEBUG: Log "[DECISION-LOG-DEBUG] Log entry appended successfully"

### Step 6 (MANDATORY)
Output Results

1. **Return log update status:**
   - log_status: SUCCESS | FAIL
   - log_file_path: Absolute path to decision-log.csv
   - entry_logged: boolean (true if new entry appended)
   - error_message: string | null (if log_status == FAIL)

2. **DEBUG Exit Trace:**
   - If environment variable DEBUG=1, emit a line to stdout before returning:
   - `[debug][task-update-decision-log] END log_status='{{log_status}}' entry_logged={{entry_logged}}`
   - This helps trace when the task completes and its outcome.

## Variables Available:
- {{timestamp}} → Timestamp in ISO 8601 format (e.g., "2025-10-26T12:00:00Z")
- {{repo_name}} → Repository name (e.g., "ic3_spool_cosine-dep-spool") or empty string
- {{solution_name}} → Solution name (e.g., "ResourceProvider") or empty string
- {{task}} → Task identifier (e.g., "@task-restore-solution", "@task-build-solution")
- {{message}} → Human-readable message describing the task result
- {{status}} → Status code (SUCCESS | FAIL | SKIPPED | BLOCKED | INFO)

## Output Contract:
- log_status: SUCCESS | FAIL
- log_file_path: string (absolute path to decision-log.csv)
- entry_logged: boolean
- error_message: string | null (if log_status == FAIL)

## Implementation Notes:
1. **Directory Creation**: Always ensure `./results/` directory exists before creating file
2. **File Encoding**: Use UTF-8 encoding for CSV file
3. **Timestamp Format**: Accept ISO 8601 UTC format (e.g., "2025-10-26T12:00:00Z")
4. **Empty Fields**: Allow empty repo_name or solution_name for repository-level tasks
5. **CSV Escaping**: Handle commas and quotes in message field (wrap in quotes if contains comma)
6. **Atomicity**: Complete file creation and append in the same execution
7. **Error Handling**:
   - If log append fails → return FAIL status with error message
   - If directory creation fails → return FAIL status
   - If validation fails → return FAIL status with validation error
8. **Idempotency**: Re-running with same parameters will add duplicate log entries (by design for audit trail)
9. **Status Values**: Common values are SUCCESS, FAIL, SKIPPED, BLOCKED, INFO

## Example Usage:

**Repository-level task logging:**
```
@task-update-decision-log 
  timestamp="2025-10-26T12:00:00Z" 
  repo_name="ic3_spool_cosine-dep-spool" 
  solution_name="" 
  task="@task-clone-repo" 
  message="Repository cloned successfully" 
  status="SUCCESS"
```

**Solution-level task logging:**
```
@task-update-decision-log 
  timestamp="2025-10-26T12:15:00Z" 
  repo_name="ic3_spool_cosine-dep-spool" 
  solution_name="ResourceProvider" 
  task="@task-restore-solution" 
  message="Restore completed with 0 errors" 
  status="SUCCESS"
```

**Task failure logging:**
```
@task-update-decision-log 
  timestamp="2025-10-26T12:30:00Z" 
  repo_name="ic3_spool_cosine-dep-spool" 
  solution_name="ResourceProvider" 
  task="@task-build-solution" 
  message="Build failed with 3 errors: NU1008, MSB3644, CS0246" 
  status="FAIL"
```

**Task skipped logging:**
```
@task-update-decision-log 
  timestamp="2025-10-26T12:45:00Z" 
  repo_name="ic3_spool_cosine-dep-spool" 
  solution_name="ResourceProvider" 
  task="@task-search-knowledge-base" 
  message="Build succeeded - KB search skipped" 
  status="SKIPPED"
```

The task should automatically handle CSV escaping when appending to the file.
