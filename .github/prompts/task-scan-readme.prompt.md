---
temperature: 0.1
---

@task-scan-readme checklist_path={{checklist_path}}

# Task name: task-scan-readme

## Process Overview
1. Debug Entry Trace
2. Checklist Load & Variable Extraction
3. README Load
4. Prerequisites & Checklist Verification
5. Structural Section Identification
6. Follow Referenced Markdown Files
7. Command Extraction
8. Command Categorization
9. Command Cleaning
10. Structured Output Assembly
11. Log to Decision Log
12. Result Tracking
13. Repo Checklist Update
14. Repo Variable Refresh
15. Verification (Post-Refresh)
16. Debug Exit Trace

## Prerequisites
- README content JSON produced by `@task-search-readme`
- Repository directory accessible
- tokens `{{commands_extracted}}` present in `## Repo Variables Available` section of repo checklist
- DEBUG environment variable optional for verbose tracing

## Description
This task analyzes the README content (from task-search-readme output) using structural reasoning to identify and extract setup/build environment commands. This task requires AI structural reasoning and **cannot** be scripted.

## Execution Policy
**CRITICAL**: DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK.  
This task MUST be performed using **direct tool calls** and **structural reasoning**:

1. Use `read_file` tool to load the README content from task-search-readme output JSON.
2. Use structural reasoning to parse and analyze README structure.
3. Use AI reasoning to identify setup sections and extract commands.
4. Use `create_file` tool to save the parsed command list to JSON output.
5. Use `replace_string_in_file` tool to update progress/results files.

**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
**NEVER use regex or simple text parsing – use structural reasoning.**  
The AI agent must analyze the README content intelligently to understand context and extract meaningful setup commands.

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
**DEBUG Entry Trace:**  
If DEBUG=1, print:  
`[debug][task-scan-readme] START checklist_path='{{checklist_path}}'`

### Step 2 (MANDATORY)
**Checklist Load & Variable Extraction:**
- Open the file at `{{checklist_path}}` (this is the authoritative repo checklist).
- Extract the following variable values ONLY from the `## Repo Variables Available` section lines:
   - `- {{repo_name}}` (value appears after `→`)
   - `- {{repo_directory}}` (value after `→`)
   - `- {{readme_content_path}}` (value after `→`) — produced by @task-search-readme
- Do NOT infer or derive these values from filename; only trust the inline variable lines.
- If any of these lines are missing or the value segment after the arrow is empty, set `status=FAIL` and abort further steps after structured output.
- If an expected line lacks an arrow (`→`), treat the value as missing (FAIL).
- If DEBUG=1, print: `[debug][task-scan-readme] extracted repo_name='{{repo_name}}' repo_directory='{{repo_directory}}' readme_content_path='{{readme_content_path}}'`
- Immute base variables: NEVER modify `repo_name`, `repo_directory`, `repo_url`, or `readme_content_path` in this task.

### Step 3 (MANDATORY)
**README Load:**
- Use `read_file` to load the JSON at `readme_content_path` (extracted in Step 2).
- Parse and extract `readme_content` and `readme_filename` fields.
- If file missing or unreadable, set `status=SKIPPED` (if produced by previous task but now absent) or `status=FAIL` (unexpected error) and proceed to output.
- If DEBUG=1, print: `[debug][task-scan-readme] loaded README from {{readme_content_path}}: {{char_count}} characters`

### Step 4 (MANDATORY)
**Prerequisites Check:**  
- If README was not found in task-search-readme (`readme_content` is null or empty), skip analysis.
- If DEBUG=1, print: `[debug][task-scan-readme] no README content available, skipping scan`
- Set status=SKIPPED and proceed to output.
- If README found, proceed with analysis.

**Pre-flight Checklist Verification:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  - `{{commands_extracted}}`
- If any token is missing or altered, restore it prior to continuing.

### Step 5 (MANDATORY)
**Structural Reasoning – Section Identification:**  
- **YOU MUST ACTUALLY READ THE README CONTENT LOADED IN STEP 2**
- Analyze the actual text of the README using AI reasoning capabilities.
- Use AI structural reasoning to identify sections in the README that contain setup/build instructions.
- Look for section headings (Markdown headers, bold text, all-caps lines) containing keywords:
  - "Prerequisites"
  - "Before you build"
  - "Setup"
  - "Local dev" / "Local development"
  - "Getting Started"
  - "Installation"
  - "Requirements"
  - "Environment setup"
  - "Dependencies"
  - "Building" / "How to build"
