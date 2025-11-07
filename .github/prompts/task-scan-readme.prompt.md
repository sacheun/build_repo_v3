---
temperature: 0.1
---

@task-scan-readme checklist_path={{checklist_path}}

# Task name: task-scan-readme


## Description
This task analyzes the README content (from task-search-readme output) using structural reasoning to identify and extract setup/build environment commands. This task requires AI structural reasoning and **cannot** be scripted.

## Execution Policy
**⚠️ CRITICAL – THIS TASK IS NON-SCRIPTABLE ⚠️**  
This task MUST be performed using **direct tool calls** and **structural reasoning**:
*STRICT MODE ON**
- All steps are **MANDATORY**.

The AI agent must analyze the README content intelligently to understand context and extract meaningful setup commands.

## Instructions (Follow this Step by Step)

### Step 1 (MANDATORY)
**Checklist Load & Variable Extraction:**
- Open the file at `{{checklist_path}}` (this is the authoritative repo checklist).
- Extract the following variable values ONLY from the `## Repo Variables Available` section lines:
   - `- {{repo_name}}` (value appears after `→`)
   - `- {{repo_directory}}` (value after `→`)
   - `- {{readme_content_path}}` (value after `→`) — produced by @task-search-readme
- Do NOT infer or derive these values from filename; only trust the inline variable lines.
- If any of these lines are missing or the value segment after the arrow is empty, set `status=FAIL` and abort further steps after structured output.
- If an expected line lacks an arrow (`→`), treat the value as missing (FAIL).
- NEVER modify `repo_name`, `repo_directory`, `repo_url`, or `readme_content_path` in this task.

### Step 2 (MANDATORY)
**README Load:**
- Use `read_file` to load the JSON at `readme_content_path` (extracted in Step 2).
- Parse and extract `readme_content` and `readme_filename` fields.
- If file missing or unreadable, set `status=SKIPPED` (if produced by previous task but now absent) or `status=FAIL` (unexpected error) and proceed to output.


### Step 3 (MANDATORY)
**Prerequisites Check:**  
- If README was not found in task-search-readme (`readme_content` is null or empty), skip analysis.
- Set status=SKIPPED and proceed to output.
- If README found, proceed with analysis.

**Pre-flight Checklist Verification:**  
- Open `tasks/{{repo_name}}_repo_checklist.md`
- Confirm the `## Repo Variables Available` section contains the templated tokens below before making any changes:
  - `{{commands_extracted}}`
- If any token is missing or altered, restore it prior to continuing.

### Step 4 (MANDATORY)
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
- Consider context: sections near the beginning of README are more likely to be setup instructions.
- Ignore sections like "Contributing", "License", "FAQ", "Troubleshooting" unless they explicitly mention setup.

### Step 5 (MANDATORY)
**Follow Referenced Markdown Files:**  
- **CRITICAL REQUIREMENT:** If README references other .md files, you MUST ALWAYS follow them.
- Use AI reasoning to identify ALL references to other markdown files:
   - Markdown link examples: Getting Started (getting_started.md), Setup Guide (docs/setup.md)
  - Plain text references: "See setup.md for instructions", "Refer to INSTALL.md", "check getting_started.md"
   - Wiki/style link examples: [[Installation]] or external wiki reference (link-to-wiki) (external links may not be locally accessible)
  - Bare filenames: "getting_started.md guide", "See BUILDING.md"
- **MANDATORY** patterns indicating setup-related markdown files to ALWAYS follow:
  - Filenames: setup.md, install.md, getting_started.md, getting_started_*.md, prerequisites.md, building.md, development.md, running_*.md, BUILDING.md, INSTALL.md, SETUP.md
  - Link text containing: "setup", "installation", "getting started", "prerequisites", "building", "development", "local dev", "running", "how to"

**For each referenced markdown file (MANDATORY):**
a. **Determine File Path (MANDATORY):**
   - If relative path (e.g., `setup.md`, `docs/setup.md`, `getting_started.md`): construct absolute path using repo_directory.
   - If URL to external wiki (e.g., `https://...`): log as external reference, cannot read locally.
   - Normalize path: handle `./`, `../`, and path separators correctly.
b. **Check File Existence (MANDATORY):**
   - Use list_dir or read_file to verify the markdown file exists in the repository.
   - Common locations to check: repo root, docs/, documentation/, .github/, wiki/
   - **MANDATORY: Try common variations** if exact path not found:
     - Uppercase: SETUP.MD, README.MD
     - Common directories: ./docs/{{filename}}, ./documentation/{{filename}}, ./{{filename}}
   - If file found, MUST proceed to read it (this is MANDATORY).
c. **Read Referenced File (MANDATORY):**
   - **MANDATORY**: Use read_file tool to load the content of the referenced markdown file.
   - Treat this as additional README content for analysis (REQUIRED, not optional).
d. **Analyze Referenced Content (MANDATORY):**
   - Apply the same structural reasoning from steps 3–6 to this markdown file.
   - Look for setup sections, extract commands, categorize them.
   - Include file source in command metadata: `source_file: "getting_started.md"`
