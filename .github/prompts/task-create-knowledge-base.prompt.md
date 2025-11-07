@task-create-knowledge-base solution_path={{solution_path}} solution_name={{solution_name}} kb_search_status={{kb_search_status}} detection_tokens={{detection_tokens}} error_signature={{error_signature}} error_code={{error_code}} error_type={{error_type}} build_stderr={{build_stderr}} errors={{errors}} warnings={{warnings}}

---
temperature: 0.1
---

Task name: task-create-knowledge-base


## Description:
This task creates new knowledge base articles when @task-search-kb returns NOT_FOUND. It researches the error using Microsoft Docs MCP server, synthesizes fix instructions from official documentation, and creates a comprehensive KB article with diagnostic hints, fix options, and safety guidance.

** IMPORTANT - ONLY RUN WHEN NEEDED **:
- This task should ONLY be invoked when kb_search_status == NOT_FOUND
- If kb_search_status == FOUND or SKIPPED, do NOT create a new KB article
- Check the kb_search_status before proceeding


** ⚠️ CRITICAL - THIS TASK IS NON-SCRIPTABLE ⚠️ **

This task requires AI STRUCTURAL REASONING and CANNOT be automated in a script.

WHY NON-SCRIPTABLE:
✓ Synthesizing a meaningful KB article requires AI reasoning about error context
✓ Researching fixes using Microsoft Docs MCP server requires structural reasoning
✓ Querying documentation with contextual understanding of the error
✓ Synthesizing fix instructions from multiple Microsoft Docs sources
✓ Creating helpful fix instructions requires understanding the problem domain
✓ Writing diagnostic hints requires comprehension, not template filling

YOU MUST USE DIRECT TOOL CALLS:
✓ **Use mcp_microsoftdocs_microsoft_docs_search to research error codes and concepts**
✓ **Use mcp_microsoftdocs_microsoft_code_sample_search to find fix code examples**
✓ **Use mcp_microsoftdocs_microsoft_docs_fetch to get comprehensive documentation**
✓ Use AI reasoning to synthesize information from Microsoft Docs into actionable fixes
✓ Use AI reasoning to write diagnostic hints and fix instructions from official documentation
✓ Use create_file to generate new KB article with helpful content based on Microsoft Docs research

DO NOT:
✗ Generate KB articles with placeholder text like "[TODO]" or "[Brief Description]"
✗ Use template filling without real content
✗ Automate this process - each KB article requires human-like understanding

** END WARNING **

## Behavior (Follow this Step by Step)
0. **Entry Trace:**
   Emit a single line:
   `[task-create-knowledge-base] START solution='{{solution_name}}' error_signature='{{error_signature}}' error_code='{{error_code}}' errors={{len(errors)}}`

1. **Prerequisite Check**: Verify this task should run.
    - If kb_search_status == FOUND: return kb_create_status=SKIPPED, reason="existing KB article found"
    - If kb_search_status == SKIPPED: return kb_create_status=SKIPPED, reason="build succeeded"
    - If kb_search_status == NOT_FOUND: proceed to step 2

