#!/usr/bin/env python3
"""Build Phase 5 integration matrix without running WHIZARD."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from ttbar_spinpol.genchain.process_matrix import load_process_rows
from ttbar_spinpol.genchain.seed_policy import derive_seed
from ttbar_spinpol.genchain.yamlio import write_json
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); ap.add_argument('--stage',default='qualification'); args=ap.parse_args(); repo=args.repo.resolve(); entries=[]
    for row in load_process_rows(repo): entries.append({'sample_id':row.sample_id,'exact_subprocess_id':row.exact_subprocess_id,'polarization':row.polarization,'process_name':row.process_name,'integration_seed':derive_seed('full6f_365gev_ee_ttbar_spinpol_v1',row.sample_id,row.exact_subprocess_id,args.stage,0,'integration'),'rendered_card':f'sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1/{row.sample_id}/{row.exact_subprocess_id}/process.sin','status':'planned_not_executed'})
    out=repo/'inspection_outputs'/'phase5_static_integration_matrix.json'; write_json(out,{'status':'PLANNED_NOT_EXECUTED','stage':args.stage,'entries':entries}); print(out); return 0
if __name__=='__main__': sys.exit(main())
