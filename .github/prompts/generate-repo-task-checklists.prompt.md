---
temperature: 0.0
---

@generate-repo-task-checklists input=<optional> append=<optional>

Task name: generate-repo-task-checklists

## Description:
This task generates task checklists for all repositories in the input file. The checklists allow agents to pick up work or resume when a previous run stops. This is a file generation task that CAN be implemented as a script.

## Execution Policy
**ALL STEPS BELOW ARE MANDATORY.**
**DO NOT SKIP OR SUMMARIZE.**
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)
### Step 1: (MANDATORY)
DEBUG Entry Trace: If DEBUG=1, print: `[debug][generate-repo-task-checklists] START input='{{input}}' append={{append}}`

### Step 2: (MANDATORY)
Input Parameters: You are given input (file path) and append (boolean) from the calling context.
   Defaults:
      input = "repositories.txt"
      append = false
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] using input_file: {{input}}, append_mode: {{append}}`

Directory Preparation:   
   **If append = false (default):**
   - **Remove the entire ./tasks directory if it exists** (including all files and subdirectories)
   - **Remove the entire ./output directory if it exists** (including all output JSON files)
   - **Remove the entire ./temp-script directory if it exists** (including all generated scripts)
   - Create fresh ./tasks, ./output, and ./temp-script directories
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] removed and recreated tasks, output, and temp-script directories (append=false)`
   - **WARNING**: This will delete all existing checklists, solution checklists, output files, and generated scripts
   
   **If append = true:**
   - Keep existing ./tasks directory and all its contents
   - Keep existing ./output directory and all its contents
   - Keep existing ./temp-script directory and all its contents
   - Create ./tasks, ./output, and ./temp-script directories if they don't exist
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] preserving existing tasks, output, and temp-script (append=true)`

### Step 3: (MANDATORY)
Read & Normalize Input (Deterministic):
   - Parse input file line by line; skip blank lines and comment lines starting with `#`.
   - Collect raw HTTPS repository URLs.
   - Normalize each URL: trim whitespace, remove trailing slashes, case-insensitive for duplicate detection.
   - Derive friendly repo name:
       * If URL contains `/_git/`, use the segment after `/_git/` (strip trailing `/` & optional `.git`).
       * Else use final path segment (strip optional `.git`).
   - De-duplicate on normalized URL (first occurrence wins).
   - Sort repositories lexicographically by repo name for stable ordering.
   - DEBUG sequence (if DEBUG=1):
       1. `[debug][generate-repo-task-checklists] found {{raw_count}} repositories in input file`
       2. `[debug][generate-repo-task-checklists] normalized unique repositories: {{count}}`
       3. `[debug][generate-repo-task-checklists] sorted order: {{repo_names_csv}}`

### Step 4: (MANDATORY)
Determine Repositories to Process:
   **If append = false:**
   - Process all sorted repositories.
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] processing all {{count}} repositories (sorted)`
   **If append = true:**
   - Read existing master checklist if present; extract existing repo names case-insensitively.
   - New repositories = normalized names not already listed.
   - Sort only the new repositories (preserve existing order).
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] found {{existing_count}} existing repos, {{new_count}} new repos (sorted new subset)`
   - Only process new repos; existing ones are skipped.

### Step 5: (MANDATORY)
Parse Task Definitions:
   - Read `.github\prompts\repo_tasks_list.prompt.md`.
   - Extract all task directives using regex `@task-[a-z0-9-]+` in first-appearance order.
   - Collect short description (full line containing directive), ignoring duplicates inside the variables block to reduce noise.
   - Extract the entire "## Repo Variables Available" section verbatim.
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] extracted {{task_count}} tasks from .github\prompts\repo_tasks_list.prompt.md`

### Step 6: (MANDATORY)
Generate or Update Master Checklist:
   - File: `./tasks/all_repository_checklist.md`
   **If append = false:**
   - Create a new checklist with all sorted repositories.
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] creating new master checklist (sorted)`
   **If append = true:**
   - Preserve existing lines & checkbox states; append new (sorted) repositories after the last existing repo line.
   - Update only `Generated:` timestamp; do not reorder existing entries.
   - If DEBUG=1, print: `[debug][generate-repo-task-checklists] appending {{new_count}} new repos (sorted) to master checklist`
   - Deterministic formatting rules:
       * Unix line endings (`\n`)
       * No trailing spaces
       * Single final newline
       * Each repo line starts with `- [ ]` or `- [x]` exactly
       * No duplicate repo names
   - Master checklist structure:
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

