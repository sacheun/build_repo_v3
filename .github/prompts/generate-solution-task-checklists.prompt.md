---
temperature: 0.0
---

@generate-solution-task-checklists checklist_path={{checklist_path}} append={{append}}

# Task name: generate-solution-task-checklists

## Process Overview
1. Debug Entry Trace
2. Checklist Load & Variable Extraction
3. Solutions JSON Validation
4. Parse Solution Task Definitions
5. Workspace Preparation
6. Derive Solution Metadata
7. Generate / Update Solution Index
8. Generate Individual Solution Checklists
9. Structured Output JSON
10. Consistency Checks
11. Debug Exit Trace
12. Repo Variable Refresh (Inline Only)

## Purpose
Generate (or append) per-solution task checklist markdown files for every Visual Studio solution discovered for a repository. These checklists enable agents to execute and track solution-level tasks (restore, build, knowledge base enrichment, fix application, logging) independently from repository pipeline tasks.

### STRICT REPO CHECKLIST NON-MODIFICATION POLICY (MANDATORY)
This task MUST generate exactly ONE new standalone solution checklist file per discovered solution path. It MUST NOT add any new section, heading, or injected block inside the repository-level checklist beyond the inline variable refresh defined in Step 12. Specifically:
- DO NOT add a section named `## Solution Task Sections` (or any variant/case) to the repo checklist.
- DO NOT append per-solution task subsections into the repo checklist.
- DO NOT duplicate or rewrite the canonical repo tasks block.
- ONLY modify the arrow values of `- {{solutions_json}}` and `- {{solutions}}` lines during Step 12.
Violation of any of the above MUST be treated as a verification failure in Step 9 (`type`: `repo_checklist_modification`).

## When This Runs
Executed AFTER repository task `@task-find-solutions` has produced a JSON file containing discovered `.sln` paths. Can be safely re-run (idempotent). In append mode it only creates missing solution checklist files; in reset/non-append mode it can regenerate all.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**  
**DO NOT SKIP OR SUMMARIZE.**  
**THIS TASK IS SCRIPTABLE**

## Input Parameters
- checklist_path (required): Path to repository checklist file `tasks/{repo_name}_repo_checklist.md`.
- append (optional, default=false): If true, do not overwrite existing solution checklist files—only add new ones for newly detected solutions.

All base values (`repo_name`, `repo_directory`, `solutions_json` path, existing `solutions` summary) MUST be read from the checklist; they are not passed as separate parameters and MUST NOT be mutated in this task.

If DEBUG=1 print:  
`[debug][generate-solution-task-checklists] START checklist_path='{{checklist_path}}' append={{append}}`

## Output Artifacts
1. Per-solution checklist files: `tasks/{{repo_name}}_{solution_name}_solution_checklist.md`  
  - Naming Convention (MANDATORY): Prefix each solution checklist with the repository name, then an underscore, then the original solution_name (without extension), then `_solution_checklist.md`.
  - Example: repo_name = `media_stack_all`, solution_name = `Core.Services` → `tasks/media_stack_all_Core.Services_solution_checklist.md`
  - Characters not allowed in filenames (e.g. `:` `*` `?` `"` `<` `>` `|`) MUST be replaced by `_` before writing. Do NOT lowercase the solution_name segment—preserve original case.
  - If two solutions produce identical filenames after sanitization, append an incrementing suffix: `_2`, `_3`, etc.
2. (Optional aggregate) Solution index file: `tasks/{{repo_name}}_solutions_checklist.md` containing a list of all solutions.  
3. JSON summary: `output/{{repo_name}}_generate-solution-task-checklists.json` with generation statistics.  

