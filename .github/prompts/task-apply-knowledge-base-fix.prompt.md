@task-apply-knowledge-base-fix solution_checklist={{solution_checklist}}

---
temperature: 0.1
---

# Task: Apply Knowledge Base Fix

## Description
Parse the KB article, extract fix instructions, and automatically apply them to the solution files to resolve the build error. Supports multiple fix options with sequential retry logic.

## Execution Policy
** CRITICAL ** DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK.This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:

This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:
1. Use read_file tool to load the README content from task-search-readme output JSON
2. Use structural reasoning to parse and analyze README structure
3. Use AI reasoning to identify setup sections and extract commands
4. Use create_file tool to save the parsed command list to JSON output
5. Use replace_string_in_file tool to update progress/results files

** ⚠️ CRITICAL - THIS TASK IS NON-SCRIPTABLE ⚠️ **

** NEVER use regex or simple text parsing - use structural reasoning **

The AI agent must analyze the README content intelligently to understand context and extract meaningful setup commands.

### YOU MUST USE DIRECT TOOL CALLS

** CRITICAL: DO NOT suggest commands or edits - EXECUTE them directly **

Use these tools:
- `read_file` - Read KB article and solution files
- `replace_string_in_file` - Apply code changes to project files
- `run_in_terminal` - Execute build commands if needed
- `file_search` - Find .csproj, Directory.Build.props, etc.

** NEVER output code blocks expecting the user to manually apply them **


## Prerequisites
- `solution_path`: Absolute path to the .sln file
- `kb_file_path`: Absolute path to the KB article markdown file
- `error_code`: Error code to fix (e.g., NU1008, MSB3644, SF0001)
- `last_option_applied`: (Optional) The last option number that was applied (e.g., "1", "2", "3"). If not provided, defaults to applying Option 1.

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
Parse KB Article

1. **Read the KB Article**:
   ```
   read_file kb_file_path={{kb_file_path}}
   ```

2. **Extract Fix Instructions:**
   - Locate the "## How to Fix" or "## Fix Options" or "## Fix" section
   - Parse all available fix options (Option 1, Option 2, Option 3, etc.)
   - Count total number of options available
   
3. **Determine Which Option to Apply:**
   - **If `last_option_applied` is NOT provided or empty:**
     * Apply **Option 1** (the first/recommended fix)
   - **If `last_option_applied` IS provided (e.g., "1"):**
     * Calculate next option: `next_option = last_option_applied + 1`
     * Check if next option exists in the KB article
     * **If next option exists:** Apply that option
     * **If next option does NOT exist:** Return `fix_status = NO_MORE_OPTIONS` (no fix applied)
   
4. **Parse the Selected Option:**
   - Extract the specific actions required for the chosen option:
     * File to modify (e.g., Directory.Build.props, *.csproj)
     * Content to add/remove/modify
     * Build parameters to change
   - Track which option number is being applied for output

5. **Identify Target Files:**
   - Determine which files need modification based on fix instructions
   - Common targets:
     * `Directory.Build.props` (for central package management)
     * `Directory.Packages.props` (for NuGet Central Package Management)
     * Individual `.csproj` files
     * Solution `.sln` file (for platform configuration)

### Step 2 (MANDATORY)
Resolve Target Files from KB Instructions

1. **Determine working directory:** use `solution_path` to derive the solution root.
2. **For each file or artifact mentioned in the selected KB option**, locate it with `file_search` or direct path resolution. Example patterns (`**/*.csproj`, `**/Directory.Packages.props`, etc.) are suggestions—follow whatever the KB article calls for.
3. **Create or stage files when the KB requires them:** if a referenced file is missing and the KB specifies creating it, prepare an empty scaffold with `create_file` before applying content.
4. Keep a running list of target files so Step 3 can reference them and the final JSON can report them.


### Step 3 (MANDATORY)
Apply the KB Fix

**Always execute changes directly with tooling (`replace_string_in_file`, `create_file`, `run_in_terminal` for command steps); never emit instructions for manual follow-up.**

1. **Interpret the KB option line-by-line:** for each action (edits, additions, command invocations), translate the instruction into the appropriate tool call.
2. **When editing files:**
   - Load the current content with `read_file`.
   - Use `replace_string_in_file` (with surrounding context) to insert, update, or remove the exact segments described in the KB.
   - Re-read to confirm the change and capture before/after snippets for `changes_made`.
3. **When the KB requires new files or sections:** create them atomically with `create_file`, populating only the content specified in the article.
4. **If the KB directs you to run commands (e.g., `dotnet tool install`, `nuget restore`)**, execute them via `run_in_terminal` and capture the outcome in your notes.
5. **Document every modification:** record file path, action taken, and a short description for later JSON output.

### Step 4 (MANDATORY)
Validate Fix Application

1. **Check File Modifications:**
   - Re-read modified files to confirm changes applied
   - Verify syntax is correct (valid XML for .csproj/.props files)

2. **Test Build (Optional Quick Validation):**
   - **DO NOT run full build** (that happens in retry loop)
   - Optionally validate file syntax only

3. **Determine Fix Status:**
   - If all changes applied successfully: `fix_status = SUCCESS`
   - If any file modification failed: `fix_status = FAIL`
   - If fix instructions unclear or not applicable: `fix_status = SKIPPED`
   - If no more options available after last_option_applied: `fix_status = NO_MORE_OPTIONS`


