---
temperature: 0.0
---

@task-generate-repo-task-checklists input=<optional> append=<optional>

Task name: task-generate-repo-task-checklists

## Description
This task generates task checklists for repositories listed in an input file. The checklists enable agents to pick up or resume work. This is a file-generation task and **is scriptable**.

## Execution Policy
**STRICT MODE: ENFORCED ORDER — NO EARLY EXIT**

> ⚠️ EVERY STEP BELOW MUST BE EXECUTED IN ORDER (Step 1 → Step 2 → ... → Step 7).  
> - **DO NOT SKIP, SUMMARIZE, MERGE, OR REORDER STEPS.**  
> - Each step MUST emit a clear checkpoint result before proceeding.  
> - If a step fails, record the failure (verification_errors) and **continue** to the next step.  
> - **Step 7 (Structured Output JSON)** MUST run in every execution (success or failure).  
> - Be deterministic and idempotent: runs with identical input must produce identical outputs aside from timestamps.

**Reliability Enforcement (apply in executor):**
- After finishing each step, print/log: `✅ Step N complete — proceeding to Step N+1` (or `❌ Step N failed — recorded; proceeding to Step N+1` on failure).
- Do not return/exit before Step 7.
- Always write the structured JSON output file at the end.

---

## Instructions (Follow Exactly — Each Step Emits a Checkpoint)

### Step 1 — Input Parameters & Directory Preparation (MANDATORY)
**Checkpoint required. Do not continue without producing checkpoint.**

1. Accept `input` (file path) and `append` (boolean). Defaults:
   - `input = "repositories.txt"`
   - `append = false`
2. Directory behavior:
   - If `append == false` (reset mode):
     - Remove `./tasks`, `./output`, and `./temp-script` directories entirely if they exist (delete all contents).
     - Create fresh `./tasks`, `./output`, and `./temp-script` directories.
   - If `append == true`:
     - Preserve existing `./tasks`, `./output`, and `./temp-script` contents.
     - Create any of the three directories that do not exist.
3. Validation:
   - If `input` file does not exist, set status=FAIL, record verification error `type=MissingInput`, but still proceed to Step 2.
4. Emit checkpoint: success or failure message.

### Step 2 — Read & Normalize Input (MANDATORY)
**Deterministic parsing. Checkpoint required.**

1. Read `input` line-by-line using UTF-8.
2. Skip blank lines and lines starting with `#`.
3. Collect only HTTPS repository URLs (ignore non-HTTPS lines but record as `ignored_input_lines`).
4. Normalize each URL:
   - Trim whitespace; remove trailing slashes.
   - Treat URLs case-insensitively for duplicate detection.
   - Remove trailing `.git` only for name extraction (preserve in `repo_url` value).
5. Derive `repo_name` (friendly):
   - If URL contains `/_git/`, take the segment after `/_git/` (strip trailing `/` and optional `.git`).
   - Else use final path segment (strip optional `.git`).
6. Produce a sorted, unique list of normalized entries (stable sort).
7. Emit checkpoint with counts and any ignored lines.

### Step 3 — Determine Repositories to Process (MANDATORY)
**Checkpoint required.**

1. If `append == false`: process all normalized, sorted repositories.
2. If `append == true`:
   - If `./tasks/all_repository_checklist.md` exists, parse existing repo names case-insensitively.
   - New repositories = normalized list minus existing names.
   - Only process the new repositories (sorted).
3. Emit checkpoint listing `repositories_total`, `repositories_to_process`, and `repositories_skipped`.

### Step 4 — Generate/Update Master Checklist (MANDATORY)
**Checkpoint required. Must be deterministic and preserve existing state in append mode.**

1. Master file path: `./tasks/all_repository_checklist.md`.
2. If `append == false`: create a new master checklist containing all sorted repository entries.
3. If `append == true`:
   - Preserve all existing lines and checkbox states.
   - Append new sorted repositories after the last repo line.
   - Update only the `Generated:` timestamp (do not reorder or change existing lines).
4. Formatting rules (strict):
   - Unix line endings (`\n`), single final newline, no trailing spaces.
   - Each repo line must be exactly: `- [ ] repo_name [repo_url]` or `- [x] repo_name [repo_url]`.
   - No duplicate repo names (case-insensitive).
5. Emit checkpoint confirming master file path and number of repo lines.

### Step 5 — Generate Individual Repository Checklist Files (MANDATORY)
**Checkpoint required. Each file must be an atomic overwrite in reset mode.**

1. For every repository in `repositories_to_process` (from Step 3):
   - File path: `./tasks/{repo_name}_repo_checklist.md`
   - When `append == false`: always WRITE the file fresh (overwrite if exists).
   - When `append == true`: if file already exists, SKIP creation for that repo.
2. File content MUST follow the canonical template EXACTLY (single authoritative template below). Preserve literal `{{...}}` placeholders.
3. Required headings (exact, case-sensitive):
   - `# Task Checklist:`
   - `## Repo Tasks (Sequential Pipeline - Complete in Order)`
   - `## Repo Variables Available`
