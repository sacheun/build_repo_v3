@solution-tasks-list solution_path={{solution_path}}

Description:
This prompt executes a sequence of tasks for a single solution file (.sln). Each task receives the output of the previous one.

Current Solution Tasks List:
1. @task-restore-solution

Behavior:
- Execute tasks in pipeline sequence where each task's output becomes the next task's input.

   1. **First Task (@task-restore-solution):**
      - Input: solution_path (absolute path to .sln)
      - Action: Print solution file path and attempt restore (dotnet restore)
      - Output: JSON summary with solution_path, solution_name, restore_status
      - Mark success/fail in solution-results.md and solution-results.csv

- If any task fails, stop further execution and return failure status.
- After all tasks complete successfully, return a dictionary (or JSON blob) of all task outputs.

Variables available:
- {{solution_path}} → Absolute path to the .sln file being processed.
- {{previous_output}} → Output from the last executed task (not used yet, reserved for future tasks).
- {{solution_name}} → Friendly solution name derived from the file name without extension.
