@task-update-knowledgebase-log knowledgebase_file={{knowledgebase_file}} option={{option}} status={{status}} repo_name={{repo_name}}

---
temperature: 0.0
---

Task name: task-update-knowledgebase-log

## Description:
This task updates the knowledgebase usage log by appending a new entry and then aggregating statistics. It maintains two CSV files:
1. **knowledgebase.log** - Detailed log of each knowledgebase application attempt
2. **knowledgebase-stats.csv** - Aggregated statistics per knowledgebase file and option

** THIS TASK IS SCRIPTABLE **

This task can be fully automated as it follows deterministic file operations.

WHY SCRIPTABLE:
✓ File existence check is a simple conditional operation
✓ CSV file creation follows a fixed header format
✓ Appending rows to CSV is a standard file operation
✓ Aggregation logic is deterministic (count by group)
✓ No AI reasoning or structural decisions required

YOU MUST USE DIRECT TOOL CALLS:
✓ Use read_file to check file existence and read content
✓ Use create_file to create new CSV files with headers
✓ Use run_in_terminal to append rows using PowerShell
✓ Use Python or PowerShell for CSV aggregation logic

DO NOT:
✗ Make manual edits to CSV files
✗ Skip aggregation step
✗ Create files in wrong directory

** END WARNING **

## Behavior (Follow this Step by Step)

0. **DEBUG Entry Trace:**
   - If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   - `[debug][task-update-knowledgebase-log] START kb_file='{{knowledgebase_file}}' option='{{option}}' status='{{status}}'`
   - This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

### Step 1: Ensure Log File Exists

1. **Check if knowledgebase.log exists:**
   - Path: `./knowledge_base_markdown/knowledgebase.log`
   - Use read_file or file existence check

2. **If file does NOT exist, create it:**
   - Create directory if needed: `./knowledge_base_markdown/`
   - Create file with headers using comma (`,`) as the separator:
   ```csv
   timestamp,knowledgebase_file,option,status
   ```
   - DEBUG: Log "[KB-LOG-DEBUG] Created new knowledgebase.log with headers"

3. **If file exists:**
   - DEBUG: Log "[KB-LOG-DEBUG] knowledgebase.log already exists"

### Step 2: Append New Log Entry

1. **Prepare log entry:**
   - timestamp: Current UTC timestamp in ISO 8601 format (e.g., "2025-10-26T12:00:00Z")
   - knowledgebase_file: {{knowledgebase_file}} (e.g., "nu1008_central_package_management.md")
   - option: {{option}} (e.g., "1", "2", "3")
   - status: {{status}} (e.g., "SUCCESS", "FAIL", "SKIPPED")

2. **Append row to knowledgebase.log using comma (`,`) as the separator:**
   - Use PowerShell to append:
   ```powershell
   Add-Content -Path ".\knowledge_base_markdown\knowledgebase.log" -Value "{{timestamp}},{{knowledgebase_file}},{{option}},{{status}}"
   ```
   - DEBUG: Log "[KB-LOG-DEBUG] Appended log entry: {{timestamp}},{{knowledgebase_file}},{{option}},{{status}}"

3. **Verify append succeeded:**
   - If append fails, return error status
   - DEBUG: Log "[KB-LOG-DEBUG] Log entry appended successfully"

### Step 3: Ensure Stats File Exists

1. **Check if knowledgebase-stats.csv exists:**
   - Path: `./knowledge_base_markdown/knowledgebase-stats.csv`
   - Use read_file or file existence check

2. **If file does NOT exist, create it:**
   - Create file with headers using comma (`,`) as the separator:
   ```csv
   knowledgebase_file,option,success,attempt
   ```
   - DEBUG: Log "[KB-LOG-DEBUG] Created new knowledgebase-stats.csv with headers"

3. **If file exists:**
   - DEBUG: Log "[KB-LOG-DEBUG] knowledgebase-stats.csv already exists"

### Step 4: Aggregate Statistics

1. **Read knowledgebase.log:**
   - Load all entries from log file
   - DEBUG: Log "[KB-LOG-DEBUG] Read {{row_count}} rows from knowledgebase.log"

2. **Group by (knowledgebase_file, option):**
   - For each unique combination of knowledgebase_file + option:
     * Count total rows (attempt)
     * Count rows where status == "SUCCESS" (success)
   - DEBUG: Log "[KB-LOG-DEBUG] Found {{unique_groups}} unique (file, option) combinations"

3. **Generate aggregated statistics:**
   - Use Python or PowerShell to perform grouping and counting
   - Example Python approach:
   ```python
   import pandas as pd
   
   # Read log file
   log_df = pd.read_csv('./knowledge_base_markdown/knowledgebase.log')
   
   # Group by knowledgebase_file and option
   stats_df = log_df.groupby(['knowledgebase_file', 'option']).agg(
       success=('status', lambda x: (x == 'SUCCESS').sum()),
       attempt=('status', 'count')
   ).reset_index()
   
   # Write to stats file
   stats_df.to_csv('./knowledge_base_markdown/knowledgebase-stats.csv', index=False)
   ```
   - DEBUG: Log "[KB-LOG-DEBUG] Aggregated statistics for {{unique_groups}} entries"

