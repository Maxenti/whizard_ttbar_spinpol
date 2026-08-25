# Phase 11C.5G-A Generation-Envelope Stress Package v1

This package builds and evaluates the frozen 60-job WHIZARD generation-envelope
stress qualification:

- 20 x 500 events from G2_S0;
- 20 x 500 events from G2_S1;
- 20 x 500 events from G2_S2;
- 60 jobs / 30,000 accepted events total.

It deliberately evaluates envelope behavior only. It does not inspect the
24 Phase-11C physics observables.

## Files

- `PHASE11C5GA_STRESS_PLAN.txt`: frozen scientific/decision plan.
- `scripts/make_itemdata.py`: deterministic 60-job seed/grid manifest builder.
- `scripts/validate_itemdata.py`: strict pre-submit manifest/grid/worker check.
- `scripts/render_submit.sh`: renders the HTCondor submit description.
- `scripts/run_all_dryruns.sh`: executes all 60 worker dry-runs.
- `scripts/gate_dryruns.py`: verifies all worker dry runs use the intended RNG recipe.
- `scripts/collect_envelope_stress.py`: technical + structural + aggregate envelope collector.

## Frozen aggregate gates

Per grid, over 10,000 accepted events:

- excess fraction <= 1%;
- aggregate average excess <= 0.01;
- global maximum excess <= 10;
- all 20 shards technically valid.

The collector exit codes are:

- `0`: PASS_ALL_GRIDS
- `2`: scientific envelope failure
- `3`: technical/incomplete result; only same-seed reruns are permitted

See the plan file for the predetermined post-result decision tree.