- If DEBUG=1, print for each identified section: `[debug][task-scan-readme] found setup section: {{section_heading}}`
- Consider context: sections near the beginning of README are more likely to be setup instructions.
- Ignore sections like "Contributing", "License", "FAQ", "Troubleshooting" unless they explicitly mention setup.

### Step 6 (MANDATORY)
**Follow Referenced Markdown Files:**  
- **CRITICAL REQUIREMENT:** If README references other .md files, you MUST ALWAYS follow them.
- **THIS IS NOT OPTIONAL – This step is MANDATORY for all README files.**
- Use AI reasoning to identify ALL references to other markdown files:
   - Markdown link examples: Getting Started (getting_started.md), Setup Guide (docs/setup.md)
  - Plain text references: "See setup.md for instructions", "Refer to INSTALL.md", "check getting_started.md"
   - Wiki/style link examples: [[Installation]] or external wiki reference (link-to-wiki) (external links may not be locally accessible)
  - Bare filenames: "getting_started.md guide", "See BUILDING.md"
- **MANDATORY** patterns indicating setup-related markdown files to ALWAYS follow:
  - Filenames: setup.md, install.md, getting_started.md, getting_started_*.md, prerequisites.md, building.md, development.md, running_*.md, BUILDING.md, INSTALL.md, SETUP.md
  - Link text containing: "setup", "installation", "getting started", "prerequisites", "building", "development", "local dev", "running", "how to"
- If DEBUG=1, print: `[debug][task-scan-readme] found reference to file: {{filename}}`

**For each referenced markdown file (MANDATORY – NOT OPTIONAL):**
a. **Determine File Path (MANDATORY):**
   - If relative path (e.g., `setup.md`, `docs/setup.md`, `getting_started.md`): construct absolute path using repo_directory.
   - If URL to external wiki (e.g., `https://...`): log as external reference, cannot read locally.
   - Normalize path: handle `./`, `../`, and path separators correctly.
   - If DEBUG=1, print: `[debug][task-scan-readme] resolving path: {{relative_path}} -> {{absolute_path}}`
b. **Check File Existence (MANDATORY):**
   - Use list_dir or read_file to verify the markdown file exists in the repository.
   - Common locations to check: repo root, docs/, documentation/, .github/, wiki/
   - **MANDATORY: Try common variations** if exact path not found:
     - Uppercase: SETUP.MD, README.MD
     - Common directories: ./docs/{{filename}}, ./documentation/{{filename}}, ./{{filename}}
   - If file not found after all attempts, print: `[debug][task-scan-readme] referenced file not found: {{filename}} (tried: {{paths_attempted}})`
   - If file found, MUST proceed to read it (this is MANDATORY).
c. **Read Referenced File (MANDATORY):**
   - **MANDATORY**: Use read_file tool to load the content of the referenced markdown file.
   - If DEBUG=1, print: `[debug][task-scan-readme] reading referenced file: {{filename}}, {{char_count}} characters`
   - Treat this as additional README content for analysis (REQUIRED, not optional).
d. **Analyze Referenced Content (MANDATORY):**
   - **MANDATORY**: Apply the same structural reasoning from steps 4–7 to this markdown file.
   - Look for setup sections, extract commands, categorize them.
   - Include file source in command metadata: `source_file: "getting_started.md"`
   - If DEBUG=1, print: `[debug][task-scan-readme] analyzing referenced file: {{filename}}`
e. **Merge Results (MANDATORY):**
   - **MANDATORY**: Add identified sections from referenced file to sections_identified array.
   - **MANDATORY**: Add extracted commands to commands_extracted array.
   - Preserve source file information for traceability.
   - If DEBUG=1, print: `[debug][task-scan-readme] merged {{section_count}} sections, {{command_count}} commands from {{filename}}`
f. **Prevent Infinite Loops:**
   - Track which markdown files have been processed (max depth: 3 levels for following references within references).
   - Do not follow references from already-processed files beyond max depth.
   - Limit total referenced files to 10 to avoid excessive processing.
   - If DEBUG=1, print: `[debug][task-scan-readme] processed {{file_count}} referenced files, depth={{current_depth}}`
g. **Prioritization (Process in this order):**
   - PRIORITY 1: Files with "setup", "install", "getting_started", "getting-started" in name (ALWAYS process these).
   - PRIORITY 2: Files linked from "Prerequisites", "Getting Started", "Installation", "Setup", "Building" sections.
   - PRIORITY 3: Files in docs/ or documentation/ directories.
   - PRIORITY 4: Other referenced .md files.
   - Files with "running_", "testing_" in names are also PRIORITY 1 as they often contain build/setup commands.

