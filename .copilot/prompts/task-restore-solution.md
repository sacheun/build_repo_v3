@task-restore-solution solution_path={{solution_path}}

Task name: task-restore-solution

Description:
This task restores NuGet packages for a specific Visual Studio solution file.
It prints out the path of the solution file and performs package restoration.

Behavior:
1. Validate the solution file path:
   - Check if {{solution_path}} exists and is a valid .sln file
   - Extract solution_name from the path (e.g., "C:\path\to\MyApp.sln" → "MyApp")

2. Print the solution file information:
   - Display the absolute path to the solution file
   - Display the solution name
   - Display the directory containing the solution

3. Execute package restoration:
   - Navigate to the solution directory
   - Execute shell command: dotnet restore {{solution_path}}

4. If restoration succeeds → return SUCCESS
   If restoration fails → return FAIL

5. Append the result to:
   - results/solution-results.md (Markdown table row with solution name)
   - results/solution-results.csv (CSV row with solution name)

6. Update the progress table:
   - In results/solution-progress.md, find the appropriate row and column for "task-restore-solution"
   - Change [ ] to [x] to mark task as completed

7. Return the solution information:
   - Solution path
   - Solution name
   - Restoration status

Implementation Notes (conceptual, not executable code):
1. A runner should perform the validation, printing, restore, logging, progress update, and JSON emission described above.
2. Idempotency: re-running must not duplicate rows or re-flip already checked progress cells.
3. Output contract (JSON) expected fields:
    - solution_path (string, absolute)
    - solution_name (string, no extension)
    - restore_status (SUCCESS | FAIL)
4. Logging order recommendation:
    a. Print metadata
    b. Run restore
    c. Append results rows
    d. Update progress checkbox
    e. Emit JSON line for chaining
5. Error handling: on invalid path or failed restore mark FAIL, skip checkbox update, still emit JSON.