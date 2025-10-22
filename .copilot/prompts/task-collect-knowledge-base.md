@task-collect-knowledge-base solution_path={{solution_path}} build_status={{build_status}} build_stderr={{build_stderr}}
---
temperature: 0.1
model: gpt-4
---

Description:
This task analyzes build failures and manages a knowledge base of known build errors. It extracts "Detection Tokens" from build error output, searches for existing knowledge base articles, and creates new ones when novel errors are encountered.

Behavior:
1. **Success Check**: If build_status == SUCCESS, return kb_status=SKIPPED (no action needed).
   - DEBUG: Log "[KB-DEBUG] Build status: {build_status}, KB collection skipped"

2. **Failure Analysis**: If build_status == FAIL, proceed with knowledge base collection:
   a. Extract "Detection Tokens" from build_stderr (error signatures that uniquely identify the issue).
      - DEBUG: Log "[KB-DEBUG] Build failed, analyzing stderr (length: {len(build_stderr)} chars)"
      - DEBUG: Log "[KB-DEBUG] First 500 chars of stderr: {build_stderr[:500]}"
      - **IMPORTANT**: If build_stderr is empty, fallback to build_stdout (dotnet build often writes errors to stdout)
      - DEBUG: Log "[KB-DEBUG] stderr is empty, checking stdout (length: {len(build_stdout)} chars)"
   b. Clean and normalize tokens (remove file paths, line numbers, timestamps).
      - DEBUG: Log "[KB-DEBUG] Extracted {len(detection_tokens)} raw tokens: {detection_tokens}"
   c. Generate a short error signature for searching.
      - DEBUG: Log "[KB-DEBUG] Normalized tokens: {detection_tokens}"

3. **Knowledge Base Search**:
   a. Ensure ./knowledge_base_markdown/ directory exists.
      - DEBUG: Log "[KB-DEBUG] KB directory exists: {os.path.exists(kb_dir)}"
   b. Search all .md files in ./knowledge_base_markdown/ for matching Detection Tokens.
      - DEBUG: Log "[KB-DEBUG] Searching {len(kb_files)} KB articles for matches"
      - DEBUG: For each file, log "[KB-DEBUG] Checking {kb_file}..."
   c. Compare using fuzzy matching or exact substring search.
      - DEBUG: Log "[KB-DEBUG] Token '{token}' found in {kb_file}" when match found
   d. If match found, return kb_status=SUCCESS with kb_file_path pointing to existing file.
      - DEBUG: Log "[KB-DEBUG] Match found! Using existing KB: {kb_file_path}"

4. **New Knowledge Base Article Creation**:
   a. If no matching Detection Tokens found, create new .md file.
      - DEBUG: Log "[KB-DEBUG] No matching KB article found, creating new one"
      - DEBUG: Log "[KB-DEBUG] Error signature: {error_signature}"
      - DEBUG: Log "[KB-DEBUG] Filename: {kb_filename}"
   b. Generate meaningful filename based on error type (e.g., "sf_baseoutputpath_missing.md").
   c. Use standardized template format (see Template section below).
   d. Include:
      - Issue title and description
      - Diagnostic hints
      - Detection tokens (extracted from stderr)
      - Fix instructions (placeholder for manual completion)
      - Example solution path
      - DEBUG: Log "[KB-DEBUG] Article content length: {len(kb_article)} chars"
   e. Save to ./knowledge_base_markdown/
      - DEBUG: Log "[KB-DEBUG] Created KB article: {kb_file_path}"

5. **Output**: Return kb_status and kb_file_path.
   - DEBUG: Log "[KB-DEBUG] Final status: kb_status={kb_status}, kb_file_path={kb_file_path}"

Variables available:
- {{solution_path}} → Absolute path to the .sln file that failed to build.
- {{solution_name}} → Friendly solution name derived from file name.
- {{build_status}} → Result of build task (SUCCESS | FAIL | SKIPPED).
- {{build_stderr}} → Standard error output from build command.

