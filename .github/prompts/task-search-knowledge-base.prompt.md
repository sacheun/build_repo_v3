@task-search-knowledge-base solution_path={{solution_path}} solution_name={{solution_name}} build_status={{build_status}} build_stderr={{build_stderr}} errors={{errors}} warnings={{warnings}}

Task name: task-search-knowledge-base

---
temperature: 0.1
---
## Description:
This task analyzes build failures, extracts detection tokens from error output, and searches existing knowledge base articles for matches. If a match is found, it returns the path to the existing KB article. If no match is found, it signals that a new KB article should be created.

## Execution Policy
** ⚠️ CRITICAL - THIS TASK IS NON-SCRIPTABLE ⚠️ **

This task requires AI STRUCTURAL REASONING and CANNOT be automated in a script.

WHY NON-SCRIPTABLE:
✓ Analyzing build error output requires understanding context, not just pattern matching
✓ Extracting meaningful detection tokens requires AI judgment
✓ Matching errors to KB articles requires semantic understanding of error messages
✓ Reading and understanding existing KB articles requires AI comprehension
✓ Determining if KB matches current error requires contextual reasoning

YOU MUST USE DIRECT TOOL CALLS:
✓ Use AI reasoning to analyze build_stderr and identify error patterns
✓ Use AI reasoning to extract meaningful detection tokens
✓ Use read_file to examine existing KB articles in knowledge_base_markdown/
✓ Use AI reasoning to determine if existing KB matches the current error
✓ Use semantic understanding to compare errors, not just keyword matching

DO NOT:
✗ Create a Python script that uses regex/string matching to find errors
✗ Use simple substring matching to search KB articles
✗ Automate this process - each error requires human-like understanding

** END WARNING **

## Instructions (Follow this Step by Step)
### Step 1 (MANDATORY)
   - If environment variable DEBUG=1 (string comparison), emit an immediate line to stdout (or terminal):
   - `[debug][task-search-knowledge-base] START solution='{{solution_name}}' build_status='{{build_status}}' error_count={{len(errors)}}`
   - This line precedes all other task operations and helps trace task sequencing when multiple tasks run in a pipeline.

