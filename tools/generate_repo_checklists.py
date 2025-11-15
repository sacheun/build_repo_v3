#!/usr/bin/env python3
"""Generate repository checklist files per task-generate-repo-task-checklists specification.
Usage:
  python tools/generate_repo_checklists.py --input repositories.txt [--append]
"""
import os, sys, json, argparse, datetime, re

SPEC_TEMPLATE = """# Task Checklist: {repo_name}
Repository: {repo_url}
Generated: {timestamp}

## Repo Tasks (Sequential Pipeline - Complete in Order)
- [ ] (1) [MANDATORY] [SCRIPTABLE] Clone repository to local directory → @task-clone-repo
- [ ] (2) [MANDATORY] [SCRIPTABLE] Find all solution files in repository → @task-find-solutions
- [ ] (3) [MANDATORY] [SCRIPTABLE] Generate per-solution checklist files → @task-generate-solution-task-checklists
- [ ] (4) [MANDATORY] [SCRIPTABLE] Search for README file in repository → @task-search-readme
- [ ] (5) [MANDATORY] [NON-SCRIPTABLE] Scan README and extract setup commands → @task-scan-readme
- [ ] (6) [MANDATORY] [NON-SCRIPTABLE] Execute safe commands from README → @task-execute-readme

## Repo Variables Available
- {{{{repo_url}}}} → {repo_url}
- {{{{repo_name}}}} → {repo_name}
- {{{{clone_path}}}} →
- {{{{repo_directory}}}} →
- {{{{solutions_json}}}} →
- {{{{readme_content}}}} →
- {{{{readme_filename}}}} →
- {{{{commands_extracted}}}} →
- {{{{executed_commands}}}} →
- {{{{skipped_commands}}}} →

## For Agents Resuming Work
Follow these rules *exactly* when resuming execution:

1. Identify the **first `[ ]` task** in the checklist.
2. [MANDATORY] tasks must be completed in numbered order (1 → 2 → 3 → 4 → 5 → 6)
3. Execute its corresponding prompt file (from `@task-...`).
4. After successful completion, update this checklist and mark `[x]`.
5. Do **not** end the run until all required tasks are completed.

## Execution Notes
- [SCRIPTABLE] tasks: clone, search-readme, find-solutions, generate-solution-task-checklists
- [NON-SCRIPTABLE] tasks: scan-readme, execute-readme
- Mark completed tasks with [x]
- Each referenced `@task-*` file is an independent prompt that must be executed completely before continuing.
""".replace('\r','')

def iso_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

def normalize_url(u:str)->str:
    u=u.strip()
    if not u: return ''
    u=re.sub(r'/+$','',u)
    return u

def derive_name(url:str)->str:
    # Preserve .git in url but strip for name extraction only
    if '/_git/' in url:
        seg=url.split('/_git/',1)[1]
    else:
        seg=url.rsplit('/',1)[-1]
    seg=re.sub(r'/+$','',seg)
    if seg.lower().endswith('.git'):
        seg=seg[:-4]
    return seg

def read_input(path:str):
    ignored=[]; entries=[]
    if not os.path.isfile(path):
        return [], ignored, True
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            raw=line.rstrip('\n')
            if not raw.strip() or raw.lstrip().startswith('#'): continue
            if not raw.strip().lower().startswith('https://'):
                ignored.append(raw)
                continue
            url=normalize_url(raw)
            name=derive_name(url)
            entries.append((name.lower(), name, url))
    # unique by lower name
    dedup={k:v for k,v,orig in entries}
    # We must retain original case of name; use last occurrence deterministic (stable due to dict insertion Python 3.7+)
    unique=[]; seen=set()
    for lower,name,url in sorted(entries, key=lambda x: x[1].lower()):
        if lower in seen: continue
        seen.add(lower)
        unique.append({'repo_name': name, 'repo_url': url})
    return unique, ignored, False

def load_existing_master(path:str):
    existing_names=set()
    if not os.path.isfile(path):
        return existing_names
    with open(path,'r',encoding='utf-8') as f:
        for line in f:
            if line.startswith('- ['):
                m=re.match(r'- \[[x ]\] ([^ ]+) \[', line)
                if m:
                    existing_names.add(m.group(1).lower())
    return existing_names

