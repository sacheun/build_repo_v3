# Build Error Knowledge Base

This directory contains markdown files documenting known build errors and their fixes. Each knowledge base article follows a standardized format to help identify, diagnose, and resolve common build failures.

## Purpose

The knowledge base is automatically populated by the `@task-collect-knowledge-base` workflow task, which:
1. Analyzes build failures
2. Extracts "Detection Tokens" (error signatures)
3. Searches for existing articles with matching tokens
4. Creates new articles for novel errors

## Article Format

Each knowledge base article includes:

### Required Sections

1. **Issue Title**: Brief description of the error
2. **Diagnostic Hints**: How to identify this specific error
3. **Detection Tokens**: Error patterns used for automatic matching
4. **Fix**: PowerShell commands or scripts to resolve the issue
5. **Notes**: Important details about when/why this occurs
6. **Safety**: What the fix modifies and precautions
7. **Expected Outcome**: What should happen after applying the fix
8. **Example Solutions**: Paths to solutions that exhibited this error

### Optional Sections

- Prerequisites
- Related Issues
- References

## Workflow Integration

### Automatic Detection

When a build fails, the workflow:
1. Captures stderr output
2. Extracts detection tokens (error codes, property names, patterns)
3. Searches all .md files in this directory for matching tokens
4. If found: references existing article
5. If not found: creates new article with auto-generated template

### Manual Enhancement

Auto-generated articles require manual completion:
- Add specific diagnostic commands
- Create fix scripts in `/scripts` directory
- Document prerequisites
- Add detailed notes based on root cause analysis
- Test and verify fixes

## File Naming Convention

Filenames should be descriptive and use this format:
- Lowercase letters
- Underscores for spaces
- Include error type or code
- Examples:
  - `sf_baseoutputpath_missing.md`
  - `msb3644_reference_assembly_missing.md`
  - `cs0246_type_not_found.md`
  - `nuget_package_restore_failed.md`

## Example Article

See `sf_baseoutputpath_missing.md` for a complete example of a well-documented knowledge base article.

## Contributing

When adding new articles manually:
1. Follow the standardized format (see template in `task-collect-knowledge-base.md`)
2. Include clear detection tokens
3. Provide working fix commands
4. Test fixes before documenting
5. Add example solution paths

## Detection Token Best Practices

Good detection tokens are:
- Specific enough to identify the exact error
- Generic enough to match variations
- Free of file paths, line numbers, timestamps
- Include error codes when available (MSB####, CS####, NU####)
- Include property names or key identifiers

### Examples of Good Tokens
- `The BaseOutputPath property is not set`
- `error MSB3644`
- `Could not find file Microsoft.Build.Tasks.Core.dll`
- `.SF.sfproj`

### Examples of Poor Tokens
- `C:\Users\...\file.cs(123,45)` (too specific, includes path)
- `at 10:23:45` (includes timestamp)
- `error` (too generic)

## Maintenance

- Review auto-generated articles periodically
- Update fix scripts as solutions evolve
- Archive obsolete articles
- Keep detection tokens current
- Document new error patterns as discovered

---

**Last Updated**: 2025-10-21
**Workflow Version**: Run 12+
