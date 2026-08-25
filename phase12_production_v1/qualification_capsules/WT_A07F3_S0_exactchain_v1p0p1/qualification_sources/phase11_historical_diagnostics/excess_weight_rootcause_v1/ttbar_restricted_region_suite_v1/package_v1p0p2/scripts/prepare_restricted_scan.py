#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_tsv,sha256,make_restricted_wt,WT_RESTRICTION
from prepare_common import freeze_base,localize_common_paths,shellq

def main():
 p=argparse.ArgumentParser(); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--repo',type=Path,required=True); p.add_argument('--source-card',type=Path,required=True); p.add_argument('--submission-dir',type=Path,required=True); p.add_argument('--output-root',type=Path,required=True); p.add_argument('--allow-source-sha-mismatch',action='store_true'); a=p.parse_args()
 pkg=a.package_root.resolve(); repo=a.repo.resolve(); sub=a.submission_dir.resolve(); out=a.output_root
 orig_sha,srcdir=freeze_base(pkg,repo,a.source_card.resolve(),sub,a.allow_source_sha_mismatch)
 text=localize_common_paths(a.source_card.resolve().read_text(),srcdir,sub/'frozen_source'); text=make_restricted_wt(text)
 card=sub/'frozen_source/process.sin'; card.write_text(text); frozen_sha=sha256(card)
 adaptive=read_tsv(sub/'frozen_config/adaptive_prescriptions.tsv'); fixed=read_tsv(sub/'frozen_config/fixed_prescriptions.tsv'); seeds=read_tsv(sub/'frozen_config/seeds.tsv')
 fmain=[x for x in fixed if x['fixed_id'] in {'F0','F1','F2'}]; fcc=[x for x in fixed if x['fixed_id']=='F3'][0]
 env='\n'.join([f'REPO={shellq(repo)}',f'SOURCE_CARD={shellq(card)}',f'FROZEN_SOURCE_CARD_SHA256={shellq(frozen_sha)}',f'ORIGINAL_SOURCE_CARD={shellq(a.source_card.resolve())}',f'ORIGINAL_SOURCE_CARD_SHA256={shellq(orig_sha)}',f'OUTPUT_ROOT={shellq(out)}',''])
 (sub/'campaign.env').write_text(env)
 parent=sub/'adaptive_parent.sub'; child=sub/'fixed_child.sub'; ctl=sub/'full_control.sub'
 parent.write_text(f'''universe = vanilla\nexecutable = {sub}/scripts/run_adaptive_parent.sh\narguments = --mode $(mode) --adaptive-id $(adaptive_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root $(node_output_root)\ninitialdir = {sub}\nshould_transfer_files = NO\ngetenv = True\nrequest_cpus = 1\nrequest_memory = 3000MB\nrequest_disk = 6000MB\n+JobFlavour = "tomorrow"\noutput = logs/$(mode).$(ClusterId).$(ProcId).out\nerror = logs/$(mode).$(ClusterId).$(ProcId).err\nlog = logs/adaptive.$(ClusterId).log\nnotification = Never\nqueue\n''')
 child.write_text(f'''universe = vanilla\nexecutable = {sub}/scripts/run_fixed_child.sh\narguments = --mode $(mode) --parent-mode $(parent_mode) --adaptive-id $(adaptive_id) --fixed-id $(fixed_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root $(node_output_root)\ninitialdir = {sub}\nshould_transfer_files = NO\ngetenv = True\nrequest_cpus = 1\nrequest_memory = 3000MB\nrequest_disk = 6000MB\n+JobFlavour = "tomorrow"\noutput = logs/$(mode).$(ClusterId).$(ProcId).out\nerror = logs/$(mode).$(ClusterId).$(ProcId).err\nlog = logs/fixed.$(ClusterId).log\nnotification = Never\nqueue\n''')
 ctl.write_text(f'''universe = vanilla\nexecutable = {sub}/scripts/run_full_control.sh\narguments = --mode $(mode) --seed-id $(seed_id) --campaign-dir {sub} --output-root $(node_output_root)\ninitialdir = {sub}\nshould_transfer_files = NO\ngetenv = True\nrequest_cpus = 1\nrequest_memory = 3000MB\nrequest_disk = 6000MB\n+JobFlavour = "tomorrow"\noutput = logs/$(mode).$(ClusterId).$(ProcId).out\nerror = logs/$(mode).$(ClusterId).$(ProcId).err\nlog = logs/control.$(ClusterId).log\nnotification = Never\nqueue\n''')
 dag=[]; rows=[]
 for ar in adaptive:
  for sr in seeds:
   aid,sid=ar['adaptive_id'],sr['seed_id']; pm=f'{aid}_{sid}'; pn='P_'+pm
   dag += [f'JOB {pn} {parent}',f'VARS {pn} mode="{pm}" adaptive_id="{aid}" seed_id="{sid}" node_output_root="{out}"']
   rows.append(dict(node=pn,stage='adaptive',mode=pm,parent_mode='',adaptive_id=aid,fixed_id='',seed_id=sid,adaptive_seed=sr['adaptive_seed'],fixed_seed=sr['fixed_seed'],adaptive_schedule=ar['schedule'],fixed_schedule='',recipe_id='',region_id='',window_id='',output_dir=str(out/'adaptive'/pm)))
   kids=[]
   fset=list(fmain)+( [fcc] if aid=='A07' else [] )
   for fr in fset:
    fid=fr['fixed_id']; cm=f'{pm}_{fid}'; cn='C_'+cm; kids.append(cn)
    dag += [f'JOB {cn} {child}',f'VARS {cn} mode="{cm}" parent_mode="{pm}" adaptive_id="{aid}" fixed_id="{fid}" seed_id="{sid}" node_output_root="{out}"']
    rows.append(dict(node=cn,stage='fixed',mode=cm,parent_mode=pm,adaptive_id=aid,fixed_id=fid,seed_id=sid,adaptive_seed=sr['adaptive_seed'],fixed_seed=sr['fixed_seed'],adaptive_schedule=ar['schedule'],fixed_schedule=fr['suffix_schedule'],recipe_id='',region_id='',window_id='',output_dir=str(out/'fixed'/pm/fid)))
   dag += [f'PARENT {pn} CHILD {" ".join(kids)}','']
 # Eight current-version VAMP+TAO controls reproduce historical integration algorithm/schedule but not historical beam spread/version.
 for sr in seeds:
  sid=sr['seed_id']; mode=f'FCCLEGACY_{sid}'; node='L_'+mode
  dag += [f'JOB {node} {ctl}',f'VARS {node} mode="{mode}" seed_id="{sid}" node_output_root="{out}"','']
  rows.append(dict(node=node,stage='control',mode=mode,parent_mode='',adaptive_id='FCCLEGACY',fixed_id='F3',seed_id=sid,adaptive_seed=sr['adaptive_seed'],fixed_seed=sr['fixed_seed'],adaptive_schedule='10:100000:"gw"',fixed_schedule='10:200000:""',recipe_id='FCCLEGACY',region_id='',window_id='',output_dir=str(out/'control'/mode)))
 if len(rows)!=496: raise SystemExit(f'ERROR expected 496 nodes got {len(rows)}')
 (sub/'campaign.dag').write_text('\n'.join(dag)+'\n')
 fields=list(rows[0]);
 with (sub/'campaign_manifest.tsv').open('w',newline='') as f: ww=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n'); ww.writeheader(); ww.writerows(rows)
 design=dict(schema='phase11_restricted_wt_qualification_v1',physics='WT-restricted 2->6 ttbar signal definition; LR100; current project beam/ISR contract',restriction=WT_RESTRICTION,total_nodes=496,adaptive_parents=120,main_fixed_children=360,fcc_schedule_children=8,legacy_numeric_controls=8,source_sha256=orig_sha,frozen_source_sha256=frozen_sha,output_root=str(out))
 (sub/'CAMPAIGN_DESIGN.json').write_text(json.dumps(design,indent=2)+'\n')
 (sub/'DECISION_POLICY.txt').write_text('Qualification is by prescription family across all eight frozen seeds. Never promote a favorable single seed. FCCLEGACY is diagnostic only and is not the primary production definition. Generation-envelope and event-level gates remain required after integration qualification.\n')
 targets=[p for p in sub.rglob('*') if p.is_file() and p.name!='PRE_SUBMISSION_INPUTS.sha256']
 with (sub/'PRE_SUBMISSION_INPUTS.sha256').open('w') as f:
  for q in sorted(targets): f.write(f'{sha256(q)}  {q}\n')
 print(f'SUBMISSION_DIR={sub}'); print(f'OUTPUT_ROOT={out}'); print('TOTAL_DAG_NODES=496'); print('RESTRICTED_PREPARE=PASS')
if __name__=='__main__': main()
