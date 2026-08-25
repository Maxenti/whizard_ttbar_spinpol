#!/usr/bin/env python3
"""Plot unrestricted region fractions and monolithic-closure pulls."""
from __future__ import annotations
import argparse,csv
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);a=p.parse_args();c=a.campaign_dir.resolve()
import matplotlib.pyplot as plt
out=c/'analysis/plots';out.mkdir(parents=True,exist_ok=True)
q=c/'analysis/region_sums.tsv'
if q.is_file():
 with q.open(newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
 keys=sorted(set((x['window_id'],x['recipe_id']) for x in r))
 for wid,rec in keys:
  x=sorted([z for z in r if z['window_id']==wid and z['recipe_id']==rec],key=lambda z:z['seed_id'])
  seeds=[z['seed_id'] for z in x]; total=[float(z['total_fb']) for z in x]
  fig,ax=plt.subplots(figsize=(9,5)); bottom=[0.0]*len(x)
  for col,label in [('DR_fb','DR'),('SR_PLUS_fb','SR+'),('SR_MINUS_fb','SR-'),('NR_fb','NR')]:
   vals=[float(z[col]) for z in x]; ax.bar(seeds,vals,bottom=bottom,label=label);bottom=[a+b for a,b in zip(bottom,vals)]
  ax.set_ylabel('cross section [fb]');ax.set_title(f'{wid} {rec}: unrestricted full-ME kinematic partition');ax.legend();fig.tight_layout();fig.savefig(out/f'region_components_{wid}_{rec}.png',dpi=180);plt.close(fig)
cl=c/'analysis/region_vs_monolithic.tsv'
if cl.is_file():
 with cl.open(newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
 if r:
  labels=[f"{z['recipe_id']}:{z['seed_id']}" for z in r]; vals=[float(z['pull']) for z in r]
  fig,ax=plt.subplots(figsize=(max(10,len(r)*0.35),5));ax.axhline(0,linewidth=1);ax.plot(range(len(vals)),vals,marker='o',linestyle='none');ax.set_xticks(range(len(labels)),labels,rotation=90);ax.set_ylabel('(region sum - monolithic)/combined error');ax.set_title('Nine-cell closure pulls');fig.tight_layout();fig.savefig(out/'region_monolithic_closure_pulls.png',dpi=180);plt.close(fig)
print(f'PLOT_DIR={out}');print('PLOT_REGIONS=PASS')