## Solution Checklist Structure (Target)
```
# Solution Task Checklist: {solution_name}
Repository: {repo_name}
Solution Path: {solution_path}
Generated: {timestamp}

## Solution Tasks (Sequential Pipeline)
- [ ] [MANDATORY 1] [SCRIPTABLE] Restore NuGet packages @task-restore-solution
- [ ] [MANDATORY 2] [SCRIPTABLE] Build solution (Clean + Build) @task-build-solution
- [ ] [CONDITIONAL] [NON-SCRIPTABLE] Search knowledge base for matching error @task-search-knowledge-base
- [ ] [CONDITIONAL] [NON-SCRIPTABLE] Create new knowledge base article @task-create-knowledge-base
- [ ] [CONDITIONAL] [NON-SCRIPTABLE] Apply knowledge base fix @task-apply-knowledge-base-fix
- [ ] [MANDATORY 3] [SCRIPTABLE] Update knowledge base usage log @task-update-knowledgebase-log

## For Agents Resuming Work
1. Start with restore then build.
2. If build fails with identifiable error codes, invoke KB search / create / apply tasks.
3. Always log KB usage updates last.

## Solution Variables Available
### Variables available:
[Content dynamically extracted from `.github/prompts/solution_tasks_list.prompt.md` "Variables available:" section]
```

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY) – Debug Entry Trace
Emit START debug line if DEBUG=1.

### Step 2 (MANDATORY) – Checklist Load & Variable Extraction
1. Read `{{checklist_path}}`.
2. Locate `## Repo Variables Available` section.
3. Extract (text after `→`) from lines:
  - `- {{repo_name}}`
  - `- {{repo_directory}}` (must not be blank; blank → FAIL)
  - `- {{solutions_json}}` (path to JSON produced by @task-find-solutions; must not be blank; blank → FAIL)
  - `- {{solutions}}` (summary list; may be blank prior to generation; capture for reference)
4. If any required line missing or required value blank set status=FAIL and skip to Structured Output.
5. If DEBUG=1 print: `[debug][generate-solution-task-checklists] extracted repo_name='{{repo_name}}' repo_directory='{{repo_directory}}' solutions_json='{{solutions_json}}'`
6. Treat all extracted base variables as immutable; do NOT modify them.

### Step 3 (MANDATORY) – Solutions JSON Validation
1. Validate `solutions_json` path exists & readable.
2. Load JSON; must contain `solutions` (array). Derive `solution_count = len(solutions)`.
3. If file missing/malformed or array absent → status=FAIL and skip remaining generation steps.
4. If DEBUG=1 print: `[debug][generate-solution-task-checklists] loaded solutions: {{solution_count}}`.

### Step 4 (MANDATORY) – Parse Solution Tasks Definition
1. Read `.github/prompts/solution_tasks_list.prompt.md`.
2. Extract:
   - Task directives (lines beginning with `@task-...` except aggregate markers)
   - "Variables available:" block lines (preserve formatting)
3. If DEBUG=1 print: `[debug][generate-solution-task-checklists] extracted {{task_count}} tasks`.

### Step 5 (MANDATORY) – Prepare Workspace
1. Ensure `./tasks` and `./output` directories exist.
2. If `append=false`:
   - Remove existing `tasks/*_solution_checklist.md` files for this repo (safe cleanup only for this repo’s solutions; do NOT delete repo checklists).
   - If DEBUG=1 print: `[debug][generate-solution-task-checklists] cleared existing solution checklists (append=false)`.
3. If `append=true` leave existing solution checklists untouched.

### Step 6 (MANDATORY) – Derive Solution Metadata
For each solution path in `solutions` array:
1. Normalize path (absolute path, resolve `..`, symlinks if feasible).
2. Derive `solution_name` = filename without extension.
3. Derive `solution_slug` = lowercase `solution_name` with non-alphanumeric replaced by `_`.
4. Track mapping in memory: `{solution_slug: {solution_name, solution_path}}`.
5. If DEBUG=1 print each: `[debug][generate-solution-task-checklists] mapping slug='{{solution_slug}}' -> '{{solution_path}}'`.

### Step 7 (MANDATORY) – Generate / Update Solution Index (Optional but Recommended)
File: `tasks/{{repo_name}}_solutions_checklist.md`
Format:
```
# Solutions Checklist: {{repo_name}}
Generated: {{timestamp}}
## Solutions
{one line per solution: - [ ] {solution_name} [{relative_or_basename}]}
```
Deterministic Rules (ENFORCED):
1. Build a list of all solutions from Step 4 and SORT them lexicographically by `solution_name` (case-insensitive compare, original case preserved in output). This sort is MANDATORY (previously recommended) to guarantee identical ordering on repeated runs.
2. Timestamp MUST be UTC ISO 8601 truncated to seconds (e.g. `2025-11-03T00:00:00Z`).
3. Line format is EXACTLY: `- [ ] {solution_name} [{basename}]` using unchecked box by default. No trailing spaces. LF line endings. Single final newline at end of file.
4. When `append=true` and the index file exists:
  - Parse existing solution lines under `## Solutions`.
  - Preserve existing lines EXACTLY (including `[x]` checked states and ordering).
  - Determine the set of NEW solutions (case-insensitive comparison on `solution_name`).
  - Sort NEW solutions (same rule as item 1 above) and APPEND them after the existing block without reordering or modifying prior lines.
  - Do NOT remove solutions that disappeared (historical retention).
