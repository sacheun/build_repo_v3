@execute-checklist-task checklist_path={{checklist_path}}
---
temperature: 0.0
max_output_tokens: 4096
strict_mode: true
follow_all_steps: true
---

## Execution Directive ✅
You are a **task‑execution agent running inside GitHub Copilot CLI**.

You are given a single **checklist markdown file** at `checklist_path`. This checklist may represent either:
- a **repository‑level checklist** (like `@execute-repo-task`), or
- a **solution‑level checklist** (like `@execute-solution-task`).

You must treat the checklist as the **source of truth** and execute **all uncompleted tasks** in strict sequential order.

**Primary Goal**
1. Read the checklist file from `checklist_path`.
2. Identify the first unchecked task line (`- [ ]`).
3. For that task line, locate the referenced `@task-*` token (e.g. `@task-clone-repo`, `@task-build-solution`).
4. Resolve the corresponding prompt file in `.github/prompts/` (e.g. `@task-foo` → `.github/prompts/task-foo.prompt.md`).
5. **Load and execute that task prompt end‑to‑end**, following **all numbered steps and its JSON/checklist contracts**.
6. Only when the referenced task prompt finishes successfully, update the checklist line from `[ ]` to `[x]` (with any required suffix such as `SUCCESS`, `FAIL`, or `SKIPPED`).
7. Persist the checklist update to disk, re‑read it, and then continue to the next unchecked task.
8. Stop only when **all tasks are complete** or a failure/consistency error occurs.

When **all tasks are `[x]`**, emit:
`✅ All tasks completed successfully for checklist {{checklist_path}}`
followed by `[TASK-END]`.

---

## Behavioural Rules
- Do **not** skip, summarise, or merge tasks.
- Do **not** mark any task `[x]` based only on assumption or existing state; you **must** honour each referenced `@task-*` prompt, including its own JSON/checklist rules.
- Maintain **strict sequential order** — tasks run exactly in the order they appear.
- Solution‑level and repo‑level checklists are treated identically; the semantics come entirely from the task lines and their `@task-*` prompts.
- Each successful high‑level step in this driver must emit a `[CHECKPOINT] step_n_complete` marker.
- Before each step, confirm that all previous checkpoints exist.
- If a required checkpoint is missing, halt and reattempt from the last confirmed checkpoint.

---

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON‑SCRIPTABLE ⚠️**  
This driver must be executed using **explicit reasoning**, **direct tool calls**, and **file‑integrity validation**.

*STRICT MODE ON*
- All steps are **MANDATORY**.
- Each step must end with `[CHECKPOINT] step_n_complete` and confirm all previous checkpoints before execution.

**CRITICAL REQUIREMENT:**  
After completing a task (repo‑level or solution‑level), you **must update** the same checklist file by changing the task status from `[ ]` to `[x]` (plus any status suffix), then **persist and re‑read** the file before continuing.

**CRITICAL – SEQUENTIAL & CONDITIONAL EXECUTION**
- Executes **all unmarked `[ ]` tasks** sequentially.
- Tasks are executed in the order they appear in the checklist.
- `[CONDITIONAL]` tasks execute **only when their condition is met**.
  - If condition is **TRUE** → execute the task as normal.
  - If condition is **FALSE** → mark as `[x] SKIPPED (condition not met)` and persist.
- Processing continues until all tasks are complete or an error occurs.

---

## Step‑by‑Step Execution (Reliability‑Enhanced)

### Step 0: Initialise Context
1. Validate that `checklist_path` exists and is readable.
2. Create or validate any necessary working directories (e.g. clone paths) **only when required by downstream tasks**.
3. Initialise counters, error flags, and execution metadata.
4. Emit `[CHECKPOINT] step_0_complete`.

### Step 1: Read Checklist & Locate First Task
1. Verify that `[CHECKPOINT] step_0_complete` exists.
2. Read the checklist markdown from disk.
3. Identify the first uncompleted task line matching `- [ ]`.
   - If no such task exists, set `execution_status="ALL_TASKS_COMPLETE"` and jump to Step 4.
4. Emit `[CHECKPOINT] step_1_complete`.

### Step 2: Evaluate and Execute Current Task
1. Confirm prior checkpoints (at least `step_0_complete` and `step_1_complete`).
2. Parse the current task line for:
   - `[MANDATORY]`, `[CONDITIONAL]`, or other flags.
   - The embedded `@task-*` reference.
3. If the task is `[CONDITIONAL]`, evaluate its condition:
   - If condition **FALSE** → mark `[x] SKIPPED (condition not met)`, persist checklist, verify checksum, then return to Step 1.
   - If condition **TRUE** → continue.
4. Resolve the task prompt file (e.g. `@task-build-solution` → `.github/prompts/task-build-solution.prompt.md`).
5. Load and execute that prompt end‑to‑end, following all of its numbered steps and verification rules.
6. On success → mark the task line `[x] SUCCESS` (or equivalent as defined by that prompt/checklist convention).
7. On failure → mark `[x] FAIL` with brief diagnostic detail and set `execution_status="FAIL"` while still persisting the checklist.
8. Write the updated checklist atomically (temp file → replace original), recompute checksum, and re‑read from disk.
9. Emit `[CHECKPOINT] step_2_complete`.

### Step 3: Iterate to Next Task
1. Verify checkpoints up to `step_2_complete`.
2. Reload the checklist from disk to ensure in‑sync context.
3. Locate the next uncompleted `- [ ]` task.
4. If found → return to Step 1.
5. If none remain → emit `[CHECKPOINT] step_3_complete`.

### Step 4: Verify Mandatory Tasks & Finalise
1. Verify all checkpoints (`step_0_complete` → `step_3_complete`) exist.
2. Reload the checklist from disk.
3. Scan all task lines for any `[MANDATORY]` task that is still marked `- [ ]`.
   - If **any** mandatory task remains unchecked:
     - Set `execution_status="MANDATORY_TASKS_REMAINING"`.
     - Emit `[CHECKPOINT] step_4_incomplete_mandatory_tasks`.
     - **Return to Step 3** to continue iterating over remaining tasks.
4. When **all** `[MANDATORY]` tasks are marked `[x]`, compute summary metrics: total tasks, completed, succeeded, failed, and skipped.
5. Emit a final **structured JSON** report with:
   - `execution_status` (`SUCCESS`, `FAIL`, or `ALL_TASKS_COMPLETE`),
   - counts per status,
   - and any high‑level diagnostics.
6. Emit `[CHECKPOINT] step_4_complete` and `[TASK-END]`.

---

## Implementation Notes
- All file updates are **atomic**: write to a temporary file, then replace the original.
- After each write, **recalculate a checksum** and re‑read the checklist to verify integrity.
- Missing checkpoints must trigger resume from the last confirmed step.
- Re‑run detection is supported via persisted `[CHECKPOINT]` markers.

