@task-scan-readme repo_directory={{repo_directory}} repo_name={{repo_name}} readme_content_path={{readme_content_path}}

Task name: task-scan-readme

Description:
This task analyzes the README content (from task-search-readme output) using structural reasoning to identify and extract setup/build environment commands. This task requires AI structural reasoning and CANNOT be scripted.

** CRITICAL ** DO NOT GENERATE OR EXECUTE A SCRIPT FOR THIS TASK.This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:

This task MUST be performed using DIRECT TOOL CALLS and STRUCTURAL REASONING:
1. Use read_file tool to load the README content from task-search-readme output JSON
2. Use structural reasoning to parse and analyze README structure
3. Use AI reasoning to identify setup sections and extract commands
4. Use create_file tool to save the parsed command list to JSON output
5. Use replace_string_in_file tool to update progress/results files

** NEVER create a Python/PowerShell/Bash script for this task **
** NEVER use regex or simple text parsing - use structural reasoning **

The AI agent must analyze the README content intelligently to understand context and extract meaningful setup commands.

Behavior:
0. DEBUG Entry Trace: If you need to output debug messages, use run_in_terminal with echo/Write-Host commands:
   "[debug][task-scan-readme] START repo_directory='{{repo_directory}}' readme_content_path='{{readme_content_path}}'"

1. Input Parameters: 
   - repo_directory: absolute path to repository root
   - repo_name: repository name
   - readme_content_path: path to the JSON file containing README content (from task-search-readme output)
     Example: "output/{repo_name}_task2_search-readme.json"

2. **CRITICAL: Load and Read README Content**:
   - MUST use read_file tool to load the file specified in readme_content_path parameter
   - MUST extract the "readme_content" field from the JSON
   - If DEBUG=1, print: `[debug][task-scan-readme] loaded README from {{readme_content_path}}: {{char_count}} characters`
   - This is MANDATORY - you cannot analyze what you haven't read
   - The README content is the INPUT to your structural reasoning analysis

3. Prerequisites Check:
   - If README was not found in task-search-readme (readme_content is null or empty), skip analysis
   - If DEBUG=1, print: `[debug][task-scan-readme] no README content available, skipping scan`
   - Set status=SKIPPED and proceed to output
   - If README found, proceed with analysis

4. **Structural Reasoning - Section Identification**:
   - ** YOU MUST ACTUALLY READ THE README CONTENT LOADED IN STEP 2 **
   - Analyze the actual text of the README using AI reasoning capabilities
   - Use AI structural reasoning to identify sections in the README that contain setup/build instructions
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
   - Consider context: sections near the beginning of README are more likely to be setup instructions
   - Ignore sections like "Contributing", "License", "FAQ", "Troubleshooting" unless they explicitly mention setup