5. When `append=false` always regenerate the entire file from scratch with sorted solutions.
6. If a solution name appears more than once (after normalization) only the first is included; subsequent duplicates are ignored and logged (DEBUG) but do not cause FAIL.
7. If DEBUG=1:
  - On creation: `[debug][generate-solution-task-checklists] writing solution index (solutions_total={{solutions_total}})`
  - On append mode update: `[debug][generate-solution-task-checklists] updating solution index existing={{existing_count}} new={{new_count}}`.
Validation:
- After writing, ensure each listed solution has a corresponding checklist file (unless append=true and file pre-existed but checklist generation skipped). If mismatch detected → status may be set to FAIL after consistency checks.
If append=true and file exists, preserve existing checkbox states; add only new, sorted solutions at the end.

### Step 8 (MANDATORY) – Generate Individual Solution Checklists
For each solution:
1. Target file path: `tasks/{{repo_name}}_{solution_name}_solution_checklist.md` (apply filename sanitization rules above).
2. If append=true and file exists → skip generation (record as skipped).  
3. Insert template (see earlier “Solution Checklist Structure”) substituting variables.
4. Inject extracted variables section content where placeholder line appears.
5. If DEBUG=1 print: `[debug][generate-solution-task-checklists] wrote checklist: {{file_path}}`.

### Step 9 (MANDATORY) – Verification & Structured Output JSON
Run verification BEFORE writing JSON. Any violation sets status=FAIL unless already FAIL.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Base variable lines present exactly once for: `- {{repo_name}}`, `- {{repo_directory}}`, `- {{solutions_json}}`, `- {{solutions}}`.
3. Solutions JSON was parsed (if status not FAIL) and `solutions_total == len(solutions array)`.
4. `solutions_processed + solutions_skipped == solutions_total`.
5. For each newly created checklist (in this run): file exists and contains headings:
  - `# Solution Task Checklist:`
  - `## Solution Tasks (Sequential Pipeline)`
  - `## Solution Variables Available` OR a variables heading containing extracted block.
6. Required task directives appear exactly once per checklist for:
  - `@task-restore-solution`
  - `@task-build-solution`
  - `@task-search-knowledge-base`
  - `@task-create-knowledge-base`
  - `@task-apply-knowledge-base-fix`
  - `@task-update-knowledgebase-log`
7. If index file created:
  - Exists at `tasks/{{repo_name}}_solutions_checklist.md`.
  - Lines under `## Solutions` referencing solutions include each processed solution exactly once.
8. Filename sanitization applied (no forbidden characters). For each checklist filename confirm it matches pattern: `tasks/{{repo_name}}_{solution_name}_solution_checklist.md` (with optional suffix `_2`, `_3`, ... for collisions).
9. No duplicate filenames after sanitization.
10. Arrow formatting: base variable lines in repo checklist use `- {{token}} → value`.
11. If append=true skipped files are truly existing on disk prior to generation.
12. On FAIL status ensure no partial checklist written missing critical headings (still record violation).

Record each failure as object: `{ "type": "<code>", "target": "<file|repo|path>", "detail": "<description>" }` in `verification_errors`.
If DEBUG=1 emit: `[debug][generate-solution-task-checklists][verification] FAIL code=<code> detail="<description>"` per violation.

Write `output/{{repo_name}}_generate-solution-task-checklists.json` including:
{
  "repo_name": "...",
  "solutions_total": <int>,
  "solutions_processed": <int>,
  "solutions_skipped": <int>,
  "solution_checklists_created": <int>,
  "solution_index_path": "tasks/{{repo_name}}_solutions_checklist.md" | null,
  "append_mode": <true|false>,
  "status": "SUCCESS" | "FAIL",
  "timestamp": "ISO 8601 UTC seconds",
  "verification_errors": [ {"type": "...", "target": "...", "detail": "..."}, ... ],
  "debug": ["..."] (optional when DEBUG=1)
}

