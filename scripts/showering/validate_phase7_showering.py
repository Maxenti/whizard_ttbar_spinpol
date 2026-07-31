#!/usr/bin/env python3
"""Static Phase 7 shower-handoff and HepMC identity validation."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from ttbar_spinpol.genchain.identity import global_event_id
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.yamlio import load_yaml
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); ap.add_argument('--lhe',type=Path,default=None); args=ap.parse_args(); repo=args.repo.resolve(); handoff=load_yaml(repo/'analysis_contracts/shower_handoff_contract.yaml'); identity=load_yaml(repo/'analysis_contracts/hepmc_event_identity_contract.yaml'); errors=[]; warnings=[]
    if handoff.get('handoff_policy',{}).get('output_format')!='HepMC3': errors.append('handoff output format must be HepMC3')
    if not handoff.get('handoff_policy',{}).get('event_identity_preservation_required'): errors.append('event identity preservation must be required')
    if global_event_id('campaign','sample','sub','unpol','shard',1)!=global_event_id('campaign','sample','sub','unpol','shard',1): errors.append('global event ID not deterministic')
    runtime_status='INCOMPLETE_LHE_INPUT' if args.lhe is None else ('STATIC_LHE_PRESENT_NOT_SHOWERED' if args.lhe.is_file() else 'FAIL')
    if runtime_status=='INCOMPLETE_LHE_INPUT': warnings.append('no LHE file supplied; runtime handoff validation remains incomplete')
    if runtime_status=='FAIL': errors.append('LHE file does not exist: '+str(args.lhe))
    status='PASS' if not errors else 'FAIL'; out=write_phase_record(repo,'phase7_shower_handoff_static',status,{'runtime_status':runtime_status,'errors':errors,'warnings':warnings,'identity_algorithm':identity.get('global_event_id',{}).get('algorithm')},['PHASE 7 SHOWER/HepMC IDENTITY STATIC VALIDATION','='*72,f'STATUS: {status}',f'RUNTIME_STATUS: {runtime_status}',f'ERRORS: {len(errors)}',f'WARNINGS: {len(warnings)}']); print(out); return 0 if not errors else 1
if __name__=='__main__': sys.exit(main())