4a. ** MANDATORY: Follow Referenced Markdown Files **:
   - ** CRITICAL REQUIREMENT: If README references other .md files, you MUST ALWAYS follow them **
   - ** THIS IS NOT OPTIONAL - This step is MANDATORY for all README files **
   - Use AI reasoning to identify ALL references to other markdown files:
     - Markdown links: `[Getting Started](getting_started.md)`, `[Setup Guide](docs/setup.md)`
     - Plain text references: "See setup.md for instructions", "Refer to INSTALL.md", "check getting_started.md"
     - Wiki links: `[[Installation]]`, `[check wiki](link-to-wiki)` (note: external wiki links may not be locally accessible)
     - Bare filenames: "getting_started.md guide", "See BUILDING.md"
   - ** MANDATORY ** Patterns indicating setup-related markdown files to ALWAYS follow:
     - Filenames: setup.md, install.md, getting_started.md, getting_started_*.md, prerequisites.md, building.md, development.md, running_*.md, BUILDING.md, INSTALL.md, SETUP.md
     - Link text containing: "setup", "installation", "getting started", "prerequisites", "building", "development", "local dev", "running", "how to"
   - If DEBUG=1, print: `[debug][task-scan-readme] found reference to file: {{filename}}`
   
   For each referenced markdown file (THIS IS MANDATORY - NOT OPTIONAL):
   
   a. **Determine File Path** (MANDATORY):
      - If relative path (e.g., `setup.md`, `docs/setup.md`, `getting_started.md`): construct absolute path using repo_directory
      - If URL to external wiki (e.g., `https://...`): log as external reference, cannot read locally
      - Normalize path: handle `./`, `../`, and path separators correctly
      - If DEBUG=1, print: `[debug][task-scan-readme] resolving path: {{relative_path}} -> {{absolute_path}}`
   
   b. **Check File Existence** (MANDATORY):
      - Use list_dir or read_file to verify the markdown file exists in the repository
      - Common locations to check: repo root, docs/, documentation/, .github/, wiki/
      - ** MANDATORY: Try common variations ** if exact path not found:
        - Uppercase: SETUP.MD, README.MD
        - Common directories: ./docs/{{filename}}, ./documentation/{{filename}}, ./{{filename}}
      - If file not found after all attempts, log: `[debug][task-scan-readme] referenced file not found: {{filename}} (tried: {{paths_attempted}})`
      - If file found, MUST proceed to read it (this is MANDATORY)
   
   c. **Read Referenced File** (MANDATORY):
      - ** MANDATORY ** Use read_file tool to load the content of the referenced markdown file
      - If DEBUG=1, print: `[debug][task-scan-readme] reading referenced file: {{filename}}, {{char_count}} characters`
      - Treat this as additional README content for analysis (REQUIRED, not optional)
   
   d. **Analyze Referenced Content** (MANDATORY):
      - ** MANDATORY ** Apply the same structural reasoning from steps 4-7 to this markdown file
      - Look for setup sections, extract commands, categorize them
      - Include file source in command metadata: `source_file: "getting_started.md"`
      - If DEBUG=1, print: `[debug][task-scan-readme] analyzing referenced file: {{filename}}`
   
   e. **Merge Results** (MANDATORY):
      - ** MANDATORY ** Add identified sections from referenced file to sections_identified array
      - ** MANDATORY ** Add extracted commands to commands_extracted array
      - Preserve source file information for traceability
      - If DEBUG=1, print: `[debug][task-scan-readme] merged {{section_count}} sections, {{command_count}} commands from {{filename}}`
   
   f. **Prevent Infinite Loops**:
      - Track which markdown files have been processed (max depth: 3 levels for following references within references)
      - Do not follow references from already-processed files beyond max depth
      - Limit total referenced files to 10 to avoid excessive processing
      - If DEBUG=1, print: `[debug][task-scan-readme] processed {{file_count}} referenced files, depth={{current_depth}}`
   
   g. **Prioritization** (Process in this order):
      - PRIORITY 1: Files with "setup", "install", "getting_started", "getting-started" in name (ALWAYS process these)
      - PRIORITY 2: Files linked from "Prerequisites", "Getting Started", "Installation", "Setup", "Building" sections
      - PRIORITY 3: Files in docs/ or documentation/ directories
      - PRIORITY 4: Other referenced .md files
      - Files with "running_", "testing_" in names are also PRIORITY 1 as they often contain build/setup commands
   
   ** IMPORTANT **: The analysis MUST NOT stop when it finds external links. When README only contains links to external documentation (wiki, .md files), this step becomes the PRIMARY way to extract commands. An analysis that reports "found only links to external files" but doesn't follow local .md files is INCOMPLETE.
   
   Example behavior for README with only external references:
   - README contains: "See [getting_started.md](getting_started.md) for setup"
   - CORRECT: Read getting_started.md, extract commands from it, report commands in output
   - INCORRECT: Report "README contains only links" and stop without reading getting_started.md

5. **Structural Reasoning - Command Extraction**:
   - ** YOU MUST ANALYZE THE ACTUAL README CONTENT, NOT JUST CREATE EMPTY OUTPUT **
   - Within identified setup sections, use structural reasoning to extract commands:
   
   a. **Code Blocks**: 
      - Fenced code blocks with ``` or ~~~
      - Indented code blocks (4 spaces or 1 tab)
      - Consider language hints: ```bash, ```sh, ```powershell, ```cmd, ```shell
      - If DEBUG=1, print: `[debug][task-scan-readme] found code block in section {{section_name}}, {{line_count}} lines`
   
   b. **Inline Code**:
      - Text wrapped in single backticks: `command here`
      - Only extract if it looks like a shell command (starts with shell prompt, contains executable name)
      - If DEBUG=1, print: `[debug][task-scan-readme] found inline command: {{command}}`
   
   c. **Ordered/Unordered Lists**:
      - List items that start with shell prompts: `$ command`, `> command`, `C:\> command`
      - List items containing inline code that are commands
      - If DEBUG=1, print: `[debug][task-scan-readme] found command in list item`
   
   d. **Command Characteristics** (use reasoning to identify):
      - Starts with executable name (npm, pip, dotnet, git, node, python, etc.)
      - Contains shell operators: &&, ||, |, >, <
      - Environment variable syntax: $VAR, %VAR%, ${VAR}
      - Common patterns: `cd`, `mkdir`, `install`, `restore`, `init`, `config`
   
   e. **Context Understanding**:
      - Commands preceded by "Run:", "Execute:", "Type:", "Install:" are likely setup commands
      - Commands in numbered steps are likely sequential setup instructions
      - Commands with explanatory text like "First, install..." are setup commands
      - Distinguish between example code (showing API usage) vs. setup commands (preparing environment)

