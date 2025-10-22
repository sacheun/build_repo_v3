@task-collect-knowledge-base solution_path={{solution_path}} build_status={{build_status}} build_stderr={{build_stderr}}
---
temperature: 0.1
model: gpt-4
---

** ⚠️ CRITICAL - THIS TASK IS NON-SCRIPTABLE ⚠️ **

This task requires AI STRUCTURAL REASONING and CANNOT be automated in a script.

WHY NON-SCRIPTABLE:
✓ Analyzing build error output requires understanding context, not just pattern matching
✓ Matching errors to KB articles requires semantic understanding of error messages
✓ Reading and understanding existing KB articles requires AI comprehension
✓ Synthesizing a new KB article with meaningful diagnostic hints requires AI reasoning
✓ Determining which error patterns are "distinctive" requires judgment
✓ Creating helpful fix instructions requires understanding the problem domain

YOU MUST USE DIRECT TOOL CALLS:
✓ Use AI reasoning to analyze build_stderr and identify error patterns
✓ Use AI reasoning to understand what type of error occurred
✓ Use read_file to examine existing KB articles in knowledge_base_markdown/
✓ Use AI reasoning to determine if existing KB matches the current error
✓ Use AI reasoning to synthesize meaningful Detection Tokens
✓ Use create_file to generate new KB article with helpful content (not templates)
✓ Use AI reasoning to write diagnostic hints and fix instructions

DO NOT:
✗ Create a Python script that uses regex/string matching to find errors
✗ Use simple substring matching to search KB articles
✗ Generate KB articles with placeholder text like "[TODO]" or "[Brief Description]"
✗ Automate this process - each error requires human-like understanding

** END WARNING **

Description:
This task analyzes build failures and manages a knowledge base of known build errors. It extracts "Detection Tokens" from build error output, searches for existing knowledge base articles, and creates new ones when novel errors are encountered.

** IMPORTANT - NON-SCRIPTABLE TASK **:
- This task requires AI structural reasoning to understand error context
- DO NOT create a Python script (ignore "Programming Language" section at bottom)
- Use direct tool calls: run_in_terminal to get error output, read_file to examine KB articles, create_file for new articles
- Each error analysis requires AI judgment - simple regex/pattern matching is insufficient
- KB article creation requires synthesizing helpful diagnostic content, not filling templates

Behavior:
1. **Success Check**: If build_status == SUCCESS, return kb_status=SKIPPED (no action needed).
   - DEBUG: Log "[KB-DEBUG] Build status: {build_status}, KB collection skipped"

