@generate-solution-task-checklists repo_name=<required> solutions=<required>
---
temperature: 0.1
model: gpt-4
---

Description:
This prompt generates solution-specific task checklists and adds them as sections to an existing repository checklist.
It allows agents to track progress for each solution within a repository.

Behavior:
1. Parse the required parameters:
   - repo_name: Friendly name of the repository (e.g., "ic3_spool_cosine-dep-spool")
   - solutions: Array of solution objects with name and path properties
     Format: [{"name": "Solution1", "path": "/path/to/solution1.sln"}, ...]

2. Locate the existing repository checklist:
   - File: ./tasks/{repo_name}_checklist.md
   - If file does not exist, return FAIL status

3. Parse solution_tasks_list.md to extract ALL solution task directives:
   - Extract task names (e.g., @task-restore-solution, @task-build-solution, etc.)
   - Extract short descriptions for each task
   - Identify which tasks are mandatory vs optional based on the conditional workflow

4. For each solution in the solutions array:
   - Create a new section in the repository checklist
   - Section title: ## Solution: {solution_name}
   - Add solution path as metadata
   - Generate task checklist using same format as repo tasks

5. Append all solution sections to the repository checklist file:
   - Preserve existing content (repo tasks section)
   - Add solution sections after repo tasks
   - Maintain proper markdown formatting

6. Solution task checklist format (per solution):
   ```
   ## Solution: {solution_name}
   
   Path: {solution_path}
   
   ### Tasks (Conditional Workflow - See solution_tasks_list.md)
   
   - [ ] [MANDATORY #1] Restore NuGet packages @task-restore-solution
   - [ ] [MANDATORY #2] Build solution (Clean + Build) @task-build-solution
   - [ ] [CONDITIONAL] Search knowledge base for error fix @task-search-knowledge-base
   - [ ] [CONDITIONAL] Create knowledge base article @task-create-knowledge-base
   - [ ] [CONDITIONAL] Apply fix from knowledge base @task-apply-knowledge-base-fix
   - [ ] [RETRY] Retry restore after fix applied @task-restore-solution-retry
   - [ ] [RETRY] Retry build after fix applied @task-build-solution-retry
   
   ### For Agents Resuming Work
   
   **Next Action:** Find the first uncompleted [MANDATORY #N] task above. If build fails, follow conditional workflow.
   
   **How to Execute:** Invoke `@solution-tasks-list solution_path={solution_path}` which executes the full conditional workflow with automatic retry logic. See `solution_tasks_list.md` for complete workflow details.
   
   **Quick Reference:**
   - [MANDATORY] tasks: Restore (#1) → Build (#2) 
   - [CONDITIONAL] tasks execute only when build fails
   - [RETRY] tasks execute automatically after applying fixes
   - Workflow supports up to 3 build attempts with KB-driven fixes
   - Mark completed tasks with [x]
   
   ---
   ```

7. Return a summary message with:
   - Repository name
   - Total solutions processed
   - Checklist file updated
   - Location of updated file

Variables available:
- {{repo_name}} → Friendly repository name
- {{solutions}} → Array of solution objects
- {{tasks_dir}} → Directory where checklists are saved (./tasks)

Output Contract:
- repo_name: string
- solutions_total: integer
- checklist_updated: boolean
- checklist_path: string
- generated_at: timestamp
- status: SUCCESS | FAIL

Task Classification (from solution_tasks_list.md):
- MANDATORY (always execute): @task-restore-solution (#1), @task-build-solution (#2)
- CONDITIONAL (execute only on build failure):
  - @task-search-knowledge-base (after build fails)
  - @task-create-knowledge-base (if KB not found)
  - @task-apply-knowledge-base-fix (if KB found or created)
- RETRY (automatic after fix applied):
  - @task-restore-solution-retry (restore again before retry build)
  - @task-build-solution-retry (build again after fix)

Implementation Notes:
1. Solutions array must contain objects with "name" and "path" properties
2. Repository checklist must already exist (created by @generate-task-checklists)
3. Solution sections are appended to existing checklist (not replaced)
4. Task numbering for mandatory tasks: #1 (Restore), #2 (Build)
5. Conditional tasks do not have numbers (they execute based on build results)
6. Workflow is non-linear with retry loops (not a simple sequential pipeline)
7. **Programming Language**: All code generated should be written in Python
8. **Temporary Scripts Directory**: Scripts should be saved to ./temp-script directory
9. Re-running this prompt will replace existing solution sections with updated content
