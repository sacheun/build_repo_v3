@solution-tasks-list solution_path={{solution_path}}
@task-restore-solution solution_path={{solution_path}}
@task-build-solution solution_path={{solution_path}}

Description:
This prompt executes a sequence of tasks for a single solution file (.sln). Each task receives the output of the previous one.

Environment Initialization:
- Before executing any task directives set environment variable DEBUG=1.
- This enables verbose logging or additional diagnostics for all subsequent task prompts.

Current Solution Tasks List:
1. @task-restore-solution
2. @task-build-solution
3. @task-collect-knowledge-base

Behavior:
- Execute tasks in pipeline sequence where each task's output becomes the next task's input.

   1. **Restore Task (@task-restore-solution):**
      - Input: solution_path (absolute path to .sln)
      - Action: Conceptual restore (dotnet restore) validation + status capture.
      - Output: solution_path, solution_name, restore_status.
      - Tracking: update solution-results.* with restore outcome.

   2. **Build Task (@task-build-solution):**
      - Prerequisite: Normally only runs if restore_status == SUCCESS (or orchestrator override).
      - Action: Conceptual MSBuild Clean+Build Release capture + diagnostics extraction.
      - Output: build_status, errors[], warnings[] plus solution_path, solution_name.
      - Tracking: append build outcome row (avoiding duplicates) to solution-results.*

   3. **Knowledge Base Collection Task (@task-collect-knowledge-base):**
      - Prerequisite: Runs after build task, processes build failures only.
      - Input: build_status, build_stderr (error output from build task).
      - Action: Extract detection tokens from build errors, search/create knowledge base markdown files.
      - Output: kb_status (SUCCESS | SKIPPED), kb_file_path (if created/found).
      - Tracking: Creates or updates markdown files in ./knowledge_base_markdown/ directory.
      - Behavior:
        a. If build_status == SUCCESS, return kb_status=SKIPPED (no action needed).
        b. If build_status == FAIL, extract "Detection Tokens" from stderr.
        c. Search existing .md files in ./knowledge_base_markdown/ for matching tokens.
        d. If match found, return kb_status=SUCCESS with kb_file_path.
        e. If no match, create new .md file with standardized format including:
           - Issue description
           - Diagnostic hints
           - Detection tokens
           - Fix instructions
           - Example solution path
        f. Generate meaningful filename based on error signature.

- If any task fails, subsequent tasks are SKIPPED and pipeline_status=FAIL.
- On success of all tasks pipeline_status=SUCCESS.
- Note: @task-collect-knowledge-base runs even if build fails (it processes failures).

Variables available:
- {{solution_path}} → Absolute path to the .sln file being processed.
- {{previous_output}} → Output from the last executed task (not used yet, reserved for future tasks).
- {{solution_name}} → Friendly solution name derived from the file name without extension.

Task name: solution-tasks-list

Directive Format:
- Each pipeline directive appears as: `@task-<task-name> key=value key2=value2`
- Placeholders like `{{solution_path}}`, `{{solution_name}}` are substituted before execution.

Execution Semantics:
0. Set DEBUG=1 in the execution environment (e.g., $env:DEBUG="1" or export DEBUG=1) prior to any task.
1. Parser reads lines starting with `@task-` (excluding @solution-tasks-list header) preserving order.
2. Substitute placeholders (e.g., {{solution_path}}, {{solution_name}}) per directive.
3. Execute restore directive; record restore_status.
4. If restore failed, mark build_status=SKIPPED; else execute build directive.
5. Merge outputs (last key wins) forming cumulative pipeline output.
6. On first failure, halt remaining directives; pipeline_status=FAIL. Else pipeline_status=SUCCESS.

Extensibility Guidelines:
- Append new tasks (e.g., test, package) as additional @task-* lines after build.
- Each task defines distinct status key (test_status, package_status, etc.).
- Avoid destructive overwrites of prior task diagnostic arrays.
- Prefer additive keys to maintain clarity in merged output.

Output Contract (aggregate pipeline output):
- solution_path: string
- solution_name: string
- restore_status: SUCCESS | FAIL
- build_status: SUCCESS | FAIL | SKIPPED
- build_stderr: string (error output from build, empty if success)
- errors: array[string] (build diagnostic error codes; empty if none or skipped)
- warnings: array[string] (build diagnostic warning codes; empty if none or skipped)
- kb_status: SUCCESS | SKIPPED (knowledge base collection status)
- kb_file_path: string (path to knowledge base file if created/found)
- pipeline_status: SUCCESS | FAIL

Implementation Notes (conceptual):
1. Ordering is source-of-truth; do not auto-sort directives.
2. Environment DEBUG=1 is a global flag; tasks may inspect it to increase verbosity.
3. Idempotency: Each task responsible for avoiding duplicate result rows in tracking artifacts.
4. Error Propagation: Failure sets pipeline_status=FAIL; subsequent tasks marked SKIPPED.
5. Diagnostics: errors/warnings arrays derived only from build task; restore does not populate them.
6. Extensibility: Additional tasks append status + optional diagnostics keys without altering prior arrays.
7. Merging: Later tasks should avoid deleting earlier keys; only add or update their own status fields.
