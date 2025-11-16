---
temperature: 0.0
---

@task-generate-solution-task-checklists checklist_path={{checklist_path}}

Task name: task-generate-solution-task-checklists

## Description
Generate individual solution-level checklist files for a repository.  
This creates ONE checklist file per solution (.sln) discovered in the repo.

## Execution Policy
**STRICT MODE: ENFORCED ORDER — NO EARLY EXIT**

> ⚠️ EVERY STEP BELOW MUST BE EXECUTED IN ORDER (Step 1 → Step 2 → ... → Step 6).  

> - **NO steps may be skipped, summarized, or merged.**
> - **Each step has its own completion checkpoint.**
> - **If any earlier step fails, mark status=FAIL but still execute Step 5 to produce output JSON.**
> - **DO NOT stop after failure unless explicitly told to.**
> - **ALWAYS continue to the next step once the current step is complete or fails.**

You are executing a **multi-step scripted task**.  
Follow steps **in exact order (Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6)**.  
Each step must output a verification result before proceeding.

---

## Instructions (Follow Exactly as Ordered)

### Step 1 — Load Repository Checklist (MANDATORY)
**Checkpoint → Must output success/fail before continuing.**

1. Treat the `checklist_path` argument as an **absolute path** (e.g., `tasks/{repo_name}_repo_checklist.md`).  
2. Verify file existence and that the filename ends with `_repo_checklist.md`.  
   - If invalid, set `status=FAIL` and skip Steps 2–4 but **still execute Step 5**.  
3. Read the file (UTF-8). Extract exact variable values from these lines (value is the text after `→`):
   ```
   - {{repo_name}} →
   - {{repo_url}} →
   - {{repo_directory}} →
   - {{solutions_json}} →
   ```
4. Validate mandatory variables (`repo_name`, `repo_directory`, `solutions_json`) are non-blank. `repo_url` may be blank; if blank substitute `<unknown>` in templates.  
5. If valid AND `solutions_json` points to an existing file, load JSON. Expect key `solutions` (array of absolute `.sln` paths).  
6. For each path in `solutions`, derive solution name = basename without extension (e.g., `C:\x\Foo.Bar.sln` → `Foo.Bar`).  
7. Build internal list objects: `{ name: <derived_name>, path: <absolute_path> }`.  
8. If file missing or malformed, record a verification error but continue with empty list (status may still be SUCCESS if checklist load passed).  
9. **Checkpoint:** Output interim success/fail (for checklist load) and continue to **Step 2** regardless.

### Step 2  Generate One Checklist File per Solution (MANDATORY)
**Checkpoint  Confirm all files created, one per solution.**

1. For **every** `solution` in the parsed list from Step 1:
   - Create file: `./tasks/{repo_name}_{solution_name}_solution_checklist.md`  
   - Sanitize `solution_name` (replace spaces/special characters with underscores).  
   - Overwrite if it exists.  
2. After processing, **verify that the number of created solution checklist files is exactly equal to the number of `solutions` entries** parsed in Step 1.
3. If the counts differ (e.g., only some solutions produced checklists), mark `status=FAIL` for this task but still proceed to Step 3 and later steps as required.
4. **Checkpoint:** Explicitly log how many solutions were parsed and how many checklist files were created, then continue to **Step 3**.

### Step 3 — Write Solution Checklist Contents (MANDATORY)
**Checkpoint → Confirm each file written with full template.**