### Step 10 (MANDATORY) – Debug Exit Trace
If DEBUG=1 print:  
`[debug][generate-solution-task-checklists] EXIT status={{status}} created={{solution_checklists_created}} skipped={{solutions_skipped}}`.

### Step 12 (MANDATORY) – Repo Variable Refresh (INLINE ONLY)
After successful generation (status=SUCCESS):
1. Open `tasks/{{repo_name}}_repo_checklist.md`.
2. Locate line beginning with `- {{solutions_json}}` and replace text after `→` with the absolute path to `output/{{repo_name}}_generate-solution-task-checklists.json`.
3. Locate line beginning with `- {{solutions}}` and replace text after `→` with `<solutions_total> solutions: name1; name2; name3 ...` truncating after 5 names with `...` if more.
4. If append=true and only new solutions were added, reflect new total count (not just added count).
5. If status=FAIL set both variable values to FAIL (do NOT modify other tokens).
6. If a variable line lacks an arrow append one before inserting value (`- {{token}} → <value>`).
7. Preserve the leading token EXACTLY.
**Inline Variable Policy:** Never create a secondary block; modify original lines only.
 **Prohibited Additions:** Do NOT add `## Solution Task Sections` or any new headings/blocks. Any such addition must trigger a verification error (`repo_checklist_modification`).

## Output Contract
- repo_name: string
- solutions_total: integer (length of input solutions array)
- solutions_processed: integer (solutions attempted for checklist generation)
- solutions_skipped: integer (already had checklist when append=true)
- solution_checklists_created: integer (newly created checklist files)
- solution_index_path: string | null
- append_mode: boolean
- status: SUCCESS | FAIL
- timestamp: ISO 8601

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Implement in Python (preferred) or PowerShell.
2. Idempotent in append=true mode—no overwrites of existing files.
3. All writes UTF-8 with newline termination.
4. Ensure atomic writes (write temp then replace) if partial write risk considered (optional).
5. Sorting: You MAY sort solutions by solution_name for deterministic output (recommended).
6. Slug collisions: If two solution names produce same slug, append numeric suffix `_2`, `_3`, etc.
7. Variable Section: Preserve exact formatting lines from source prompt to keep downstream parsing stable.
8. Do NOT modify unrelated repository checklist files.
9. Logging: Keep debug logs concise—avoid dumping full file contents.
10. Script naming: `temp-script/generate_solution_task_checklists.py` (or similar).

## Error Handling
- Critical failure conditions (abort and status=FAIL):
  - Missing / unreadable `solutions_json` path extracted from checklist.
  - JSON malformed or missing `solutions` array.
  - Inability to write output directories/files.
- Non-critical (log and continue):
  - One solution path missing (skip that solution only).
  - Duplicate solution names (resolve via suffix strategy).
- On critical failure: do NOT write partial output JSON unless capturing failure status.
- Always include meaningful stderr-like diagnostic text inside debug log lines.

## Consistency Checks
After generation:
1. Verify count alignment: `solutions_total == len(solutions array parsed)`.
2. Verify each created checklist contains required task directives (at least the 6 base tasks).
3. If index file created, verify every processed solution appears exactly once.
4. Confirm JSON output file exists and includes mandatory keys: `repo_name`, `status`, `timestamp`.
5. If any consistency check fails → set status=FAIL (unless already FAIL) and log reason.

## Cross-References
Use freshest in-memory values; never reuse stale prior-run values. Variables:
- repo_name – repository identifier (from checklist)
- solutions_json – path to discovery JSON (from checklist)
- solutions – array of absolute solution paths
- solution_name / solution_slug – derived per solution
- solution_checklists_created – count of newly written files
- solutions_skipped – count of skipped existing files
- append_mode – boolean input
- status – final task status
- timestamp – ISO 8601 completion time
Ensure per-solution checklist metadata (solution_path, solution_name) matches discovery JSON EXACTLY (case preserved).

## Example Minimal Output JSON
```json
{
  "repo_name": "sample-repo",
  "solutions_total": 2,
  "solutions_processed": 2,
  "solutions_skipped": 0,
  "solution_checklists_created": 2,
  "solution_index_path": "tasks/sample-repo_solutions_checklist.md",
  "append_mode": false,
  "status": "SUCCESS",
  "timestamp": "2025-11-03T08:12:45Z"
}
```