def write_master(path:str, repos, append_mode):
    timestamp=iso_now()
    lines=[]
    if append_mode and os.path.isfile(path):
        with open(path,'r',encoding='utf-8') as f:
            existing=f.read().splitlines()
        lines=existing
        # update Generated line only
        for i,l in enumerate(lines):
            if l.startswith('Generated: '):
                lines[i]=f'Generated: {timestamp}'
                break
        # append new repos after last repo line
        existing_names=set()
        for l in lines:
            if l.startswith('- ['):
                m=re.match(r'- \[[x ]\] ([^ ]+) \[', l)
                if m:
                    existing_names.add(m.group(1).lower())
        for r in repos:
            if r['repo_name'].lower() in existing_names: continue
            lines.append(f"- [ ] {r['repo_name']} [{r['repo_url']}]")
    else:
        lines.append(f'Generated: {timestamp}')
        for r in repos:
            lines.append(f"- [ ] {r['repo_name']} [{r['repo_url']}]")
    content='\n'.join(lines)+'\n'
    with open(path,'w',encoding='utf-8', newline='\n') as f:
        f.write(content)
    return path, sum(1 for l in lines if l.startswith('- ['))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', default='repositories.txt')
    ap.add_argument('--append', action='store_true')
    args=ap.parse_args()
    input_file=args.input
    append_mode=args.append
    mode='append' if append_mode else 'reset'
    verification_errors=[]

    # Step1 directory prep
    tasks_dir='./tasks'; output_dir='./output'; temp_dir='./temp-script'
    if append_mode:
        for d in (tasks_dir, output_dir, temp_dir):
            os.makedirs(d, exist_ok=True)
        if not os.path.isfile(input_file):
            verification_errors.append({'type':'MissingInput','target':input_file,'detail':'Input file not found'})
        print('✅ Step 1 complete — proceeding to Step 2')
    else:
        for d in (tasks_dir, output_dir, temp_dir):
            if os.path.isdir(d):
                for root,dirs,files in os.walk(d, topdown=False):
                    for name in files: os.remove(os.path.join(root,name))
                    for name in dirs: os.rmdir(os.path.join(root,name))
            os.makedirs(d, exist_ok=True)
        if not os.path.isfile(input_file):
            verification_errors.append({'type':'MissingInput','target':input_file,'detail':'Input file not found'})
        print('✅ Step 1 complete — proceeding to Step 2')

    # Step2 read & normalize
    repos, ignored, missing = read_input(input_file)
    if missing:
        # repos empty handled
        if not verification_errors: # ensure missing error recorded
            verification_errors.append({'type':'MissingInput','target':input_file,'detail':'Input file not found'})
    print(f"✅ Step 2 complete — proceeding to Step 3 (repos={len(repos)} ignored={len(ignored)})")

    # Step3 determine to process
    master_path=os.path.join(tasks_dir,'all_repository_checklist.md')
    if append_mode:
        existing=load_existing_master(master_path)
        to_process=[r for r in repos if r['repo_name'].lower() not in existing]
        skipped=[r for r in repos if r['repo_name'].lower() in existing]
    else:
        to_process=repos
        skipped=[]
    print(f"✅ Step 3 complete — proceeding to Step 4 (total={len(repos)} to_process={len(to_process)} skipped={len(skipped)})")

    # Step4 master checklist
    try:
        write_master(master_path, repos, append_mode)
        print(f"✅ Step 4 complete — proceeding to Step 5 (master={master_path})")
    except Exception as e:
        verification_errors.append({'type':'MasterWriteError','target':master_path,'detail':str(e)})
        print('❌ Step 4 failed — recorded; proceeding to Step 5')

    # Step5 individual files
    generated_paths=[]
    for r in to_process:
        fname=f"{r['repo_name']}_repo_checklist.md"
        fpath=os.path.join(tasks_dir,fname)
        if append_mode and os.path.isfile(fpath):
            print(f"✅ Step 5 checkpoint (skipped existing {fname})")
            continue
        content=SPEC_TEMPLATE.format(repo_name=r['repo_name'], repo_url=r['repo_url'], timestamp=iso_now())
        try:
            with open(fpath,'w',encoding='utf-8', newline='\n') as f:
                f.write(content)
            # validation
            with open(fpath,'r',encoding='utf-8') as vf:
                data=vf.read().splitlines()
            if sum(1 for l in data if l.startswith('# Task Checklist:'))!=1 or sum(1 for l in data if l.startswith('## Repo Variables Available'))!=1:
                raise ValueError('Header count validation failed')
            generated_paths.append(fpath)
            print(f"✅ Step 5 checkpoint (created {fname})")
        except Exception as e:
            if os.path.isfile(fpath): os.remove(fpath)
            verification_errors.append({'type':'RepoFileError','target':fpath,'detail':str(e)})
            print(f"❌ Step 5 checkpoint (failed {fname})")
    print('✅ Step 5 complete — proceeding to Step 6')

    # Step6 populate base repo vars (already populated in template for url/name)
    for p in generated_paths:
        try:
            with open(p,'r',encoding='utf-8') as f: lines=f.read().splitlines()
            # ensure single occurrences of variable lines
            url_lines=[i for i,l in enumerate(lines) if l.startswith('- {{repo_url}}')]
            name_lines=[i for i,l in enumerate(lines) if l.startswith('- {{repo_name}}')]
            if len(url_lines)!=1 or len(name_lines)!=1:
                verification_errors.append({'type':'VariableDuplication','target':p,'detail':'Duplicate or missing repo_url/repo_name lines'})
                print(f"❌ Step 6 checkpoint (validation failed for {os.path.basename(p)})")
            else:
                print(f"✅ Step 6 checkpoint (validated vars for {os.path.basename(p)})")
        except Exception as e:
            verification_errors.append({'type':'VariableValidationError','target':p,'detail':str(e)})
            print(f"❌ Step 6 checkpoint (error reading {os.path.basename(p)})")
    print('✅ Step 6 complete — proceeding to Step 7')

    # Step7 structured JSON
    json_path=os.path.join(output_dir,f"{mode}_task5_generate-repo-checklists.json")
    result={
        'input_file': input_file,
        'append_mode': append_mode,
        'repositories_total': len(repos),
        'repositories_processed': len(to_process),
        'repositories_skipped': len(skipped),
        'generated_checklist_paths': generated_paths,
        'master_checklist_path': master_path if os.path.isfile(master_path) else None,
        'status': 'SUCCESS' if not verification_errors and len(repos)==len(to_process)+len(skipped) else 'FAIL',
        'timestamp': iso_now(),
        'verification_errors': verification_errors,
        'mode': mode
    }
    with open(json_path,'w',encoding='utf-8', newline='\n') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    print(f"✅ Step 7 checkpoint (output {json_path})")

if __name__=='__main__':
    main()
