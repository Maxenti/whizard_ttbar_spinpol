# 365 GeV smoke v1p3 parser correction

## Trigger

The authoritative source
`sindarin/production/ee_ttbar_epmum_LR100_sc_ISR_500GeV.sin.in` uses:

```text
seed = __SEED__
n_events = __N_EVENTS__
$sample = "__OUTPUT_SAMPLE__"
```

v1p2 accepted the templated event-count assignment but still required a
literal decimal seed. The run therefore stopped safely before WHIZARD.

## Correction

The v1p3 preparer treats the complete right-hand side of each controlled
assignment as replaceable input while still requiring exactly one assignment:

- `seed` becomes the configured literal seed;
- `n_events` becomes the configured literal event count;
- `$sample` becomes the quoted configured output sample identifier.

The source `campaign_id` is now controlled metadata and is rewritten to the
365 GeV pilot campaign identifier. The prepared-input contract additionally
requires exactly one canonical `$sample` assignment and rejects unresolved
controlled placeholders.

## Safety properties

The source template remains read-only. Preparation fails before WHIZARD if:

- any controlled assignment is absent or duplicated;
- any controlled production placeholder remains;
- any stale `500GeV` token remains;
- ISR metadata is false or missing;
- the explicit `epmum` decay process contract is not satisfied.
