@workflow-loop input=<optional> clone=<optional> clean_results=<optional>
---
temperature: 0.1
model: gpt-5
---

** ⚠️⚠️⚠️ CRITICAL MISTAKES TO AVOID ⚠️⚠️⚠️ **

**❌ MISTAKE: Processing Repository 1 without KB workflow, then starting Repository 2**
```
Repository 1:
  ✓ task-process-solutions (4 solutions found, 4 build FAIL)
  ❌ NO task-search-knowledge-base logged
  ❌ NO task-create-knowledge-base logged  
  ❌ NO task-apply-knowledge-base-fix logged
  ❌ NO retry builds logged
  ❌ SKIPPED: task-validate-all-solution-tasks-completed
  
Repository 2:
  ✓ task-clone-repo ❌ (WRONG - Cannot start Repo 2 until Repo 1 validates!)
```
**Why wrong:** KB workflow was completely skipped, validation was skipped, moved to next repo prematurely.

**✅ CORRECT: Complete KB workflow for all failures, validate, then move to next repo**
```
Repository 1:
  ✓ task-process-solutions:
    Solution 1 FAIL → Search KB → Create KB → Apply fix → Retry build ✓
    Solution 2 FAIL → Search KB → Create KB → Apply fix → Retry build ✓
    Solution 3 SUCCESS ✓
    Solution 4 FAIL → Search KB → Apply fix → Retry build ✓
  ✓ task-validate-all-solution-tasks-completed (validates KB workflow was executed) ✓
  
Repository 2: (Now safe to start)
  ✓ task-clone-repo
  ...
```

**MANDATORY REQUIREMENTS:**
1. ✅ task-process-solutions MUST execute KB workflow for ALL build failures
2. ✅ task-validate-all-solution-tasks-completed MUST run before next repository
3. ✅ Validation MUST check that KB tasks are logged for all failures
4. ✅ DO NOT start next repository until validation_status == SUCCESS

---

Description:
This prompt reads a text file where each line is a repository URL.
For each line, it executes a list of tasks defined in the `@tasks` prompt.
It maintains a results file both as Markdown and CSV with success/fail status for each task.

Behavior:
1. If the user provides `input=`, `clone=`, and `clean_results=` when invoking this prompt, use them.
   Defaults:
      input = "repositories.txt"
      clone = "./cloned"
      clean_results = true
2. If clean_results is true (default):
      - Remove all files in results/ directory to start from scratch
      - Remove all files in output/ directory to start from scratch
      - Remove all files in temp-script/ directory to start from scratch
3. Ensure the clone directory exists; create if it does not.

3. Create and initialize a repository progress markdown file:
      - results/repo-progress.md (Repository Progress tracking table)
      - Parse all repository URLs from input file to get friendly repo names
      - Parse repo_tasks_list.md to extract ALL task directive names (e.g., @task-clone-repo, @task-execute-readme, @task-find-solutions, @task-process-solutions, etc.)
      - Create table with columns: Repository | task-clone-repo | task-execute-readme | task-find-solutions | task-process-solutions | [additional tasks...]
      - **IMPORTANT**: Include a column for EVERY task found in repo_tasks_list.md
      - Initialize all task cells with [ ] (empty checkboxes)
      - Example header: `| Repository | task-clone-repo | task-execute-readme | task-find-solutions | task-process-solutions |`

4. Create and initialize a decision log CSV file:
      - results/decision-log.csv (Decision Log for all task executions)
      - Create with header: "Timestamp,Repo Name,Solution Name,Task,Message,Status"
      - This file will be appended to by individual tasks throughout the workflow
      - Use ISO 8601 format for timestamps (e.g., "2025-10-22T14:30:45Z")

5. Initialize results files:
      - results/repo-results.md (Repository Markdown table)
      - results/repo-results.csv (Repository CSV table)
    
6. Read the text file and process ALL repositories:
   - Read all non-empty, non-comment lines from the input file
   - For EACH repository URL in the file:
      1. Extract a friendly repo_name from the URL
      2. Call `@repo_tasks-list` with repo_url and clone_path
      3. Append success/fail for each task to Markdown + CSV
      4. Update repo-progress.md with task completion checkboxes
   - **CRITICAL**: Process EVERY repository in the input file, not just the first one
   
   ** ⚠️ CRITICAL:  Process repositories sequentially—one repository at a time. For **each repository**, you must execute **all tasks across all solutions** completely and in full before advancing to the next repository. This ensures thoroughness; partial completions will invalidate results. ⚠️ **


7. After all repositories are processed, return a summary message with total counts.

Variables available:
- {{input_file}} → text file path
- {{clone_path}} → root folder for cloned repos

Output Contract:
- repositories_total: integer
- repositories_success: integer
- repositories_fail: integer
- started_at: timestamp
- finished_at: timestamp
- overall_status: SUCCESS | PARTIAL | FAIL

Implementation Notes (conceptual):
1. Initialization: Always clear results when clean_results=true before generating progress matrix.
2. Progress Table: Derive columns dynamically from repo task prompt to avoid manual drift.
3. Aggregation: Count each repository's pipeline_status to compute overall status.
4. Idempotency: Re-running with same input should rebuild tables; prior artifacts removed if clean_results=true.
5. Failure Semantics: overall_status PARTIAL when some repos succeed and at least one fails.
6. **Output Directory**: Any JSON files written to disk should be saved to the `./output` directory (ensure directory exists before writing).
7. **Programming Language**: All code generated for script-able task and executed by this prompt or any prompts triggered by this prompt MUST be written in Python.
8. **Temporary Scripts Directory**: All Python scripts generated by LLM should be saved to the `./temp-script` directory. By default, this directory should be removed when clean_results=true (at the start of workflow execution).
