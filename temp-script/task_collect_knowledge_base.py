import os
import re
from datetime import datetime

# This script is executed via exec() from task_process_solutions.py
# Variables available from parent scope: sol, repo_name, DEBUG, build_result, result (subprocess result)

solution_name = sol['name']
solution_path = sol['path']
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Check if build succeeded - if so, skip knowledge base collection
if build_result == 'SUCCESS':
    if DEBUG == '1':
        print(f'[run12][kb] {solution_name}: SKIPPED (build succeeded)')
    kb_status = 'SKIPPED'
    kb_file_path = ''
else:
    # Build failed, proceed with knowledge base collection
    if DEBUG == '1':
        print(f'[run12][kb] {solution_name}: Analyzing build failure for knowledge base')
    
    # Get stderr from build result
    build_stderr = result.stderr if hasattr(result, 'stderr') and result.stderr else ''
    
    if not build_stderr:
        if DEBUG == '1':
            print(f'[run12][kb] {solution_name}: No stderr available, skipping')
        kb_status = 'SKIPPED'
        kb_file_path = ''
    else:
        # Extract detection tokens from stderr
        detection_tokens = []
        
        # Pattern 1: Property not set errors
        property_errors = re.findall(r'The (\w+) property is not set', build_stderr, re.IGNORECASE)
        detection_tokens.extend([f'The {prop} property is not set' for prop in property_errors])
        
        # Pattern 2: MSBuild errors
        msbuild_errors = re.findall(r'error (MSB\d+):', build_stderr)
        detection_tokens.extend([f'error {code}' for code in msbuild_errors])
        
        # Pattern 3: C# compilation errors
        cs_errors = re.findall(r'error (CS\d+):', build_stderr)
        detection_tokens.extend([f'error {code}' for code in cs_errors])
        
        # Pattern 4: NuGet errors
        nuget_errors = re.findall(r'error (NU\d+):', build_stderr)
        detection_tokens.extend([f'error {code}' for code in nuget_errors])
        
        # Pattern 5: Service Fabric specific
        if '.SF.sfproj' in build_stderr or 'ServiceFabric' in build_stderr:
            detection_tokens.append('Service Fabric project')
        
        # Pattern 6: Missing file/assembly
        missing_file = re.findall(r'Could not find (?:file|assembly) ["\']([^"\']+)["\']', build_stderr)
        detection_tokens.extend([f'Could not find file {os.path.basename(f)}' for f in missing_file[:3]])
        
        if DEBUG == '1':
            print(f'[run12][kb] Extracted {len(detection_tokens)} detection tokens: {detection_tokens[:5]}')
        
        # Generate error signature for filename
        error_signature = 'unknown_build_error'
        if property_errors:
            error_signature = f"{property_errors[0].lower()}_property_not_set"
        elif msbuild_errors:
            error_signature = f"msb_{msbuild_errors[0].lower()}"
        elif cs_errors:
            error_signature = f"cs_{cs_errors[0].lower()}"
        elif '.SF.sfproj' in build_stderr:
            error_signature = 'service_fabric_build_error'
        
        # Ensure knowledge base directory exists
        kb_dir = 'knowledge_base_markdown'
        os.makedirs(kb_dir, exist_ok=True)
        
        # Search existing knowledge base files for matching tokens
        kb_file_path = ''
        found_match = False
        
        if detection_tokens:
            for kb_file in os.listdir(kb_dir):
                if kb_file.endswith('.md'):
                    kb_path = os.path.join(kb_dir, kb_file)
                    with open(kb_path, 'r', encoding='utf-8', errors='ignore') as f:
                        kb_content = f.read()
                    
                    # Check if any detection token appears in the knowledge base file
                    for token in detection_tokens:
                        if token.lower() in kb_content.lower():
                            found_match = True
                            kb_file_path = kb_path
                            if DEBUG == '1':
                                print(f'[run12][kb] Found matching KB article: {kb_file}')
                            break
                    
                    if found_match:
                        break
        
        if found_match:
            kb_status = 'SUCCESS'
            print(f'[run12][kb] {solution_name}: Found existing KB article: {os.path.basename(kb_file_path)}')
        else:
            # Create new knowledge base article
            kb_filename = f'{error_signature}.md'
            kb_file_path = os.path.join(kb_dir, kb_filename)
            
            # Generate issue title from tokens
            if property_errors:
                issue_title = f"{property_errors[0]} Property Not Set"
            elif msbuild_errors:
                issue_title = f"MSBuild Error {msbuild_errors[0]}"
            elif cs_errors:
                issue_title = f"Compilation Error {cs_errors[0]}"
            else:
                issue_title = "Build Failure"
            
            # Create knowledge base article using template
            kb_article = f"""## Issue: {issue_title}
This build failure occurs when processing solution: {solution_name}

### Diagnostic Hints
- Search build output for the error patterns listed in Detection Tokens below.
- Identify affected project files in the solution.
- Check project configuration and dependencies.
- Review build logs for additional context.

### Detection Tokens
"""
            for token in detection_tokens[:10]:  # Limit to first 10 tokens
                kb_article += f"- {token}\n"
            
            kb_article += f"""
## Fix:
```pwsh
# Diagnostic: Identify affected files
# [Add specific diagnostic commands based on error type]

# Apply fix via script (to be created)
# pwsh -File scripts/fix_{error_signature}.ps1 -RepoRoot <repo_root>

# Note: After applying fix, re-run workflow restore/build tasks
```

### Notes
- This knowledge base article was auto-generated from build failure.
- Manual review and completion required.
- Add specific fix instructions based on root cause analysis.
- Document any prerequisites or dependencies.

### Safety
- Review all changes before applying.
- Test fix in isolated environment first.
- Create backup or commit current state before applying fixes.

### Expected Outcome
- Build should succeed after applying the appropriate fix.
- Verify by running: dotnet build "{solution_path}"

### Example Solutions with this Error
- {solution_path}

### Build Error Output (First 500 chars)
```
{build_stderr[:500]}
```

---
**Created**: {timestamp}
**Repository**: {repo_name}
**Solution**: {solution_name}
"""
            
            # Write knowledge base article
            with open(kb_file_path, 'w', encoding='utf-8') as f:
                f.write(kb_article)
            
            kb_status = 'SUCCESS'
            print(f'[run12][kb] {solution_name}: Created new KB article: {kb_filename}')
            
            if DEBUG == '1':
                print(f'[run12][kb] Article path: {kb_file_path}')
                print(f'[run12][kb] Detection tokens: {len(detection_tokens)}')

# Note: kb_status and kb_file_path are now available for next task or tracking