2. **RESEARCH THE ERROR USING MICROSOFT DOCS MCP SERVER**:
   
   ** MANDATORY STEP - MUST QUERY MICROSOFT DOCUMENTATION **:
   - **REQUIREMENT**: This is a MANDATORY step - you MUST query the Microsoft Docs MCP server
   - Use the `microsoftdocs/mcp` MCP server to research the error
   - Use errors[] array from build task as primary source of error codes
   - Query for error codes from errors[] (e.g., "NU1008", "MSB3644", "CS0246")
   - Query for related concepts (e.g., "Central Package Management", "Service Fabric", ".NET build errors")
   - Use AI reasoning to formulate effective search queries
   - **PRINT TO CONSOLE**: `[KB-CREATE] Starting Microsoft Docs MCP server research for errors: {errors}`
   - **MUST LOG TO DECISION LOG**: This step is mandatory and will be logged
   
   Steps:
   a. **Formulate search query** based on error analysis:
      - **PRIMARY**: Use error codes from errors[] array as search terms
      - If error_code exists: Use error_code as primary search term
      - Include error_type in query (NuGet, MSBuild, Compiler, Platform)
      - Include key technology from detection_tokens
      - Example queries:
        * "NU1008 central package management NuGet" (from errors[] array)
        * "MSB3644 reference assembly mismatch"
        * "Service Fabric sfproj Platform configuration"
   
   b. **Use mcp_microsoftdocs_microsoft_docs_search** to find relevant documentation:
      ```
      Tool: mcp_microsoftdocs_microsoft_docs_search
      Parameters:
        query: "[error_code] [error_type] [key_technology]"
      ```
      - **PRINT TO CONSOLE**: `[KB-CREATE] Querying Microsoft Docs MCP server for: {search_query}`
      - **EXECUTE QUERY**: Call mcp_microsoftdocs_microsoft_docs_search tool
      - **PRINT TO CONSOLE**: `[KB-CREATE] Microsoft Docs returned {num_results} documentation results`
      - **USE AI**: Analyze search results to identify most relevant articles
      - Extract URLs for reference section
   
   c. **Use mcp_microsoftdocs_microsoft_code_sample_search** to find code examples:
      ```
      Tool: mcp_microsoftdocs_microsoft_code_sample_search
      Parameters:
        query: "[error_type] fix [technology]"
        language: "csharp" | "powershell" | "xml" (based on error context)
      ```
      Examples:
      - For NU1008: query="Central Package Management Directory.Packages.props", language="xml"
      - For MSBuild: query="MSBuild property configuration", language="xml"
      - For C# errors: query="namespace resolution", language="csharp"
      - **PRINT TO CONSOLE**: `[KB-CREATE] Querying Microsoft Docs code samples for: {code_query} (language: {language})`
      - **EXECUTE QUERY**: Call mcp_microsoftdocs_microsoft_code_sample_search tool
      - **PRINT TO CONSOLE**: `[KB-CREATE] Microsoft Docs returned {num_samples} code samples`
      - **USE AI**: Extract relevant code snippets for fix examples
   
   d. **If search results are insufficient, use mcp_microsoftdocs_microsoft_docs_fetch**:
      - Identify the most relevant documentation URL from search results
      - Fetch full documentation content for comprehensive understanding
      ```
      Tool: mcp_microsoftdocs_microsoft_docs_fetch
      Parameters:
        url: "[microsoft_docs_url_from_search]"
      ```
      - **PRINT TO CONSOLE**: `[KB-CREATE] Fetching full Microsoft Docs article from: {doc_url}`
      - **EXECUTE FETCH**: Call mcp_microsoftdocs_microsoft_docs_fetch tool
      - **PRINT TO CONSOLE**: `[KB-CREATE] Successfully fetched full documentation (length: {content_length} chars)`
      - **USE AI**: Read and comprehend full documentation for deeper understanding
   
   e. **Use AI structural reasoning to analyze Microsoft Docs results**:
      - Understand the root cause explanation from official docs
      - Identify recommended fixes from Microsoft documentation
      - Extract relevant configuration examples from code samples
      - Identify prerequisites and version requirements
      - Note any breaking changes or compatibility concerns
      - Synthesize the information into actionable fix steps

3. **SYNTHESIZE FIX INSTRUCTIONS USING MICROSOFT DOCS RESEARCH**:
   
   ** USE AI REASONING TO DRAFT HELPFUL FIX CONTENT **:
   - Based on Microsoft Docs research, create fix instructions that are:
     * Accurate (aligned with official Microsoft guidance)
     * Actionable (specific commands/steps developers can execute)
     * Complete (include all necessary context and prerequisites)
     * Safe (warn about potential breaking changes)
   
   Steps:
   a. **Draft Issue Description** from Microsoft Docs understanding:
      - 1-2 sentence summary of what causes this build failure
      - Based on root cause explanation from Microsoft Docs
      - Use clear, non-technical language when possible
   
   b. **Draft Diagnostic Hints** based on Microsoft Docs understanding:
      - How to identify this error in build output
      - What configuration/files to check
      - Common scenarios where this error occurs
      - Specific patterns to look for in error messages
   
   c. **Draft Fix Instructions** from Microsoft Docs research:
      
      **Option 1: Recommended Fix** (from Microsoft Docs - always include):
      - Brief description of the recommended approach
      - Step-by-step instructions with specific commands
      - Code examples from Microsoft code samples
      - Expected outcome after applying fix
      
      **Option 2: Alternative Approach** (if applicable):
      - Alternative approach when recommended fix is not suitable
      - Use cases for when to use this approach
      - Step-by-step instructions
      
      **Option 3: Workaround** (if fix is complex or breaking):
      - Temporary workaround solution
      - Warning about limitations
      - When to use workaround vs full fix
   
   d. **Draft Root Cause Section** from Microsoft Docs explanation:
      - Why this error occurs (from official docs)
      - Technical details about the underlying issue
      - Related technologies or dependencies
      - Version or framework information
   
   e. **Draft Notes Section** with contextual information:
      - When/why this error occurs (from Microsoft Docs explanation)
      - Prerequisites or version requirements (e.g., ".NET 6+", "NuGet 6.2+")
      - Breaking change warnings
      - Related features or technologies
      - Common patterns that trigger this error
   
   f. **Draft Safety Section** based on fix impact:
      - What files/configurations will be modified by the fix
      - Potential side effects or breaking changes
      - Breaking change risk level (LOW | MEDIUM | HIGH)
      - Reversibility of changes (how to undo)
   - Testing recommendations after applying fix
   - Specific guidance on when to use this fix

