## Issue: Service Fabric BaseOutputPath / OutputPath Not Set
If a Service Fabric solution fails to build with messages like:
- `The BaseOutputPath property is not set`
- `The OutputPath property is not set`
for a project ending in `.SF.sfproj`, the project may be missing explicit output path property definitions.

### Diagnostic Hints
- Search build output for `BaseOutputPath` or `OutputPath` missing property errors.
- Identify all `.SF.sfproj` files in the repository (Service Fabric projects).
- Open each affected `.SF.sfproj` and check if it already defines `<BaseOutputPath>` or `<OutputPath>` within a `<PropertyGroup>`.
- Apply the fix ONLY if these elements are absent.

### Detection Tokens
- The BaseOutputPath property is not set
- The OutputPath property is not set
- .SF.sfproj

## Fix:
```pwsh
# Enumerate Service Fabric project files (diagnostic)
pwsh -Command "Get-ChildItem -Recurse -Filter *.SF.sfproj | Select-Object -ExpandProperty FullName"

# Apply output path fix via maintained script (additive, idempotent)
pwsh -File scripts/apply_sf_output_path_fix.ps1 -RepoRoot <repo_root>

# (Workflow tools will run restore_solution.py and build_solution.py; direct msbuild invocation not required here.)
```

### Notes
- The script injects the XML snippet BEFORE the first `<Import Project=` element when present, else before `</Project>`.
- The script skips projects that already define `<BaseOutputPath>`.
- Safe to re-run; it won't duplicate the snippet.
- After applying the fix, proceed with normal workflow restore/build tools (no manual msbuild required).

### Safety
- This modification is additive and does not remove existing properties.
- Review diffs before committing changes back to a remote.

### Expected Outcome
- Build succeeds for previously failing Service Fabric projects, eliminating BaseOutputPath/OutputPath errors.

### Example Solutions with this Error
- C:\Users\sacheu\speckit_repos\example_repo\ServiceFabricApp\ServiceFabricApp.sln

---
**Created**: 2025-10-21 23:45:00
**Last Updated**: 2025-10-21 23:45:00