1. For each checklist file, overwrite the file with this canonical template (write atomically; no legacy sections may remain):  
   ```markdown
   # Solution Checklist: {solution_name}
   Repository: {repo_url}
   Generated: {timestamp}

   ## Solution: {solution_name}

   ### Solution Tasks
   - [ ] (1) [MANDATORY] [SCRIPTABLE] Restore NuGet packages → @task-restore-solution (see details in #file: .github/prompts/task-restore-solution.prompt.md)
   - [ ] (2) [MANDATORY] [SCRIPTABLE] Build solution (Clean + Build) → @task-build-solution (see details in #file: .github/prompts/task-build-solution.prompt.md)
   - [ ] (3) [MANDATORY] [SCRIPTABLE] Validate build artifacts  → @task-validate-build-artifacts (see details in #file: .github/prompts/task-validate-build-artifacts.prompt.md)
   - [ ] (4) [MANDATORY] [SCRIPTABLE] Dotnet Build solution → @task-dotnet-build-solution (see details in #file: .github/prompts/task-dotnet-build-solution.prompt.md)
   - [ ] (5) [MANDATORY] [NON-SCRIPTABLE] Search knowledge base for error fix → @task-search-knowledge-base (see details in #file: .github/prompts/task-search-knowledge-base.prompt.md)
   - [ ] (6) [MANDATORY] [NON-SCRIPTABLE] Create new knowledge base for error → @task-create-knowledge-base (see details in #file: .github/prompts/task-create-knowledge-base.prompt.md)
   - [ ] (7) [MANDATORY] [NON-SCRIPTABLE] Apply fix from knowledge base → @task-apply-knowledge-base-fix (see details in #file: .github/prompts/task-apply-knowledge-base-fix.prompt.md)
   - [ ] (8) [MANDATORY] [SCRIPTABLE] Build solution (Clean + Build) → @task-build-solution retry (see details in #file: .github/prompts/task-build-solution.prompt.md)

   ### Solution Variables
   - solution_name: {solution_name}
   - solution_path: {solution_path}
   - parent_repo: {repo_name}
   - restore_status: (blank)
   - build_count: 0
   - build_status: (blank)
   - verify_status: (blank)
   - expected_artifacts: (blank)
   - missing_artifacts: (blank)
   - verified_artifacts: (blank)
   - dotnetbuild_status: (blank)

   ** Knowledge base **
   - kb_search_status: (blank)
   - kb_file_path: (blank)
   - kb_article_status: (blank)
   - kb_create_status: (blank)
   - last_option_applied: 0
   - fix_status = (blank)
   - fix_applied_attempt_1: (blank)
   - kb_option_applied_attempt_1: (blank)
   - retry_build_status_attempt_1: (blank)

   ## For Agents Resuming Work
   1. Start at the first unchecked task in order.
   2. Update build status/timestamp variables after each build.
   3. Record any KB article references inline below tasks.
   ```
3. **Checkpoint:** Log verification status and continue to **Step 4**.

### Step 4 — Update Repository Checklist (MANDATORY)
**Checkpoint → Confirm repo checklist updated correctly.**

1. Open `tasks/{{repo_name}}_repo_checklist.md`.  
2. Mark `[x]` on the `@task-generate-solution-task-checklists` entry **only after** all earlier steps in this prompt (including file generation and validation) have succeeded.  
3. Do not modify other items.  
4. **Checkpoint:** Record success/fail. Continue to **Step 5**.

### Step 5 — Structured Output JSON (**ALWAYS EXECUTE THIS STEP**)
**Checkpoint → Must always produce JSON output file.**

1. Write JSON: `output/{repo_name}_task5_generate-solution-checklists.json`  
2. Include all keys:
   - repo_name
   - repo_directory
   - solutions_total
   - checklist_paths
   - status (SUCCESS | FAIL)
   - timestamp (ISO 8601 UTC)
   - generated_files (optional)
   - skipped_solutions (array)
3. **Checkpoint:** Confirm JSON written successfully.

### Step 6 — Final Verification of Repository Checklist Update (MANDATORY)
**Checkpoint → Ensure checklist reflects correct completion status.**

1. Reopen `tasks/{{repo_name}}_repo_checklist.md`.  
2. Verify that the entry for `@task-generate-solution-task-checklists` is **checked `[x]`**.  
3. Immediately re-open each file after writing and assert all canonical markers exist:
   - Header lines (`# Solution Checklist:` / `Repository:` / `Generated:`) appear exactly once.
   - Section headings exactly match `## Solution:`, `### Solution Tasks`, `### Solution Variables`, and `** Knowledge base **`.
   - Every task line contains a checkbox, sequential number 1–8, `[MANDATORY]` tag, the specific `@task-…` handle shown above, and uses the arrow character (`→`).
   - Variable lines follow the exact colon format shown (e.g., `- solution_name: {solution_name}`) and include all entries.
   - Knowledge base lines exactly match the block listed above (names, ordering, placeholders).
   - If any check fails, mark the attempt as `status=FAIL`, report the discrepancy, and stop further processing.
4. If unchecked or missing, log a warning and **redo from Step 0** (reload and re‑execute the entire process).  
5. Only mark task as `FINAL SUCCESS` if the verification passes.  
6. Output a final confirmation message:  
   > ✅ “All checklist updates verified successfully — task complete.”

### Reliability Enforcement
- After each step, log: `✅ Step N complete — proceeding to Step N+1`  
- Never stop early before Step 6.  
- Always produce structured JSON output at the end.
