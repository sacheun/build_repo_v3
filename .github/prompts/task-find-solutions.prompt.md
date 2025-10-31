---
temperature: 0.0
---

@task-find-solutions repo_directory={{repo_directory}} repo_name={{repo_name}}

Task name: task-find-solutions

## Description:
This task discovers all Visual Studio solution files (.sln) within a repository directory tree. This is a straightforward file search operation that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python script that:
1. Validates the repository directory exists
2. Recursively searches for all .sln files
3. Collects absolute paths to all discovered solutions
4. Saves the result to JSON output
5. Updates progress and results files

## Behavior (Follow this Step by Step)
0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-find-solutions] START repo_directory='{{repo_directory}}'`

1. Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

2. Input Validation: Verify that repo_directory exists and is accessible
   - If directory does not exist, set status=FAIL
   - If DEBUG=1 and directory does not exist, print: `[debug][task-find-solutions] directory does not exist: {{repo_directory}}`
   - If DEBUG=1 and directory exists, print: `[debug][task-find-solutions] directory validated: {{repo_directory}}`

3. Recursive Solution Discovery: Search all subdirectories recursively for files with .sln extension
   - Use recursive glob pattern: **/*.sln (or equivalent for the language)
   - Convert each discovered path to absolute path string
   - If DEBUG=1, print: `[debug][task-find-solutions] searching for *.sln files recursively`
   - For each solution found, if DEBUG=1, print: `[debug][task-find-solutions] found: {{solution_path}}`

4. Path Collection: Build array of absolute paths to all discovered .sln files
   - Order may vary by filesystem traversal; no guaranteed sorting
   - If DEBUG=1 after collection complete, print: `[debug][task-find-solutions] discovered {{count}} solution(s)`

5. Structured Output: Save JSON object to output/{repo_name}_task5_find-solutions.json with:
   - local_path: echoed from input (repo_directory)
   - repo_name: echoed from input
   - solutions: array of absolute paths to .sln files (empty array if none found)
   - solution_count: integer count of discovered solutions
   - status: SUCCESS if directory validated (even if 0 solutions found), FAIL if directory invalid
   - timestamp: ISO 8601 format datetime when task completed

5a. Log to Decision Log:
   - Call @task-update-decision-log to log task execution:
   - For EACH solution discovered:
     * Extract solution name from path (e.g., "C:\...\MyApp.sln" → "MyApp")
     * Call:
     ```
     @task-update-decision-log 
       timestamp="{{timestamp}}" 
       repo_name="{{repo_name}}" 
       solution_name="" 
       task="task-find-solutions" 
       message="Found solution: {{solution_name}}" 
       status="SUCCESS"
     ```
   - If NO solutions found:
     * Call:
     ```
     @task-update-decision-log 
       timestamp="{{timestamp}}" 
       repo_name="{{repo_name}}" 
       solution_name="" 
       task="task-find-solutions" 
       message="No solutions found" 
       status="SUCCESS"
     ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - The solution_name is blank since this is a repository-level task
   - Status: "SUCCESS" (even if 0 solutions found, as long as directory was valid)

6. Result Tracking:
   - Append the result to:
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-find-solutions | {{solution_count}} solutions | status | symbol (✓ or ✗)

7. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][task-find-solutions] EXIT repo_directory='{{repo_directory}}' status={{status}} solution_count={{solution_count}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the find-solutions task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-find-solutions] allowing simple grep filtering.
- Entry Message: "[debug][task-find-solutions] START repo_directory='<path>'" emitted before step 1.
- Validation Messages: "[debug][task-find-solutions] directory validated: <path>" or "directory does not exist: <path>".
- Search Message: "[debug][task-find-solutions] searching for *.sln files recursively" before discovery.
- Discovery Messages: "[debug][task-find-solutions] found: <solution_path>" for each .sln file discovered.
- Count Message: "[debug][task-find-solutions] discovered <N> solution(s)" after collection complete.
- Exit Message: "[debug][task-find-solutions] EXIT repo_directory='<path>' status=<SUCCESS|FAIL> solution_count=<N>" emitted after step 7.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- local_path: string (absolute path to repository root, echoed from input)
- repo_name: string (repository name, echoed from input)
- solutions: array[string] (absolute paths to all .sln files discovered, empty array if none found)
- solution_count: integer (number of solutions discovered)
- status: SUCCESS | FAIL (SUCCESS if directory valid, FAIL if directory does not exist)
- timestamp: string (ISO 8601 datetime when task completed)

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. Idempotency: Discovery re-runs always produce a fresh list; same input yields same output.
3. Ordering: Filesystem traversal order may differ across runs; no guarantee of stable ordering unless explicitly sorted.
4. Filtering: Only .sln extension; does not validate solution file contents or accessibility.
5. Performance: Use efficient recursive search API (e.g., Path.rglob in Python, Get-ChildItem -Recurse in PowerShell).
6. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
7. Progress Update: Only set [x] in repo-progress for task-find-solutions on SUCCESS.
8. Empty Results: Finding 0 solutions is SUCCESS (directory was valid, just no solutions present).
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task5_find-solutions.py
10. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired.