### Step 7: (MANDATORY)
Generate Individual Checklist Files (Single Canonical Template):
    - For each repository to process (sorted subset for append=false; sorted new subset for append=true):
          * Name file exactly `./tasks/{repo_name}_repo_checklist.md`.
          * Always WRITE the file fresh (overwrite if exists when append=false). Never append partial content.
          * If append=true and file exists, SKIP creation entirely.
          * If DEBUG=1, print: `[debug][generate-repo-task-checklists] generating checklist for: {{repo_name}}` or skip line.
    - Checklist MUST contain exactly one occurrence of each required heading. If after writing the file the heading `# Task Checklist:` appears more than once, set status=FAIL.
    - Required headings (exact, case-sensitive):
          * `# Task Checklist:`
          * `## Repo Tasks (Sequential Pipeline - Complete in Order)`
          * `## Repo Variables Available`
          * `## Parsed Task Directives`
    - Preserve placeholder braces literally (do NOT interpolate `{{...}}`).
    - Timestamp: UTC ISO 8601 truncated to seconds with optional trailing `Z` (e.g., `2025-11-03T00:00:00Z`). Use consistent format across all generated files in a run.
    - Canonical template (the ONLY template – do not duplicate below):
       ```
       # Task Checklist: {repo_name}
       Repository: {repo_url}
       Generated: [timestamp]

       ## Repo Tasks (Sequential Pipeline - Complete in Order)
       - [ ] [MANDATORY] [SCRIPTABLE] Clone repository to local directory @task-clone-repo (1)
       - [ ] [MANDATORY] [SCRIPTABLE] Search for README file in repository @task-search-readme (2)
       - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme
       - [ ] [CONDITIONAL] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme
       - [ ] [MANDATORY] [SCRIPTABLE] Find all solution files in repository @task-find-solutions (3)
       - [ ] [MANDATORY] [SCRIPTABLE] Generate solution-specific task sections in checklist @generate-solution-task-checklists (4)

       ## For Agents Resuming Work
       **Next Action:**
       1. Check if all [MANDATORY] tasks are completed
       2. If YES and {{readme_content}} is not blank and not "NONE", execute @task-scan-readme
       3. If {{commands_extracted}} is not blank and not "NONE", execute @task-execute-readme
       4. [CONDITIONAL] tasks require AI reasoning and manual tool calls - not automated

       **How to Execute:** Invoke the corresponding task prompt.

       **Quick Reference:**
       - [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4)
       - [CONDITIONAL] @task-scan-readme runs when {{readme_content}} not blank and not "NONE"
       - [CONDITIONAL] @task-execute-readme runs when {{commands_extracted}} not blank and not "NONE"
       - [SCRIPTABLE] tasks: clone, search-readme, find-solutions, generate-solution-task-checklists
       - [NON-SCRIPTABLE] tasks: scan-readme, execute-readme
       - Mark completed tasks with [x]

       ## Repo Variables Available
       [Variables section verbatim]

       ## Parsed Task Directives
       - One bullet per unique directive in first-appearance order
       ```
    - Do NOT include any secondary or alternative template examples. The above block is authoritative.
    - Post-write validation (Mandatory):
          1. Count occurrences of `# Task Checklist:` → MUST equal 1.
          2. Count occurrences of `## Repo Variables Available` → MUST equal 1.
          3. Ensure no duplicated task lines (each directive appears once).
          4. If any violation found, delete the faulty file and set status=FAIL before JSON output.
    - Task classification (for reference – do not duplicate in file):
          * MANDATORY (sequential): @task-clone-repo (1), @task-search-readme (2), @task-find-solutions (3), @generate-solution-task-checklists (4)
          * CONDITIONAL: @task-scan-readme, @task-execute-readme
          * SCRIPTABLE: @task-clone-repo, @task-search-readme, @task-find-solutions, @generate-solution-task-checklists
          * NON-SCRIPTABLE: @task-scan-readme, @task-execute-readme
    - Dynamic Variables Section: Extract the entire "## Repo Variables Available" section from `.github\prompts\repo_tasks_list.prompt.md` verbatim.

### Step 8: (MANDATORY)
Structured Output: Save JSON object to output/generate-repo-task-checklists.json with:
   - input_file: path to input file used
   - append_mode: boolean (true/false)
   - repositories_total: integer (total in input file)
   - repositories_processed: integer (new repos if append=true, all if append=false)
   - repositories_skipped: integer (existing repos if append=true, 0 if append=false)
   - checklists_generated: integer (number of individual checklist files created)
   - master_checklist_path: string (./tasks/all_repository_checklist.md)
   - individual_checklists_path: string (./tasks/)
   - status: SUCCESS if all files generated, FAIL if error occurred
   - timestamp: ISO 8601 format datetime when task completed

### Step 9: (MANDATORY)
DEBUG Exit Trace: If DEBUG=1, print:
   "[debug][generate-repo-task-checklists] EXIT status={{status}} processed={{repositories_processed}} generated={{checklists_generated}}"

## Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. URL Parsing: Extract friendly repo names from URLs (e.g., last segment after final /)
3. Dynamic Task Extraction: Parse .github\prompts\repo_tasks_list.prompt.md to get task list and variables section
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure
   Core reproducibility requirements have been embedded inline in Steps 3–7. Consolidated summary:
   - Normalization & sorting (Step 3) produce stable repo ordering.
   - Append mode preserves existing order; only sorted new entries appended (Step 4 & 6).
   - Master checklist formatting rules prevent whitespace drift (Step 6).
   - Individual checklist deterministic content + directive uniqueness enforced (Step 7).
   - Consistency checks & key ordering already defined in Consistency Checks and Step 8.
   - No randomness, locale neutrality, placeholder fidelity guaranteed through explicit rules.
   Following these embedded rules ensures repeat runs with identical inputs produce identical artifacts except for timestamp.