## DEBUG Examples
```
[debug][generate-solution-task-checklists] START checklist_path='tasks/media_stack_all_repo_checklist.md' append=false
[debug][generate-solution-task-checklists] loaded solutions: 3
[debug][generate-solution-task-checklists] mapping slug='core_services' -> 'D:/repos/media_stack_all/src/Core.Services/Core.Services.sln'
[debug][generate-solution-task-checklists] wrote checklist: tasks/core_services_solution_checklist.md
[debug][generate-solution-task-checklists] EXIT status=SUCCESS created=3 skipped=0
```

## Final Notes
The correctness of downstream solution task execution (restore/build/KB lifecycle) depends on accurate variable section replication and stable checklist filenames. Preserve formatting strictly.
## Deterministic Summary (Concise)
The following guarantees ensure reproducible outputs for identical inputs:
- Solution ordering: Stable lexicographic (case-insensitive) sort by `solution_name` on every non-append run; append mode inserts only new solutions in sorted order after existing lines.
- Slug derivation: `solution_slug = lowercase(solution_name)` with non-alphanumeric replaced by `_`; collisions resolved by suffix `_2`, `_3`, etc. (first occurrence keeps base slug).
- Path normalization: Use absolute path; preserve original case; resolve `..` segments; never modify filename casing.
- Timestamp: UTC ISO 8601 truncated to whole seconds (e.g. `2025-11-03T00:00:00Z`).
- Line endings: All generated markdown and JSON files use LF; no trailing spaces; single final newline.
- Variable section: Inserted verbatim from `solution_tasks_list.prompt.md` (no reflow, no trimming).
- JSON field values: Derived solely from deterministic counts (ordering doesn’t affect semantics). Given same inputs, JSON content identical except timestamp.
- Append mode stability: Existing index and checklist files retained; only new solutions added—no reordering of historical entries.
- Debug log format: Consistent key=value pairs enabling diff-friendly tracing; absence of DEBUG leaves no extraneous variability.

## Manual Usage (Source of Truth)
This markdown is the authoritative specification. You may execute it manually without any helper script:
1. Collect `checklist_path`, then read `repo_name` and `solutions_json` from the checklist, choose `append=true|false`.
2. Load JSON, extract array `solutions` (absolute paths). If `solution_count` missing, compute as `len(solutions)`.
3. Derive `solution_name`, `solution_slug` (collision handling) for each path; discard duplicates beyond the first.
4. Sort solutions by `solution_name` (case-insensitive) unless in append mode where only new solutions are sorted and appended.
5. Create/Update index file per deterministic rules above.
6. For each solution (skipping existing when append=true) write checklist file using the template plus injected Variables section.
7. Produce structured JSON summary with timestamp truncated to seconds (UTC) and save to `output/{{repo_name}}_generate-solution-task-checklists.json`.
8. Run consistency checks: counts, presence of required directives, index coverage.
9. Record FAIL only on critical validation or I/O issues; otherwise SUCCESS.

If automation is desired, a script may implement these steps; however the script must conform exactly to this specification and never introduce non-deterministic ordering, formatting drift, or extraneous data.
---
temperature: 0.0
---

@generate-repo-task-checklists input=<optional> append=<optional>

Task name: generate-repo-task-checklists

## Description
This task generates task checklists for all repositories in the input file. The checklists allow agents to pick up work or resume when a previous run stops. This is a file generation task that **must** be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow Step by Step)

### Step 1 (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-repo-task-checklists] START input='{{input}}' append={{append}}`

### Step 2 (MANDATORY)
Input Parameters:
- You are given `input` (file path) and `append` (boolean) from the calling context.

Defaults:
- input = "repositories.txt"
- append = false

If DEBUG=1, print: `[debug][generate-repo-task-checklists] using input_file: {{input}}, append_mode: {{append}}`

Directory Preparation:
- **If append = false (default):**
  - **Remove the entire ./tasks directory if it exists** (including all files and subdirectories)
  - **Remove the entire ./output directory if it exists** (including all output JSON files)
  - **Remove the entire ./temp-script directory if it exists** (including all generated scripts)
  - Create fresh ./tasks, ./output, and ./temp-script directories
  - If DEBUG=1, print: `[debug][generate-repo-task-checklists] removed and recreated tasks, output, and temp-script directories (append=false)`
  - **WARNING**: This will delete all existing checklists, solution checklists, output files, and generated scripts