4. After writing, perform post-write validation:
   - Count occurrences of `# Task Checklist:` → MUST equal 1.
   - Count occurrences of `## Repo Variables Available` → MUST equal 1.
   - Ensure no duplicated task directive lines.
   - If validation fails, delete the faulty file, record a verification error, and continue.
5. Emit per-repo checkpoint (created/skipped/failed).

**Canonical repository checklist template (DO NOT ALTER — ONE TRUE TEMPLATE):**
```markdown
# Task Checklist: {repo_name}
Repository: {repo_url}
Generated: {timestamp}

## Repo Tasks (Sequential Pipeline - Complete in Order)
- [ ] (1) [MANDATORY] [SCRIPTABLE] Clone repository to local directory → @task-clone-repo (see details in #file: .github/prompts/task-clone-repo.prompt.md)
- [ ] (2) [MANDATORY] [SCRIPTABLE] Find all solution files in repository → @task-find-solutions (see details in #file: .github/prompts/task-find-solutions.prompt.md)
- [ ] (3) [MANDATORY] [SCRIPTABLE] Generate per-solution checklist files → @task-generate-solution-task-checklists (see details in #file: .github/prompts/task-generate-solution-task-checklists.prompt.md)
- [ ] (4) [MANDATORY] [SCRIPTABLE] Search for README file in repository → @task-search-readme (see details in #file: .github/prompts/task-search-readme.prompt.md)
- [ ] (5) [MANDATORY] [NON-SCRIPTABLE] Scan README and extract setup commands → @task-scan-readme (see details in #file: .github/prompts/task-scan-readme.prompt.md)
- [ ] (6) [MANDATORY] [NON-SCRIPTABLE] Execute safe commands from README → @task-execute-readme (see details in #file: .github/prompts/task-execute-readme.prompt.md)

## Repo Variables Available
- {{repo_url}} → {repo_url}
- {{repo_name}} → {repo_name}
- {{clone_path}} →
- {{repo_directory}} →
- {{solutions_json}} →
- {{readme_content}} →
- {{readme_filename}} →
- {{commands_extracted}} →
- {{executed_commands}} →
- {{skipped_commands}} →

## For Agents Resuming Work
Follow these rules *exactly* when resuming execution:

1. Identify the **first `[ ]` task** in the checklist.
2. [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4 → 5 → 6)
3. Execute its corresponding prompt file (from `@task-...`).
4. After successful completion, update this checklist and mark `[x]`.
5. Do **not** end the run until all required tasks are completed.

## Execution Notes
- [SCRIPTABLE] tasks: clone, search-readme, find-solutions, generate-solution-task-checklists
- [NON-SCRIPTABLE] tasks: scan-readme, execute-readme
- Mark completed tasks with [x]
- Each referenced `@task-*` file is an independent prompt that must be executed completely before continuing.

```

### Step 6 — Populate Base Repo Variables (MANDATORY)
**Checkpoint required.**

1. In each generated repository checklist file, populate ONLY these two arrow lines:
   - `- {{repo_url}} → {repo_url}` (exact normalized URL used by the run)
   - `- {{repo_name}} → {repo_name}` (derived friendly name)
2. Leave all other `{{...}}` lines blank (preserve arrow format).
3. Do not duplicate variable lines or re-emit the variables heading.
4. Validation: Exactly one occurrence of each variable line; duplicates → record verification error and set file result=FAIL.
5. Emit checkpoint per file.

### Step 7 — Structured Output JSON (MANDATORY — ALWAYS RUN)
**Final checkpoint. This must run even on earlier failures.**

1. Write JSON to: `output/{mode}_task5_generate-repo-checklists.json` where `mode` is `reset` or `append`.
2. Required keys (must be present; use `null`, empty arrays, or zeros where appropriate on failure):
   - input_file
   - append_mode
   - repositories_total
   - repositories_processed
   - repositories_skipped
   - generated_checklist_paths
   - master_checklist_path
   - status (SUCCESS | FAIL)
   - timestamp (ISO 8601 UTC, seconds precision)
   - verification_errors (array of `{ type, target, detail }`)
   - mode ("reset" | "append")
3. Determine overall `status`:
   - SUCCESS only if all mandatory validations and file writes succeeded.
   - Otherwise FAIL.
4. Emit final checkpoint: JSON file path and overall status.

---

## Output Contract
(unchanged from original; ensure JSON file contains all specified fields)

## Implementation Notes
1. THIS IS SCRIPTABLE: produce a Python script implementing these exact steps.
2. Deterministic behavior and idempotency are required.
3. Use UTF-8, Unix line endings, single final newline.
4. Timestamp format: ISO 8601 UTC truncated to seconds (e.g., 2025-11-03T00:00:00Z).
5. Error Handling: collect all verification errors; never raise unhandled exceptions out of the run — always produce Step 7 JSON.
6. Append Mode: compare normalized repo names case-insensitively.
7. Logging: print a short human-readable log message at each checkpoint.
8. **Script Location:** Save generated script to `temp-script`.
