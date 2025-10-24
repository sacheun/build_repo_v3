@task-apply-knowledge-base-fix solution_path={{solution_path}} kb_file_path={{kb_file_path}} error_code={{error_code}}
---
temperature: 0.1
---

# Task: Apply Knowledge Base Fix

## Purpose
Parse the KB article, extract fix instructions, and automatically apply them to the solution files to resolve the build error.

## Prerequisites
- `solution_path`: Absolute path to the .sln file
- `kb_file_path`: Absolute path to the KB article markdown file
- `error_code`: Error code to fix (e.g., NU1008, MSB3644, SF0001)

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
   - Locate the "## How to Fix" or "## Fix Options" section
   - Identify the **Recommended** fix (Option 1)
   - Parse the specific actions required:
     * File to modify (e.g., Directory.Build.props, *.csproj)
     * Content to add/remove/modify
     * Build parameters to change

3. **Identify Target Files:**
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
  "fix_status": "SUCCESS | FAIL | SKIPPED",
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
  }
}
```

### Status Definitions:
- **SUCCESS**: All fix instructions applied successfully, files modified correctly
- **FAIL**: Unable to apply fix due to file access issues, syntax errors, or unexpected file structure
- **SKIPPED**: Fix instructions not applicable to this solution (wrong error code, files don't match KB expectations)

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

### Scenario 1: Central Package Management (NU1008)
**KB Instructions:**
- Remove Version from all PackageReference
- Add PackageVersion to Directory.Packages.props

**Implementation:**
1. Find all .csproj files: `file_search **/*.csproj`
2. For each .csproj:
   - Read file, find all `<PackageReference Include="X" Version="Y" />`
   - Use `replace_string_in_file` to change to `<PackageReference Include="X" />`
   - Track package name and version
3. Create/update Directory.Packages.props:
   - Add `<PackageVersion Include="X" Version="Y" />` for each package

### Scenario 2: Platform Configuration (Service Fabric)
**KB Instructions:**
- Add Platform=x64 to build

**Implementation:**
1. Find Directory.Build.props or create it
2. Add `<Platform>x64</Platform>` to PropertyGroup
3. Or track that msbuild needs `/p:Platform=x64` parameter (handled by build task)

### Scenario 3: Package Version Conflicts (NU1605)
**KB Instructions:**
- Update conflicting packages to consistent version

**Implementation:**
1. Parse stderr to find conflicting packages and versions
2. Determine target version (usually highest)
3. Find all .csproj or Directory.Packages.props with those packages
4. Update all to consistent version using `replace_string_in_file`

---

## Debug Output

When DEBUG=1 is set, output verbose logs:

```
[FIX-DEBUG] Parsing KB article: nu1008_central_package_management.md
[FIX-DEBUG] Fix type: NU1008 - Central Package Management
[FIX-DEBUG] Target action: Remove Version from PackageReference
[FIX-DEBUG] Finding .csproj files in solution directory
[FIX-DEBUG] Found 3 project files
[FIX-DEBUG] Modifying Project1.csproj: Removing Version from Newtonsoft.Json
[FIX-DEBUG] Modifying Project2.csproj: Removing Version from Microsoft.Extensions.Logging
[FIX-DEBUG] Creating Directory.Packages.props with 5 package versions
[FIX-DEBUG] Fix applied successfully - 4 files modified
```

---

## Task Output File

Save output to: `output/{repo_name}_{solution_name}_task-apply-kb-fix.json`

Example filename: `ic3_spool_cosine-dep-spool_MigrateCosmosDb_task-apply-kb-fix.json`

This output becomes input to the retry build step in the workflow loop.
