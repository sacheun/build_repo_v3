---
temperature: 0.1
---

@task-search-knowledge-base solution_checklist={{solution_checklist}}

# Task name: task-search-knowledge-base

## Description
Analyze build failures, extract detection tokens from error output, and search existing knowledge base articles for semantic matches. If a matching KB article is found, return its path; if not, signal that a new KB article should be created.

## Execution Policy
**⚠️ CRITICAL — THIS TASK IS NON-SCRIPTABLE **

This task requires AI STRUCTURAL semantic reasoning. Do **not** replace it with simple regex or scripted matching.
- Use AI reasoning to analyze `build_stderr` and `errors[]` tokens.
- Use `read_file` to open KB articles under `knowledge_base_markdown/` and apply semantic comparison.
- Do not create a script that performs only substring or regex matching.
- Each decision must be justified in debug logs where helpful.

**STRICT SEQUENTIAL MODE:** Execute steps in exact order and do not skip any numbered step. After each step, explicitly confirm completion before proceeding.

---

## Instructions (Follow these steps exactly in sequence)

### Step 1 (MANDATORY) — Checklist Load & Validation
1. Open `{{solution_checklist}}` from disk (fresh read). If not found, set `status=FAIL`, set `kb_search_status=SKIPPED`, and go directly to Step 4 (Checklist Update).
2. Extract variables from the checklist (value after `→`):
   - `- {{repo_name}}` → repo_name
   - `- {{solution_name}}` → solution_name
   - `- {{solution_path}}` → solution_path (absolute)
   - `- {{kb_search_status}}` → previous kb_search_status (may be blank)
   - `- {{kb_file_path}}` → previous kb_file_path (may be blank)
3. Validate `solution_path` exists and is absolute. If invalid, set `status=FAIL`, `kb_search_status=FAIL`, and continue to Step 5.
4. If `kb_search_status` is already `FOUND` and `kb_file_path` exists, you may short-circuit to Step 5 with `kb_search_status=FOUND` (still run Step 6 afterward).
5. Confirm Step 1 completed and record any validation warnings.

✅ Checkpoint: Variables loaded and basic validation completed.

