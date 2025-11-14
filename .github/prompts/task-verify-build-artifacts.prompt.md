@task-verify-build-artifacts solution_path={{solution_path}} repo_name={{repo_name}}
---
temperature: 0.0
---

Task name: task-verify-build-artifacts

## Description
Validate that a build for the specified Visual Studio solution produced all expected output artifacts. The task inspects each project referenced by the solution, derives the expected output files, and confirms they exist. Missing artifacts must trigger a clear failure message and the solution checklist must be updated to reflect the outcome.

## Reliability Framework (MANDATORY)
- **Sequential enforcement**: Execute Steps 1->10 in order without skipping, merging, or reordering.
- **Checkpointing**: After each step print `OK Step N complete` or `FAIL Step N failed - <reason>` (replace `<reason>` with specifics).
- **Atomic reads/writes**: Load files fully into memory before parsing; perform all checklist edits atomically (write to temp then replace).
- **Fail fast**: On missing artifacts, record details, set `status=FAIL`, then continue through checklist update and final structured output steps.

---
## Instructions (Follow this Step by Step)

### Step 1 - Input & Readiness Validation (MANDATORY)
1. Confirm `{{solution_path}}` is provided, is a string, and the file exists.
2. Require the path to end with `.sln`; otherwise record a contract error, set `status=FAIL`, and proceed to Step 10.
3. Derive `solution_name = basename(solution_path)` and `solution_root = dirname(solution_path)`.
4. Read the checklist and locate `build_status` within `### Solution Variables`. If missing, set `status=FAIL` (`result="CONTRACT_ERROR"`) and proceed to Step 10.
5. If `build_status != SUCCEEDED`:
   - Set `status = SKIPPED`, `result = "BUILD_NOT_READY"`, and maintain `verify_status = "SKIPPED"` for use in later steps.
   - Initialize empty lists `expected_artifacts = []`, `missing = []`, `verified = []` (later converted to `(blank)` values in Step 9).
   - Emit the Step 1 checkpoint explaining the skip and jump directly to Step 9 (skip Steps 2–8).
6. Otherwise initialize `verify_status = "PENDING_VERIFICATION"` and emit checkpoint summarizing resolved paths.


### Step 2 - Load Solution Projects (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 2 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. Parse the solution file and extract project entries referencing buildable project types (`.csproj`, `.vbproj`, `.vcxproj`, `.fsproj`).
3. Normalize relative project paths to absolute paths based on `solution_root`.
4. Build `projects[] = [{ project_path, project_guid, project_type_guid }]`.
5. Emit checkpoint reporting the project count.


### Step 3 - Project File Validation (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 3 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. Verify each project file in `projects[]` exists on disk.
3. For any missing file, log `FAIL Missing project file: <path>` and mark status `FAIL` (continue through Step 10).
4. Emit checkpoint once validation completes.

### Step 4 - Extract Build Metadata (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 4 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. Load each project file as XML (namespace tolerant).
3. Resolve configuration/platform using precedence: `Release|AnyCPU`, `Release|x64`, `Release|x86`, then unconditional `PropertyGroup`.
4. For each project capture:
   - `OutputPath`
   - `OutDir` (if present)
   - `AssemblyName`
   - `TargetFramework` and/or `TargetFrameworks`
   - `TargetExt` (fallback to `.dll` or `.exe` as appropriate)
4. Emit checkpoint listing each project with derived `OutputPath` and `AssemblyName`.

### Step 5 - Determine Expected Artifacts (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 5 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. Use captured metadata to compute expected artifact paths:
   - Prefer `OutDir`; otherwise combine project directory, `OutputPath`, and `AssemblyName + TargetExt`.
   - Normalize to absolute paths.
2. If `TargetFrameworks` specifies multiple frameworks, create an artifact path per framework.
3. Populate `expected_artifacts[] = [{ project_path, artifacts: [paths...] }]`.
4. Emit checkpoint summarizing artifact counts per project.

### Step 6 - Filesystem Verification (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 6 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. Check existence of every artifact path with `os.path.exists`.
3. Append found artifacts to `verified[]` and missing ones to `missing[]`.
4. Emit checkpoint reporting totals for verified vs missing artifacts.

### Step 7 - Failure Handling (MANDATORY)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 7 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. If `missing[]` is non-empty:
   - Print each failure as `FAIL Missing artifact: <path>`.
   - Set `status = FAIL`, `result = "MISSING_ARTIFACTS"`, and `verify_status = "FAILED"`.