4. **Write aggregated data to knowledgebase-stats.csv:**
   - Overwrite the entire file with new statistics
   - Format: `knowledgebase_file,option,success,attempt`
   - Example row: `nu1008_central_package_management.md,1,3,5`
   - DEBUG: Log "[KB-LOG-DEBUG] Wrote {{row_count}} rows to knowledgebase-stats.csv"

### Step 5: Output Results

1. **Return log update status:**
   - log_status: SUCCESS | FAIL
   - log_file_path: Absolute path to knowledgebase.log
   - stats_file_path: Absolute path to knowledgebase-stats.csv
   - entry_logged: boolean (true if new entry appended)
   - stats_updated: boolean (true if stats file regenerated)

2. **DEBUG Exit Trace:**
   - If environment variable DEBUG=1, emit a line to stdout before returning:
   - `[debug][task-update-knowledgebase-log] END log_status='{{log_status}}' entry_logged={{entry_logged}} stats_updated={{stats_updated}}`
   - This helps trace when the task completes and its outcome.

## Variables Available:
- {{knowledgebase_file}} → Filename of the KB article (e.g., "nu1008_central_package_management.md")
- {{option}} → Fix option number that was applied (e.g., "1", "2", "3")
- {{status}} → Status of the KB fix application (e.g., "SUCCESS", "FAIL", "SKIPPED")
- {{repo_name}} → (Optional) Repository name for decision log context

## Output Contract:
- log_status: SUCCESS | FAIL
- log_file_path: string (absolute path to knowledgebase.log)
- stats_file_path: string (absolute path to knowledgebase-stats.csv)
- entry_logged: boolean
- stats_updated: boolean
- error_message: string | null (if log_status == FAIL)

## Implementation Notes:
1. **Directory Creation**: Always ensure `./knowledge_base_markdown/` directory exists before creating files
2. **File Encoding**: Use UTF-8 encoding for all CSV files
3. **Timestamp Format**: Use ISO 8601 UTC format (e.g., "2025-10-26T12:00:00Z")
4. **Aggregation Logic**: Use pandas or equivalent for reliable CSV grouping and aggregation
5. **Atomicity**: Complete both log append and stats update in the same execution
6. **Error Handling**:
   - If log append fails → return FAIL status with error message
   - If stats aggregation fails → log error but return SUCCESS for log append
   - If directory creation fails → return FAIL status
7. **Idempotency**: Re-running with same parameters will add duplicate log entries (by design for audit trail)
8. **Stats Regeneration**: Always regenerate the entire stats file from log file (don't do incremental updates)

## Example Usage:

**First call (after applying Option 1):**
```
@task-update-knowledgebase-log 
  knowledgebase_file="nu1008_central_package_management.md" 
  option="1" 
  status="SUCCESS"
  repo_name="ic3_spool_cosine-dep-spool"
```

**Result:**
- knowledgebase.log: New row added with timestamp
- knowledgebase-stats.csv: Updated with success=1, attempt=1 for (nu1008_central_package_management.md, 1)

**Second call (after applying Option 2):**
```
@task-update-knowledgebase-log 
  knowledgebase_file="nu1008_central_package_management.md" 
  option="2" 
  status="FAIL"
  repo_name="ic3_spool_cosine-dep-spool"
```

**Result:**
- knowledgebase.log: New row added
- knowledgebase-stats.csv: 
  - Entry for option="1": success=1, attempt=1 (unchanged)
  - Entry for option="2": success=0, attempt=1 (new)

## Example Files:

**knowledgebase.log:**
```csv
timestamp,knowledgebase_file,option,status
2025-10-26T12:00:00Z,nu1008_central_package_management.md,1,SUCCESS
2025-10-26T12:15:00Z,nu1008_central_package_management.md,1,SUCCESS
2025-10-26T12:30:00Z,nu1008_central_package_management.md,2,FAIL
2025-10-26T12:45:00Z,sf_baseoutputpath_missing.md,1,SUCCESS
2025-10-26T13:00:00Z,nu1008_central_package_management.md,1,FAIL
```

**knowledgebase-stats.csv:**
```csv
knowledgebase_file,option,success,attempt
nu1008_central_package_management.md,1,2,3
nu1008_central_package_management.md,2,0,1
sf_baseoutputpath_missing.md,1,1,1
```

This shows:
- Option 1 of nu1008 KB: 2 successes out of 3 attempts (66% success rate)
- Option 2 of nu1008 KB: 0 successes out of 1 attempt (0% success rate)
- Option 1 of sf KB: 1 success out of 1 attempt (100% success rate)
