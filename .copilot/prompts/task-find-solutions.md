@task-find-solutions repo_directory={{repo_directory}}
---
temperature: 0.1
---

Task name: task-find-solutions

Description:
This tool discovers all Visual Studio solution files (.sln) within a specified repository directory tree {{repo_directory}} and returns their absolute paths. It performs a recursive search from the given root directory and outputs a JSON structure containing the repository path and a list of all discovered solution files.

Behavior:

1. Input Validation: Reads JSON from stdin expecting a local_path field (absolute path to repository root); raises ContractError if missing or if the path does not exist on disk.

2. Recursive Discovery: Uses Path.rglob("*.sln") to search all subdirectories recursively for files ending in .sln, converting each Path object to an absolute string path.

3. Output: Returns JSON object with two fields: local_path (echoed input) and solutions (array of absolute .sln file paths in discovery order, which may vary by filesystem); writes to stdout for workflow consumption.

3a. Log to Decision Log:
   - For EACH solution file discovered, append to: results/decision-log.csv
   - Append row with: "{{timestamp}},{{repo_name}},,task-find-solutions,Found solution: {{solution_name}},SUCCESS"
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - {{solution_name}}: Extract from solution file path (e.g., "MyApp.sln" → "MyApp") - used only in the Message field
   - The solution_name column (third column) should be blank (empty) since this is a repository-level discovery task
   - If no solutions found, append single row: "{{timestamp}},{{repo_name}},,task-find-solutions,No solutions found,SUCCESS"

4. Logging: Emits debug messages showing input payload and count of discovered solutions

5. Error Handling: Throws ContractError for invalid input (missing or nonexistent path), which the caller must handle; does not validate solution file contents or accessibility.

Output Contract:
- local_path: string (absolute path to repository root)
- solutions: array[string] (absolute .sln paths)
- solution_count: integer (number of discovered solutions)

Implementation Notes (conceptual):
1. Idempotency: Discovery re-runs always produce a fresh list; downstream should handle duplicates gracefully.
2. Ordering: Filesystem traversal order may differ; no guarantee of stable ordering unless explicitly sorted.
3. Filtering: Only .sln extension; future enhancement could include exclusion patterns.
4. Performance: Prefer single recursive search API (e.g., rglob) to minimize IO overhead.
5. Error Handling: On invalid repo_directory, return FAIL (or raise) and omit solutions field.


