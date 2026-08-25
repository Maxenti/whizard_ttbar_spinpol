#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent)); from common import parse_log,write_tsv

def loadj(p):
 try:return json.loads(p.read_text())
 except:return {}
def findlog(d):
 for n in ['console.log','whizard.log']:
  if (d/n).is_file(): return d/n
 x=sorted(d.glob('*.log'));return x[0] if x else None
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);p.add_argument('--outdir',type=Path);a=p.parse_args();c=a.campaign_dir.resolve();out=a.outdir or c/'collected';out.mkdir(parents=True,exist_ok=True)
with (c/'campaign_manifest.tsv').open(newline='') as f: manifest=list(csv.DictReader(f,delimiter='\t'))
nodes=[];iters=[]
for r in manifest:
 d=Path(r['output_dir']); status=(d/'STATUS.txt').read_text().strip() if (d/'STATUS.txt').is_file() else 'MISSING'
 md={}
 for n in ['metadata.json','fixed_child_metadata.json']:
  if (d/n).is_file():md=loadj(d/n);break
 log=findlog(d)
 nr=dict(r);nr.update(output_status=status,metadata_status=md.get('status',''),whizard_rc=md.get('whizard_rc',''),phs_sha256=md.get('phs_sha256',md.get('final_phs_sha256','')),vg2_sha256=md.get('vg2_sha256',md.get('final_vg2_sha256','')),parent_vg2_sha256=md.get('parent_vg2_sha256',''),reuse_message_count=md.get('reuse_message_count',''),new_grid_init_count=md.get('new_grid_init_count',''),phs_unchanged=md.get('phs_unchanged',''),console_log=str(log or ''),artifact_present=int((d/'integration_artifacts.tar.gz').is_file()))
 nodes.append(nr)
 if log:
  for x in parse_log(log):
   z={k:r.get(k,'') for k in ['node','stage','mode','adaptive_id','fixed_id','seed_id','recipe_id','region_id','window_id','aggregate']};z.update(x);iters.append(z)
write_tsv(out/'node_summary.tsv',nodes);write_tsv(out/'iteration_rows.tsv',iters)
print(f'NODE_SUMMARY={out/"node_summary.tsv"}');print(f'ITERATION_ROWS={out/"iteration_rows.tsv"}');print(f'NODES_EXPECTED={len(nodes)}');print(f'NODES_PASS={sum(x["output_status"]=="PASS" for x in nodes)}');print('COLLECT_CAMPAIGN=PASS')
