#!/usr/bin/env python3
"""Render static SINDARIN cards for all exact subprocess rows."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from ttbar_spinpol.genchain.card_renderer import render_file
from ttbar_spinpol.genchain.checksums import sha256
from ttbar_spinpol.genchain.process_matrix import load_process_rows, expected_counts
from ttbar_spinpol.genchain.seed_policy import derive_seed
from ttbar_spinpol.genchain.yamlio import write_json
POL={'unpolarized':(0.0,0.0),'LR100':(-1.0,1.0),'RL100':(1.0,-1.0)}
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve()
    template_root=repo/'sindarin/templates/full6f_365gev_v1'; output_root=repo/'sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1'; rows=load_process_rows(repo); rendered=[]
    for row in rows:
        pol=POL[row.polarization]; seed=derive_seed('full6f_365gev_ee_ttbar_spinpol_v1',row.sample_id,row.exact_subprocess_id,'render',0,'whizard')
        outdir=output_root/row.sample_id/row.exact_subprocess_id; common_out=outdir/'common'; common_out.mkdir(parents=True,exist_ok=True)
        context={'SQRTS_GEV':'365.0','ISR_HANDLER':'true','ISR_ENABLED':'true','ELECTRON_POLARIZATION':pol[0],'POSITRON_POLARIZATION':pol[1],'INTEGRATION_ITERATIONS':0,'INTEGRATION_CALLS':0,'PROCESS_NAME':row.process_name,'FINAL_STATE':', '.join(row.final_state),'N_EVENTS':0,'GENERATOR_SEED':seed,'OUTPUT_LHE':f'EOS_OUTPUT_ROOT/{row.sample_id}/{row.exact_subprocess_id}.lhe','PARAMETER_BLOCK':'','COMMON_DIR':str(common_out)}
        for inc in ['model','parameters','beams','isr','polarization','integration','event_output','diagnostics']: render_file(template_root/f'common/{inc}.inc.in', common_out/f'{inc}.inc', context)
        template=template_root/('dilepton/process.sin.in' if row.topology=='prompt_dilepton' else 'semileptonic/process.sin.in'); render_file(template,outdir/'process.sin',context)
        meta={'sample_id':row.sample_id,'channel':row.channel,'topology':row.topology,'polarization':row.polarization,'exact_subprocess_id':row.exact_subprocess_id,'final_state':list(row.final_state),'generator_seed':seed,'process_sin_sha256':sha256(outdir/'process.sin')}; write_json(outdir/'render_context.json',meta); rendered.append(meta)
    write_json(output_root/'rendered_cards_manifest.json',{'status':'PASS','counts':expected_counts(rows),'rendered_count':len(rendered),'rendered':rendered})
    print(json.dumps({'status':'PASS','rendered_count':len(rendered)},indent=2)); return 0
if __name__=='__main__': sys.exit(main())
