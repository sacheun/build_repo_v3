---
temperature: 0.0
---

@generate-repo-task-checklists input=<optional> append=<optional>

Task name: generate-repo-task-checklists

## Description:
This task generates task checklists for all repositories in the input file. The checklists allow agents to pick up work or resume when a previous run stops. This is a file generation task that CAN be implemented as a script.

## Execution Policy
**STRICT MODE ON**
- ALL STEPS BELOW ARE MANDATORY.
- DO NOT SKIP OR SUMMARIZE.
**THIS TASK IS SCRIPTABLE**

## Instructions (Follow this Step by Step)

### Step 1: (MANDATORY)
Input Parameters: You are given input (file path) and append (boolean) from the calling context.
   Defaults:
      input = "repositories.txt"
      append = false

Directory Preparation:   
   **If append = false (default):**
   - **Remove the entire ./tasks directory if it exists** (including all files and subdirectories)
   - **Remove the entire ./output directory if it exists** (including all output JSON files)
   - **Remove the entire ./temp-script directory if it exists** (including all generated scripts)
   - Create fresh ./tasks, ./output, and ./temp-script directories

   **If append = true:**
   - Keep existing ./tasks directory and all its contents
   - Keep existing ./output directory and all its contents
   - Keep existing ./temp-script directory and all its contents
   - Create ./tasks, ./output, and ./temp-script directories if they don't exist


### Step 2: (MANDATORY)
Read & Normalize Input (Deterministic):
   - Parse input file line by line; skip blank lines and comment lines starting with `#`.
   - Collect raw HTTPS repository URLs.
   - Normalize each URL: trim whitespace, remove trailing slashes, case-insensitive for duplicate detection.
   - Derive friendly repo name:
       * If URL contains `/_git/`, use the segment after `/_git/` (strip trailing `/` & optional `.git`).
       * Else use final path segment (strip optional `.git`).


### Step 3: (MANDATORY)
Determine Repositories to Process:
   **If append = false:**
   - Process all sorted repositories.
   **If append = true:**
   - Read existing master checklist if present; extract existing repo names case-insensitively.
   - New repositories = normalized names not already listed.
   - Sort only the new repositories (preserve existing order).
   - Only process new repos; existing ones are skipped.



### Step 4: (MANDATORY)
Generate or Update Master Checklist:
   - File: `./tasks/all_repository_checklist.md`
   **If append = false:**
   - Create a new checklist with all sorted repositories.
   **If append = true:**
   - Preserve existing lines & checkbox states; append new (sorted) repositories after the last existing repo line.
   - Update only `Generated:` timestamp; do not reorder existing entries.
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

