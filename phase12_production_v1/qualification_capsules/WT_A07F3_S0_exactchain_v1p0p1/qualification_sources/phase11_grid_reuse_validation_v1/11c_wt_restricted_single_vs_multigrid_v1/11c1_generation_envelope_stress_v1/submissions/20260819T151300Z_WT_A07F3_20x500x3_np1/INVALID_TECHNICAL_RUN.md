# WT Phase-11C envelope stress — technical invalidation

Campaign:
20260819T151300Z_WT_A07F3_20x500x3_np1

Condor cluster:
6062923

Outcome:
60 / 60 jobs executed and produced output directories/LHE products, but
60 / 60 workers returned status 1 from their post-run frozen-workspace
integrity gate.

Observed uniformly:
- STATUS=FAIL
- WORKSPACE_UNCHANGED=0
- NEW_GRID_INIT_COUNT=1
- PHS remained compatible
- VG2 changed from the frozen input hash

Classification:
SYSTEMATIC WORKER/CHECKPOINT-CONTRACT FAILURE.

This campaign is NOT a valid generation-envelope measurement and its LHE
events must not be used for Phase-11C physics or envelope qualification.

Root-cause hypothesis:
The WT A07/F3 workspace was passed to the previously qualified generation
worker using checkpoint_kind=G2 as a compatibility label. In that worker,
G2 has semantic meaning and selects the historical stored prescription

    5:50000:"gw", 3:200000:""

whereas the WT A07/F3 workspace contains

    10:100000:"gw", 10:200000:""

Frozen-grid reuse requires integrate(proc_epmum) to request the exact
prescription represented by the serialized integration state. The mismatch
caused WHIZARD to perform new integration and modify proc_epmum.m1.vg2.

The immutable source workspace tarballs on EOS were not modified; workers
operated on private extracted copies.

Required correction:
Create and separately qualify a WT-specific generation worker whose
checkpoint contract explicitly represents A07/F3 and requests

    iterations = 10:100000:"gw", 10:200000:""

before simulate(proc_epmum).

After a small reuse qualification passes, replay the original 60 validation
seeds in a NEW output tree. This is a technical replay, not a stochastic
retry-until-pass.
