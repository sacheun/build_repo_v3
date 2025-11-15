---
temperature: 0.0
---

@task-clone-repo clone_path={{clone_path}} checklist_path={{checklist_path}}

# Task name: task-clone-repo

## Description
This task clones or refreshes a repository from `repo_url` into the `clone_path` directory.

## Execution Policy
**STRICT MODE ENABLED**
- Execute all numbered steps **in exact order: 1 → 6**.  
- **Do not skip, summarise, or merge** any step.
- After finishing each step, explicitly confirm completion before continuing.
- If any step fails, **stop immediately**, set `status=FAIL`, and emit JSON output.
- The task is **NOT complete** until **Step 6 (Final Checklist Verification)** passes successfully.
- Step 6 may **re-run Steps 1–4** automatically if the checklist file was not updated.

**This task is fully SCRIPTABLE.**

---

## Step 1 — Load Variables (MANDATORY)
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

## Step 2 — Verify Target Directory (MANDATORY)
1. Compute `repo_directory = {{clone_path}}/{{repo_name}}`
2. Check if directory exists.
   - If missing → mark `operation = CLONE`
   - If exists → mark `operation = REFRESH`
3. Confirm that the value of `repo_directory` is correct and accessible.

✅ **Checkpoint:** Directory status and `operation` flag determined.

---

## Step 3 — Perform Git Operation (MANDATORY)
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

## Step 4 — Update Checklist File (MANDATORY)
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

✅ **Checkpoint:** Checklist update attempted.

---

## Step 5 — Emit Structured JSON Output (MANDATORY)
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
  "git_output": "...",
  "checklist_verified": "PENDING"
}
```

✅ **Checkpoint:** Output file written (pending final verification).
---

## Step 6 — Final Checklist Verification & Retry Guard (MANDATORY)
1. Reopen `{{checklist_path}}` from disk.
2. Confirm the checklist line for `@task-clone-repo` reflects the final `status` (`[x]` when SUCCESS, `[ ]` when FAIL).
3. Under `## Repo Variables Available`, ensure the `{{clone_path}}` and `{{repo_directory}}` entries match the resolved values from Steps 1-2 and appear exactly once.
4. If verification fails (line unchanged, variables missing, or mismatched values), log `WARNING: checklist verification failed - restarting from Step 1`, then repeat Steps 1-4 before attempting Step 6 again.
5. Once verification succeeds, update the JSON file from Step 5 by setting `"checklist_verified": "CONFIRMED"` (or `"FAIL"` if verification ultimately fails) and save it atomically.

✅ **Checkpoint:** Checklist verification complete and output synchronized.
---



## Implementation Notes
1. **STRICT SEQUENTIAL EXECUTION:** Must complete Step 6 for success.  
2. **Idempotent Behaviour:** Existing directories trigger REFRESH, not reclone.  
3. **Error Handling:** Any failed git command or checklist check sets `status=FAIL`.  
4. **Reliability Guarantee:** Step 6 enforces that the checklist update is **confirmed on disk**.  
5. **Script Location:** Save generated script to `temp-script/step{N}_repo{M}_task1_clone-repo.py`.

---

## End of Task
Mark the task complete **only when Step 6 confirms** the checklist file is updated and verified.
