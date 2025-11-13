---
temperature: 0.1
---

@task-scan-readme checklist_path={{checklist_path}}

# Task name: task-scan-readme

## Description
This task analyzes the README content (from task-search-readme output) using structural reasoning to identify and extract setup/build environment commands. This task requires AI structural reasoning and **cannot** be scripted.

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
This task MUST be performed using **direct tool calls** and **structural reasoning**.  
**STRICT EXECUTION MODE ENABLED – NO STEPS MAY BE SKIPPED.**

The AI agent must follow all numbered steps **sequentially and atomically**.  
If any step cannot be completed successfully, it must stop immediately, emit a structured JSON with the last successful step, and mark `status=FAIL`.

---

## Reliability Control Rules
To ensure **no skipped steps**, apply these control rules throughout execution:
1. **After each step**, assert completion by writing an internal checkpoint log (`step_completed=N`). If a checkpoint is missing, execution halts.
2. **Never jump ahead** to later steps — each must follow in order.
3. **If an early failure occurs**, stop and emit structured output with the partial state; do not attempt subsequent steps.
4. **At the end**, verify all mandatory steps (1–9) have checkpoint logs; if any missing, set `status=FAIL_MISSING_STEP`.

---

## Instructions (Step-by-Step with Reliability Enforcement)

### Step 1 – Checklist Load & Variable Extraction (MANDATORY)
- Load `{{checklist_path}}`.  
- Extract only the values listed under `## Repo Variables Available`.  
- If any expected variable is missing or malformed, stop immediately and set `status=FAIL`.  

### Step 2 – README Load & Preflight Verification (MANDATORY)
- Load the file at `readme_content_path` extracted in Step 1.  
- Validate existence, readability, and non-empty content.  
- If missing: set `status=SKIPPED` and stop.  
- Verify `tasks/{{repo_name}}_repo_checklist.md` contains line `- {{commands_extracted}} →`. Restore if missing.  

### Step 3 – Structural Reasoning: Identify Setup Sections (MANDATORY)
- Read the actual README content.  
- Identify section headings indicating setup/build instructions using reasoning, not regex alone.  
- Ignore unrelated sections.  

### Step 4 – Follow Referenced Markdown Files (MANDATORY)
- Identify, resolve, and read all referenced `.md` files per the priority hierarchy.  
- Follow up to 3 levels deep; skip external wiki links but record them.  
- Apply the same reasoning rules from Steps 3–6 to each referenced file.  

### Step 5 – Extract Commands (MANDATORY)
- From setup sections, extract real setup commands (shell or environment commands).  
- Exclude clone/fetch commands.  
- Use reasoning to distinguish example code from setup commands.  

### Step 6 – Categorize Commands (MANDATORY)
- Categorize each command by type (install, version_check, config, directory, etc.).  

### Step 7 – Clean Commands (MANDATORY)
- Normalize commands: remove prompts, continuation symbols, comments.  
- Rejoin multi-line commands.  

### Step 8 – Update Repo Checklist (MANDATORY)
- Update only the `- {{commands_extracted}} →` line in `tasks/{{repo_name}}_repo_checklist.md`.  
  - If commands were found, point the line to `output/{{repo_name}}_task3_scan-readme.json (field=commands_extracted)`.  
  - If no commands were found, set the value to `None`.
- Mark `@task-scan-readme` as complete.  

### Step 9 – Structured Output Assembly (MANDATORY)
- Write final JSON to `output/{{repo_name}}_task3_scan-readme.json`.  
- Include all required fields.  
- Validate all checkpoints 1–9 exist; if any missing, set `status=FAIL_MISSING_STEP`.  
- Log checkpoint: `step_completed=9`.

---

### Step 10 - Post-Run Verification And Retry Guard (MANDATORY)
Re-open and fully re-parse `tasks/{{repo_name}}_repo_checklist.md` from disk (no cached content). Perform ALL checks below:

1. Task line correctness:
  - Locate the line containing `@task-scan-readme`.
  - If `status=SUCCESS` the line MUST be `[x]`; if `status=SKIPPED` may be `[x]` or `[ ]` (implementation choice) but note outcome; if `status=FAIL` it MUST be `[ ]`.
2. Variable line presence (exactly once):
  - `- {{commands_extracted}} → output/{{repo_name}}_task3_scan-readme.json (field=commands_extracted)`
  - Single arrow `→`, one space before and after, no duplicates, no trailing spaces.
3. JSON file integrity:
  - Open `output/{{repo_name}}_task3_scan-readme.json`; verify file exists and is parseable JSON.
  - Confirm keys: `commands_extracted` (array) and `total_commands` (integer) present.
4. Semantic alignment by status:
  - SUCCESS & commands found: `total_commands > 0` AND `len(commands_extracted) == total_commands`.
  - SUCCESS & no commands: `total_commands == 0` AND `len(commands_extracted) == 0`.
  - SKIPPED: Either zero commands OR array empty; ensure reason logged earlier; do not fail unless mismatch between counts.
  - FAIL / FAIL_MISSING_STEP: JSON still exists; counts may be zero; MUST NOT contain placeholder strings like `FAIL` instead of arrays.
5. Consistency with checklist variable line:
  - The variable line MUST reference the JSON path exactly; it MUST NOT list raw commands inline (those live only in JSON).
6. Failure handling:
  - If ANY check fails (missing line, wrong bracket state, duplicate, JSON mismatch, count mismatch), re-run Steps 1–9 completely (single automatic retry) and attempt Step 10 again.
7. Record internal checkpoint: `step_completed=10` only on pass.

NOTE: Do NOT mutate previously written JSON content other than adding a verification flag if internal framework supports it.

---

## Output Contract
```json
{
  "repo_directory": "<string>",
  "repo_name": "<string>",
  "readme_filename": "<string|null>",
  "sections_identified": [],
  "commands_extracted": [],
  "referenced_files_processed": [],
  "total_commands": 0,
  "status": "SUCCESS|NONE|SKIPPED|FAIL|FAIL_MISSING_STEP",
  "timestamp": "<ISO 8601>"
}
```

## Final Reliability Assertion
Before emitting output, verify:
- All mandatory steps (1–10) completed and checkpointed.
- No skipped or merged steps.
- If any missing, re-run from last valid checkpoint automatically once; if still missing, fail with diagnostic report.

---