### Step 5 (MANDATORY)
Checklist Task & Variable Update
1. **Open the checklist:** load `{{solution_checklist}}` from disk (fresh read).
2. **Determine the attempt index for this run:**
    - If an option was applied, parse `option_applied` (`"1"`, `"2"`, `"3"`) → `attempt_index`.
    - If `option_applied` is `null` (e.g., `fix_status = NO_MORE_OPTIONS`), derive `attempt_index = int(last_option_applied or 0) + 1` and cap within `[1,3]`.
    - Store `attempt_label = {1: "CONDITIONAL number 5 - Attempt 1", 2: "CONDITIONAL number 7 - Attempt 2", 3: "CONDITIONAL number 9 - Attempt 3"}[attempt_index]`.
3. **Update the checklist task line:**
    - Locate the bullet containing `@task-apply-knowledge-base-fix` and the matching attempt label.
    - Replace the leading checkbox with `[x]`.
    - When `fix_status` is `SKIPPED` or `NO_MORE_OPTIONS`, append ` - SKIPPED ({reason})` using a concise reason (e.g., `no more KB options`). Otherwise keep the existing suffix when the fix executed.
4. **Refresh solution variables in `### Solution Variables`:**
    - Locate or insert the line starting with `- fix_applied_attempt_{attempt_index}:` and replace everything after the colon with:
       * ` APPLIED` when `fix_status = SUCCESS`.
       * ` NOT_APPLIED` when `fix_status` is `FAIL` or `FAIL_VERIFICATION`.
       * ` SKIPPED ({reason})` when `fix_status` is `SKIPPED` or `NO_MORE_OPTIONS`. Use clear, short wording for `{reason}`.
    - Locate or insert the line starting with `- kb_option_applied_attempt_{attempt_index}:` and set the value to:
       * ` {option_applied}` when an option number exists.
       * ` null` when no option ran (e.g., `NO_MORE_OPTIONS`).
    - Leave attempt slots for other indices untouched, as well as unrelated variables (`solution_path`, `build_status`, etc.).
5. **Write changes atomically** (temp file replace) so the checklist is never partially updated.


### Step 6 (MANDATORY)
Structured Output
- Emit a single JSON object (stdout and saved file) containing:
  - `fix_status`: `SUCCESS` | `FAIL` | `SKIPPED` | `NO_MORE_OPTIONS` | `FAIL_VERIFICATION`.
  - `option_applied`: option number as string (`"1"`, `"2"`, `"3"`) or `null` when no option ran.
  - `fix_applied`: short human-readable summary of the change or reason for skip.
  - `kb_file_path`: absolute path to the KB article used.
  - `error_code`: error code addressed (e.g., `"NU1008"`).
  - `target_files`: array of absolute file paths touched during the fix (may be empty).
  - `changes_made`: array of `{ file, action, description }` entries documenting edits.
  - `validation`: object with fields like `files_modified` (int) and `syntax_valid` (bool) capturing any quick checks performed.
  - `available_options`: object summarizing `{ total, last_applied, next_available }` so the workflow can decide on retries.
  - `timestamp`: ISO 8601 UTC string for traceability.
- Write the same JSON payload to `output/{repo_name}_{solution_name}_task-apply-kb-fix.json` atomically.


## Step 7 — Final Verification and Redo Safeguard (MANDATORY)

1. Reload `{{solution_checklist}}` from disk (fresh read).
2. Verify the checklist reflects the outcome from Step 5:
   - Locate the `@task-apply-knowledge-base-fix` entry for the computed attempt index and confirm the leading checkbox is `[x]`.
   - When `fix_status` is `SKIPPED` or `NO_MORE_OPTIONS`, ensure the line ends with `- SKIPPED (...)` using the same reason written in Step 5.
3. Verify the solution variables under `### Solution Variables` match Step 5 updates:
   - `fix_applied_attempt_{attempt_index}` carries the expected value (`APPLIED`, `NOT_APPLIED`, or `SKIPPED (...)`).
   - `kb_option_applied_attempt_{attempt_index}` matches `option_applied` (or `null`).
   - No duplicate variable lines exist and unrelated variables remain unchanged.
4. If any verification fails:
   - Re-run Steps 1–6 exactly once and repeat Step 7.
5. If verification still fails after the retry, set `fix_status=FAIL_VERIFICATION`  and exit.

---

## Output Contract
- `fix_status`: `SUCCESS` | `FAIL` | `SKIPPED` | `NO_MORE_OPTIONS` | `FAIL_VERIFICATION`
- `option_applied`: string option number (`"1"`, `"2"`, `"3"`) or `null`
- `fix_applied`: concise description of the applied change or skip rationale
- `kb_file_path`: absolute path to the KB article referenced during the fix
- `error_code`: string error code (e.g., `"NU1008"`) or `null`
- `target_files`: array of absolute file paths that were touched (empty array when none)
- `changes_made`: array of objects `{ file, action, description }` summarising each modification
- `validation`: object containing quick-check data such as `files_modified` (int) and `syntax_valid` (bool)
- `available_options`: object with keys `total`, `last_applied`, `next_available`
- `timestamp`: ISO 8601 UTC string


## Implementation Notes

1. **File Encoding:** Preserve original file encoding when modifying (UTF-8, UTF-8 BOM, etc.)
2. **Line Endings:** Preserve original line endings (CRLF on Windows, LF on Unix)
3. **Whitespace:** Maintain consistent indentation when adding XML elements
4. **Backup:** Tool handles backups automatically via source control (no manual backup needed)
5. **Atomicity:** Apply all changes for a fix together - don't partially apply
6. **Error Handling:**
   - If file doesn't exist and can't be created → fix_status = FAIL
   - If file locked or permission denied → fix_status = FAIL
   - If KB instructions ambiguous → fix_status = SKIPPED
7. **Safety:**
   - Only modify files mentioned in KB article
   - Don't make additional "improvements" beyond the fix
   - Preserve all existing content not related to the fix