6. **Command Categorization**:
   For each extracted command, use structural reasoning to categorize by purpose:
   - **package_install**: npm install, pip install, dotnet restore, nuget restore, yarn install
   - **version_check**: node --version, python --version, git --version, dotnet --version
   - **config**: git config, npm config, environment variable settings
   - **directory**: cd, mkdir, directory navigation
   - **environment_setup**: source, export, setx, setting up paths
   - **build_tool**: msbuild, dotnet build, npm run (note: may be marked unsafe later)
   - **other**: anything else that looks like a setup command
   
   If DEBUG=1, print for each command: `[debug][task-scan-readme] extracted command [{{category}}]: {{command}}`

7. **Command Cleaning**:
   - Remove shell prompts: `$`, `>`, `C:\>`, `PS>`, `#`
   - Remove line continuations: `\`, `^`
   - Remove comments: everything after `#` or `//` or `REM`
   - Trim whitespace
   - Handle multi-line commands (join with proper syntax)
   - If DEBUG=1, print: `[debug][task-scan-readme] cleaned {{original_count}} commands to {{cleaned_count}} valid commands`

8. Structured Output: Save JSON object to output/{repo_name}_task3_scan-readme.json with:
   - repo_directory: echoed from input
   - repo_name: echoed from input
   - readme_filename: from task-search-readme output
   - sections_identified: array of {section_heading, line_number, keywords_matched}
   - commands_extracted: array of objects with:
     - command: cleaned command string
     - category: categorization (package_install, version_check, etc.)
     - source_section: which section it came from
     - source_type: code_block, inline_code, list_item
     - line_number: approximate line in README
     - context: surrounding text that helps understand the command
   - total_commands: count of extracted commands
   - status: SUCCESS if commands extracted, NONE if no commands found, SKIPPED if no README, FAIL if error
   - timestamp: ISO 8601 format datetime

8a. Log to Decision Log:
   - Append to: results/decision-log.csv
   - For each section identified, append row with: "{{timestamp}},{{repo_name}},,task-scan-readme,Found setup section: {{section_heading}},SUCCESS"
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - The solution_name column (third column) is blank since this is a repository-level task
   - If no sections found but README exists, append: "{{timestamp}},{{repo_name}},,task-scan-readme,No setup sections found in README,NONE"
   - If README not found (status=SKIPPED), append: "{{timestamp}},{{repo_name}},,task-scan-readme,README not found - scan skipped,SKIPPED"
   - If scan failed (status=FAIL), append: "{{timestamp}},{{repo_name}},,task-scan-readme,Scan failed: {{error_reason}},FAIL"

9. Result Tracking:
   - Use create_file or replace_string_in_file to append the result to:
     - results/repo-results.md (Markdown table row)
     - results/repo-results.csv (CSV row)
   - Update the progress table:
     - In results/repo-progress.md, find the row for {{repo_name}} and column for "task-scan-readme"
     - Change [ ] to [x] to mark task as completed

10. DEBUG Exit Trace: Use run_in_terminal to emit:
   "[debug][task-scan-readme] EXIT repo_directory='{{repo_directory}}' status={{status}} commands_extracted={{total_commands}}"

Conditional Verbose Output (DEBUG):
- Purpose: Provide visibility into the structural reasoning process
- Activation: Only when DEBUG environment variable equals "1"
- Format: All messages start with [debug][task-scan-readme]
- Entry Message: "[debug][task-scan-readme] START repo_directory='<path>'" 
- Section Messages: "[debug][task-scan-readme] found setup section: <heading>"
- Code Block Messages: "[debug][task-scan-readme] found code block in section <name>, <N> lines"
- Inline Messages: "[debug][task-scan-readme] found inline command: <command>"
- Extraction Messages: "[debug][task-scan-readme] extracted command [<category>]: <command>"
- Cleaning Messages: "[debug][task-scan-readme] cleaned <N> commands to <M> valid commands"
- Exit Message: "[debug][task-scan-readme] EXIT repo_directory='<path>' status=<status> commands_extracted=<N>"

Output Contract:
- repo_directory: string (absolute path)
- repo_name: string
- readme_filename: string | null (from task-readme)
- sections_identified: array of objects (section_heading, line_number, keywords_matched, source_file)
- commands_extracted: array of objects (command, category, source_section, source_type, source_file, line_number, context)
- referenced_files_processed: array of strings (paths to markdown files that were read and analyzed)
- total_commands: number (count of commands_extracted)
- status: SUCCESS | NONE | SKIPPED | FAIL
- timestamp: string (ISO 8601)

