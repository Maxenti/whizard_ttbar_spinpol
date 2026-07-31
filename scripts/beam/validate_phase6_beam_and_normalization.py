#!/usr/bin/env python3
"""Static Phase 6 beam/ISR/polarization/normalization validation."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from ttbar_spinpol.genchain.normalization import expected_yield, weighted_efficiency
from ttbar_spinpol.genchain.phase_records import write_phase_record
from ttbar_spinpol.genchain.yamlio import load_yaml
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve(); cfg=load_yaml(repo/'campaigns/full6f_365gev_ee_ttbar_spinpol_v1/beam/beam_configurations.yaml'); errors=[]; beams=cfg.get('beam_configurations',{}); pol=cfg.get('polarizations',{})
    if 'monochromatic_isr_on' not in beams or 'monochromatic_isr_off' not in beams: errors.append('required monochromatic controls missing')
    if pol.get('LR100',{}).get('electron_polarization') != -1.0: errors.append('LR100 electron polarization mismatch')
    if pol.get('RL100',{}).get('positron_polarization') != -1.0: errors.append('RL100 positron polarization mismatch')
    if abs(weighted_efficiency(25,100)-0.25)>1e-15: errors.append('weighted efficiency formula failed')
    if abs(expected_yield(1000,0.5,0.2)-100)>1e-15: errors.append('yield formula failed')
    status='PASS' if not errors else 'FAIL'; out=write_phase_record(repo,'phase6_beam_normalization_static',status,{'errors':errors,'beam_configurations':sorted(beams)},['PHASE 6 BEAM/ISR/POLARIZATION/NORMALIZATION VALIDATION','='*72,f'STATUS: {status}',f'ERRORS: {len(errors)}']); print(out); return 0 if not errors else 1
if __name__=='__main__': sys.exit(main())