**IMPORTANT:**  
The analysis MUST NOT stop when it finds external links. When README only contains links to external documentation (wiki, .md files), this step becomes the PRIMARY way to extract commands. An analysis that reports "found only links to external files" but doesn't follow local .md files is INCOMPLETE.

Example behavior for README with only external references:
- README contains: "See getting_started.md for setup"
- CORRECT: Read getting_started.md, extract commands from it, report commands in output
- INCORRECT: Report "README contains only links" and stop without reading getting_started.md

### Step 7 (MANDATORY)
**Structural Reasoning – Command Extraction:**  
- **YOU MUST ANALYZE THE ACTUAL README CONTENT, NOT JUST CREATE EMPTY OUTPUT**
- Within identified setup sections, use structural reasoning to extract commands:
  a. **Code Blocks:**
     - Fenced code blocks with ``` or ~~~
     - Indented code blocks (4 spaces or 1 tab)
     - Consider language hints: ```bash, ```sh, ```powershell, ```cmd, ```shell
     - If DEBUG=1, print: `[debug][task-scan-readme] found code block in section {{section_name}}, {{line_count}} lines`
  b. **Inline Code:**
     - Text wrapped in single backticks: `command here`
     - Only extract if it looks like a shell command (starts with shell prompt, contains executable name)
     - If DEBUG=1, print: `[debug][task-scan-readme] found inline command: {{command}}`
  c. **Ordered/Unordered Lists:**
     - List items that start with shell prompts: `$ command`, `> command`, `C:\> command`
     - List items containing inline code that are commands
     - If DEBUG=1, print: `[debug][task-scan-readme] found command in list item`
  d. **Command Characteristics (use reasoning to identify):**
     - Starts with executable name (npm, pip, dotnet, git, node, python, etc.)
     - Contains shell operators: &&, \\, >, <
     - Environment variable syntax: $VAR, %VAR%, ${VAR}
     - Common patterns: `cd`, `mkdir`, `install`, `restore`, `init`, `config`
  e. **Context Understanding:**
     - Commands preceded by "Run:", "Execute:", "Type:", "Install:" are likely setup commands
     - Commands in numbered steps are likely sequential setup instructions
     - Commands with explanatory text like "First, install..." are setup commands
     - Distinguish between example code (showing API usage) vs. setup commands (preparing environment)
   f. **Explicit Exclusion Policy (MANDATORY):**
       - DO NOT include repository acquisition commands (e.g. any form of `git clone ...`) in `commands_extracted`.
       - Rationale: cloning is a one-time repository fetch, not an environment setup operation.
       - If such commands appear, ignore them (do not count toward total_commands) and do not list them in the checklist summary.

### Step 8 (MANDATORY)
**Command Categorization:**  
For each extracted command, use structural reasoning to categorize by purpose:
- **package_install**: npm install, pip install, dotnet restore, nuget restore, yarn install
- **version_check**: node --version, python --version, git --version, dotnet --version
- **config**: git config, npm config, environment variable settings
- **directory**: cd, mkdir, directory navigation
- **environment_setup**: source, export, setx, setting up paths
- **build_tool**: msbuild, dotnet build, npm run (note: may be marked unsafe later)
- **other**: anything else that looks like a setup command

If DEBUG=1, print for each command: `[debug][task-scan-readme] extracted command [{{category}}]: {{command}}`

### Step 9 (MANDATORY)
**Command Cleaning:**  
Remove shell prompts: $, >, C:\>, PS>, #
Remove line continuations: backslash (\) or caret (^)
Remove comments: truncate at first occurrence of one of: # // REM
Trim whitespace
Handle multi-line commands (join with proper syntax)
 Apply exclusion filters (MANDATORY): discard any cleaned command whose original form began with or contains a repository clone invocation (e.g. starts with `git clone`, `gh repo clone`). These MUST NOT appear in the final JSON.
If DEBUG=1, print: `[debug][task-scan-readme] cleaned {{original_count}} commands to {{cleaned_count}} valid commands`

### Step 10 (MANDATORY)
Structured Output Assembly:
Generate JSON only (no verification in this step) at `output/{{repo_name}}_task3_scan-readme.json`. The `verification_errors` array is emitted empty here and populated in Step 15.