### Step 2 (MANDATORY) — Failure Detection & Token Extraction
1. If `build_status == SUCCESS` (from task context), in the solution checklist md file, set `kb_search_status=SKIPPED`, `detection_tokens=[]`, `error_signature=null` and go to Step 4 (Checklist Update).
2. If `build_status == FAIL`:
   a. Use `errors[]` array (if provided) as primary source of error codes (e.g., NU1008, MSB3644, CS0246).
   b. Use `build_stderr` (or fallback to `build_stdout`) as secondary context. Truncate to 5000 chars for analysis.
   c. Apply AI reasoning (not regex) to extract distinctive detection tokens:
      - Always include explicit error codes (NU####, MSB####, CS####) when present.
      - Extract property/configuration names (e.g., BaseOutputPath, OutputPath).
      - Extract platform/technology keywords (e.g., Service Fabric, .sfproj, central package management).
      - Normalize tokens: lowercase, remove file paths and line numbers, replace spaces with underscores where appropriate.
   d. Produce a concise `error_signature` combining the 2–3 most distinctive tokens in `lowercase_underscore` form (e.g., `nu1008_central_package_management`).

✅ Checkpoint: detection_tokens and error_signature produced (or SKIPPED for success).

### Step 3 (MANDATORY) — Knowledge Base Semantic Search
1. Confirm `./knowledge_base_markdown/` exists. If missing, set `kb_search_status=NOT_FOUND` and continue to Step 4.
2. List `.md` files in `./knowledge_base_markdown/` (exclude README.md and non-KB files).
3. For each KB article file:
   a. Use `read_file` to load the article content (do not rely on filenames alone).
   b. Parse or locate a "Detection Tokens" or similar section if present; otherwise, use semantic analysis on the article text to determine the error types it addresses.
   c. Using AI judgment, compare the current `detection_tokens` / `error_signature` to the article's tokens/content:
      - Exact error code match (strong signal)
      - Matching root cause and corrective steps (semantic match)
      - Similar technology/platform context (weaker signal)
   d. If the article semantically matches, set `kb_search_status=FOUND`, `kb_file_path={absolute_path}`, and return immediately from Step 3.
4. If no KB article matches after checking all files, in the solution checklist md,  set `kb_search_status=NOT_FOUND`, `kb_file_path=None`.

✅ Checkpoint: KB search completed and result recorded (FOUND | NOT_FOUND | NOT_FOUND_DIR).

### Step 4 (MANDATORY) — Checklist & Variable Update (INLINE ONLY)
1. Open `{{solution_checklist}}` for editing (fresh read).
2. Locate the line containing `@task-search-knowledge-base` (it begins `- [ ] (4) [MANDATORY]  ...`).
3. Build a suffix string based on `kb_search_status`:
   - FOUND → `KB FOUND`
   - NOT_FOUND → `NO KB FOUND`
   - SKIPPED → `SKIPPED (build succeeded)`
   - Any other value → `ERROR`
4. Replace the entire task line with:
   `- [x] [CONDITIONAL (4)] Search knowledge base for error fix @task-search-knowledge-base - {suffix}`
5. In the same file, locate `### Solution Variables` and update only:
   - `kb_search_status` → `FOUND` | `NOT_FOUND` | `SKIPPED` | `ERROR`
   - `kb_file_path` → absolute KB path when FOUND, else `N/A` (SKIPPED/NOT_FOUND) or `FAIL` (ERROR)
   - `kb_article_status` → set to `REFERENCED` when FOUND; otherwise leave the existing value unchanged
6. Preserve formatting, avoid duplicating lines, and save atomically (write to temp then replace).

✅ Checkpoint: Checklist line and related variables updated and saved.

### Step 5 (MANDATORY) — Output Results & Logging
1. Produce JSON output (return structure) with the following contract:
   - `kb_search_status`: FOUND | NOT_FOUND | SKIPPED | ERROR | NOT_RUN
   - `kb_file_path`: string | null
   - `kb_article_status`: REFERENCED | null
   - `detection_tokens`: array[string]
   - `error_signature`: string | null
   - `error_code`: string | null
   - `error_type`: string | null
   - `timestamp`: ISO 8601 UTC string

✅ Checkpoint: Output JSON prepared and logged.


### Step 6 (FINAL VERIFICATION AND REDO SAFEGUARD)
**Explicit Checklist & Output Verification with One Automatic Retry**

1. Re-open `{{solution_path}}` from disk (do not use cached content).
2. Verify the task line and variables were updated as per Step 4:
   - Task line must be present and use `[x]` when `kb_search_status` != `SKIPPED`.
   - `kb_search_status` variable must equal the value produced in Step 5.
   - `kb_file_path` must be `N/A`, valid absolute path, or `FAIL` consistent with `kb_search_status`.
3. Verify that the JSON output (if any) exists and is valid JSON with required fields.
   - When `kb_search_status == FOUND`: `kb_file_path` must point to an existing KB .md file.
   - When `kb_search_status == NOT_FOUND`: JSON must exist and `detection_tokens` must be non-empty.
4. If ANY verification check fails, log: `WARNING: checklist verification failed - restarting from Step 1`, then **redo Steps 1–5 exactly once**, and re-run Step 6 verification.
5. If verification still fails after retry, set `status=FAIL`, `kb_search_status=ERROR`, log `VERIFICATION_ABORTED`, and return final output indicating failure.
6. On success, log `VERIFICATION_PASSED` and return final output indicating success.

✅ Checkpoint: Final verification passed or definitive failure recorded.

---

## Output Contract
- `kb_search_status`: FOUND | NOT_FOUND | SKIPPED | ERROR
- `kb_file_path`: string | null
- `kb_article_status`: REFERENCED | null
- `detection_tokens`: array[string]
- `error_signature`: string | null
- `error_code`: string | null
- `error_type`: string | null
- `timestamp`: ISO 8601 UTC string

## Implementation Notes
1. This task requires AI judgment — do not reduce to simple scripted matching.
2. Use `read_file` to load KB articles for semantic comparison.
3. Save all checklist file edits atomically to avoid partial writes.
4. Always perform Step 6 verification; do not mark complete until verification passes.
5. If re-running after a failed verification, ensure you do not produce duplicate entries in checklist files.
6. Log debug messages for token extraction and final verification steps to aid debugging.

---