- **If append = true:**
  - Keep existing ./tasks directory and all its contents
  - Keep existing ./output directory and all its contents
  - Keep existing ./temp-script directory and all its contents
  - Create ./tasks, ./output, and ./temp-script directories if they don't exist
  - If DEBUG=1, print: `[debug][generate-repo-task-checklists] preserving existing tasks, output, and temp-script (append=true)`

### Step 3 (MANDATORY)
Read Input File:
- Read the input file to get all repository URLs
- Parse line by line; skip empty lines and lines beginning with hash symbol #
- Extract repository URLs
- If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{count}} repositories in input file`

### Step 4 (MANDATORY)
Determine Repositories to Process:
- **If append = false:**
  - Process all repositories from input file
  - If DEBUG=1, print: `[debug][generate-repo-task-checklists] processing all {{count}} repositories`
- **If append = true:**
  - Read existing ./tasks/all_repository_checklist.md (if it exists)
  - Extract list of repositories already tracked in master checklist
  - Compare with repositories from input file
  - Identify new repositories = repositories in input file but NOT in master checklist
  - If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{existing_count}} existing repos, {{new_count}} new repos`
  - Only process these new repositories

### Step 5 (MANDATORY)
Parse Task Definitions:
- Read .github/prompts/repo_tasks_list.prompt.md to extract:
  - All task directives (e.g., @task-clone-repo, @task-search-readme, etc.)
  - Short descriptions for each task
  - The complete "Variables available:" section content
- If DEBUG=1, print: `[debug][generate-repo-task-checklists] extracted {{task_count}} tasks from .github/prompts/repo_tasks_list.prompt.md`

### Step 6 (MANDATORY)
Generate or Update Master Checklist:
- File: ./tasks/all_repository_checklist.md

- **If append = false:**
  - Create new file with all repositories from input file
  - If DEBUG=1, print: `[debug][generate-repo-task-checklists] creating new master checklist`
  - Format:
    ```
    # All Repositories Checklist
    Generated: [timestamp]
    Source: [input file path]
    ## Repositories
    - [ ] repo_name_1 [repo_url_1]
    - [ ] repo_name_2 [repo_url_2]
    - [ ] repo_name_3 [repo_url_3]
    ...
    ```

- **If append = true:**
  - If file exists:
    - Read existing content
    - Preserve existing repository entries (keep their checkbox status)
    - Append new repositories to the "## Repositories" section
    - Update "Generated" timestamp
    - If DEBUG=1, print: `[debug][generate-repo-task-checklists] appending {{new_count}} repos to master checklist`
  - If file does not exist:
    - Create new file with new repositories only
    - If DEBUG=1, print: `[debug][generate-repo-task-checklists] creating master checklist (no existing file)`

### Step 7 (MANDATORY)
Generate Individual Checklist Files:
For each repository to process:
- Extract repo_name from URL
- If DEBUG=1, print: `[debug][generate-repo-task-checklists] generating checklist for: {{repo_name}}`
- **Important:** Always name the checklist exactly `./tasks/{repo_name}_repo_checklist.md` (no alternate paths or filenames).

- **If append = false:**
  - Create checklist for all repositories from input file

- **If append = true:**
  - Only create checklists for new repositories (not already in master checklist)
  - Skip creating files for repositories that already have checklist files
  - If DEBUG=1 and skipping, print: `[debug][generate-repo-task-checklists] skipping existing: {{repo_name}}`
  - If a repository is in input file but doesn't have a checklist file, create it