Structured Output JSON (output/{{repo_name}}_task3_scan-readme.json) MUST include:

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for:
   - `- {{repo_name}}` (non-empty if not SKIPPED)
   - `- {{repo_directory}}` (non-empty if not SKIPPED)
   - `- {{readme_content_path}}` (non-empty if status not SKIPPED)
3. `- {{commands_extracted}}` line exists (may be blank pre-refresh).
4. If status=SUCCESS:
   - `total_commands > 0`.
   - `total_commands == len(commands_extracted array)`.
5. If status=NONE: `total_commands == 0` and README existed.
6. If status=SKIPPED: README missing or unreadable (char_count=0 or null) and commands_extracted array empty.
7. No duplicate variable lines for repo_name, repo_directory, commands_extracted.
8. Task directive line `@task-scan-readme` appears exactly once.
9. Arrow formatting: each variable line uses `- {{token}} → value`.
10. Base variables (`repo_name`, `repo_directory`, `readme_content_path`) unchanged (compare loaded vs post-verification; if changed → violation).

Record each failure as: `{ "type": "<code>", "target": "<file|repo>", "detail": "<description>" }` in `verification_errors`.
If DEBUG=1 emit for each: `[debug][task-scan-readme][verification] FAIL code=<code> detail="<description>"`.

Structured Output JSON (output/{{repo_name}}_task3_scan-readme.json) MUST include:
- repo_directory
- repo_name
- readme_filename
- sections_identified (array)
- commands_extracted (array)
- referenced_files_processed (array)
- total_commands
- status (SUCCESS|NONE|SKIPPED|FAIL)
- timestamp (ISO 8601 UTC seconds)
- verification_errors (array, empty if none)
- debug (optional array when DEBUG=1)

### Step 11 (MANDATORY)
**Log to Decision Log:**  
Call @task-update-decision-log to log task execution:
```
@task-update-decision-log
timestamp="{{timestamp}}"
repo_name="{{repo_name}}"
solution_name=""
task="task-scan-readme"
message="{{message}}"
status="{{status}}"
```
- Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
- The solution_name is blank since this is a repository-level task
- Message format:
  - If sections found: "Found {{section_count}} setup sections across {{file_count}} files"
  - If no sections found but README exists: "No setup sections found in README"
  - If README not found (status=SKIPPED): "README not found – scan skipped"
  - If scan failed (status=FAIL): "Scan failed: {{error_reason}}"

### Step 12 (MANDATORY)
**Result Tracking:**  
Append the result to:
- results/repo-results.csv (CSV row)
- Row format: timestamp, repo_name, task-scan-readme, status, symbol (✓ or ✗)
   (CSV row presence and formatting are verified ONLY in Step 15; do not perform early verification here.)

### Step 13 (MANDATORY)
**Repo Checklist Update:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Set `[x]` only on the `@task-scan-readme` entry for the current repository
- Do not modify other checklist items or other repositories' files

### Step 14 (MANDATORY)
**Repo Variable Refresh (INLINE ONLY):**
- Open `tasks/{{repo_name}}_repo_checklist.md`.
- Locate the line beginning with `- {{commands_extracted}}`.
- Replace ONLY the text after `→` with:
   * If commands extracted: comma-separated list of the first up to 10 command names (truncate with `...` if more).
   * If no commands and README existed: NONE
   * If README missing and status=SKIPPED: SKIPPED
   * If failure: FAIL
- If the line lacks an arrow, append one then the value: `- {{commands_extracted}} → <value>`.
- Preserve `- {{commands_extracted}}` prefix verbatim.
**Inline Variable Policy:** Never create a new section; update in place only.

### Step 15 (MANDATORY)
Verification (Post-Refresh):
Perform verification AFTER Steps 13–14 (checklist update and variable refresh). Load the JSON produced in Step 10 and current checklist state.

Verification checklist:
1. Checklist file exists at `{{checklist_path}}`.
2. Variable lines present exactly once for required tokens: repo_name, repo_directory, readme_content_path, commands_extracted.
3. Arrow formatting correct (single `→`).
4. No duplicate variable lines among repo_name, repo_directory, commands_extracted.
5. Task directive `@task-scan-readme` appears exactly once.
6. JSON required keys present: repo_name, repo_directory, sections_identified, commands_extracted, total_commands, status, timestamp.
7. Status-specific rules:
   - SUCCESS: total_commands > 0 AND len(commands_extracted array) == total_commands.
   - NONE: total_commands == 0 AND README existed (readme_content_path valid) AND commands_extracted array empty.
   - SKIPPED: README missing/unreadable; commands_extracted empty; total_commands == 0.
