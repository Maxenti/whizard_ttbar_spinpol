# Deterministic sharded showering

## Purpose

The qualification shower stage processes exactly 10,000 source events per
sample without scanning or rewriting unused events from larger authoritative
LHE files.  The default family contains 16 samples and requests 160 Condor
jobs, giving 10 shards and 1,000 events per sample/job.

## Control variables

```bash
export SHOWER_TOTAL_JOBS=160
export SHOWER_TOTAL_EVENTS_PER_SAMPLE=10000
```

`SHOWER_TOTAL_JOBS` is a global SC+ISO count.  It must be divisible by the
number of selected samples.  With 16 samples:

| Total jobs | Jobs/sample | Events/job |
|---:|---:|---:|
| 80 | 5 | 2,000 |
| 160 | 10 | 1,000 |
| 320 | 20 | 500 |

If the event count is not divisible by the jobs/sample count, events are
balanced deterministically with a difference of at most one event.

## Input-shard contract

`prepare_lhe_shards.py`:

1. reads the LHE prefix once;
2. reads only the first requested event window;
3. writes non-overlapping half-open ranges `[start, stop)`;
4. updates `<xsecinfo neve="...">` for every shard;
5. writes per-shard SHA256 checksums;
6. records source size, modification time, selected-window digest, ranges, and
   output paths in `shower/manifests/lhe_shard_manifest.csv`;
7. never reads the unused tail of a larger source LHE.

For 10 shards/sample the ranges are:

```text
shard_0000 [   0, 1000)
shard_0001 [1000, 2000)
...
shard_0009 [9000,10000)
```

## Worker contract

Every Condor worker receives one exact LHE shard.  Before showering it:

- verifies the input shard SHA256;
- verifies `stop - start == requested_events`;
- canonicalizes only that shard;
- inserts explicit W resonances only in that shard;
- asserts both preparation summaries processed exactly the requested count;
- asserts two W resonances were inserted per event;
- runs PYTHIA with the same exact event count;
- records the parent LHE, persistent shard path/checksum, source range, and
  preparation summaries in metadata.

A worker cannot silently process the remaining events from the parent file,
because the parent file is never copied or passed to either preparation tool.

## Resources

Default per 1,000-event shard:

```yaml
resources:
  request_cpus: 1
  request_memory_mb: 1000
  request_disk_gb: 2
  job_flavour: workday
```

PYTHIA is run as a serial process, so requesting more than one CPU does not
increase event throughput.  The memory request retains a conservative factor
above the observed ~250--320 MB footprint of the 10,000-event jobs.  Two GB of
scratch is ample for a 1,000-event LHE shard, prepared intermediates, HepMC3,
and logs.

## Ordered workflow

```bash
scripts/qis/run_next_production_gate.sh preflight
scripts/qis/run_next_production_gate.sh plan-showers
scripts/qis/run_next_production_gate.sh prepare-shower-shards
scripts/qis/run_next_production_gate.sh smoke-sharded-worker
scripts/qis/run_next_production_gate.sh submit-showers
```

After Condor completion:

```bash
scripts/qis/run_next_production_gate.sh validate-showers
scripts/qis/run_next_production_gate.sh collect-showers
scripts/qis/run_next_production_gate.sh spin15
```

## Retry semantics

The default modes are:

```bash
export SHOWER_SHARD_MODE=resume
export SHOWER_SUBMIT_MODE=resume
```

Input shards are reused only if their source stat, event ranges, file
existence, and SHA256 checksums remain valid.  Shower jobs are skipped only if
both HepMC3 and metadata exist and metadata reports a successful exact event
count.  Use `force` only to intentionally rebuild the full corresponding
stage.

## Validation and collection

The strict validator checks:

- exact expected `(sample, shard)` key sets;
- no source-range gaps or overlaps;
- aggregate 10,000 events per sample;
- unique deterministic seeds;
- input-shard path and SHA256 provenance;
- exact canonical-v2 and explicit-W event counts;
- exact inserted-W count;
- actual HepMC3 event counts via `pyhepmc`;
- closure limits and warning policies.

The collector merges shards in source-event order and requires exactly 10,000
HepMC3 events in every merged sample before producing downstream Spin-15
inputs.
