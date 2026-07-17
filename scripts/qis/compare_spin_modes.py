#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse, json
import pandas as pd
import numpy as np
from qis_ttbar.level_c.state_distances import compare_states


def rho(payload):
    t=payload["tomography"]; return np.array(t["rho_physical_real"])+1j*np.array(t["rho_physical_imag"])

def main()->int:
    p=argparse.ArgumentParser(description="Compare correlated and isotropic tomography outputs")
    p.add_argument("--sc-root",required=True); p.add_argument("--iso-root",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    rows=[]
    for sc in sorted(Path(a.sc_root).glob("*/inclusive.json")):
        iso=Path(a.iso_root)/sc.parent.name/"inclusive.json"
        if not iso.exists(): continue
        ps,pi=json.loads(sc.read_text()),json.loads(iso.read_text()); row={"sample_id":sc.parent.name,**compare_states(rho(ps),rho(pi))}
        for key in ("concurrence","negativity","chsh_max","mutual_information"):
            row[f"sc_{key}"]=ps["qis"][key]; row[f"iso_{key}"]=pi["qis"][key]; row[f"delta_{key}"]=ps["qis"][key]-pi["qis"][key]
        rows.append(row)
    frame=pd.DataFrame(rows); Path(a.output).parent.mkdir(parents=True,exist_ok=True); frame.to_csv(a.output,index=False); print(frame.to_string(index=False)); return 0
if __name__=="__main__": raise SystemExit(main())