8. Consistency: safe that checklist `- {{commands_extracted}}` summary (if populated) reflects SUCCESS/NONE/SKIPPED semantics (FAIL not allowed unless status=FAIL).
9. Base variables unchanged from Step 2 extraction.
10. Results CSV row present and correctly formatted for this task execution (pattern: `{{timestamp}},{{repo_name}},task-scan-readme,{{status}},✓|✗`).

Violations: record objects `{ "type": "<code>", "target": "<file|variable|json>", "detail": "<description>" }`.
Suggested codes: file_missing, variable_missing, variable_empty, duplicate_variable, arrow_format_error, json_missing_key, count_mismatch, status_inconsistent, base_variable_modified, results_row_missing.

Status Adjustment:
- Begin with existing JSON status. If status in {SUCCESS, NONE} and violations exist → set status=FAIL. If SKIPPED and violations unrelated to README absence appear, may set status=FAIL.

Update JSON: overwrite verification_errors (sorted by type then target) and updated status if changed. Preserve timestamp.

**DEBUG Exit Trace:**  
If DEBUG=1, print:  
`[debug][task-scan-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} commands_extracted={{total_commands}}]`

## Output Contract
- repo_directory: string (absolute path) (extracted from checklist)
- repo_name: string (extracted from checklist)
- readme_filename: string or null (from task-search-readme output JSON)
- sections_identified: array of objects (section_heading, line_number, keywords_matched, source_file)
- commands_extracted: array of objects (command, category, source_section, source_type, source_file, line_number, context)
- referenced_files_processed: array of strings (paths to markdown files that were read and analyzed)
- total_commands: number (count of commands_extracted)
- status: SUCCESS, NONE, SKIPPED, FAIL
- timestamp: string (ISO 8601)

## Implementation Notes (conceptual)
1. **THIS IS NOT A SCRIPT**: Use direct tool calls – read_file, run_in_terminal, create_file, replace_string_in_file, list_dir
2. **Structural Reasoning Required**: AI must understand README structure, not just pattern matching
3. **Follow Documentation References**: When README references other .md files for setup (e.g., "see setup.md"), read and analyze those files too
4. **Context Matters**: Use surrounding text to determine if something is a setup command vs example code
5. **Language Awareness**: Understand different markdown dialects, code fence syntax, list formats
6. **False Positive Prevention**: Don't extract every code snippet – use reasoning to identify actual setup commands
7. **Multi-line Handling**: Commands split across lines (with \ or ^) should be joined properly
8. **Empty Results**: If no setup commands found after analyzing README AND all referenced local .md files, return empty arrays and status=NONE (scan completed, but no commands found)
9. **Error Handling**: If README content is malformed or cannot be parsed, set status=FAIL and log reason
10. **Next Task Dependency**: The output of this task (commands_extracted array) is input to task-execute-readme
11. **Parameter Usage**: The readme_content_path parameter specifies where to load README content – do not hardcode paths
12. **Referenced Files Tracking**: Store list of processed referenced markdown files (avoid duplicates, depth <= 3).

## Error Handling
- For any step that fails:
   - Log the error with details (exception type, message, partial context)
   - If a critical step fails (cannot read primary README, cannot parse commands), set status=FAIL and abort remaining steps
   - Do not update checklist or results CSV on critical failure
   - Non-critical failures (one referenced file missing) should be logged; continue processing others

## Consistency Checks
- After creating output file `output/{{repo_name}}_task3_scan-readme.json`, verify it exists and contains keys: `repo_name`, `sections_identified`, `commands_extracted`, `status`.
- After updating `tasks/{{repo_name}}_repo_checklist.md`, verify the checkbox for `@task-scan-readme` is set only if status is SUCCESS/NONE/SKIPPED (not FAIL) and variable `{{commands_extracted}}` token remains present.
- If any verification fails, log an error and abort subsequent updates.

## Cross-References
- Always reference and use the freshest values collected earlier in this task (never reuse stale interim data).
- Variables for this task workflows:
   - repo_directory (absolute path)
   - repo_name (repository identifier)
   - readme_content_path (path to search-readme JSON)
   - readme_filename (extracted from search-readme output)
   - sections_identified (array of detected setup sections)
   - commands_extracted (array of command metadata objects)
   - referenced_files_processed (list of additional markdown files analyzed)
   - total_commands (count of commands_extracted)
   - status (SUCCESS | NONE | SKIPPED | FAIL)
   - timestamp (ISO 8601)
- Ensure any checklist variable updates mirror the final JSON output exactly.