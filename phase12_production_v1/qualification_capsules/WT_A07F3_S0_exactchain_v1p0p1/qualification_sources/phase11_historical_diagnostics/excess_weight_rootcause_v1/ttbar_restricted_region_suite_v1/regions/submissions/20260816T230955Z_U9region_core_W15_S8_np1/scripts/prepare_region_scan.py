#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import read_tsv,sha256,make_region_source,region_cut
from prepare_common import freeze_base,localize_common_paths,shellq

def main():
 p=argparse.ArgumentParser(); p.add_argument('--package-root',type=Path,required=True); p.add_argument('--repo',type=Path,required=True); p.add_argument('--source-card',type=Path,required=True); p.add_argument('--submission-dir',type=Path,required=True); p.add_argument('--output-root',type=Path,required=True); p.add_argument('--profile',choices=['core','extended','historical_fcc','window_scan'],default='core'); p.add_argument('--top-mass-GeV',type=float,default=172.5); p.add_argument('--half-width-GeV',type=float,default=15.0); p.add_argument('--allow-source-sha-mismatch',action='store_true'); a=p.parse_args()
 pkg=a.package_root.resolve(); repo=a.repo.resolve(); sub=a.submission_dir.resolve(); out=a.output_root
 orig_sha,srcdir=freeze_base(pkg,repo,a.source_card.resolve(),sub,a.allow_source_sha_mismatch)
 base=localize_common_paths(a.source_card.resolve().read_text(),srcdir,sub/'frozen_source')
 bins=read_tsv(sub/'frozen_config/region_bins.tsv'); recipes=read_tsv(sub/'frozen_config/region_recipes.tsv'); windows=read_tsv(sub/'frozen_config/region_windows.tsv'); seeds=read_tsv(sub/'frozen_config/seeds.tsv'); adap={x['adaptive_id']:x for x in read_tsv(sub/'frozen_config/adaptive_prescriptions.tsv')}; fixed={x['fixed_id']:x for x in read_tsv(sub/'frozen_config/fixed_prescriptions.tsv')}
 if a.profile=='core': recipes=[r for r in recipes if r['core']=='1']; win=[('W15',a.half_width_GeV)]
 elif a.profile=='extended': recipes=[r for r in recipes if r['extended']=='1']; win=[('W15',a.half_width_GeV)]
 elif a.profile=='historical_fcc': recipes=[r for r in recipes if r['historical']=='1']; win=[('W15',a.half_width_GeV)]
 else: recipes=[r for r in recipes if r['recipe_id']=='M1']; win=[(x['window_id'],float(x['half_width_GeV'])) for x in windows]
 # Make one frozen source tree per window+region because cuts are part of physics configuration.
 for wid,half in win:
  low=a.top_mass_GeV-half; high=a.top_mass_GeV+half
  for br in bins:
   rid=br['region_id']; d=sub/'region_sources'/wid/rid; (d/'common').mkdir(parents=True,exist_ok=True)
   import shutil; shutil.copytree(sub/'frozen_source/common',d/'common',dirs_exist_ok=True)
   if (sub/'frozen_source/render_context.json').is_file(): shutil.copy2(sub/'frozen_source/render_context.json',d/'render_context.json')
   cut=region_cut(rid,low,high); (d/'common/region_cuts.inc').write_text('# Full-ME kinematic partition; no diagram restriction.\n'+cut+'\n')
   text=base.replace(str(sub/'frozen_source/common'),str(d/'common'))
   text=make_region_source(text,str(d/'common/region_cuts.inc')); (d/'process.sin').write_text(text)
 # Common environment has source selected per-node by campaign.env generated wrapper variable REGION_SOURCE_ROOT.
 (sub/'campaign.env').write_text('\n'.join([f'REPO={shellq(repo)}',f'REGION_SOURCE_ROOT={shellq(sub/"region_sources")}',f'ORIGINAL_SOURCE_CARD={shellq(a.source_card.resolve())}',f'ORIGINAL_SOURCE_CARD_SHA256={shellq(orig_sha)}',f'OUTPUT_ROOT={shellq(out)}','']))
 # Region-aware wrappers set SOURCE_CARD and SHA then exec standard workers.
 (sub/'scripts/run_region_parent.sh').write_text('''#!/usr/bin/env bash\nset -euo pipefail\nREGION_ID=""; WINDOW_ID=""; REST=()\nwhile [[ $# -gt 0 ]]; do case "$1" in --region-id) REGION_ID="$2";shift 2;; --window-id) WINDOW_ID="$2";shift 2;; *) REST+=("$1");shift;; esac; done\nCAMPAIGN_DIR=""\nfor ((i=0;i<${#REST[@]};i++)); do [[ "${REST[$i]}" == --campaign-dir ]] && CAMPAIGN_DIR="${REST[$((i+1))]}"; done\nsource "$CAMPAIGN_DIR/campaign.env"\nSOURCE_CARD="$REGION_SOURCE_ROOT/$WINDOW_ID/$REGION_ID/process.sin"; export SOURCE_CARD; export FROZEN_SOURCE_CARD_SHA256=$(sha256sum "$SOURCE_CARD"|awk '{print $1}')\n# Standard worker sources campaign.env, so write a process-local overlay and point it through env variables is not possible. Create temp campaign.env copy? Instead worker accepts sourced variables only.\nTMPENV=$(mktemp "$CAMPAIGN_DIR/.campaign.env.region.XXXXXX")\ncp "$CAMPAIGN_DIR/campaign.env" "$TMPENV"\nprintf "SOURCE_CARD='%s'\\nFROZEN_SOURCE_CARD_SHA256='%s'\\n" "$SOURCE_CARD" "$FROZEN_SOURCE_CARD_SHA256" >> "$TMPENV"\n# Standard worker is taught to honor CAMPAIGN_ENV_OVERRIDE. Use mktemp rather\n# than a PID-only name because different execute hosts can share a PID.\nexport CAMPAIGN_ENV_OVERRIDE="$TMPENV"\nset +e\n"$CAMPAIGN_DIR/scripts/run_adaptive_parent.sh" "${REST[@]}"\nRC=$?\nset -e\nrm -f "$TMPENV"\nexit "$RC"\n'''); (sub/'scripts/run_region_parent.sh').chmod(0o755)
 (sub/'scripts/run_region_child.sh').write_text((sub/'scripts/run_region_parent.sh').read_text().replace('run_adaptive_parent.sh','run_fixed_child.sh')); (sub/'scripts/run_region_child.sh').chmod(0o755)
 # Patch copied standard workers to support an override env file generated by region wrapper.
 for nm in ['run_adaptive_parent.sh','run_fixed_child.sh']:
  q=sub/'scripts'/nm; t=q.read_text(); t=t.replace('CAMPAIGN_ENV="$CAMPAIGN_DIR/campaign.env"','CAMPAIGN_ENV="${CAMPAIGN_ENV_OVERRIDE:-$CAMPAIGN_DIR/campaign.env}"'); q.write_text(t)
 parent=sub/'region_parent.sub'; child=sub/'region_child.sub'
 parent.write_text(f'''universe = vanilla\nexecutable = {sub}/scripts/run_region_parent.sh\narguments = --region-id $(region_id) --window-id $(window_id) --mode $(mode) --adaptive-id $(adaptive_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root $(node_output_root)\ninitialdir = {sub}\nshould_transfer_files = NO\ngetenv = True\nrequest_cpus = 1\nrequest_memory = 3000MB\nrequest_disk = 6000MB\n+JobFlavour = "tomorrow"\noutput=logs/$(mode).$(ClusterId).$(ProcId).out\nerror=logs/$(mode).$(ClusterId).$(ProcId).err\nlog=logs/region_parent.$(ClusterId).log\nnotification=Never\nqueue\n''')
 child.write_text(f'''universe = vanilla\nexecutable = {sub}/scripts/run_region_child.sh\narguments = --region-id $(region_id) --window-id $(window_id) --mode $(mode) --parent-mode $(parent_mode) --adaptive-id $(adaptive_id) --fixed-id $(fixed_id) --seed-id $(seed_id) --campaign-dir {sub} --output-root $(node_output_root)\ninitialdir = {sub}\nshould_transfer_files = NO\ngetenv = True\nrequest_cpus = 1\nrequest_memory = 3000MB\nrequest_disk = 6000MB\n+JobFlavour = "tomorrow"\noutput=logs/$(mode).$(ClusterId).$(ProcId).out\nerror=logs/$(mode).$(ClusterId).$(ProcId).err\nlog=logs/region_child.$(ClusterId).log\nnotification=Never\nqueue\n''')
 dag=[]; rows=[]
 for wid,half in win:
  for br in bins:
   rid=br['region_id']
   for rr in recipes:
    rec,aid,fid=rr['recipe_id'],rr['adaptive_id'],rr['fixed_id']; ar=adap[aid]; fr=fixed[fid]
    for sr in seeds:
     sid=sr['seed_id']; pm=f'{wid}_{rid}_{rec}_{aid}_{sid}'; pn='P_'+pm
     dag += [f'JOB {pn} {parent}',f'VARS {pn} region_id="{rid}" window_id="{wid}" mode="{pm}" adaptive_id="{aid}" seed_id="{sid}" node_output_root="{out/wid/rid/rec}"']
     od_parent=out/wid/rid/rec/'adaptive'/pm
     rows.append(dict(node=pn,stage='adaptive',mode=pm,parent_mode='',adaptive_id=aid,fixed_id='',seed_id=sid,adaptive_seed=sr['adaptive_seed'],fixed_seed=sr['fixed_seed'],adaptive_schedule=ar['schedule'],fixed_schedule='',recipe_id=rec,region_id=rid,window_id=wid,aggregate=br['aggregate'],half_width_GeV=half,output_dir=str(od_parent)))
     cm=f'{pm}_{fid}'; cn='C_'+cm
     dag += [f'JOB {cn} {child}',f'VARS {cn} region_id="{rid}" window_id="{wid}" mode="{cm}" parent_mode="{pm}" adaptive_id="{aid}" fixed_id="{fid}" seed_id="{sid}" node_output_root="{out/wid/rid/rec}"',f'PARENT {pn} CHILD {cn}','']
     od_child=out/wid/rid/rec/'fixed'/pm/fid
     rows.append(dict(node=cn,stage='fixed',mode=cm,parent_mode=pm,adaptive_id=aid,fixed_id=fid,seed_id=sid,adaptive_seed=sr['adaptive_seed'],fixed_seed=sr['fixed_seed'],adaptive_schedule=ar['schedule'],fixed_schedule=fr['suffix_schedule'],recipe_id=rec,region_id=rid,window_id=wid,aggregate=br['aggregate'],half_width_GeV=half,output_dir=str(od_child)))
 expected={'core':432,'extended':720,'historical_fcc':144,'window_scan':432}[a.profile]
 if len(rows)!=expected: raise SystemExit(f'ERROR expected {expected} nodes got {len(rows)}')
 (sub/'campaign.dag').write_text('\n'.join(dag)+'\n'); fields=list(rows[0])
 with (sub/'campaign_manifest.tsv').open('w',newline='') as f: ww=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');ww.writeheader();ww.writerows(rows)
 design=dict(schema='phase11_unrestricted_region_partition_v1',physics='unrestricted full6f matrix element with disjoint kinematic top-mass regions',profile=a.profile,top_mass_GeV=a.top_mass_GeV,windows=win,total_nodes=len(rows),recipes=[r['recipe_id'] for r in recipes],seeds=8,regions=9,original_source_sha256=orig_sha,output_root=str(out))
 (sub/'CAMPAIGN_DESIGN.json').write_text(json.dumps(design,indent=2)+'\n'); (sub/'DECISION_POLICY.txt').write_text('All nine elementary cells retain the unrestricted matrix element. Region closure against the monolithic unrestricted result is mandatory. No region is a diagram-level classification. Qualification is by recipe across all seeds and all cells.\n')
 targets=[q for q in sub.rglob('*') if q.is_file() and q.name!='PRE_SUBMISSION_INPUTS.sha256']
 with (sub/'PRE_SUBMISSION_INPUTS.sha256').open('w') as f:
  for q in sorted(targets): f.write(f'{sha256(q)}  {q}\n')
 print(f'SUBMISSION_DIR={sub}');print(f'OUTPUT_ROOT={out}');print(f'TOTAL_DAG_NODES={len(rows)}');print('REGION_PREPARE=PASS')
if __name__=='__main__': main()
