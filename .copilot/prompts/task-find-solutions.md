@task-find-solutions repo_directory={{repo_directory}}

Task name: task-clone-repo

Description:
This tool discovers all Visual Studio solution files (.sln) within a specified repository directory tree {{repo_directory}} and returns their absolute paths. It performs a recursive search from the given root directory and outputs a JSON structure containing the repository path and a list of all discovered solution files.

Behavior:

1. Input Validation: Reads JSON from stdin expecting a local_path field (absolute path to repository root); raises ContractError if missing or if the path does not exist on disk.

2. Recursive Discovery: Uses Path.rglob("*.sln") to search all subdirectories recursively for files ending in .sln, converting each Path object to an absolute string path.

3. Output: Returns JSON object with two fields: local_path (echoed input) and solutions (array of absolute .sln file paths in discovery order, which may vary by filesystem); writes to stdout for workflow consumption.

4. Logging: Emits debug messages showing input payload and count of discovered solutions

5. Error Handling: Throws ContractError for invalid input (missing or nonexistent path), which the caller must handle; does not validate solution file contents or accessibility.