3. Otherwise set `status = SUCCESS`, `result = "ARTIFACTS_VERIFIED"`, and `verify_status = "SUCCEEDED"`.
4. Emit checkpoint with status summary.

### Step 8 - Success Confirmation (CONDITIONAL)
1. If `verify_status = "SKIPPED"`, log the checkpoint as `OK Step 8 complete - skipped (build_status != SUCCEEDED)` and continue to Step 9.
2. If `status = SUCCESS`, print `OK Verified artifact: <path>` for every entry in `verified[]`.
3. Emit checkpoint confirming acknowledgements were printed (or skipped when failing).


### Step 9 - Checklist Update (MANDATORY)
1. Locate solution checklist at `tasks/{{repo_name}}_{{solution_name}}_solution_checklist.md`.
   - If the file is missing, record a verification error, set `status=FAIL`, and proceed to Step 10.
2. Mark the task line containing `@task-validate-build-artifacts` as complete by changing `- [ ]` → `- [x]` (leave marked if already completed).
3. Prepare variable updates using deterministic ordering based on the `verify_status` value tracked through prior steps:
   - Write `verify_status` → one of `"SKIPPED"`, `"SUCCEEDED"`, or `"FAILED"` as currently held.
   - If `verify_status = "SKIPPED"`, set the artifact variables (`expected_artifacts`, `missing_artifacts`, `verified_artifacts`) → the literal text `(blank)`.
   - If `verify_status = "SUCCEEDED"`, use the collected arrays to populate the artifact variables.
   - If `verify_status = "FAILED"`, set `missing_artifacts` to the missing list while still filling `expected_artifacts` and `verified_artifacts` as above.
   * `expected_artifacts` → pipe-delimited string of all expected artifact paths (sorted, absolute). If none, set to `(blank)`.
   * `missing_artifacts` → pipe-delimited string of missing artifact paths (sorted). If none, set to `(blank)`.
   * `verified_artifacts` → pipe-delimited string of verified artifact paths (sorted). If none, set to `(blank)`.
4. Ensure exactly one `- <name> → <value>` line exists for each variable; insert if missing, replace otherwise. Preserve other variable lines unchanged.
5. Write the checklist atomically and emit the step checkpoint.

### Step 10 - Verification & Structured Output (ALWAYS EXECUTE)
1. Re-open the checklist from disk and confirm:
   - The task line for `@task-validate-build-artifacts` is checked.
   - `verify_status` matches the computed outcome (`SUCCEEDED`, `FAILED`, or `SKIPPED`).
   - `expected_artifacts`, `missing_artifacts`, and `verified_artifacts` exactly match the pipe-delimited strings (or `(blank)`) derived in Step 9 from the `expected`, `missing`, and `verified` arrays (or `(blank)` when skipping).
   - If any check fails, retry Step 9 once; if still inconsistent, append to verification errors and keep `status=FAIL`.
2. Compose JSON payload:
   ```json
   {
     "solution_path": "...",
     "solution_name": "...",
     "projects_total": <int>,
     "artifacts_verified": ["..."],
     "artifacts_missing": ["..."],
       "status": "SUCCESS|FAIL|SKIPPED",
       "result": "ARTIFACTS_VERIFIED|MISSING_ARTIFACTS|CONTRACT_ERROR|BUILD_NOT_READY",
     "timestamp": "<ISO8601 UTC>",
     "warnings": [],
     "errors": []
   }
   ```
3. Write JSON to stdout and atomically to `output/{{solution_name}}_verify-build-artifacts.json`.
4. Emit final checkpoint.

---

## Example Success Output
```
ProjectA -> bin/Release/ProjectA.dll
ProjectB -> bin/Release/ProjectB.exe
```

## Example Failure Output
```
FAIL Missing artifact: bin/Release/ProjectB.exe
```

## Implementation Notes
- Strip XML namespaces before querying elements to simplify parsing.
- Use `os.path.abspath` and `os.path.normpath` for consistent path comparisons.
- When `TargetExt` is missing, infer `.dll` for library projects and `.exe` for executables using project type or output kind heuristics.
- Do not modify solution or project files; read-only inspection only.
- Keep console output concise while clearly listing missing artifacts.
