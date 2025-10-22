"""
Task: Collect knowledge base for build failures
Executed via exec() from task_build_solution.py
Variables from parent scope: sol, repo_name, DEBUG, build_result, result
"""

import os
import re
from datetime import datetime

solution_name = sol['name']

print(f"\n--- Task: task-collect-knowledge-base ---")
print(f"Solution: {solution_name}")

# Check DEBUG mode
DEBUG_MODE = DEBUG if 'DEBUG' in dir() else os.environ.get('DEBUG') == '1'

kb_status = "SKIPPED"
kb_file_path = ""
detection_tokens = []

# Only process if build failed
if build_result == "SUCCESS":
    print("KB collection SKIPPED (build succeeded)")
    if DEBUG_MODE:
        print(f"[KB-DEBUG] Build status: {build_result}, KB collection skipped")
    kb_status = "SKIPPED"
else:
    print("KB collection PROCESSING (build failed)")
    if DEBUG_MODE:
        print(f"[KB-DEBUG] Build status: {build_result}, proceeding with KB collection")
    
    # Extract stderr from result object
    if DEBUG_MODE:
        print(f"[KB-DEBUG] result object: type={type(result)}, has_stderr={hasattr(result, 'stderr') if result else 'result is None'}")
        if result:
            print(f"[KB-DEBUG] result attributes: {dir(result)}")
    
    build_stderr = result.stderr if result and hasattr(result, 'stderr') else ""
    build_stdout = result.stdout if result and hasattr(result, 'stdout') else ""
    
    if DEBUG_MODE:
        print(f"[KB-DEBUG] stderr length: {len(build_stderr)}, stdout length: {len(build_stdout)}")
        print(f"[KB-DEBUG] build_stderr is {'empty' if not build_stderr else 'populated'}")
    
    if not build_stderr:
        print("No stderr available for KB analysis")
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Checking stdout for errors (length: {len(build_stdout)})")
            if build_stdout:
                print(f"[KB-DEBUG] First 500 chars of stdout: {build_stdout[:500]}")
        
        # Fallback: check stdout if stderr is empty (dotnet build often writes errors to stdout)
        if build_stdout:
            print("Analyzing stdout for error patterns (stderr was empty)...")
            build_stderr = build_stdout  # Use stdout as error source
            if DEBUG_MODE:
                print(f"[KB-DEBUG] Using stdout as error source (length: {len(build_stderr)} chars)")
            # Don't skip - we have stdout to analyze
        else:
            kb_status = "SKIPPED"
    
    if build_stderr:
        # Extract detection tokens from build stderr
        print(f"Analyzing {len(build_stderr)} chars of stderr...")
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Build failed, analyzing stderr (length: {len(build_stderr)} chars)")
            print(f"[KB-DEBUG] First 500 chars of stderr: {build_stderr[:500]}")
        
        # Pattern 1: Property errors (e.g., "The BaseOutputPath property is not set")
        property_errors = re.findall(r'The (\w+) property is not set', build_stderr, re.IGNORECASE)
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Pattern 'property_errors' matched: {property_errors}")
        for prop in property_errors:
            token = f"The {prop} property is not set"
            detection_tokens.append(token)
            print(f"Detected property error: {token}")
        
        # Pattern 2: MSBuild errors (e.g., "error MSB4018:")
        msbuild_errors = re.findall(r'error (MSB\d+):', build_stderr)
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Pattern 'msbuild_errors' matched: {msbuild_errors}")
        for err in msbuild_errors:
            detection_tokens.append(err)
            print(f"Detected MSBuild error: {err}")
        
        # Pattern 3: C# compiler errors (e.g., "error CS0246:")
        cs_errors = re.findall(r'error (CS\d+):', build_stderr)
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Pattern 'cs_errors' matched: {cs_errors}")
        for err in cs_errors:
            detection_tokens.append(err)
            print(f"Detected C# error: {err}")
        
        # Pattern 4: NuGet errors (e.g., "error NU1102:")
        nuget_errors = re.findall(r'error (NU\d+):', build_stderr)
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Pattern 'nuget_errors' matched: {nuget_errors}")
        for err in nuget_errors:
            detection_tokens.append(err)
            print(f"Detected NuGet error: {err}")
        
        # Pattern 5: Service Fabric specific errors
        if '.SF.sfproj' in build_stderr or 'Service Fabric' in build_stderr:
            detection_tokens.append('.SF.sfproj')
            print("Detected Service Fabric project")
            if DEBUG_MODE:
                print("[KB-DEBUG] Pattern 'Service Fabric' matched")
        
        # Pattern 6: Missing file/assembly errors
        missing_files = re.findall(r'Could not find (?:file|assembly) ["\']([^"\']+)["\']', build_stderr, re.IGNORECASE)
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Pattern 'missing_files' matched: {missing_files}")
        for file in missing_files:
            # Normalize: remove paths, keep just filename
            filename = os.path.basename(file)
            token = f"Could not find {filename}"
            detection_tokens.append(token)
            print(f"Detected missing file: {token}")
        
        # Remove duplicates
        detection_tokens = list(set(detection_tokens))
        print(f"Total unique detection tokens: {len(detection_tokens)}")
        if DEBUG_MODE:
            print(f"[KB-DEBUG] Extracted {len(detection_tokens)} unique tokens: {detection_tokens}")
            print(f"[KB-DEBUG] Regex pattern matches - Property: {len(property_errors)}, MSBuild: {len(msbuild_errors)}, CS: {len(cs_errors)}, NuGet: {len(nuget_errors)}, Missing files: {len(missing_files)}")
        
        if not detection_tokens:
            print("No detection tokens found in stderr")
            if DEBUG_MODE:
                print("[KB-DEBUG] No detection tokens extracted - stderr may not contain recognizable error patterns")
            kb_status = "SKIPPED"
        else:
            # Search existing KB articles for matching tokens
            kb_dir = 'knowledge_base_markdown'
            os.makedirs(kb_dir, exist_ok=True)
            
            if DEBUG_MODE:
                print(f"[KB-DEBUG] KB directory exists: {os.path.exists(kb_dir)}")
            
            found_match = False
            matched_file = None
            
            if os.path.exists(kb_dir):
                kb_files = [f for f in os.listdir(kb_dir) if f.endswith('.md') and f != 'README.md']
                if DEBUG_MODE:
                    print(f"[KB-DEBUG] Searching {len(kb_files)} KB articles for matches")
                
                for kb_file in kb_files:
                    if DEBUG_MODE:
                        print(f"[KB-DEBUG] Checking {kb_file}...")
                    kb_path = os.path.join(kb_dir, kb_file)
                    try:
                        with open(kb_path, 'r', encoding='utf-8') as f:
                            kb_content = f.read()
                        
                        # Check if any detection token matches
                        for token in detection_tokens:
                            if token.lower() in kb_content.lower():
                                found_match = True
                                matched_file = kb_file
                                print(f"Found matching KB article: {kb_file} (token: {token})")
                                if DEBUG_MODE:
                                    print(f"[KB-DEBUG] Token '{token}' found in {kb_file}")
                                break
                        
                        if found_match:
                            break
                    except Exception:
                        pass
            
            if found_match:
                kb_status = "SUCCESS"
                kb_file_path = os.path.join(kb_dir, matched_file)
                print(f"KB reference: {kb_file_path}")
                if DEBUG_MODE:
                    print(f"[KB-DEBUG] Match found! Using existing KB: {kb_file_path}")
            else:
                # Create new KB article
                print("No matching KB article found, creating new one...")
                if DEBUG_MODE:
                    print("[KB-DEBUG] No matching KB article found, creating new one")
                
                # Generate error signature for filename
                signature_parts = []
                for token in detection_tokens[:3]:  # Use first 3 tokens
                    # Normalize token to lowercase, replace spaces/special chars with underscores
                    normalized = re.sub(r'[^a-z0-9]+', '_', token.lower()).strip('_')
                    signature_parts.append(normalized)
                    if DEBUG_MODE:
                        print(f"[KB-DEBUG] Signature normalization: {token} → {normalized}")
                
                error_signature = '_'.join(signature_parts)[:50]  # Limit length
                kb_filename = f"{error_signature}.md"
                kb_file_path = os.path.join(kb_dir, kb_filename)
                
                if DEBUG_MODE:
                    print(f"[KB-DEBUG] Signature parts: {signature_parts}")
                    print(f"[KB-DEBUG] Error signature: {error_signature}")
                    print(f"[KB-DEBUG] Filename: {kb_filename}")
                
                # Generate issue title
                if property_errors:
                    issue_title = f"Property Not Set: {', '.join(property_errors[:3])}"
                elif msbuild_errors:
                    issue_title = f"MSBuild Error: {', '.join(msbuild_errors[:3])}"
                elif cs_errors:
                    issue_title = f"C# Compiler Error: {', '.join(cs_errors[:3])}"
                elif nuget_errors:
                    issue_title = f"NuGet Error: {', '.join(nuget_errors[:3])}"
                else:
                    issue_title = "Build Error"
                
                # Generate KB article
                kb_article = f"""## Issue: {issue_title}

### Diagnostic Hints
1. Review the build error output below for specific error codes and messages.
2. Check for missing properties, dependencies, or configuration issues.
3. Search this file for detection tokens that match your build errors.

### Detection Tokens
"""
                for token in detection_tokens:
                    kb_article += f"- `{token}`\n"
                
                kb_article += f"""
## Fix:

**Step 1: Identify the root cause**
```powershell
# Review the build stderr output
# {build_stderr[:500]}...
```

**Step 2: Apply the fix**
```powershell
# TODO: Add specific fix commands after manual investigation
# Example: dotnet restore
# Example: Update project file properties
```

### Notes
- This KB article was auto-generated from build failure on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Repository: {repo_name}
- Solution: {solution_name}
- **MANUAL ENHANCEMENT REQUIRED**: Add tested fix commands and detailed steps.

### Safety
- Review all changes before committing
- Test fix on a single solution first
- Consider impact on other projects

### Expected Outcome
After applying the fix:
- `dotnet restore` should complete without errors
- `dotnet build` should complete successfully
- All projects in solution should build

### Example Solutions
- {sol['path']}
"""
                
                # Write KB article
                try:
                    with open(kb_file_path, 'w', encoding='utf-8') as f:
                        f.write(kb_article)
                    print(f"Created new KB article: {kb_file_path}")
                    if DEBUG_MODE:
                        print(f"[KB-DEBUG] Article content length: {len(kb_article)} chars")
                        print(f"[KB-DEBUG] Created KB article: {kb_file_path}")
                    kb_status = "SUCCESS"
                except Exception as e:
                    print(f"Error creating KB article: {e}")
                    if DEBUG_MODE:
                        print(f"[KB-DEBUG] Failed to create KB article: {e}")
                    kb_status = "FAIL"

# Update tracking files
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if DEBUG_MODE:
    print(f"[KB-DEBUG] Final status: kb_status={kb_status}, kb_file_path={kb_file_path}")

# Update solution-results.csv
with open('results/solution-results.csv', 'a', encoding='utf-8') as f:
    f.write(f"{repo_name},{solution_name},task-collect-knowledge-base,{kb_status},{timestamp}\n")

# Update solution-progress.md checkbox
with open('results/solution-progress.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if f"| {repo_name} | {solution_name} |" in line:
        parts = line.split('|')
        parts[5] = ' [x] ' if kb_status in ["SUCCESS", "SKIPPED"] else ' [ ] '
        lines[i] = '|'.join(parts)
        break

with open('results/solution-progress.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"KB Status: {kb_status}")
if kb_file_path:
    print(f"KB File: {kb_file_path}")