e. **Merge Results (MANDATORY):**
   - Add identified sections from referenced file to sections_identified array.
   - Add extracted commands to commands_extracted array.
   - Preserve source file information for traceability.
f. **Prevent Infinite Loops:**
   - Track which markdown files have been processed (max depth: 3 levels for following references within references).
   - Do not follow references from already-processed files beyond max depth.
   - Limit total referenced files to 10 to avoid excessive processing.
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

### Step 6 (MANDATORY)
**Structural Reasoning – Command Extraction:**  
- **YOU MUST ANALYZE THE ACTUAL README CONTENT, NOT JUST CREATE EMPTY OUTPUT**
- Within identified setup sections, use structural reasoning to extract commands:
  a. **Code Blocks:**
     - Fenced code blocks with ``` or ~~~
     - Indented code blocks (4 spaces or 1 tab)
     - Consider language hints: ```bash, ```sh, ```powershell, ```cmd, ```shell
  b. **Inline Code:**
     - Text wrapped in single backticks: `command here`
     - Only extract if it looks like a shell command (starts with shell prompt, contains executable name)
  c. **Ordered/Unordered Lists:**
     - List items that start with shell prompts: `$ command`, `> command`, `C:\> command`
     - List items containing inline code that are commands
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

### Step 7 (MANDATORY)
**Command Categorization:**  
For each extracted command, use structural reasoning to categorize by purpose:
- **package_install**: npm install, pip install, dotnet restore, nuget restore, yarn install
- **version_check**: node --version, python --version, git --version, dotnet --version
- **config**: git config, npm config, environment variable settings
- **directory**: cd, mkdir, directory navigation
- **environment_setup**: source, export, setx, setting up paths
- **build_tool**: msbuild, dotnet build, npm run (note: may be marked unsafe later)
- **other**: anything else that looks like a setup command


### Step 8 (MANDATORY)
**Command Cleaning:**  
Remove shell prompts: $, >, C:\>, PS>, #
Remove line continuations: backslash (\) or caret (^)
Remove comments: truncate at first occurrence of one of: # // REM
Trim whitespace
Handle multi-line commands (join with proper syntax)
 Apply exclusion filters (MANDATORY): discard any cleaned command whose original form began with or contains a repository clone invocation (e.g. starts with `git clone`, `gh repo clone`). These MUST NOT appear in the final JSON.

### Step 9 (MANDATORY)
Structured Output Assembly:
Generate JSON only (no verification in this step) at `output/{{repo_name}}_task3_scan-readme.json`. 

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
- debug (optional array when DEBUG=1)

### Step 10 (MANDATORY)
**Repo Checklist Update & Variable Refresh (Single Operation):**
- Open `tasks/{{repo_name}}_repo_checklist.md` (at `{{checklist_path}}`).
- Set `[x]` only on the `@task-scan-readme` entry for the current repository (do not alter any other task markers).
- Locate the existing variable line beginning with `- {{commands_extracted}}`.
   - If missing, restore the token exactly as: `- {{commands_extracted}} →` before assigning a value.
- Replace ONLY the text after `→` with:
   * If one or more commands extracted (status=SUCCESS): comma-separated list of up to the first 10 command strings (truncate with `...` if more).
   * If no commands and README existed (status=NONE): `NONE`
   * If README missing/unreadable (status=SKIPPED): `SKIPPED`
   * If status=FAIL: `FAIL`
- If the line lacks an arrow, append one then the value: `- {{commands_extracted}} → <value>`.
- Preserve the exact prefix `- {{commands_extracted}}` (no casing or spacing changes).
- Do not modify base variables (`repo_name`, `repo_directory`, `readme_content_path`).

### End of Steps

## Output Contract
- `repo_directory`: string (absolute path) (extracted from checklist)
- `repo_name`: string (extracted from checklist)
- `readme_filename`: string or null (from task-search-readme output JSON)
- `sections_identified`: array of objects (section_heading, line_number, keywords_matched, source_file)
- `commands_extracted`: array of objects (command, category, source_section, source_type, source_file, line_number, context)
- `referenced_files_processed`: array of strings (paths to markdown files that were read and analyzed)
- `total_commands`: number (count of commands_extracted)
- `status`: SUCCESS, NONE, SKIPPED, FAIL
- `timestamp`: string (ISO 8601)

## Implementation Notes (conceptual)
1. **THIS IS NOT A SCRIPT**: Use direct tool calls – read_file, run_in_terminal, create_file, replace_string_in_file, list_dir
2. **Structural Reasoning Required**: AI must understand README structure, not just pattern matching
3. **Follow Documentation References**: When README references other .md files for setup (e.g., "see setup.md"), read and analyze those files too
4. **Context Matters**: Use surrounding text to determine if something is a setup command vs example code
5. **Language Awareness**: Understand different markdown dialects, code fence syntax, list formats
6. **False Positive Prevention**: Don't extract every code snippet – use reasoning to identify actual setup commands
7. **Empty Results**: If no setup commands found after analyzing README AND all referenced local .md files, return empty arrays and status=NONE (scan completed, but no commands found)
8. **Referenced Files Tracking**: Store list of processed referenced markdown files (avoid duplicates, depth <= 3).
