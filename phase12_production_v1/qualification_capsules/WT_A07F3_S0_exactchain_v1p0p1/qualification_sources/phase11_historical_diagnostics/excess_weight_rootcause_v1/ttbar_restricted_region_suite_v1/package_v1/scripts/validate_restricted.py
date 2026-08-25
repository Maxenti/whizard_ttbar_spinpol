#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--campaign-dir',type=Path,required=True);a=p.parse_args();c=a.campaign_dir.resolve();T=json.loads((c/'frozen_config/validation_thresholds.json').read_text())
with (c/'analysis/node_numerical_metrics.tsv').open(newline='') as f: m=list(csv.DictReader(f,delimiter='\t'))
with (c/'collected/node_summary.tsv').open(newline='') as f:n=list(csv.DictReader(f,delimiter='\t'))
issues=[]
if any(r['output_status']!='PASS' for r in n):issues.append('technical outputs incomplete/failing')
# Adaptive family must have 8/8 diagnostic numerical-screen pass for qualification candidate.
for aid in [f'A{i:02d}' for i in range(15)]:
 x=[r for r in m if r['stage']=='adaptive' and r['adaptive_id']==aid]
 if len(x)!=8:
  issues.append(f'{aid}: expected 8 parsed adaptive seed results, found {len(x)}')
 elif sum(int(r['numerical_screen_pass']) for r in x)<8:
  issues.append(f'{aid}: not 8/8 numerical-screen stable')
# F0/F1 equal-budget paired pull diagnostic.
by=defaultdict(dict)
for r in m:
 if r['stage']=='fixed':by[(r['adaptive_id'],r['seed_id'])][r['fixed_id']]=r
pair=[]
for k,v in sorted(by.items()):
 if 'F0' in v and 'F1' in v:
  a0,a1=v['F0'],v['F1'];d=float(a0['final_integral_fb'])-float(a1['final_integral_fb']);den=math.hypot(float(a0['final_error_fb']),float(a1['final_error_fb']));pull=d/den if den else math.nan;pair.append((k,pull));
  if abs(pull)>T['fixed_pair']['max_abs_normalized_difference']:issues.append(f'{k}: F0/F1 pull {pull:.3g}')
out=c/'analysis/restricted_validation_report.txt';out.write_text('RESTRICTED WT INTEGRATION VALIDATION\n===================================\n'+('\n'.join(issues) if issues else 'All predeclared integration diagnostic screens pass.')+'\n\nIMPORTANT: this does not replace generation-envelope stress, cross-grid event-level validation, or final-recipe rehearsal.\n')
print(out.read_text());print('RESTRICTED_VALIDATION_STATUS='+('PASS_INTEGRATION_SCREEN' if not issues else 'FAIL_OR_INCOMPLETE'))