### Step 5: (MANDATORY)
Generate Individual Repository Checklist Files:
    - For each repository to process (sorted subset for append=false; sorted new subset for append=true):
          * Name file exactly `./tasks/{repo_name}_repo_checklist.md`.
          * Always WRITE the file fresh (overwrite if exists when append=false). Never append partial content.
          * If append=true and file exists, SKIP creation entirely.
    - Checklist MUST contain exactly one occurrence of each required heading. If after writing the file the heading `# Task Checklist:` appears more than once, set status=FAIL.
    - Required headings (exact, case-sensitive):
          * `# Task Checklist:`
          * `## Repo Tasks (Sequential Pipeline - Complete in Order)`
          * `## Repo Variables Available`
    - Preserve placeholder braces literally (do NOT interpolate `{{...}}`).
    - Timestamp: UTC ISO 8601 truncated to seconds with optional trailing `Z` (e.g., `2025-11-03T00:00:00Z`). Use consistent format across all generated files in a run.
    - Canonical template (the ONLY template – do not duplicate below):
       ```
       # Task Checklist: {repo_name}
       Repository: {repo_url}
       Generated: [timestamp]

       ## Repo Tasks (Sequential Pipeline - Complete in Order)
       - [ ] [MANDATORY] [SCRIPTABLE] Clone repository to local directory @task-clone-repo (1)
       - [ ] [MANDATORY] [SCRIPTABLE] Find all solution files in repository @task-find-solutions (2)
       - [ ] [MANDATORY] [SCRIPTABLE] Generate per-solution checklist files (no inline sections) @generate-solution-task-checklists (3)
      - [ ] [MANDATORY] [SCRIPTABLE] Search for README file in repository @task-search-readme (4)
       - [ ] [MANDATORY] [NON-SCRIPTABLE] Scan README and extract setup commands @task-scan-readme (5)
       - [ ] [MANDATORY] [NON-SCRIPTABLE] Execute safe commands from README @task-execute-readme (6)


       ## For Agents Resuming Work
       **Next Action:**
       1. Check if all [MANDATORY] tasks are completed
       2. Find the next tasks which is not marked with [x]
       3. **How to Execute:** Invoke the corresponding task prompt.

       **Quick Reference:**
       - [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4 → 5 → 6)
       - [SCRIPTABLE] tasks: clone, search-readme, find-solutions, generate-solution-task-checklists
       - [NON-SCRIPTABLE] tasks: scan-readme, execute-readme
       - Mark completed tasks with [x]

   ## Repo Variables Available
   (Single authoritative variable block. EXACTLY ONE LINE PER TOKEN. No duplicate descriptive lines permitted. Every line MUST use arrow format even if value blank.)
   - {{repo_url}} → {repo_url}
   - {{repo_name}} → {repo_name}
   - {{clone_path}} →
   - {{repo_directory}} →
   - {{solutions_json}} →
   - {{solutions}} →
   - {{readme_content}} →
   - {{readme_filename}} →
   - {{commands_extracted}} →
   - {{executed_commands}} →
   - {{skipped_commands}} →

   ## Variable Definitions (Reference Only – DO NOT PARSE FOR VALUES)
   - repo_url: Original repository URL provided to the workflow.
   - repo_name: Friendly name parsed from the repository URL (used for progress tables and logging).
   - clone_path: Root folder where repositories are cloned (populated later by task-clone-repo).
   - repo_directory: Absolute path to the cloned repository (populated later by task-clone-repo).
   - readme_content: README file content (output of @task-search-readme).
   - readme_filename: README filename (output of @task-search-readme).
   - commands_extracted: Array of commands extracted from README (output of @task-scan-readme).
   - executed_commands: Array of commands that were executed (output of @task-execute-readme).
   - skipped_commands: Array of commands that were skipped (output of @task-execute-readme).
   - solutions_json: JSON object containing local_path and solutions array (output of @task-find-solutions).
   - solutions: Array of solution objects with name and path properties (extracted from solutions_json, output of @task-find-solutions).
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

### Step 6: (MANDATORY)
Populate Base Repo Variables (repo_url & repo_name):
   - The template already contains authoritative arrow lines for ALL variable tokens.
   - Populate ONLY the values for:
    * `- {{repo_url}} → {repo_url}` (replace placeholder with exact normalized URL)
    * `- {{repo_name}} → {repo_name}` (replace placeholder with derived friendly name)
   - Leave all other variable values blank (i.e., keep trailing arrow with nothing after) – they will be filled by later tasks.
   - Extraction logic for repo_name (deterministic):
      * Azure DevOps (URL contains `/_git/`): final segment after last `/` (strip `.git`).
   - Pre-normalize URL: trim whitespace, strip trailing slashes, preserve case.
   - Absolutely forbid creating duplicate variable lines or re-emitting the variables heading.
   - Validation (per checklist): EXACTLY ONE occurrence of each variable line. Any duplicate → status=FAIL.


### End of Steps

## Output Contract
- input_file: string (path to repositories source file actually used; default or provided)
- append_mode: boolean (true when running in append mode, else false)
- repositories_total: number (total normalized unique repositories encountered in input)
- repositories_processed: number (repositories for which individual checklist files were generated this run)
- repositories_skipped: number (append=true existing repos skipped)
- generated_checklist_paths: array of strings (paths to newly created repo checklist files)
- master_checklist_path: string (path to `./tasks/all_repository_checklist.md` if generated or updated)
- status: SUCCESS | FAIL (FAIL if any mandatory validation or file write error occurred)
- timestamp: string (ISO 8601 UTC, seconds precision) when JSON output written
- verification_errors: array of objects { type, target, detail } (empty if status=SUCCESS)
- mode: string ("reset" when append=false, "append" when append=true)



## Implementation Notes:
1. **THIS IS SCRIPTABLE**: Generate a Python script to execute this task
2. URL Parsing: Extract friendly repo names from URLs (e.g., last segment after final /)
3. Dynamic Task Extraction: Parse .github\prompts\repo_tasks_list.prompt.md to get task list and variables section
4. Contract Compliance: Always save JSON output file with all fields regardless of success/failure
   Core reproducibility requirements have been embedded inline in Steps 2–6. Consolidated summary:
   - Normalization & sorting (Step 2) produce stable repo ordering.
   - Append mode preserves existing order; only sorted new entries appended (Step 3 & 4).
   - Master checklist formatting rules prevent whitespace drift (Step 4).
   - Individual checklist deterministic content + directive uniqueness enforced (Step 5).
   - Base repo variable population deterministic (Step 6) with single authoritative arrow-form block (no descriptive duplicates).
   - Consistency checks & key ordering enforced through the above steps (no separate step reference).
   - No randomness, locale neutrality, placeholder fidelity guaranteed through explicit rules.
   Following these embedded rules ensures repeat runs with identical inputs produce identical artifacts except for timestamp.
5. Markdown Format: Use `- [ ]` for unchecked, `- [x]` for checked checkboxes
6. Timestamp Format: Use ISO 8601 format (e.g., "2025-10-24T14:30:00")
7. Error Handling: If input file not found, set status=FAIL and return with empty results
8. Append Mode Logic: Compare normalized URLs (trim trailing slashes, case-insensitive), preserve existing entries, only create files for new repos



