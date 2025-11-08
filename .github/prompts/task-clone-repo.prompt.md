---
temperature: 0.0
---

@task-clone-repo clone_path={{clone_path}} checklist_path={{checklist_path}}

# Task name: task-clone-repo

## Description
This task clones or refreshes a repository from `repo_url` into the `clone_path` directory.

## Execution Policy
**STRICT MODE ENABLED**
- Execute all steps **in the exact order**.
- **Do not skip, summarise, or merge** any step.
- After finishing each step, explicitly confirm completion before moving to the next.
- If any step fails, **stop immediately** and set `status=FAIL`.

**This task is fully SCRIPTABLE.**

---

## Step-by-Step Instructions

### Step 1 — Load Variables (MANDATORY)
1. Verify that `{{checklist_path}}` exists.  
   - If missing, immediately set `status=FAIL`, emit JSON output (see Step 5), and ABORT.
2. Open the checklist file and locate section header:  
   `## Repo Variables Available`
3. From that section, extract values for:
   - `- {{repo_url}} → value`
   - `- {{repo_name}} → value`
4. Trim whitespace and store these as variables:
   - `repo_url` = extracted URL  
   - `repo_name` = extracted name  
5. Confirm both values are non-empty before continuing.  
   - If empty, set `status=FAIL` and ABORT.

✅ **Checkpoint:** Both `repo_url` and `repo_name` successfully loaded.

---

### Step 2 — Verify Target Directory (MANDATORY)
1. Compute `repo_directory = {{clone_path}}/{{repo_name}}`
2. Check if directory exists.
   - If missing → mark `operation = CLONE`
   - If exists → mark `operation = REFRESH`
3. Confirm that the value of `repo_directory` is correct and accessible.

✅ **Checkpoint:** Directory status and `operation` flag determined.

---

### Step 3 — Perform Git Operation (MANDATORY)
If `operation == CLONE`:
1. Run:
   ```bash
   git clone --depth 1 {{repo_url}} {{clone_path}}/{{repo_name}}
   ```
2. Capture stdout/stderr as `git_output`.

If `operation == REFRESH`:
1. Run sequentially (do not merge commands):
   ```bash
   cd {{clone_path}}/{{repo_name}}
   git reset --hard HEAD
   git clean -fd
   git pull
   ```
2. Capture all output into `git_output`.

3. After each command, check exit code:
   - Any non-zero → `clone_status=FAIL`, `status=FAIL`, then go directly to Step 5 (output).

✅ **Checkpoint:** Git operation finished with status recorded.

---

### Step 4 — Update Checklist File (MANDATORY)
1. Open `{{checklist_path}}` in-place.
2. Locate the line for `@task-clone-repo` and mark `[x]` only if `clone_status=SUCCESS`.
3. Under `## Repo Variables Available`, ensure lines exist (exactly one per variable):
   ```
   - {{clone_path}} → {clone_path}
   - {{repo_directory}} → {repo_directory}
   ```
4. Use exact spacing and single arrow format `→`.
5. Do not duplicate or re-order variable lines.
6. If `clone_status=FAIL`, still ensure `repo_url` and `repo_name` are present.
7. Save the updated checklist in place.

✅ **Checkpoint:** Checklist updated successfully.

---

### Step 5 — Emit Structured JSON Output (MANDATORY)
Create file:  
`output/{{repo_name}}_task1_clone-repo.json`

Include **all fields**, even if failure occurred:
```json
{
  "repo_url": "...",
  "clone_path": "...",
  "repo_name": "...",
  "repo_directory": "...",
  "operation": "CLONE or REFRESH",
  "clone_status": "SUCCESS or FAIL",
  "status": "SUCCESS or FAIL",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "git_output": "..."
}
```

✅ **Checkpoint:** Output file written successfully.

---

## Implementation Notes
1. **STRICT SEQUENTIAL EXECUTION:** Do not parallelise or skip. Each checkpoint must succeed before continuing.
2. **Idempotent Behaviour:** Existing directories trigger REFRESH, not reclone.
3. **Error Handling:** Any failed git command sets `clone_status=FAIL` and halts further actions except Step 5.
4. **Consistency:** Always emit JSON output regardless of failure.
5. **Script Location:** Save generated script to `temp-script/step{N}_repo{M}_task1_clone-repo.py`.

---

## End of Task
Mark task complete only after Step 5 finishes successfully.
