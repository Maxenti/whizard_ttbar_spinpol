# Production package test report

## Scope

The package was tested as a repository overlay with an EOS-like campaign root.
The test exercised all eight production configurations and the complete
workflow:

1. configuration parsing and seed expansion;
2. SINDARIN template generation;
3. concrete Condor item-data and submit-file generation;
4. scratch execution through the shard wrapper;
5. raw LHE, log, metadata, and workspace staging;
6. shard and sample manifest construction;
7. decay-width calibration;
8. forced-decay LHE normalization;
9. per-sample collection and LHE merging;
10. strict production-output validation.

## Results

| Test | Result |
|---|---:|
| Python files compile | PASS |
| Shell wrapper parses with `bash -n` | PASS |
| Production CSV contains 8 unique samples | PASS |
| Expanded campaign contains 80 unique sample/shard seeds | PASS |
| Generated template matrix contains 8 templates | PASS |
| Synthetic smoke shards completed | 8/8 |
| Raw validation | 128 PASS, 0 WARN, 0 FAIL |
| Finalized/merged validation | 144 PASS, 0 WARN, 0 FAIL |

## Important limitation

The orchestration test used a deterministic fake WHIZARD executable. It proves
the workflow and data contracts, but not the installed WHIZARD 3.1.5 ISR syntax
or real integration behavior. Run the supplied eight-configuration smoke
campaign on lxplus and require strict validation before submitting the full
80-shard campaign.
