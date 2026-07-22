# 365 GeV LHE matrix v1p1 Condor stream-path correction

The original matrix submitter placed Condor stdout and stderr in
`CAMPAIGN_ROOT/logs/`. A pilot submission reached the output-transfer stage but
was held because that directory was absent at the access point.

The v1p1 submitter:

- resolves the campaign root physically with `cd -P`, avoiding ambiguity when
  the repository `runs/` directory is a symlink into EOS;
- stores Condor streams under `CAMPAIGN_ROOT/condor/stdout/` and
  `CAMPAIGN_ROOT/condor/stderr/`;
- creates all stream directories immediately before writing the descriptor;
- performs a write probe in every Condor output directory before submission;
- leaves physics output in each sample run directory exactly as before.

This is an execution-layer correction only. It does not change any SINDARIN,
seed, event count, matrix definition, validation threshold, or physics product.