4. **GENERATE KB ARTICLE FILE**:
   
   a. Generate meaningful filename based on error signature:
      - Use error_signature from task-search-kb output
      - Ensure lowercase, alphanumeric + underscore/hyphen only
      - Add .md extension
   - Example: "nu1008_central_package_management.md", "sf_baseoutputpath_missing.md"
   
   b. Assemble complete KB article using template structure:
      - Fill template with REAL CONTENT from Microsoft Docs research
      - Include diagnostic hints from step 3b
      - Include fix options from step 3c
      - Include root cause from step 3d
      - Include notes from step 3e
      - Include safety section from step 3f
      - Include detection tokens from task-search-kb
      - Include References section with Microsoft Docs URLs
      - Include Example Solutions Affected with solution_path
   - **DO NOT use placeholder text** - synthesize actual helpful content
   
   c. Save to ./knowledge_base_markdown/:
      - Ensure directory exists (create if needed)
      - Use create_file tool to save KB article
   - Use absolute path: ./knowledge_base_markdown/{kb_filename}
   - **USE create_file**: Save the synthesized KB article

5. **Output**: Return creation results.
   - **Log to Decision Log (MANDATORY STEPS):**
     * **MUST LOG MICROSOFT DOCS QUERIES**: Log each MCP server query as a separate entry:
       - For microsoft_docs_search:
       ```
       @task-update-decision-log 
         timestamp="{{timestamp}}" 
         repo_name="{{repo_name}}" 
         solution_name="{{solution_name}}" 
         task="task-create-knowledge-base" 
         message="Queried Microsoft Docs MCP: {{search_query}}" 
         status="INFO"
       ```
       - For code_sample_search:
       ```
       @task-update-decision-log 
         timestamp="{{timestamp}}" 
         repo_name="{{repo_name}}" 
         solution_name="{{solution_name}}" 
         task="task-create-knowledge-base" 
         message="Queried Microsoft Docs code samples: {{code_query}}" 
         status="INFO"
       ```
       - For docs_fetch:
       ```
       @task-update-decision-log 
         timestamp="{{timestamp}}" 
         repo_name="{{repo_name}}" 
         solution_name="{{solution_name}}" 
         task="task-create-knowledge-base" 
         message="Fetched Microsoft Docs article: {{doc_url}}" 
         status="INFO"
       ```
     * **FINAL TASK STATUS**: Log the overall task completion:
       ```
       @task-update-decision-log 
         timestamp="{{timestamp}}" 
         repo_name="{{repo_name}}" 
         solution_name="{{solution_name}}" 
         task="task-create-knowledge-base" 
         message="{{message}}" 
         status="{{status}}"
       ```
       - Use ISO 8601 format for timestamp (e.g., "2025-10-22T14:30:45Z")
       - Message format:
         * If kb_create_status == SUCCESS: "Created KB: {{kb_filename}}" (e.g., "Created KB: nu1008_central_package_management.md")
         * If kb_create_status == SKIPPED and kb_search_status == FOUND: "KB already exists - creation skipped"
         * If kb_create_status == SKIPPED and kb_search_status == SKIPPED: "Build succeeded - KB not needed"
       - {{kb_filename}}: Extract filename from kb_file_path (e.g., "nu1008_central_package_management.md")
       - Status:
         * "SUCCESS" if kb_create_status == SUCCESS
         * "SKIPPED" if kb_create_status == SKIPPED
    - **Exit Trace:** Emit `[task-create-knowledge-base] END kb_create_status='{{kb_create_status}}' kb_file_created={{kb_file_created}}`

Variables available:
- {{solution_path}} → Absolute path to the .sln file that failed to build
- {{solution_name}} → Friendly solution name derived from file name
- {{kb_search_status}} → Result from task-search-knowledge-base (FOUND | NOT_FOUND | SKIPPED)
- {{detection_tokens}} → Array of error signatures from task-search-knowledge-base
- {{error_signature}} → Generated signature for filename (e.g., "nu1008_central_package")
- {{error_code}} → Error code if applicable (e.g., "NU1008", "MSB3644")
- {{error_type}} → Error type (e.g., "NuGet", "MSBuild", "Compiler", "Platform")
- {{build_stderr}} → Standard error output from build command (for additional context)
- {{errors}} → Array of diagnostic error codes from build task (e.g., ["NU1008", "MSB3644"])
- {{warnings}} → Array of diagnostic warning codes from build task (e.g., ["NU1101", "CS0618"])

