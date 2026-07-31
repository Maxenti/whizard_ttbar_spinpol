#!/usr/bin/env python3
"""Evaluate the Phase 2 runtime contract from a captured runtime manifest."""

from __future__ import annotations
import argparse, datetime, json, sys
from pathlib import Path
from ttbar_spinpol.contracts.yaml_compat import load_path
from ttbar_spinpol.runtime.versioning import parse_version, version_at_least
from ttbar_spinpol.provenance.records import atomic_write_json, atomic_write_text
from ttbar_spinpol.provenance.checksums import write_sha256_manifest

def probe_text(probe: dict) -> str:
    return f"{probe.get('stdout','')} {probe.get('stderr','')}"

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--runtime-manifest",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path)
    parser.add_argument("--allow-missing-external",action="store_true")
    args=parser.parse_args()
    repo=args.repo.resolve()
    runtime=json.loads(args.runtime_manifest.read_text())
    contract=load_path(repo/"analysis_contracts/runtime_contract.yaml")
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=(args.output_dir or repo/"inspection_outputs"/f"phase2_runtime_validation_{stamp}").resolve()
    out.mkdir(parents=True,exist_ok=False)
    errors=[]; warnings=[]
    probes=runtime.get("probes",{})
    # Python is always available because this validator is executing.
    py=parse_version(probe_text(probes.get("python",{})))
    if not version_at_least(py,(3,9)):
        errors.append(f"Python >=3.9 required; observed {py}")
    required_components=contract.get("required_components",{})
    whiz_required=tuple(int(x) for x in str(required_components.get("whizard",{}).get("required_version","3.1.8")).split("."))
    p8_required=tuple(int(x) for x in str(required_components.get("pythia8",{}).get("required_version","8.316")).split("."))
    hepmc_required=(int(required_components.get("hepmc3",{}).get("required_major_version",3)),)
    checks=[("whizard",whiz_required),("pythia8_config",p8_required),("hepmc3_config",hepmc_required)]
    for name,required in checks:
        probe=probes.get(name,{})
        if not probe.get("found"):
            message=f"{name} not discovered"
            (warnings if args.allow_missing_external else errors).append(message)
            continue
        observed=parse_version(probe_text(probe))
        if not version_at_least(observed,required):
            errors.append(f"{name} version {observed} does not satisfy {required}")
    status="PASS" if not errors else ("INCOMPLETE_RUNTIME_VALIDATION" if args.allow_missing_external else "FAIL")
    payload={"phase":"2","status":status,"timestamp_utc":stamp,"repository":str(repo),
             "inputs":[str(args.runtime_manifest)],"outputs":[],"errors":errors,"warnings":warnings}
    atomic_write_json(out/"validation.json",payload)
    atomic_write_json(out/"runtime_manifest.json",runtime)
    report=["PHASE 2 RUNTIME VALIDATION","="*72,"",f"STATUS:\n  {status}","",
            f"ERROR COUNT:\n  {len(errors)}","",f"WARNING COUNT:\n  {len(warnings)}",""]
    if errors: report+=["ERRORS:"]+[f"  - {e}" for e in errors]+[""]
    if warnings: report+=["WARNINGS:"]+[f"  - {e}" for e in warnings]+[""]
    atomic_write_text(out/"PHASE2_RUNTIME_REPORT.txt","\n".join(report))
    write_sha256_manifest([p for p in out.iterdir() if p.is_file() and p.name!="SHA256SUMS.txt"],out,out/"SHA256SUMS.txt")
    print("\n".join(report)); print(f"Output: {out}")
    return 0 if status in {"PASS","INCOMPLETE_RUNTIME_VALIDATION"} else 1
if __name__=="__main__":
    sys.exit(main())