5. Markdown Format: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes
6. Timestamp Format: Use ISO 8601 format (e.g., "2025-10-24T14:30:00")
7. Error Handling: If input file not found, set status=FAIL and return with empty results
8. Append Mode Logic: Compare normalized URLs (trim trailing slashes, case-insensitive), preserve existing entries, only create files for new repos
9. (Deprecated) Script Generation: Previously a helper script (generate_task_checklists.py) could automate Steps 3–8. This repository now treats THIS MARKDOWN as the single source of truth. Do NOT regenerate or rely on any local script; perform tasks manually or via an agent following Steps 1–9 exactly. If automation is desired in the future, re-implement using these steps verbatim.

## Error Handling
- Missing input file: Set status=FAIL, repositories_total=0, repositories_processed=0, repositories_skipped=0. Do not attempt further steps.
- IOError while reading repo_tasks_list.prompt.md: Set status=FAIL and include error_message in structured output (add field if needed). Skip checklist generation.
- JSON write failure: Retry once; if still failing, set status=FAIL but keep any generated markdown files.
- Directory removal failure (append=false): Log warning and continue; do NOT abort unless tasks directory cannot be recreated.
- Empty repository list after parsing input: status=SUCCESS with repositories_total=0; generate master checklist with header only.

## Consistency Checks
- Step numbering must be strictly sequential (1..9). Validate after generation; if mismatch, set status=FAIL.
- Master checklist must contain every processed repository exactly once. Compare count of lines starting with "- [ ]" or "- [x]" under ## Repositories with repositories_processed.
- Each individual checklist must include headings: "# Task Checklist:", "## Repo Tasks", and "## Repo Variables Available".
- Dynamic variables section must not be empty (at least one bullet or line of content extracted).
- If append=true, repositories_skipped + repositories_processed MUST equal repositories_total from input file.

## Cross-References
- {{input}} → Input file path used to derive repositories.
- {{append}} → Append mode controlling cleanup logic.
- {{repositories_total}} → Total repositories parsed from input.
- {{repositories_processed}} → Number of repos for which checklist files were created.
- {{repositories_skipped}} → Repositories not processed due to append mode.
- {{checklists_generated}} → Count of checklist files physically written.
- {{master_checklist_path}} → Path to master checklist markdown file.
- {{individual_checklists_path}} → Directory path containing per-repo checklists.
- {{status}} → Overall task status (SUCCESS/FAIL).
- {{timestamp}} → ISO 8601 completion time.

## Deterministic Summary (Concise)
All determinism rules are already embedded inline in Steps 3–7 and Manual Usage. This summary is retained only for quick reference:
- Normalize & de-duplicate URLs (trim, strip trailing '/', case-insensitive); derive friendly name (`/_git/` segment else last path; strip `.git`).
- Sort repositories lexicographically by friendly name (append mode: keep existing order, sort only new subset).
- Timestamps: UTC ISO8601 truncated to whole seconds.
- Formatting: LF endings, no trailing spaces, single final newline, repo lines `- [ ] name [url]`.
- Placeholders: keep `{{variable}}` literal; do not expand.
- Directives: unique first appearance order; skip duplicates inside variables block.
   - Present them under a single heading `## Parsed Task Directives` with one bullet per directive.

8. Idempotency (append=false):
   - A run with append=false MUST fully remove then recreate `./tasks`, `./output`, `./temp-script` before generation.
   - Subsequent runs with identical input produce identical file contents (except timestamp).

9. No Randomness:
   - Do not use random sampling, hashing-based ordering, or any non-deterministic APIs.
   - Avoid environment-dependent locale effects (force UTF-8; treat input as plain text).

10. Failure Modes:
   - On recoverable warnings (e.g., inability to delete a single file), proceed while logging `[debug][generate-repo-task-checklists] warning: ...`.
   - Only set status=FAIL for contract violations or required artifact generation failure.

11. Consistency Assertions (before writing JSON):
   - Validate master repo count equals repositories_processed when append=false.
   - Validate (repositories_processed + repositories_skipped) == repositories_total when append=true.
   - Ensure each generated checklist contains the three required headings and at least one variable bullet.
   - Confirm ordering of repo entries matches sorted repo names.

12. JSON Stability:
   - Key order stable as specified in Step 8; do not include extraneous, transient fields.
   - If an error occurs, include `error_message` as the last key.

13. Line Prefix Integrity:
   - Repository entries MUST begin with `- [ ]` or `- [x]` exactly; do not introduce additional whitespace.

14. Model Interaction:
   - Temperature must be 0 for generation scripts to avoid variability (already set in front-matter).
   - Do not rely on speculative reasoning to infer tasks beyond those explicitly parsed.

Reproducibility Guarantee: If the above rules are followed, running the task multiple times with identical inputs and settings (ignoring timestamp) yields byte-for-byte identical markdown and JSON artifacts.


