#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math,statistics,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import numerical_metrics,write_tsv
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);p.add_argument('--thresholds',type=Path);a=p.parse_args();c=a.campaign_dir.resolve();col=c/'collected';out=c/'analysis';out.mkdir(exist_ok=True)
th=a.thresholds or c/'frozen_config/validation_thresholds.json'; T=json.loads(th.read_text())
with (col/'iteration_rows.tsv').open(newline='') as f: rs=list(csv.DictReader(f,delimiter='\t'))
# Normalize numeric strings from either old or new collectors.
g=defaultdict(list)
for r in rs:
 try:
  x=dict(r); 
  for k in ['line_number','iteration','calls']: x[k]=int(float(x[k]))
  for k in ['integral_fb','error_fb','relative_error','reported_err_pct','accuracy','efficiency_pct']: x[k]=float(x[k])
  x.setdefault('row_kind','iteration')
  # Old collector did not mark aggregate rows. Infer: duplicate iteration number with larger calls and extra summary often occurs.
  g[r.get('node') or r.get('mode')].append(x)
 except Exception: pass
metrics=[]
for node,rows in g.items():
 # If old collector has no row_kind, mark last duplicate/larger-call rows as aggregate heuristically.
 if all(x.get('row_kind','')=='iteration' for x in rows):
  by=defaultdict(list)
  for x in rows: by[x['iteration']].append(x)
  for vv in by.values():
   if len(vv)>1:
    mx=max(vv,key=lambda x:x['calls'])
    if mx['calls']>max(z['calls'] for z in vv if z is not mx): mx['row_kind']='aggregate'
 m=numerical_metrics(rows)
 if not m: continue
 r0=rows[0]; rec=dict(node=node,stage=r0.get('stage',''),mode=r0.get('mode',''),adaptive_id=r0.get('adaptive_id',''),fixed_id=r0.get('fixed_id',''),seed_id=r0.get('seed_id',''),recipe_id=r0.get('recipe_id',''),region_id=r0.get('region_id',''),window_id=r0.get('window_id',''));rec.update(m)
 A=T['adaptive']; rec['numerical_screen_pass']=int(m['max_postfirst_reported_error_pct']<=A['max_postfirst_reported_error_pct'] and m['max_accuracy']<=A['max_accuracy'] and m['max_normalized_iteration_jump']<=A['max_normalized_iteration_jump'] and m['final_relative_error_pct']<=A['max_final_relative_error_pct']);metrics.append(rec)
write_tsv(out/'node_numerical_metrics.tsv',metrics)
# family summaries by stage/adaptive/fixed/recipe/region/window
fam=defaultdict(list)
for r in metrics:fam[(r['stage'],r['adaptive_id'],r['fixed_id'],r['recipe_id'],r['region_id'],r['window_id'])].append(r)
fr=[]
for k,v in sorted(fam.items()):
 vals=[x['final_integral_fb'] for x in v if math.isfinite(x['final_integral_fb'])]; relrange=(max(vals)-min(vals))/statistics.mean(vals) if len(vals)>1 and statistics.mean(vals)!=0 else 0
 # inverse-variance consistency
 sw=sum(1/x['final_error_fb']**2 for x in v if x['final_error_fb']>0); mu=sum(x['final_integral_fb']/x['final_error_fb']**2 for x in v if x['final_error_fb']>0)/sw if sw else math.nan; chi=sum((x['final_integral_fb']-mu)**2/x['final_error_fb']**2 for x in v if x['final_error_fb']>0); nd=max(1,sum(x['final_error_fb']>0 for x in v)-1)
 fr.append(dict(stage=k[0],adaptive_id=k[1],fixed_id=k[2],recipe_id=k[3],region_id=k[4],window_id=k[5],n=len(v),screen_pass=sum(x['numerical_screen_pass'] for x in v),relative_range=relrange,reduced_chi2=chi/nd,weighted_mean_fb=mu,weighted_error_fb=math.sqrt(1/sw) if sw else math.nan))
write_tsv(out/'family_stability.tsv',fr)
print(f'NODE_METRICS={out/"node_numerical_metrics.tsv"}');print(f'FAMILY_STABILITY={out/"family_stability.tsv"}');print('ANALYZE_STABILITY=PASS')
