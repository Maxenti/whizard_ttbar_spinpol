# HTCondor workflow

## Filesystem contract

```text
AFS: source, Git, build, submit descriptions, itemdata, live stdout/stderr/log
worker scratch: event processing and temporary outputs
EOS: persistent HepMC3, ntuples, tomography, manifests, reports
```

The submission helpers pre-create EOS directories serially to avoid namespace races and use per-job partial outputs.

## Shower campaign

```bash
python3 scripts/showering/submit_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
python3 scripts/showering/submit_showering.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml --submit
```

## Analysis campaign

```bash
python3 scripts/qis/submit_qis_analysis.py --config configs/qis/level_a_500GeV_ISR_sc_v1.yaml
```

## Resume behavior

A job is skipped only when its expected persistent product and success metadata both pass validation. A file that exists without success metadata is treated as incomplete. Force replacement is an explicit option and should not be used for ordinary recovery.

## Resource defaults

Showering defaults to one CPU, 3 GB memory, and 6 GB disk. Tomography defaults to one CPU and 6 GB memory. Adjust only after inspecting `condor_history` peak memory and disk usage.