Implementation Notes (conceptual):
1. **THIS IS NOT A SCRIPT**: Use direct tool calls - read_file, run_in_terminal, create_file, replace_string_in_file, list_dir
2. **Structural Reasoning Required**: AI must understand README structure, not just pattern matching
3. **Follow Documentation References**: When README references other .md files for setup (e.g., "see setup.md"), read and analyze those files too
4. **Context Matters**: Use surrounding text to determine if something is a setup command vs example code
5. **Language Awareness**: Understand different markdown dialects, code fence syntax, list formats
6. **False Positive Prevention**: Don't extract every code snippet - use reasoning to identify actual setup commands
7. **Multi-line Handling**: Commands split across lines (with \ or ^) should be joined properly
8. **Tool-Based Execution**: 
   - ** STEP 1: MANDATORY ** Use read_file to load the file specified in readme_content_path parameter
   - ** STEP 2: MANDATORY ** Extract readme_content field and READ IT with your AI reasoning
   - ** STEP 3: MANDATORY ** Use AI reasoning capabilities to analyze the actual README text structure
   - ** STEP 4: OPTIONAL ** If README references other .md files, use read_file to load and analyze them
   - ** STEP 5: ** Use create_file to save output/{repo_name}_task3_scan-readme.json
   - ** STEP 6: ** Use replace_string_in_file to update progress tables
   - ** DO NOT SKIP STEPS 1-3 ** - You cannot analyze a README you haven't read
   - ** STEP 4 IS NOW MANDATORY ** - If README references local .md files (not external URLs), you MUST read and analyze them using read_file
9. **Empty Results**: If no setup commands found after analyzing README AND all referenced local .md files, return empty arrays and status=NONE (scan completed, but no commands found)
10. **Error Handling**: If README content is malformed or cannot be parsed, set status=FAIL and log reason
11. **Next Task Dependency**: The output of this task (commands_extracted array) is input to task-execute-readme
12. **Parameter Usage**: The readme_content_path parameter specifies where to load README content - do not hardcode paths
13. **Referenced Files Tracking**: Store list of processed markdown files in referenced_files_processed array to show which files contributed to command extraction

Examples of Structural Reasoning:

**Example 1: Code Block with Language Hint**
```markdown
## Setup

Install dependencies:

```bash
npm install
npm run build
```
```
→ Identifies "Setup" as setup section
→ Extracts 2 commands from bash code block
→ Categories: package_install, build_tool

**Example 2: Inline Commands in List**
```markdown
### Prerequisites

1. Install Node.js: `node --version` should show v14+
2. Run `npm install` to get dependencies
```
→ Identifies "Prerequisites" as setup section
→ Extracts `node --version` (inline, version_check)
→ Extracts `npm install` (inline, package_install)

**Example 3: Multi-line Command**
```markdown
Restore packages:
```
msbuild MySolution.sln \
  /restore \
  /p:Configuration=Release
```
```
→ Joins lines: `msbuild MySolution.sln /restore /p:Configuration=Release`
→ Category: build_tool

**Example 4: Context-Based Filtering**
```markdown
## API Usage

Call the API:
```javascript
const result = api.doSomething();
```
```
→ Section "API Usage" - NOT a setup section
→ Language "javascript" + no shell commands → SKIP extraction
→ This is example code, not setup

**Example 5: Following Referenced Markdown Files**
```markdown
# MyProject

## Getting Started

For setup instructions, see [docs/setup.md](docs/setup.md).

For build instructions, check [BUILDING.md](BUILDING.md).
```

→ Identifies links to setup.md and BUILDING.md
→ Constructs paths: `{repo_directory}/docs/setup.md`, `{repo_directory}/BUILDING.md`
→ Uses read_file to load docs/setup.md content:
```markdown
# Setup Guide

1. Install dependencies: `npm install`
2. Configure environment: `cp .env.example .env`
3. Run setup script: `./scripts/setup.sh`
```
→ Extracts 3 commands from setup.md with source_file="docs/setup.md"
→ Uses read_file to load BUILDING.md content:
```markdown
# Building

Build the project:
```bash
npm run build
```
```
→ Extracts 1 command from BUILDING.md with source_file="BUILDING.md"
→ Final output:
  - commands_extracted: 4 commands total
  - referenced_files_processed: ["docs/setup.md", "BUILDING.md"]
  - sections_identified includes sections from all 3 files (README.md, docs/setup.md, BUILDING.md)
