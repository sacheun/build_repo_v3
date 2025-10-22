@task-process-solutions solutions_json={{solutions_json}}

Task name: task-process-solutions

Description:
This task takes a JSON object returned by task-find-solutions.md and processes each solution file found.
For each solution, it executes a list of tasks to perform operations on the solution.

Behavior:
1. Parse the input JSON object from {{solutions_json}} which contains:
   - local_path: repository directory path
   - solutions: array of absolute paths to .sln files

2. For each solution file in the solutions array:
   - Extract solution_name from the solution path (e.g., "C:\path\to\MyApp.sln" → "MyApp")
   - Execute the task list for this solution:
     * @task-restore-solution solution_path={{solution_path}}

3. Create and initialize a solutions progress markdown file:
      - results/solution-progress.md (Repository Progress tracking table)
      - Parse all repository URLs from input file to get friendly repo names
      - Parse all task names for a solution (see step #2 above)
      - Create table with solution names and its repo name as rows and task names as columns
      - Initialize all cells with [ ] (empty checkboxes)

4. Track progress for each solution processed:
   - Log each solution processing attempt
   - Count successful vs failed operations

5. If all solutions process successfully → return SUCCESS
   If any solution fails → return FAIL

6. Append the result to:
   - results/solution-results.md (Markdown table row)
   - results/solution-results.csv (CSV row)


7. Return summary of processed solutions:
   - Total solutions found
   - Successfully processed count
   - Failed processing count