Detection Token Extraction Rules:
1. Look for common error patterns:
   - Property not set: "The <PropertyName> property is not set"
   - Missing file: "Could not find file"
   - Missing assembly: "Could not load file or assembly"
   - Compilation error: "error CS####:"
   - MSBuild error: "error MSB####:"
   - NuGet error: "NU####:"
   - Service Fabric: "SF.sfproj", "BaseOutputPath", "OutputPath"
   - DEBUG: Log each pattern match: "[KB-DEBUG] Pattern 'property_errors' matched: {matches}"

2. Normalize tokens:
   - Remove file paths (C:\...\file.cs → file.cs)
   - Remove line numbers (line 123 → line)
   - Keep error codes (CS0246, MSB3644, NU1101)
   - Keep property names (BaseOutputPath, OutputPath)
   - DEBUG: Log normalization: "[KB-DEBUG] Before normalization: {raw_token} → After: {normalized_token}"

3. Create signature:
   - Combine 2-3 most distinctive tokens
   - Use lowercase, underscore-separated format
   - Example: "baseoutputpath_property_not_set"
   - DEBUG: Log signature creation: "[KB-DEBUG] Signature parts: {signature_parts} → {error_signature}"

Knowledge Base Article Template:
```markdown
## Issue: [Brief Description of Error]
[1-2 sentence summary of what causes this build failure]

### Diagnostic Hints
- [How to identify this specific error in build output]
- [What files/projects to check]
- [Key indicators or patterns to look for]

### Detection Tokens
- [Error message pattern 1]
- [Error message pattern 2]
- [Error code or property name]

## Fix:
```pwsh
# [Brief description of what the fix does]
pwsh -Command "[diagnostic command to identify affected files]"

# [Command to apply the fix]
pwsh -File scripts/[fix_script_name].ps1 -RepoRoot <repo_root>

# [Note about workflow integration]
```

### Notes
- [Important details about the fix]
- [When/why this error occurs]
- [Any prerequisites or warnings]

### Safety
- [What the fix modifies]
- [Reversibility or backup recommendations]
- [Review steps before committing]

### Expected Outcome
- [What should happen after fix is applied]
- [How to verify the fix worked]

### Example Solutions
- {{solution_path}}
```

Output Contract:
- kb_status: SUCCESS | SKIPPED
- kb_file_path: string (absolute path to .md file, empty if skipped)
- detection_tokens: array[string] (extracted error signatures)

Implementation Notes:
1. Always create ./knowledge_base_markdown/ directory if it doesn't exist.
2. Use safe filenames (lowercase, alphanumeric + underscore/hyphen only).
3. Avoid overwriting existing files; append timestamp if needed.
4. Log actions for debugging (e.g., "[kb] Searching for tokens...", "[kb] Created new article...").
5. If DEBUG=1 or DEBUG environment variable is set, output detailed extraction and matching process with [KB-DEBUG] prefix.
6. The template includes placeholder sections that require manual completion by developers.
7. The task focuses on capturing error patterns, not solving them automatically.
8. **IMPORTANT**: Check if DEBUG variable exists (from parent scope) or os.environ.get('DEBUG') == '1'.
9. **CRITICAL DEBUG POINTS**:
   - Log the result object type and attributes: "[KB-DEBUG] result object: type={type(result)}, has_stderr={hasattr(result, 'stderr')}"
   - Log captured stderr vs stdout: "[KB-DEBUG] stderr length: {len(stderr)}, stdout length: {len(stdout) if has stdout else 'N/A'}"
   - Log whether build_stderr is empty: "[KB-DEBUG] build_stderr is {'empty' if not build_stderr else 'populated'}"
   - Log regex pattern matches count: "[KB-DEBUG] Property errors: {len(property_errors)}, MSBuild: {len(msbuild_errors)}, CS: {len(cs_errors)}, NuGet: {len(nuget_errors)}"

Programming Language:
- All code generated MUST be written in Python.
- Save script to ./temp-script/task_collect_knowledge_base.py
