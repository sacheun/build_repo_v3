@task-search-readme repo_directory={{repo_directory}} repo_name={{repo_name}}

Task name: task-search-readme

Description:
This task searches for and reads the README documentation file from a repository's root directory. This is a simple file location and content extraction task that CAN be implemented as a script.

** THIS TASK IS SCRIPTABLE **

This task can be implemented as a Python/PowerShell/Bash script that:
1. Searches for README files in the repository root
2. Reads the content of the first match found
3. Saves the result to JSON output
4. Updates progress and results files

Behavior:
0. DEBUG Entry Trace: If DEBUG=1, print: `[debug][task-search-readme] START repo_directory='{{repo_directory}}'`

1. Input Parameters: You are given repo_directory (absolute path to repository root) and repo_name from the calling context.

2. README Candidate Search: Iterates through prioritized list of common README filenames in exact order:
   - README.md
   - readme.md
   - README.txt
   - README.rst
   - README
   - Readme.md

3. File Discovery: Checks repository root directory for each candidate filename; stops on first match found.
   - If DEBUG=1, print: `[debug][task-search-readme] checking for: {{candidate_filename}}`
   - On first match, if DEBUG=1, print: `[debug][task-search-readme] found README file: {{matched_filename}}`

4. Content Extraction: 
   - If match found, reads entire file content as UTF-8 text with error ignore mode (handles encoding issues gracefully)
   - If DEBUG=1, print: `[debug][task-search-readme] content length: {{content_length}} characters`
   - If no match found, content remains null
   - If DEBUG=1 and no match, print: `[debug][task-search-readme] no README file found in repository root`

5. Structured Output: Save JSON object to output/{repo_name}_task2_search-readme.json with:
   - repo_directory: echoed from input
   - repo_name: echoed from input
   - readme_content: string if found, null otherwise
   - readme_filename: name of matched file, null if not found
   - status: SUCCESS if README found, FAIL if not found
   - timestamp: ISO 8601 format datetime when task completed

6. Result Tracking:
   - Append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Row format: timestamp | repo_name | task-search-readme | status | symbol (✓ or ✗)

7. Progress Update:
   - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-search-readme"
   - Change [ ] to [x] to mark task as completed

8. DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][task-search-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} readme_found={{readme_filename}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide clear trace that the search-readme task was called and for which repository, plus completion status.
- Activation: Only when DEBUG environment variable equals "1".
- Format Guarantees: Always starts with prefix [debug][task-search-readme] allowing simple grep filtering.
- Entry Message: "[debug][task-search-readme] START repo_directory='<path>'" emitted before step 1.
- Search Messages: "[debug][task-search-readme] checking for: <filename>" for each candidate checked.
- Found Message: "[debug][task-search-readme] found README file: <filename>" when match is found.
- Content Message: "[debug][task-search-readme] content length: <N> characters" after reading content.
- Not Found Message: "[debug][task-search-readme] no README file found in repository root" if no match.
- Exit Message: "[debug][task-search-readme] EXIT repo_directory='<path>' status=<SUCCESS|FAIL> readme_found=<filename|null>" emitted after step 7.
- Non-Interference: Does not modify success criteria or output contract; purely informational.

Output Contract:
- repo_directory: string (absolute path to repository root, echoed from input)
- repo_name: string (repository name, echoed from input)
- readme_content: string | null (full content of README file, null if not found)
- readme_filename: string | null (name of matched README file, null if not found)
- status: SUCCESS | FAIL (SUCCESS if README found and read, FAIL if not found)
- timestamp: string (ISO 8601 datetime when task completed)

Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python/PowerShell/Bash script to execute this task
2. Prioritization: Check filenames in exact order listed; first match wins.
3. Error Handling: File read errors (permissions, encoding) should be caught and logged; set status=FAIL if content cannot be extracted.
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
5. Progress Update: Mark [x] in repo-progress for task-search-readme on both SUCCESS and FAIL (task completed, even if README not found).
6. Content Handling: Return entire file content; do not truncate or summarize at this stage.
7. Encoding Tolerance: Use UTF-8 with ignore mode to handle malformed characters gracefully.
8. Null Safety: Ensure readme_content and readme_filename are explicitly null (not empty string) when no README found.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: step{N}_repo{M}_task2_search-readme.py (or .ps1/.sh)
10. Environment: Set DEBUG=1 environment variable at the start of the script if debug output is desired.

Example Script Structure (Python):
```python
import os
import json
from pathlib import Path
from datetime import datetime

os.environ['DEBUG'] = '1'

repo_name = "{{repo_name}}"
repo_directory = r"{{repo_directory}}"

print(f"[debug][task-search-readme] START repo_directory='{repo_directory}'")

readme_candidates = ["README.md", "readme.md", "README.txt", "README.rst", "README", "Readme.md"]
readme_filename = None
readme_content = None

for candidate in readme_candidates:
    print(f"[debug][task-search-readme] checking for: {candidate}")
    candidate_path = Path(repo_directory) / candidate
    if candidate_path.exists():
        readme_filename = candidate
        print(f"[debug][task-search-readme] found README file: {readme_filename}")
        try:
            with open(candidate_path, 'r', encoding='utf-8', errors='ignore') as f:
                readme_content = f.read()
            print(f"[debug][task-search-readme] content length: {len(readme_content)} characters")
        except Exception as e:
            print(f"[debug][task-search-readme] error reading file: {e}")
            readme_content = None
        break

if readme_filename is None:
    print("[debug][task-search-readme] no README file found in repository root")

status = "SUCCESS" if readme_filename else "FAIL"
timestamp = datetime.now().isoformat()

output_data = {
    "repo_directory": repo_directory,
    "repo_name": repo_name,
    "readme_content": readme_content,
    "readme_filename": readme_filename,
    "status": status,
    "timestamp": timestamp
}

output_file = Path("output") / f"{repo_name}_task2_search-readme.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2)

# Update progress and results (code omitted for brevity)

print(f"[debug][task-search-readme] EXIT repo_directory='{repo_directory}' status={status} readme_found={readme_filename}")
```
