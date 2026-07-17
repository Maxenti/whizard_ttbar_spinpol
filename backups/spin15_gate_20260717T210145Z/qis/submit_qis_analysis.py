#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, datetime as dt, json, shlex, subprocess
from pathlib import Path


def main()->int:
    repo=Path(__file__).resolve().parents[2]
    p=argparse.ArgumentParser(description="Submit one tomography job per ntuple")
    p.add_argument("--input-dir", required=True); p.add_argument("--output-root", required=True)
    p.add_argument("--config", default=str(repo/"configs/qis/level_a_500GeV_ISR_sc_v1.yaml"))
    p.add_argument("--replicas", type=int, default=1000); p.add_argument("--submit",action="store_true"); p.add_argument("--resume",action="store_true")
    a=p.parse_args(); inputs=sorted(Path(a.input_dir).glob("*.parquet")) or sorted(Path(a.input_dir).glob("*.csv"))
    stamp=dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); control=repo/"condor/runtime_submissions/qis_analysis"/stamp
    for d in (control,control/"stdout",control/"stderr",Path(a.output_root)): d.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for path in inputs:
        output=Path(a.output_root)/path.stem
        if a.resume and (output/"inclusive.json").exists(): continue
        jobs.append({"wrapper":str(repo/"scripts/qis/run_analysis_job.sh"),"arguments":shlex.join(["python3",str(repo/"scripts/qis/run_tomography.py"),str(path),"--config",a.config,"--output-dir",str(output),"--replicas",str(a.replicas)]),"repo_root":str(repo),"stdout_path":str(control/"stdout"/f"{path.stem}.$(ClusterId).$(ProcId).out"),"stderr_path":str(control/"stderr"/f"{path.stem}.$(ClusterId).$(ProcId).err"),"event_log":str(control/"qis_analysis.condor.log"),"job_cpus":"1","job_memory_mb":"6000","job_flavour":"tomorrow","batch_name":"qis_tomography"})
    if not jobs: print("No jobs"); return 0
    item=control/"jobs.itemdata"; fields=list(jobs[0]);
    with item.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=" ",quoting=csv.QUOTE_MINIMAL,lineterminator="\n"); w.writeheader(); w.writerows(jobs)
    submit=control/"qis_analysis.sub"; submit.write_text((repo/"condor/qis/qis_analysis.sub").read_text().replace("$(itemdata)",str(item)))
    (control/"jobs.json").write_text(json.dumps(jobs,indent=2)+"\n"); print(f"Prepared jobs: {len(jobs)}\nSubmit file: {submit}")
    return subprocess.run(["condor_submit",str(submit)]).returncode if a.submit else 0
if __name__=="__main__": raise SystemExit(main())