2. **Failure Analysis**: If build_status == FAIL, proceed with knowledge base collection:
   
   ** USE AI STRUCTURAL REASONING - NOT REGEX **:
   - Read and comprehend the build error output (don't just scan for patterns)
   - Understand what type of error occurred (missing property, compilation error, missing file, etc.)
   - Identify the root cause using AI understanding of error messages
   - Determine distinctive characteristics that uniquely identify this error
   
   a. Extract "Detection Tokens" from build_stderr (error signatures that uniquely identify the issue).
      - DEBUG: Log "[KB-DEBUG] Build failed, analyzing stderr (length: {len(build_stderr)} chars)"
      - DEBUG: Log "[KB-DEBUG] First 500 chars of stderr: {build_stderr[:500]}"
      - **IMPORTANT**: If build_stderr is empty, fallback to build_stdout (dotnet build often writes errors to stdout)
      - DEBUG: Log "[KB-DEBUG] stderr is empty, checking stdout (length: {len(build_stdout)} chars)"
      - **USE AI**: Don't just extract with regex - understand the error context
   b. Clean and normalize tokens (remove file paths, line numbers, timestamps).
      - DEBUG: Log "[KB-DEBUG] Extracted {len(detection_tokens)} raw tokens: {detection_tokens}"
      - **USE AI**: Determine which tokens are actually meaningful vs noise
   c. Generate a short error signature for searching.
      - DEBUG: Log "[KB-DEBUG] Normalized tokens: {detection_tokens}"
      - **USE AI**: Create a signature that captures the essence of the error

3. **Knowledge Base Search**:
   
   ** USE read_file AND AI REASONING - NOT SIMPLE STRING MATCHING **:
   - Use read_file tool to load each KB article in knowledge_base_markdown/
   - Read and comprehend the KB article content (understand what error it addresses)
   - Compare the current error to the KB article using semantic understanding
   - Determine if the KB article is relevant to the current error (not just keyword matching)
   
   a. Ensure ./knowledge_base_markdown/ directory exists.
      - DEBUG: Log "[KB-DEBUG] KB directory exists: {os.path.exists(kb_dir)}"
   b. Search all .md files in ./knowledge_base_markdown/ for matching Detection Tokens.
      - DEBUG: Log "[KB-DEBUG] Searching {len(kb_files)} KB articles for matches"
      - DEBUG: For each file, log "[KB-DEBUG] Checking {kb_file}..."
      - **USE read_file**: Actually read each KB article, don't just scan filenames
   c. Compare using AI understanding of error semantics (not just fuzzy matching or substring search).
      - DEBUG: Log "[KB-DEBUG] Token '{token}' found in {kb_file}" when match found
      - **USE AI**: Determine if the KB article truly addresses the same error
   d. If match found, return kb_status=SUCCESS with kb_file_path pointing to existing file.
      - DEBUG: Log "[KB-DEBUG] Match found! Using existing KB: {kb_file_path}"

4. **New Knowledge Base Article Creation**:
   
   ** USE create_file AND AI REASONING - NOT TEMPLATE FILLING **:
   - Synthesize a meaningful, helpful KB article using AI understanding
   - Write diagnostic hints that explain HOW to identify this error (not generic text)
   - Write fix instructions that explain WHAT to do (based on understanding the error)
   - DO NOT generate placeholder text like "[TODO]" or "[Brief Description]"
   - The KB article should be immediately useful to a developer, not a template
   
   a. If no matching Detection Tokens found, create new .md file.
      - DEBUG: Log "[KB-DEBUG] No matching KB article found, creating new one"
      - DEBUG: Log "[KB-DEBUG] Error signature: {error_signature}"
      - DEBUG: Log "[KB-DEBUG] Filename: {kb_filename}"
   b. Generate meaningful filename based on error type (e.g., "sf_baseoutputpath_missing.md").
      - **USE AI**: Create a descriptive filename that indicates the error type
   c. Use standardized template format (see Template section below), but FILL IT WITH REAL CONTENT.
      - **USE AI**: Write actual diagnostic hints, not placeholders
      - **USE AI**: Write actual fix instructions based on understanding the error
   d. Include:
      - Issue title and description (REAL description of what's wrong)
      - Diagnostic hints (REAL hints on how to identify this error)
      - Detection tokens (extracted from stderr using AI understanding)
      - Fix instructions (REAL instructions, not "TODO" placeholders)
      - Example solution path (the actual solution that failed)
      - DEBUG: Log "[KB-DEBUG] Article content length: {len(kb_article)} chars"
   e. Save to ./knowledge_base_markdown/
      - DEBUG: Log "[KB-DEBUG] Created KB article: {kb_file_path}"
      - **USE create_file**: Save the synthesized KB article

5. **Output**: Return kb_status and kb_file_path.
   - DEBUG: Log "[KB-DEBUG] Final status: kb_status={kb_status}, kb_file_path={kb_file_path}"

Variables available:
- {{solution_path}} → Absolute path to the .sln file that failed to build.
- {{solution_name}} → Friendly solution name derived from file name.
- {{build_status}} → Result of build task (SUCCESS | FAIL | SKIPPED).
- {{build_stderr}} → Standard error output from build command.

Detection Token Extraction Rules:

** IMPORTANT - USE AI REASONING, NOT JUST REGEX **:
The rules below are GUIDELINES for AI analysis, not strict regex patterns to automate.
You must understand the error context and extract meaningful tokens using AI judgment.

1. Look for common error patterns (understand them, don't just match them):
   - Property not set: "The <PropertyName> property is not set"
   - Missing file: "Could not find file"
   - Missing assembly: "Could not load file or assembly"
   - Compilation error: "error CS####:"
   - MSBuild error: "error MSB####:"
   - NuGet error: "NU####:"
   - Service Fabric: "SF.sfproj", "BaseOutputPath", "OutputPath"
   - DEBUG: Log each pattern match: "[KB-DEBUG] Pattern 'property_errors' matched: {matches}"
   - **USE AI**: Understand WHY these patterns matter, not just that they exist

2. Normalize tokens (using AI understanding of what's meaningful):
   - Remove file paths (C:\...\file.cs → file.cs)
   - Remove line numbers (line 123 → line)
   - Keep error codes (CS0246, MSB3644, NU1101)
   - Keep property names (BaseOutputPath, OutputPath)
   - DEBUG: Log normalization: "[KB-DEBUG] Before normalization: {raw_token} → After: {normalized_token}"
   - **USE AI**: Determine which parts of the error message are distinctive

3. Create signature (using AI judgment about what's important):
   - Combine 2-3 most distinctive tokens
   - Use lowercase, underscore-separated format
   - Example: "baseoutputpath_property_not_set"
   - DEBUG: Log signature creation: "[KB-DEBUG] Signature parts: {signature_parts} → {error_signature}"
   - **USE AI**: Choose tokens that uniquely identify this error type

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
2. **AI REASONING REQUIRED**: Each error analysis requires understanding context, not pattern matching.
3. Always create ./knowledge_base_markdown/ directory if it doesn't exist (use create_directory tool).
4. Use safe filenames (lowercase, alphanumeric + underscore/hyphen only).
5. Avoid overwriting existing files; append timestamp if needed.
6. Log actions for debugging (e.g., "[kb] Searching for tokens...", "[kb] Created new article...").
7. If DEBUG=1 or DEBUG environment variable is set, output detailed extraction and matching process with [KB-DEBUG] prefix.
8. The KB article you create should have REAL diagnostic content, not placeholder text.
9. The task focuses on identifying error patterns AND providing helpful guidance, not just cataloging errors.
10. **CRITICAL**: Use read_file to examine existing KB articles - don't just check filenames.
11. **CRITICAL**: Use create_file to write new KB articles with synthesized helpful content.
