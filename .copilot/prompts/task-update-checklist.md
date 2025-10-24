@task-update-checklist repo_name={{repo_name}} task_name={{task_name}} solution_name={{solution_name}}
---
temperature: 0.1
---

Description:
This prompt updates a task checklist to mark a completed task as done.
It updates either a repository-level task or a solution-level task based on whether solution_name is provided.

Behavior:
1. Parse the required parameters:
   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")
   - task_name: Name of the task to mark as complete (e.g., "@task-clone-repo", "@task-build-solution")
   - solution_name: (Optional) Name of the solution if updating a solution task

2. Locate the repository checklist file:
   - File: ./tasks/{repo_name}_checklist.md
   - If file does not exist, return FAIL status with error message

3. Read the current checklist content

4. Determine the scope of the update:
   
   **If solution_name is NOT provided (repository-level task):**
   - Search for the task in the repository tasks section (before any "## Solution:" sections)
   - Find the line containing the task_name (e.g., "@task-clone-repo")
   - Update the checkbox from `- [ ]` to `- [x]`
   - If task not found, return FAIL status with error message
   
   **If solution_name IS provided (solution-level task):**
   - Search for the section: `## Solution: {solution_name}`
   - Within that section only, find the line containing the task_name
   - Update the checkbox from `- [ ]` to `- [x]`
   - If section not found, return FAIL status with error message
   - If task not found in that section, return FAIL status with error message

5. Write the updated content back to the checklist file

6. Check if all tasks are completed:
   
   **For repository-level update:**
   - Count remaining uncompleted tasks in repository section (lines with `- [ ]`)
   - If all repository tasks are completed, set repo_tasks_complete = true
   
   **For solution-level update:**
   - Count remaining uncompleted tasks in that solution section
   - If all tasks for that solution are completed, set solution_tasks_complete = true
   - Also check if all solutions in the repository have all tasks completed
   - If so, set all_solutions_complete = true

7. Return status with completion information

Variables available:
- {{repo_name}} → Friendly repository name
- {{task_name}} → Task directive name to mark complete
- {{solution_name}} → (Optional) Solution name for solution-specific tasks
- {{tasks_dir}} → Directory where checklists are saved (./tasks)

Output Contract:
- repo_name: string
- task_name: string
- solution_name: string | null
- task_updated: boolean
- previous_status: "incomplete" | "complete"
- current_status: "incomplete" | "complete"
- scope: "repository" | "solution"
- repo_tasks_complete: boolean (true if all repo tasks are done)
- solution_tasks_complete: boolean | null (true if all tasks for this solution are done)
- all_solutions_complete: boolean | null (true if all solutions have all tasks done)
- checklist_path: string
- updated_at: timestamp
- status: SUCCESS | FAIL
- error_message: string | null

Implementation Notes:
1. **Exact Match Required**: Task name must match exactly (including @ symbol)
2. **Scope Isolation**: Solution tasks only update within their solution section
3. **Idempotent**: Marking an already completed task as complete returns SUCCESS (no-op)
4. **Atomic Update**: Read entire file, modify, write back to avoid partial updates
5. **Section Boundaries**: Solution sections start with `## Solution:` and end at next `##` or EOF
6. **Completion Tracking**: Track completion at three levels:
   - Repository tasks (all tasks before first solution section)
   - Solution tasks (tasks within specific solution section)
   - All solutions (true only if ALL solutions have ALL tasks complete)
7. **Programming Language**: All code generated should be written in Python
8. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory
9. **Error Handling**: Return descriptive error messages for:
   - Checklist file not found
   - Solution section not found
   - Task not found in specified scope
   - Invalid task name format

Example Usage:
```
# Mark repository-level task as complete
@task-update-checklist repo_name="ic3_spool_cosine-dep-spool" task_name="@task-clone-repo"

# Mark solution-level task as complete
@task-update-checklist repo_name="ic3_spool_cosine-dep-spool" task_name="@task-build-solution" solution_name="ResourceProvider"
```

Completion Detection Logic:
```
Repository Tasks Complete:
  - Count all `- [ ]` in lines before first `## Solution:`
  - If count == 0, set repo_tasks_complete = true

Solution Tasks Complete:
  - Count all `- [ ]` in lines between `## Solution: {name}` and next `##` or EOF
  - If count == 0, set solution_tasks_complete = true

All Solutions Complete:
  - For each `## Solution:` section, check if all tasks are `- [x]`
  - If ALL sections have zero `- [ ]`, set all_solutions_complete = true
```
