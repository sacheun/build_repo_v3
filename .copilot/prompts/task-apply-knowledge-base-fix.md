@task-apply-knowledge-base-fix solution_path={{solution_path}} kb_file_path={{kb_file_path}} error_code={{error_code}} last_option_applied={{last_option_applied}}
---
temperature: 0.1
---

# Task: Apply Knowledge Base Fix

## Purpose
Parse the KB article, extract fix instructions, and automatically apply them to the solution files to resolve the build error. Supports multiple fix options with sequential retry logic.

## Prerequisites
- `solution_path`: Absolute path to the .sln file
- `kb_file_path`: Absolute path to the KB article markdown file
- `error_code`: Error code to fix (e.g., NU1008, MSB3644, SF0001)
- `last_option_applied`: (Optional) The last option number that was applied (e.g., "1", "2", "3"). If not provided, defaults to applying Option 1.

## Behavior

0. **DEBUG Entry Trace:**
   - If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   - `[debug][task-apply-knowledge-base-fix] START solution='{{solution_name}}' kb_file='{{kb_file_path}}' error_code='{{error_code}}'`
   - This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

## YOU MUST USE DIRECT TOOL CALLS

** CRITICAL: DO NOT suggest commands or edits - EXECUTE them directly **

Use these tools:
- `read_file` - Read KB article and solution files
- `replace_string_in_file` - Apply code changes to project files
- `run_in_terminal` - Execute build commands if needed
- `file_search` - Find .csproj, Directory.Build.props, etc.

** NEVER output code blocks expecting the user to manually apply them **

---

## Step 1: Parse KB Article

1. **Read the KB Article:**
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

---

## Step 2: Locate Target Files

1. **Find Solution Directory:**
   - Extract directory from solution_path: `Path.GetDirectoryName(solution_path)`

2. **Search for Target Files:**
   - Use `file_search` to locate files matching the pattern from KB instructions
   - Example patterns:
     * `**/Directory.Build.props` - Find build props files
     * `**/*.csproj` - Find all project files
     * `**/Directory.Packages.props` - Find package props files

3. **Validate Files Exist:**
   - If required file doesn't exist, create it (e.g., Directory.Packages.props)
   - If file exists, read current content before modifying

---

## Step 3: Apply Fix Instructions

** CRITICAL: Use `replace_string_in_file` or `create_file` - DO NOT output code blocks **

### Example Fix Patterns:

**Pattern 1: NU1008 - Central Package Management**
- **Action:** Remove `<Version>` from PackageReference, add to Directory.Packages.props
- **Target:** All .csproj files + Directory.Packages.props
- **Implementation:**
  1. Read each .csproj file
  2. Find `<PackageReference Include="..." Version="x.x.x" />`
  3. Use `replace_string_in_file` to remove Version attribute
  4. Add corresponding `<PackageVersion Include="..." Version="x.x.x" />` to Directory.Packages.props

**Pattern 2: Service Fabric Platform**
- **Action:** Add `/p:Platform=x64` to build command or set in props
- **Target:** Directory.Build.props or solution configuration
- **Implementation:**
  1. Check if Directory.Build.props exists
  2. Add `<Platform>x64</Platform>` to PropertyGroup
  3. Or note that msbuild command needs `/p:Platform=x64` parameter

**Pattern 3: NU1605 - Package Downgrade**
- **Action:** Update package versions to consistent versions
- **Target:** .csproj files or Directory.Packages.props
- **Implementation:**
  1. Identify all conflicting package versions
  2. Determine highest required version
  3. Update all references to use highest version

### Fix Application Steps:

1. **For Each Required Change:**
   - Read target file with `read_file`
   - Identify exact string to replace (include context lines)
   - Use `replace_string_in_file` with:
     * `oldString`: Current content (with 3-5 lines context)
     * `newString`: Fixed content (with same context)
   - Verify change was applied successfully

2. **Create Missing Files if Needed:**
   - If Directory.Packages.props doesn't exist, create it:
   ```xml
   <Project>
     <PropertyGroup>
       <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
     </PropertyGroup>
     <ItemGroup>
       <!-- Package versions will be added here -->
     </ItemGroup>
   </Project>
   ```

3. **Track All Changes:**
   - Maintain array of changes_made:
     * File path
     * Change description
     * Old value → New value

---

## Step 4: Validate Fix Application

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

---

## Step 5: Output Results

1. **DEBUG Exit Trace:**
   - If environment variable DEBUG=1, emit a line to stdout before returning:
   - `[debug][task-apply-knowledge-base-fix] END fix_status='{{fix_status}}' files_modified={{files_modified}}`
   - This helps trace when the task completes and its outcome.

