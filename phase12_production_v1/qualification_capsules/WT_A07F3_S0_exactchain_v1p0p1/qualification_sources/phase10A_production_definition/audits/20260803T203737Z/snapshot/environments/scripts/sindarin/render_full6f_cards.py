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


def configure_generated_polarization_blocks(generated_root):
    """Apply WHIZARD-3.1.8-compatible polarization blocks after card rendering.

    Current campaign naming convention:
      *_unpol_* : omit polarization include entirely
      *_LR100_* : e- left,  e+ right => @(-1), @(+1)
      *_RL100_* : e- right, e+ left  => @(+1), @(-1)
    """
    root = Path(generated_root)
    if not root.exists():
        return {"unpol_scrubbed": 0, "lr_written": 0, "rl_written": 0}

    counts = {"unpol_scrubbed": 0, "lr_written": 0, "rl_written": 0}

    for card in sorted(root.glob("**/process.sin")):
        card_text = card.read_text(encoding="utf-8")
        card_lines = card_text.splitlines()
        card_str = str(card)

        if "_unpol_" in card_str:
            new_lines = [line for line in card_lines if "polarization.inc" not in line]
            if new_lines != card_lines:
                card.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                counts["unpol_scrubbed"] += 1
            continue

        pol = card.parent / "common" / "polarization.inc"

        if "_LR100_" in card_str:
            pol.write_text(
                "beams_pol_density = @(-1), @(+1)\n"
                "beams_pol_fraction = 100%, 100%\n",
                encoding="utf-8",
            )
            counts["lr_written"] += 1

        elif "_RL100_" in card_str:
            pol.write_text(
                "beams_pol_density = @(+1), @(-1)\n"
                "beams_pol_fraction = 100%, 100%\n",
                encoding="utf-8",
            )
            counts["rl_written"] += 1

    return counts



def scrub_unpolarized_polarization_includes(generated_root):
    """Remove polarization includes from unpolarized generated process cards.

    WHIZARD 3.1.8 rejects the zero-polarization block used in the initial scaffold.
    Unpolarized cards should omit polarization.inc entirely.
    """
    root = Path(generated_root)
    if not root.exists():
        return 0
    changed = 0
    for card in sorted(root.glob("*_unpol_*/**/process.sin")):
        lines = card.read_text(encoding="utf-8").splitlines()
        new_lines = [line for line in lines if "polarization.inc" not in line]
        if new_lines != lines:
            card.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            changed += 1
    return changed


WHIZARD_PARTICLE_NAMES = {
    "e-": "e1",
    "e+": "E1",
    "mu-": "e2",
    "mu+": "E2",
    "tau-": "e3",
    "tau+": "E3",
    "nu_e": "n1",
    "anti_nu_e": "N1",
    "nu_mu": "n2",
    "anti_nu_mu": "N2",
    "nu_tau": "n3",
    "anti_nu_tau": "N3",
    "anti_u": "ubar",
    "anti_d": "dbar",
    "anti_s": "sbar",
    "anti_c": "cbar",
    "anti_b": "bbar",
}

def to_whizard_particle(name: str) -> str:
    return WHIZARD_PARTICLE_NAMES.get(name, name)

POL={'unpolarized':(0.0,0.0),'LR100':(-1.0,1.0),'RL100':(1.0,-1.0)}
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',required=True,type=Path); args=ap.parse_args(); repo=args.repo.resolve()
    template_root=repo/'sindarin/templates/full6f_365gev_v1'; output_root=repo/'sindarin/generated/full6f_365gev_ee_ttbar_spinpol_v1'; rows=load_process_rows(repo); rendered=[]
    for row in rows:
        pol=POL[row.polarization]; seed=derive_seed('full6f_365gev_ee_ttbar_spinpol_v1',row.sample_id,row.exact_subprocess_id,'render',0,'whizard')
        outdir=output_root/row.sample_id/row.exact_subprocess_id; common_out=outdir/'common'; common_out.mkdir(parents=True,exist_ok=True)
        context={'SQRTS_GEV':'365.0','ISR_HANDLER':'true','ISR_ENABLED':'true','ELECTRON_POLARIZATION':pol[0],'POSITRON_POLARIZATION':pol[1],'INTEGRATION_ITERATIONS':0,'INTEGRATION_CALLS':0,'PROCESS_NAME':row.process_name,
            "SAMPLE_BASENAME": row.process_name,'FINAL_STATE':', '.join(to_whizard_particle(x) for x in row.final_state),'N_EVENTS':0,'GENERATOR_SEED':seed,'OUTPUT_LHE':f'EOS_OUTPUT_ROOT/{row.sample_id}/{row.exact_subprocess_id}.lhe','PARAMETER_BLOCK':'','COMMON_DIR':str(common_out)}
        for inc in ['model','parameters','beams','isr','polarization','integration','event_output','diagnostics']: render_file(template_root/f'common/{inc}.inc.in', common_out/f'{inc}.inc', context)
        template=template_root/('dilepton/process.sin.in' if row.topology=='prompt_dilepton' else 'semileptonic/process.sin.in'); render_file(template,outdir/'process.sin',context)
        meta={'sample_id':row.sample_id,'channel':row.channel,'topology':row.topology,'polarization':row.polarization,'exact_subprocess_id':row.exact_subprocess_id,'final_state':list(row.final_state),'generator_seed':seed,'process_sin_sha256':sha256(outdir/'process.sin')}; write_json(outdir/'render_context.json',meta); rendered.append(meta)
    write_json(output_root/'rendered_cards_manifest.json',{'status':'PASS','counts':expected_counts(rows),'rendered_count':len(rendered),'rendered':rendered})
    pol_counts = configure_generated_polarization_blocks(output_root)
    print(f"POLARIZATION_BLOCKS_CONFIGURED={pol_counts}")
    print(json.dumps({'status':'PASS','rendered_count':len(rendered)},indent=2)); return 0
if __name__=='__main__': sys.exit(main())
