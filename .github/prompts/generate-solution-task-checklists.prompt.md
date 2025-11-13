---
temperature: 0.0
---

@generate-solution-task-checklists checklist_path={{checklist_path}}

Task name: generate-solution-task-checklists

## Description
Generate individual solution-level checklist files for a repository.  
This creates ONE checklist file per solution (.sln) discovered in the repo.

## Execution Policy
**STRICT MODE: ENFORCED EXECUTION ORDER**

> ⚠️ **Every step below MUST be executed sequentially.**
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

---

### Step 2 — Generate One Checklist File per Solution (MANDATORY)
**Checkpoint → Confirm all files created.**

1. For each `solution` in the parsed list:
   - Create file: `./tasks/{repo_name}_{solution_name}_solution_checklist.md`  
   - Sanitize `solution_name` (replace spaces/special characters with underscores).  
   - Overwrite if it exists.  
2. Ensure at least one checklist file created.  
3. **Checkpoint:** Record verification result and continue to **Step 3**.

---

### Step 3 — Write Solution Checklist Contents (MANDATORY)
**Checkpoint → Confirm each file written with full template.**

1. For each checklist file, write this canonical template atomically (FULL CONTENT – do not truncate):  
   ```markdown
   # Solution Checklist: {solution_name}
   Repository: {repo_url}
   Generated: {timestamp}

   ## Solution: {solution_name}

   ### Solution Variables
   - Solution name: {solution_name}
   - Solution path: {solution_path}
   - Parent repo: {repo_name}
   - restore_status: (blank)
   - Last build status: (blank)
   - Last build timestamp: (blank)
   - Build attempts: 0
   - build_status: (blank)
   - verify_status: (blank)
   - kb_search_status: (blank)
   - kb_file_path: (blank)
   - kb_article_status: (blank)
   - fix_applied_attempt_1: (blank)
   - kb_option_applied_attempt_1: (blank)
   - retry_build_status_attempt_1: (blank)
   - fix_applied_attempt_2: (blank)
   - kb_option_applied_attempt_2: (blank)
   - retry_build_status_attempt_2: (blank)
   - fix_applied_attempt_3: (blank)
   - kb_option_applied_attempt_3: (blank)
   - retry_build_status_attempt_3: (blank)

   ### Tasks
   - [ ] (1) [MANDATORY] [SCRIPTABLE] Restore NuGet packages → @task-restore-solution
   - [ ] (2) [MANDATORY] [SCRIPTABLE] Build solution (Clean + Build) → @task-build-solution
   - [ ] (3) [CONDITIONAL] [NON-SCRIPTABLE] Search knowledge base for error fix → @task-search-knowledge-base
   - [ ] (4) [CONDITIONAL] [NON-SCRIPTABLE] Create knowledge base article → @task-create-knowledge-base
   - [ ] (5) [CONDITIONAL Attempt 1] [NON-SCRIPTABLE] Apply fix from KB → @task-apply-knowledge-base-fix
   - [ ] (6) [CONDITIONAL Attempt 1] [SCRIPTABLE] Retry build after fix → @task-build-solution-retry
   - [ ] (7) [CONDITIONAL Attempt 2] [NON-SCRIPTABLE] Apply fix from KB → @task-apply-knowledge-base-fix
   - [ ] (8) [CONDITIONAL Attempt 2] [SCRIPTABLE] Retry build after fix → @task-build-solution-retry
   - [ ] (9) [CONDITIONAL Attempt 3] [NON-SCRIPTABLE] Apply fix from KB → @task-apply-knowledge-base-fix
   - [ ] (10) [CONDITIONAL Attempt 3] [SCRIPTABLE] Retry build after fix → @task-build-solution-retry
   - [ ] (11) [MANDATORY] [SCRIPTABLE] Validate build artifacts  → @task-validate-build-artifacts

   ### Retry Attempts Guidance
   Attempt 1: Initial restore/build.
   Attempt 2: Apply first KB fix then rebuild.
   Attempt 3: Apply second KB fix then rebuild; escalate if still failing.

   ## For Agents Resuming Work
   1. Start at the first unchecked task in order.
   2. Update build status/timestamp variables after each build.
   3. Record any KB article references inline below tasks.
   ```

2. Verify that each file includes headings: “### Solution Variables”, “### Tasks”, and “### Retry Attempts Guidance”.  
3. **Checkpoint:** Log verification status and continue to **Step 4**.

---

### Step 4 — Update Repository Checklist (MANDATORY)
**Checkpoint → Confirm repo checklist updated correctly.**

1. Open `tasks/{{repo_name}}_repo_checklist.md`.  
2. Mark `[x]` on the `@generate-solution-task-checklists` entry **only**.  
3. Do not modify other items.  
4. **Checkpoint:** Record success/fail. Continue to **Step 5**.

---

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

---

### Step 6 — Final Verification of Repository Checklist Update (MANDATORY)
**Checkpoint → Ensure checklist reflects correct completion status.**

1. Reopen `tasks/{{repo_name}}_repo_checklist.md`.  
2. Verify that the entry for `@generate-solution-task-checklists` is **checked `[x]`**.  
3. If unchecked or missing, log a warning and **redo from Step 0** (reload and re‑execute the entire process).  
4. Only mark task as `FINAL SUCCESS` if the verification passes.  
5. Output a final confirmation message:  
   > ✅ “All checklist updates verified successfully — task complete.”

---

### Reliability Enforcement
- After each step, log: `✅ Step N complete — proceeding to Step N+1`  
- Never stop early before Step 6.  
- Always produce structured JSON output at the end.
