# v1p2: standard-schedd path policy for the 365 GeV LHE matrix

## Failure addressed

The v1p1 submitter used `cd -P` to resolve the campaign root. In the canonical
repository layout, `runs` points to EOS, so descriptor fields became literal
`/eos/...` paths. CERN standard schedds reject those paths before queue commit.
No production job was submitted by that failed command.

## Correct path contract

For standard schedds:

- keep the repository and campaign paths submit-visible through AFS;
- allow the repository `runs` symlink to resolve to EOS when files are opened;
- create stdout and stderr directories through the logical AFS path;
- never write the physical EOS target into the submit descriptor;
- reject a direct `/eos/...` campaign-root argument;
- scan the completed descriptor for accidental literal EOS paths.

The physical target remains useful for diagnostics and is printed separately.

## Scope

This correction affects Condor orchestration only. It does not alter generated
inputs, WHIZARD settings, ISR treatment, decay channels, polarization, random
seeds, sample counts, event counts, or validation thresholds.