- Format:
    ```
    # Task Checklist: {repo_name}
    Repository: {repo_url}
    Generated: [timestamp]
    ## Repo Tasks (Sequential Pipeline - Complete in Order)
  - [ ] [MANDATORY 1] [SCRIPTABLE] Clone repository to local directory @task-clone-repo
  - [ ] [MANDATORY 2] [SCRIPTABLE] Search for README file in repository @task-search-readme
    - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
    - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme
  - [ ] [MANDATORY 3] [SCRIPTABLE] Find all solution files in repository @task-find-solutions
  - [ ] [MANDATORY 4] [SCRIPTABLE] Generate solution-specific task sections in checklist @generate-solution-task-checklists

    ## For Agents Resuming Work
    **Next Action:**
    1. Check if all [MANDATORY] tasks are completed
    2. If YES and {{readme_content}} is not blank and not "NONE", execute @task-scan-readme
    3. If {{commands_extracted}} is not blank and not "NONE", execute @task-execute-readme
    4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

    **How to Execute:** Invoke the corresponding task prompt (e.g., `@task-clone-repo`) as defined in `.github/prompts/repo_tasks_list.prompt.md`. Each task prompt contains its execution requirements, inputs/outputs, and whether it's scriptable.

    **Quick Reference:**
  - [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4)
    - [CONDITIONAL] [NON-SCRIPTABLE] @task-scan-readme executes when {{readme_content}} is not blank and not "NONE"
    - [CONDITIONAL] [NON-SCRIPTABLE] @task-execute-readme executes when {{commands_extracted}} is not blank and not "NONE"
    - [SCRIPTABLE] tasks can be automated with scripts
    - [NON-SCRIPTABLE] tasks require AI reasoning and direct tool calls
    - Mark completed tasks with [x]

    ## Repo Variables Available
    ### Variables available:
    [Content dynamically extracted from .github/prompts/repo_tasks_list.prompt.md "Variables available:" section]
    ```

### Step 8 (MANDATORY)
Structured Output:
- Save JSON object to `output/generate-repo-task-checklists.json` with:
  - input_file: path to input file used
  - append_mode: boolean (true/false)
  - repositories_total: integer (total in input file)
  - repositories_processed: integer (new repos if append=true, all if append=false)
  - repositories_skipped: integer (existing repos if append=true, 0 if append=false)
  - checklists_generated: integer (number of individual checklist files created)
  - master_checklist_path: string (`./tasks/all_repository_checklist.md`)
  - individual_checklists_path: string (`./tasks/`)
  - status: SUCCESS if all files generated, FAIL if error occurred
  - timestamp: ISO 8601 format datetime when task completed

### Step 9 (MANDATORY)
DEBUG Exit Trace: If DEBUG=1, print:
`[debug][generate-repo-task-checklists] EXIT status={{status}} processed={{repositories_processed}} generated={{checklists_generated}}`

## Implementation Notes
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task.
2. URL Parsing: Extract friendly repo names from URLs (e.g., last segment after final /).
3. Dynamic Task Extraction: Parse .github/prompts/repo_tasks_list.prompt.md to get task list and variables section.
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure.
5. Markdown Format: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes.
6. Timestamp Format: Use ISO 8601 format (e.g., "2025-10-24T14:30:00").
7. Error Handling: If input file not found, set status=FAIL and return with empty results.
8. Append Mode Logic: Compare normalized URLs (trim trailing slashes, case-insensitive), preserve existing entries, only create files for new repos.
9. Script Location: Save generated script to temp-script/ directory with naming pattern: generate_task_checklists.py (or .ps1/.sh)
\n+## Error Handling
- For any step that fails:
  - Log error details (exception type, message, failing path or operation)
  - If reading the input file or removing/creating required directories fails, set status=FAIL and abort subsequent steps
  - Do not partially update master or individual checklists on failure (avoid inconsistent state)
  - If one repository fails to process, log it and continue with others (unless failure mode is global/critical)
\n+## Consistency Checks
- After writing each individual checklist, verify required task lines and the `## Repo Variables Available` section are present.
- After generating master checklist, verify all repository names from processed set appear exactly once.
- After writing `output/generate-repo-task-checklists.json`, verify keys: `repositories_total`, `repositories_processed`, `status` exist.
- If append=true, confirm no duplicate repository entries were added to master checklist.
- If any verification fails, log an error and set status=FAIL.
\n+## Cross-References
- Always reference the most recent derived values before writing files.
- Variables involved in this task:
  - input / input_file (source repository list)
  - append / append_mode (controls preservation of existing artifacts)
  - repositories_total
  - repositories_processed
  - repositories_skipped
  - checklists_generated
  - master_checklist_path
  - individual_checklists_path
  - status
  - timestamp
- Ensure JSON output mirrors in-memory counts; do not rely on stale counters.
