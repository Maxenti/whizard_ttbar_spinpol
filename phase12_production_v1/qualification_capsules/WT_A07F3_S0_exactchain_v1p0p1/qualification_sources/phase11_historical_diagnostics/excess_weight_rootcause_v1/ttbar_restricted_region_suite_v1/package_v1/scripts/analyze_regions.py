#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,math
from collections import defaultdict
from pathlib import Path
import sys;sys.path.insert(0,str(Path(__file__).resolve().parent));from common import write_tsv
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);a=p.parse_args();c=a.campaign_dir.resolve();out=c/'analysis';out.mkdir(exist_ok=True)
with (out/'node_numerical_metrics.tsv').open(newline='') as f:m=list(csv.DictReader(f,delimiter='\t'))
# Use fixed descendants only; each elementary cell is an independent disjoint integral.
g=defaultdict(list)
for r in m:
 if r['stage']=='fixed' and r.get('region_id'): g[(r['window_id'],r['recipe_id'],r['seed_id'])].append(r)
rows=[]
aggmap={'II':'DR','IL':'SR_PLUS','IH':'SR_PLUS','LI':'SR_MINUS','HI':'SR_MINUS','LL':'NR','LH':'NR','HL':'NR','HH':'NR'}
for key,v in sorted(g.items()):
 byrid={r['region_id']:r for r in v}
 if len(byrid)!=9: continue
 def summ(ids):
  vals=[float(byrid[i]['final_integral_fb']) for i in ids];errs=[float(byrid[i]['final_error_fb']) for i in ids];return sum(vals),math.sqrt(sum(e*e for e in errs))
 tot,te=summ(list(byrid)); dr,dre=summ(['II']); sp,spe=summ(['IL','IH']); sm,sme=summ(['LI','HI']); nr,nre=summ(['LL','LH','HL','HH'])
 rows.append(dict(window_id=key[0],recipe_id=key[1],seed_id=key[2],n_regions=9,total_fb=tot,total_error_fb=te,DR_fb=dr,DR_error_fb=dre,SR_PLUS_fb=sp,SR_PLUS_error_fb=spe,SR_MINUS_fb=sm,SR_MINUS_error_fb=sme,NR_fb=nr,NR_error_fb=nre))
write_tsv(out/'region_sums.tsv',rows);print(f'REGION_SUMS={out/"region_sums.tsv"}');print('ANALYZE_REGIONS=PASS')