2. **Log to Decision Log:**
   - Append to: results/decision-log.csv
   - Append row with: "{{timestamp}},{{repo_name}},{{solution_name}},task-apply-knowledge-base-fix,Applied KB fix: {{kb_file_name}},{{status}}"
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - {{kb_file_name}}: Extract filename from kb_file_path (e.g., "nu1008_central_package_management.md")
   - Status: "SUCCESS" if fix_status is SUCCESS, "FAIL" if fix_status is FAIL, "SKIPPED" if fix_status is SKIPPED

3. **Return JSON Output:**

Return JSON output with the following structure:

```json
{
  "fix_status": "SUCCESS | FAIL | SKIPPED | NO_MORE_OPTIONS",
  "option_applied": "1 | 2 | 3 | null",
  "fix_applied": "Description of what was fixed",
  "kb_file_path": "path/to/kb/article.md",
  "error_code": "NU1008",
  "target_files": [
    "C:\\...\\Directory.Packages.props",
    "C:\\...\\Project1.csproj"
  ],
  "changes_made": [
    {
      "file": "C:\\...\\Directory.Packages.props",
      "action": "created",
      "description": "Created central package management file"
    },
    {
      "file": "C:\\...\\Project1.csproj",
      "action": "modified",
      "description": "Removed Version from PackageReference 'Newtonsoft.Json'"
    }
  ],
  "validation": {
    "files_modified": 2,
    "syntax_valid": true
  },
  "available_options": {
    "total": 3,
    "last_applied": "1",
    "next_available": "2"
  }
}
```

### Status Definitions:
- **SUCCESS**: All fix instructions applied successfully, files modified correctly
- **FAIL**: Unable to apply fix due to file access issues, syntax errors, or unexpected file structure
- **SKIPPED**: Fix instructions not applicable to this solution (wrong error code, files don't match KB expectations)
- **NO_MORE_OPTIONS**: The last_option_applied was provided, but no additional options are available in the KB article (all options exhausted)

---

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

---

## Common Fix Scenarios

### Scenario 1: Central Package Management (NU1008) - Multiple Options
**KB Structure:**
- **Option 1:** Remove Version from PackageReference, add to Directory.Packages.props
- **Option 2:** Disable CPM globally
- **Option 3:** Use specific package versions in Directory.Build.props

**Implementation (Option Selection):**
- **First attempt (last_option_applied not provided):**
  * Apply Option 1 (recommended CPM approach)
  * Return `option_applied: "1"`
  
- **Second attempt (last_option_applied = "1"):**
  * Skip Option 1, apply Option 2
  * Return `option_applied: "2"`
  
- **Third attempt (last_option_applied = "2"):**
  * Skip Options 1 & 2, apply Option 3
  * Return `option_applied: "3"`
  
- **Fourth attempt (last_option_applied = "3"):**
  * No Option 4 exists in KB
  * Return `fix_status: "NO_MORE_OPTIONS"`, `option_applied: null`

### Scenario 2: Platform Configuration (Service Fabric) - Multiple Options
**KB Structure:**
- **Option 1:** Add Platform=x64 to build command
- **Option 2:** Modify .sfproj file to set default Platform
- **Option 3:** Use nuget restore fallback

**Implementation:**
Follow same sequential option logic as Scenario 1

### Scenario 3: Package Version Conflicts (NU1605) - Single Option
**KB Structure:**
- **Option 1:** Update conflicting packages to consistent version

**Implementation:**
- **First attempt:** Apply Option 1
- **Second attempt (last_option_applied = "1"):** Return `NO_MORE_OPTIONS`

---

## Debug Output

When DEBUG=1 is set, output verbose logs:

```
[FIX-DEBUG] Parsing KB article: nu1008_central_package_management.md
[FIX-DEBUG] last_option_applied: 1
[FIX-DEBUG] Total options available in KB: 3
[FIX-DEBUG] Calculating next option: 1 + 1 = 2
[FIX-DEBUG] Applying Option 2: Disable CPM globally
[FIX-DEBUG] Fix type: NU1008 - Central Package Management
[FIX-DEBUG] Target action: Add <ManagePackageVersionsCentrally>false</ManagePackageVersionsCentrally>
[FIX-DEBUG] Finding Directory.Build.props
[FIX-DEBUG] Modifying Directory.Build.props: Adding CPM disable flag
[FIX-DEBUG] Fix applied successfully - 1 file modified
[FIX-DEBUG] option_applied: "2", next_available: "3"
```

---

## Task Output File

Save output to: `output/{repo_name}_{solution_name}_task-apply-kb-fix.json`

Example filename: `ic3_spool_cosine-dep-spool_MigrateCosmosDb_task-apply-kb-fix.json`

This output becomes input to the retry build step in the workflow loop.
