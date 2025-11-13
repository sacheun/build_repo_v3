@execute-solution-task solution_checklist=<required>

---
temperature: 0.0
---

## Description:
This prompt finds all unmarked tasks from a **solution-level checklist markdown file** and executes them **strictly in sequence**, ensuring that **no task is skipped** and all results are properly persisted to disk.

It continues processing until all tasks are complete or an error occurs, maintaining checkpoint validation after every step.

---

## Reliability Enforcement Addendum (Mandatory)
To guarantee deterministic, step-by-step reliability:
- Every step **MUST emit** a `[CHECKPOINT] step_n_complete` marker before continuing.
- Each subsequent step **MUST verify** that all prior checkpoints exist.
- If any prior checkpoint is missing, **halt and reattempt from last confirmed checkpoint.**
- All file read/write operations are **atomic** (write to temp → replace original).
- After each write, **recalculate checksum** and re-read the file from disk.
- No step may be summarised, combined, or skipped — **full sequential integrity required.**

If an error or inconsistency is detected:
- Emit `[ERROR-DETECTED] step_n_failed` immediately.
- Perform rollback or resume recovery as defined in fallback policy.

---

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
Execution requires **explicit reasoning**, **tool invocation**, and **file integrity validation**.

**STRICT MODE ON**
- Every step is **MANDATORY**.
- Missing or incomplete step = `execution_status="FAIL"`.
- Steps 0 → 4 must complete in sequence with checkpoints validated between each.

**CRITICAL REQUIREMENT:**  
After completing each task, update the solution checklist file:
- Change the corresponding task status from `[ ]` → `[x]`.
- Persist update immediately and validate checksum before proceeding.

**CRITICAL - SEQUENTIAL EXECUTION:**
- Executes **ALL unmarked `[ ]`** tasks in the order listed.
- Conditional tasks execute only when their condition is satisfied.
- Each task execution is persisted and verified before continuing.
- After each task, **reload the checklist file** to ensure Copilot context is in sync.

---

## Step-by-Step Execution (Reliability-Enhanced)

### Step 0: Initialise Parameters (MANDATORY)
1. Validate that `solution_checklist` exists and is accessible.
2. Create or verify temporary working context if required.
3. Initialise counters, error flags, and execution metadata.

---

### Step 1: Parse Solution Checklist (MANDATORY)
1. Verify `[CHECKPOINT] step_0_complete` exists.
2. Read the checklist markdown from disk.
3. Locate section: `"## Tasks (Sequential Pipeline - Complete in Order)"`.
4. Identify the first unmarked (`- [ ]`) task.
   - If none found → `execution_status="ALL_TASKS_COMPLETE"` and jump to Step 4.


---

### Step 2: Evaluate and Execute Task (MANDATORY)
Verify `[CHECKPOINT] step_1_complete` exists.

#### Step 2.1 – Conditional Logic
1. Determine if the current task is `[CONDITIONAL]`.
2. Evaluate condition.
   - If condition **FALSE** →  
     - Mark `[x] SKIPPED (condition not met)`  
     - Update checklist and re-validate checksum  
     - Return to Step 1  
   - If condition **TRUE**, proceed to Step 2.2.

#### Step 2.2 – Task Invocation
1. Execute the corresponding task prompt (e.g. `@task-build-solution`, `@task-run-tests`, etc.).
2. Capture output, logs, and result metadata.
3. If task fails →  
   - Mark `[x] FAIL` with diagnostic info.  
   - Set `execution_status="FAIL"` and proceed to recovery.
4. On success → mark `[x] SUCCESS` in checklist.
5. Persist update and validate checksum.


---

### Step 3: Continue to Next Task (MANDATORY)
1. Confirm `[CHECKPOINT] step_2_complete` exists.
2. Reload checklist from disk.
3. Find next unmarked `[ ]` task.
4. If found → return to Step 1.
5. If none → emit `[CHECKPOINT] step_3_complete`.

---

### Step 4: Finalise and Summarise (MANDATORY)
1. Verify all checkpoints (`step_0` → `step_3`) exist.
2. Summarise results — count total, succeeded, failed, and skipped tasks.
3. Output structured JSON report with `execution_status`.

---

## Implementation Notes (Reliability Enhancements)
- Every step validates all prior checkpoints before executing.
- Atomic file updates guarantee no corruption between runs.
- Missing checkpoints trigger resume from last confirmed state.
- Re-run detection supported via persisted `[CHECKPOINT]` markers.
- Checksum validation ensures context integrity across iterations.
- Failures always emit `[ERROR-DETECTED]` with full diagnostic info.

---

✅ **Reliability Guarantees**
- Steps **cannot** be skipped or summarised.
- Automatically **recovers** from partial or interrupted runs.
- Compatible with your repository-level `@execute-repo-task` reliability model.
- Ensures **Copilot CLI consistency**, even under truncated or long multi-task executions.
