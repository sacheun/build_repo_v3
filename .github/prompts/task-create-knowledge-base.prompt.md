@task-create-knowledge-base solution_checklist={{solution_checklist}}

---
temperature: 0.1
---

Task name: task-create-knowledge-base


## Description:
This task creates new knowledge base articles when @task-search-kb returns NOT_FOUND. It researches the error using Microsoft Docs MCP server, synthesizes fix instructions from official documentation, and creates a comprehensive KB article with diagnostic hints, fix options, and safety guidance.

** IMPORTANT - ONLY RUN WHEN NEEDED **:
- This task should ONLY be invoked when kb_search_status in solution_checklist  == NOT_FOUND
- If kb_search_status == FOUND or SKIPPED, do NOT create a new KB article
- Check the kb_search_status before proceeding

## Execution Policy

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

## Instructions (Follow these steps exactly in sequence)


### Step 1 — Prerequisite Check (MANDATORY)
1. Verify this task should run.
   - If kb_search_status == FOUND: return `kb_create_status=SKIPPED`, reason=`"existing KB article found"`,  proceed to Step 6.
   - If kb_search_status == SKIPPED: return `kb_create_status=SKIPPED`, reason=`"build succeeded"`,  proceed to Step 6.
   - If kb_search_status == NOT_FOUND: proceed to Step 2.

### Step 2 — Research Using Microsoft Docs MCP Server (MANDATORY)
   - Always use the `microsoftdocs/mcp` server. Build search terms from `errors[]`, `error_code`, `error_type`, and `detection_tokens`; log each query as `[KB-CREATE] Querying Microsoft Docs MCP server for: {query}`.
   - Call **mcp_microsoftdocs_microsoft_docs_search**, capture result counts, and shortlist URLs that explain the failure. Record each chosen link for later citation.
   - When the fix needs code, call **mcp_microsoftdocs_microsoft_code_sample_search** (specify language such as `xml`, `csharp`, or `powershell`) and extract the snippet that best illustrates Microsoft’s guidance.
   - If the search summaries lack detail, fetch the full article with **mcp_microsoftdocs_microsoft_docs_fetch** and note prerequisites, version requirements, or compatibility warnings.
   - Summarize the official guidance: root cause, recommended remediation path, alternatives, prerequisites, and risks. These insights drive the content you will draft in Step 3.

### Step 3 — Synthesize Fix Instructions (MANDATORY)
   - Convert the research into clear guidance covering the sections below. Keep the tone instructional and base every statement on Microsoft Docs material.
     * **Issue Description:** Two-sentence overview of what triggers the failure.
     * **Diagnostic Hints:** How to spot the problem in logs or project files.
     * **Fix Options:** Document the recommended fix, plus alternates or workarounds when Microsoft provides them; include commands and expected outcomes.
     * **Root Cause:** Explain why the failure occurs, referencing relevant technologies, configurations, or versions.
     * **Notes:** Capture prerequisites, breaking-change considerations, or related features mentioned by Microsoft.
     * **Safety & Testing:** Warn about files/settings changed, risk level, rollback steps, and post-fix validation to perform.

### Step 4 — Generate KB Article File (MANDATORY)
   - Create a filename from `error_signature` (lowercase, letters/digits/`_`/`-`, `.md` suffix) and place the file under `./knowledge_base_markdown/` using `create_file`.
   - Populate the document by following the **Knowledge Base Article Template** verbatim—same headings, order, and hierarchy. Replace every placeholder with the researched content from Step 3, add detection tokens, reference URLs gathered in Step 2, and list affected solutions (include `{{solution_path}}`).
   - Do not leave placeholders or speculative guidance; every section must be grounded in Microsoft documentation.

### Step 5 — Checklist Update & Variable Refresh (INLINE ONLY)

1. Open `{{solution_checklist}}` (fresh read).
2. Locate the task line for `@task-create-knowledge-base` for this attempt.
3. Mark task as:
   - `[x] ... - KB CREATED` when `kb_create_status == SUCCESS`
   - `[x] ... - SKIPPED` when `kb_create_status == SKIPPED`
   - `[x] ... - ERROR` when a failure occurred
4. Update Solution Variables in **### Solution Variables**:
   - `kb_article_status` → CREATED | SKIPPED | ERROR
   - `kb_file_path` → absolute path if created, else `N/A`
5. Do not alter unrelated lines.
6. Save atomically.

### Step 6 — FINAL VERIFICATION AND REDO SAFEGUARD

1. Re-open `{{solution_checklist}}` from disk (no cached content).
2. Verify:
   - Task line present and correctly marked `[x]`.
   - Variables updated exactly according to Step 5 results.
   - `kb_file_path` exists when `kb_create_status == SUCCESS`.
3. If any check fails:
   - Log: `VERIFICATION FAILED — RESTARTING`
   - Re-run Steps 1–5 once.
4. Re-run verification.
5. If still failing:
   - Set `kb_create_status=ERROR`
   - Set `kb_article_status=ERROR`
   - Log `VERIFICATION_ABORTED`
6. On success, log `VERIFICATION_PASSED`.


## Output Contract:
- kb_create_status: SUCCESS | SKIPPED
- kb_file_path: string (absolute path to created .md file, null if skipped)
- microsoft_docs_urls: array[string] (URLs referenced in research)
- detection_tokens: array[string] Array of error signatures from task-search-knowledge-base
- error_signature: string Generated signature for filename (e.g., "nu1008_central_package")
- error_code: string Error code if applicable (e.g., "NU1008", "MSB3644")
- error_type: string Error type (e.g., "NuGet", "MSBuild", "Compiler", "Platform")
- build_stderr: string Standard error output from build command (for additional context)
- errors: array[string] Array of diagnostic error codes from build task (e.g., ["NU1008", "MSB3644"])
- warnings: array[string] Array of diagnostic warning codes from build task (e.g., ["NU1101", "CS0618"])


## Implementation Notes:
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

--- 

## Knowledge Base Article Template:
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


---
