---
temperature: 0.0
---

@task-search-readme checklist_path={{checklist_path}}

# Task name: task-search-readme

## Description
This task locates and reads the repository’s main README file (if present) from the root of `repo_directory`. It extracts content and records output metadata.

## Execution Policy
**STRICT MODE ENABLED**
- Steps must run **exactly in sequence**.
- **Do not summarise, merge, or skip** any step.
- After completing each step, explicitly confirm completion before moving to the next.
- If any step fails, immediately set `status=FAIL` and skip directly to Step 5 (JSON output).

---

## Step-by-Step Instructions

### Step 1 — Load Variables (MANDATORY)
1. Verify that `{{checklist_path}}` exists.  
   - If missing, set `status=FAIL`, emit output JSON (Step 5), and **ABORT immediately**.
2. Open `{{checklist_path}}` and locate section header:  
   `## Repo Variables Available`
3. Parse variable lines beginning with:
   - `- {{repo_directory}}`
   - `- {{repo_name}}`
4. Extract each variable’s value (text to the right of `→`), trim whitespace, and assign to:
   - `repo_directory`
   - `repo_name`
5. If `repo_directory` is blank or missing, set preliminary `status=FAIL`.  
   - Continue only far enough to update checklist and generate JSON output later (do not attempt search).

✅ **Checkpoint:** Both variables loaded and validated. Confirm before continuing.

---

### Step 2 — Locate README Candidate (MANDATORY)
1. Search **only in the root of** `repo_directory`.  
   - Do **not** recurse into subdirectories.
2. Perform a **case-insensitive** filename scan for these patterns (in priority order):
   1. `README.md`
   2. `README.txt`
   3. `README.rst`
   4. `README` (no extension)
3. If multiple matches exist, select the highest priority one.  
4. If no match found, record `readme_filename = null` and skip Step 3 content read.  
   Status will be handled in Step 5.

✅ **Checkpoint:** Candidate README file resolved or explicitly noted as missing.

---

### Step 3 — Extract Content (MANDATORY)
1. If `readme_filename` is not null:
   - Open file in UTF-8 encoding with `errors="ignore"`.
   - Read entire content to string `readme_content`.
2. If no file found, set `readme_content = null`.

✅ **Checkpoint:** Content successfully read or confirmed missing.

---

### Step 4 — Update Checklist File (MANDATORY)
1. Open `{{checklist_path}}` for inline edit.
2. In the checklist:
   - Mark `[x]` for `@task-search-readme` **only if** `readme_content` was successfully loaded.  
     Leave `[ ]` if failed.
3. Under section `## Repo Variables Available`, ensure these lines exist exactly once:
   ```
   - {{readme_content}} → output/{{repo_name}}_task2_search-readme.json (field=readme_content)
   - {{readme_filename}} → <actual filename or empty if none>
   ```
4. Keep arrow (`→`) format exact.  
   - One arrow per line, single space before and after.
5. Do **not** edit unrelated variables (e.g. `{{repo_directory}}`, `{{commands_extracted}}`, etc.).
6. Save changes inline, preserving file structure.

✅ **Checkpoint:** Checklist updated and verified.

---

### Step 5 — Structured Output JSON (MANDATORY)
Create file:  
`output/{{repo_name}}_task2_search-readme.json`

The JSON must always include **all fields**, even on failure:

```json
{
  "repo_directory": "{{repo_directory}}",
  "repo_name": "{{repo_name}}",
  "readme_content": "{{readme_content or null}}",
  "readme_filename": "{{readme_filename or null}}",
  "status": "{{SUCCESS or FAIL}}",
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
}
```

✅ **Checkpoint:** Output file written successfully.

---

### Step 6 - Final Verification And Retry Guard (MANDATORY)
Re-open and re-parse `{{checklist_path}}` to ensure on-disk consistency. Perform ALL of the following checks:

1. Task line accuracy:
   - Locate the line containing `@task-search-readme`.
   - If `status=SUCCESS` it MUST be `[x]`; if `status=FAIL` it MUST be `[ ]`.
2. Required variable lines (exactly once each) under `## Repo Variables Available`:
   - `- {{readme_content}} → output/{{repo_name}}_task2_search-readme.json (field=readme_content)`
   - `- {{readme_filename}} → <actual filename or empty if none>`
3. Semantic validation by status:
   - SUCCESS + README found: `readme_filename` non-empty AND JSON file exists AND JSON.readme_content length > 0.
   - SUCCESS + no README: `readme_filename` empty AND JSON.readme_content is null.
   - FAIL: JSON exists; variable lines may remain but MUST NOT contain placeholder words like `FAIL` in place of a path.
4. Formatting rules:
   - Each variable line contains a single arrow `→` with one space before and after.
   - No duplicate occurrences of the variable lines.
   - No trailing spaces after the value.
5. Consistency with JSON file:
   - Open `output/{{repo_name}}_task2_search-readme.json` and confirm fields `readme_content` and `readme_filename` match the checklist values.
6. Failure handling:
   - If ANY check fails, log `WARNING: checklist verification failed - restarting from Step 1` then re-run Steps 1–5 completely and attempt Step 6 again (single automatic retry).
7. Finalization:
   - If retry still fails, leave checklist unchanged, set `status=FAIL` if not already, and proceed to completion.
   - On success, log `VERIFICATION_PASSED` internally.

✅ **Checkpoint:** Step 6 verification passed OR failure recorded after retry.

---

## Implementation Notes
1. **Strict sequential execution:** complete one step fully before next.  
2. **Idempotent behaviour:** running again should not duplicate variables or add new sections.  
3. **Search scope:** root directory only, non-recursive.  
4. **Encoding tolerance:** use UTF-8 with `ignore` for invalid bytes.  
5. **Prioritisation:** `.md` > `.txt` > `.rst` > none.  
6. **Output integrity:** always emit JSON, even when status = FAIL.  
7. **Script Location:** Save generated script in  
   `temp-script/step{N}_repo{M}_task2_search-readme.py`

---

## End of Task
Mark task complete only when Step 5 finishes successfully.