### Step 2 (MANDATORY)
  **Success Check**: If build_status == SUCCESS, return kb_search_status=SKIPPED (no action needed).
   - DEBUG: Log "[KB-SEARCH-DEBUG] Build status: {build_status}, KB search skipped"
   - Return: kb_search_status=SKIPPED, kb_file_path=null, detection_tokens=[]

 **Failure Analysis**: If build_status == FAIL, proceed with error analysis:
   
   ** USE AI STRUCTURAL REASONING - NOT REGEX **:
   - Read and comprehend the build error output (don't just scan for patterns)
   - Understand what type of error occurred (missing property, compilation error, missing file, etc.)
   - Identify the root cause using AI understanding of error messages
   - Determine distinctive characteristics that uniquely identify this error
   - **CRITICAL**: Use errors[] array from build task containing extracted diagnostic codes (NU1008, MSB3644, CS0234, etc.)
   
   a. Analyze error information from build task:
      - DEBUG: Log "[KB-SEARCH-DEBUG] Build failed with {len(errors)} errors, {len(warnings)} warnings"
      - DEBUG: Log "[KB-SEARCH-DEBUG] Error codes: {errors}"
      - **PRIMARY SOURCE**: Use errors[] array as the primary source of error codes
      - **SECONDARY SOURCE**: Use build_stderr for additional context and error messages
      - DEBUG: Log "[KB-SEARCH-DEBUG] First 500 chars of stderr: {build_stderr[:500]}"
   
   b. Extract "Detection Tokens" from errors[] and build_stderr:
      - Start with error codes from errors[] array (e.g., ["NU1008", "MSB3644"])
      - Extract additional context from build_stderr (error signatures that uniquely identify the issue)
      - **IMPORTANT**: If build_stderr is empty, fallback to build_stdout (dotnet build often writes errors to stdout)
      - DEBUG: Log "[KB-SEARCH-DEBUG] stderr is empty, checking stdout (length: {len(build_stdout)} chars)"
      - **USE AI**: Don't just extract with regex - understand the error context
      - NuGet errors: NU#### (e.g., NU1008, NU1605)
      - MSBuild errors: MSB#### (e.g., MSB3644, MSB4019)
      - C# compiler errors: CS#### (e.g., CS0246, CS0234)
      - Platform-specific errors (Service Fabric, .sfproj, etc.)
      - Property errors (BaseOutputPath, OutputPath, etc.)
      - DEBUG: Log "[KB-SEARCH-DEBUG] Identified error type: {error_type}, code: {error_code}"
   
   c. Extract distinctive tokens using AI judgment:
      - Look for common error patterns (understand them, don't just match them):
        * Property not set: "The <PropertyName> property is not set"
        * Missing file: "Could not find file"
        * Missing assembly: "Could not load file or assembly"
        * Compilation error: "error CS####:"
        * MSBuild error: "error MSB####:"
        * NuGet error: "NU####:"
        * Service Fabric: "SF.sfproj", "BaseOutputPath", "OutputPath"
      - DEBUG: Log "[KB-SEARCH-DEBUG] Extracted {len(raw_tokens)} raw tokens: {raw_tokens}"
      - **USE AI**: Understand WHY these patterns matter, not just that they exist
   
   d. Clean and normalize tokens (using AI understanding of what's meaningful):
      - Remove file paths (C:\...\file.cs → file.cs)
      - Remove line numbers (line 123 → line)
      - Keep error codes (CS0246, MSB3644, NU1101)
      - Keep property names (BaseOutputPath, OutputPath)
      - Keep distinctive keywords (central package, package downgrade, etc.)
      - DEBUG: Log "[KB-SEARCH-DEBUG] Normalized tokens: {detection_tokens}"
      - **USE AI**: Determine which parts of the error message are distinctive
   
   e. Generate error signature for searching (using AI judgment about what's important):
      - Combine 2-3 most distinctive tokens
      - Use lowercase, underscore-separated format
      - Example: "nu1008_central_package_management", "baseoutputpath_property_not_set"
      - DEBUG: Log "[KB-SEARCH-DEBUG] Error signature: {error_signature}"
      - **USE AI**: Choose tokens that uniquely identify this error type

### Step 3 (MANDATORY)
**Knowledge Base Search**:
   
   ** USE read_file AND AI REASONING - NOT SIMPLE STRING MATCHING **:
   - Use read_file tool to load each KB article in knowledge_base_markdown/
   - Read and comprehend the KB article content (understand what error it addresses)
   - Compare the current error to the KB article using semantic understanding
   - Determine if the KB article is relevant to the current error (not just keyword matching)
   
   a. Ensure ./knowledge_base_markdown/ directory exists.
      - DEBUG: Log "[KB-SEARCH-DEBUG] KB directory exists: {kb_dir_exists}"
      - If directory doesn't exist, return kb_search_status=NOT_FOUND (no existing KB articles)
   
   b. List all .md files in ./knowledge_base_markdown/ (exclude README.md and other non-KB files).
      - DEBUG: Log "[KB-SEARCH-DEBUG] Searching {len(kb_files)} KB articles for matches"
      - **USE list_dir or file_search**: Get list of KB article files
   
   c. For each KB article, use read_file to load and analyze:
      - DEBUG: Log "[KB-SEARCH-DEBUG] Checking {kb_file}..."
      - **USE read_file**: Actually read the KB article content
      - Look for "Detection Tokens" section in the KB article
      - Extract the detection tokens from the KB article
      - DEBUG: Log "[KB-SEARCH-DEBUG] KB article tokens: {kb_tokens}"
   
   d. Compare using AI understanding of error semantics:
      - **USE AI REASONING**: Compare current error's detection tokens with KB article tokens
      - Don't just do substring matching - understand if errors are semantically similar
      - Consider:
        * Same error code (NU1008 matches NU1008)
        * Similar error patterns (both about package versions)
        * Same root cause (both about Central Package Management)
      - DEBUG: Log "[KB-SEARCH-DEBUG] Semantic similarity score: {similarity_score}"
      - **USE AI**: Determine if the KB article truly addresses the same error
   
   e. If match found (AI determines KB article is relevant):
      - DEBUG: Log "[KB-SEARCH-DEBUG] Match found! Using existing KB: {kb_file_path}"
      - Return: kb_search_status=FOUND, kb_file_path={absolute_path_to_kb}, detection_tokens={extracted_tokens}
   
   f. If no match found after checking all KB articles:
      - DEBUG: Log "[KB-SEARCH-DEBUG] No matching KB article found"
      - Return: kb_search_status=NOT_FOUND, kb_file_path=null, detection_tokens={extracted_tokens}

### Step 4 (MANDATORY)
**Output**: Return search results.
   - DEBUG: Log "[KB-SEARCH-DEBUG] Final status: kb_search_status={status}, kb_file_path={path}, tokens={tokens}"

Variables available:
- {{solution_path}} → Absolute path to the .sln file that failed to build
- {{solution_name}} → Friendly solution name derived from file name
- {{build_status}} → Result of build task (SUCCESS | FAIL | SKIPPED)
- {{build_stderr}} → Standard error output from build command

Output Contract:
- kb_search_status: FOUND | NOT_FOUND | SKIPPED
- kb_file_path: string (absolute path to existing .md file if FOUND, null otherwise)
- detection_tokens: array[string] (extracted error signatures)
- error_signature: string (generated signature for this error)
- error_code: string (e.g., "NU1008", "MSB3644", null if not applicable)
- error_type: string (e.g., "NuGet", "MSBuild", "Compiler", "Platform")

Implementation Notes:
1. **AI REASONING REQUIRED**: Each error analysis requires understanding context, not pattern matching.
2. Always check if ./knowledge_base_markdown/ directory exists before searching.
3. Use read_file to actually read KB article content - don't just check filenames.
4. Use semantic understanding to match errors - not just keyword/substring matching.
5. If DEBUG=1 or DEBUG environment variable is set, output detailed extraction and matching process with [KB-SEARCH-DEBUG] prefix.
6. The detection_tokens array should contain meaningful, normalized tokens that uniquely identify the error.
7. The error_signature should be a concise, lowercase, underscore-separated string suitable for filename generation.
8. This task focuses on SEARCHING existing KB - it does NOT create new KB articles.
9. Return NOT_FOUND to signal that @task-create-kb should be invoked.
10. Return FOUND with kb_file_path to signal that existing KB article can be referenced.

Detection Token Extraction Guidelines:

** IMPORTANT - USE AI REASONING, NOT JUST REGEX **:
The guidelines below are for AI analysis, not strict regex patterns to automate.
You must understand the error context and extract meaningful tokens using AI judgment.

1. **Error Code Priority**:
   - Always extract error codes if present (NU####, MSB####, CS####)
   - Error codes are the strongest detection tokens
   - Example: "NU1008", "MSB3644", "CS0246"

2. **Property/Configuration Names**:
   - Extract property names that are central to the error
   - Example: "BaseOutputPath", "OutputPath", "Platform"

3. **Technology/Platform Keywords**:
   - Extract technology-specific keywords
   - Example: "Service Fabric", ".sfproj", "Central Package Management", "package downgrade"

4. **Error Pattern Keywords**:
   - Extract distinctive error patterns
   - Example: "property is not set", "could not find file", "package version management"

5. **Normalization Rules**:
   - Remove file paths and line numbers (too specific)
   - Keep error codes and property names (distinctive)
   - Lowercase all tokens for consistency
   - Use underscores to separate multi-word concepts
   - Example: "The BaseOutputPath property is not set" → ["baseoutputpath", "property is not set"]

Example Detection Token Sets:

**NU1008 Error:**
```
detection_tokens: ["NU1008", "central package version management", "PackageReference items", "PackageVersion items"]
error_signature: "nu1008_central_package_management"
error_code: "NU1008"
error_type: "NuGet"
```

**Service Fabric Platform Error:**
```
detection_tokens: ["BaseOutputPath", "OutputPath", ".sfproj", "Service Fabric", "Platform='x64'"]
error_signature: "sf_baseoutputpath_missing"
error_code: null
error_type: "Platform"
```

**Package Downgrade Error:**
```
detection_tokens: ["NU1605", "Detected package downgrade", "Warning As Error", "Microsoft.Extensions"]
error_signature: "nu1605_package_downgrade"
error_code: "NU1605"
error_type: "NuGet"
```

---

## Step 6: Output Results

1. **DEBUG Exit Trace:**
   - If environment variable DEBUG=1, emit a line to stdout before returning:
   - `[debug][task-search-knowledge-base] END kb_search_status='{{kb_search_status}}' error_code='{{error_code}}'`
   - This helps trace when the task completes and its outcome.

2. **Log to Decision Log:**
   - Call @task-update-decision-log to log task execution:
   ```
   @task-update-decision-log 
     timestamp="{{timestamp}}" 
     repo_name="{{repo_name}}" 
     solution_name="{{solution_name}}" 
     task="task-search-knowledge-base" 
     message="{{message}}" 
     status="{{status}}"
   ```
   - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
   - Message format:
     * If build_status == SUCCESS: "Build succeeded - search skipped"
     * If kb_search_status == FOUND: "Searching for: {{error_signature}} - KB found: {{kb_filename}}"
     * If kb_search_status == NOT_FOUND: "Searching for: {{error_signature}} - No KB found"
   - {{error_signature}}: The error signature generated in step 2 (e.g., "nu1008_central_package_management")
   - {{kb_filename}}: Extract filename from kb_file_path if found (e.g., "nu1008_central_package_management.md")
   - Status:
     * "SKIPPED" if build_status == SUCCESS
     * "FOUND" if kb_search_status == FOUND
     * "NOT_FOUND" if kb_search_status == NOT_FOUND

3. **Return JSON Output:**

Output the following JSON structure to the output file.