Output Contract:
- kb_create_status: SUCCESS | SKIPPED
- kb_file_path: string (absolute path to created .md file, null if skipped)
- kb_file_created: boolean (true if new file created, false if skipped)
- microsoft_docs_urls: array[string] (URLs referenced in research)

Implementation Notes:
1. **CRITICAL - USE MICROSOFT DOCS MCP SERVER FOR RESEARCH**:
   - Always query Microsoft Docs when creating KB articles
   - Use `mcp_microsoftdocs_microsoft_docs_search` for initial error research
   - Use `mcp_microsoftdocs_microsoft_code_sample_search` for code examples and fixes
   - Use `mcp_microsoftdocs_microsoft_docs_fetch` for comprehensive documentation when needed
   - Synthesize fix instructions from official Microsoft guidance, not assumptions
   - Include Microsoft Docs URLs in the References section of KB articles
2. **AI REASONING REQUIRED**: KB article creation requires understanding and synthesis, not template filling.
3. Always create ./knowledge_base_markdown/ directory if it doesn't exist (use create_directory tool).
4. Use safe filenames (lowercase, alphanumeric + underscore/hyphen only).
5. Avoid overwriting existing files; if collision, append timestamp.
6. Output minimized (no conditional debug mode).
7. The KB article must have REAL diagnostic content from Microsoft Docs, not placeholder text.
8. This task focuses on CREATING new KB articles with authoritative content.
9. Only run when kb_search_status == NOT_FOUND (checked in step 1).
10. Include actual code examples from Microsoft code sample searches.

Knowledge Base Article Template:
```markdown
# [Error Code]: [Brief Description of Error]

## Issue Description
[1-2 sentence summary of what causes this build failure based on Microsoft Docs research]

## Diagnostic Hints
- [How to identify this specific error in build output - from Microsoft Docs]
- [What files/projects to check - based on official guidance]
- [Key indicators or patterns to look for - from error analysis]

## Detection Tokens
- `[Error message pattern 1 - extracted from build_stderr]`
- `[Error message pattern 2 - distinctive error signature]`
- `[Error code or property name - e.g., NU1008, MSB3644]`

## How to Fix

### Option 1: [Recommended Fix Name] (Recommended)
[Brief description of the recommended approach from Microsoft Docs]

**Steps:**
1. [Step 1 from Microsoft guidance]
2. [Step 2 with specific commands/configuration]
3. [Step 3 with code examples]

**Example (from Microsoft Docs code samples):**
```xml
<!-- Or other language based on fix context: csharp, powershell, etc. -->
[Code snippet from Microsoft code sample search]
```

### Option 2: [Alternative Fix Name]
[Alternative approach if recommended fix is not suitable]

**Steps:**
1. [Alternative step 1]
2. [Alternative step 2]

**When to use:** [Explain scenarios where this alternative is better]

### Option 3: [Workaround Name]
[Workaround if fix is complex or breaking]

**Steps:**
1. [Workaround step 1]
2. [Workaround step 2]

**Note:** [Warning about limitations of workaround]

## Root Cause
[Explanation from Microsoft Docs of WHY this error occurs]
- [Technical detail 1 from documentation]
- [Technical detail 2 from research]
- [Version or dependency information]

## Notes
- [Important details about the fix from Microsoft Docs]
- [When/why this error occurs - contextual information]
- [Prerequisites or version requirements - e.g., "NuGet 6.2+", ".NET SDK 6.0.300+"]
- [Related technologies or features]

## Safety
- **What changes:** [Files/configurations modified by the fix]
- **Breaking change risk:** [LOW | MEDIUM | HIGH] - [Explanation]
- **Reversibility:** [How to undo the fix if needed]
- **Testing:** [Recommendation on testing after applying fix]
- **Recommendation:** [Specific guidance on when to use this fix]

## Expected Outcome
After applying the fix:
- [What should happen after fix is applied]
- [How to verify the fix worked - specific validation steps]
- [Expected build output or behavior]

## References
- [Microsoft Docs URL 1 - main documentation article]
- [Microsoft Docs URL 2 - related guidance]
- [Code sample URL - if used from Microsoft samples]

## Example Solutions Affected
- {{solution_path}} ({{solution_name}})
```

**IMPORTANT**: The template above shows the STRUCTURE. You must fill it with REAL CONTENT from:
1. Microsoft Docs research (using MCP server queries)
2. AI structural reasoning about the error
3. Code examples from Microsoft code sample searches
4. Your understanding of the build failure context

DO NOT use placeholder text like "[TODO]" or "[Brief Description]" - synthesize actual helpful content.
