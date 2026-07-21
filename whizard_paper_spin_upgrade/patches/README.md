# Existing-file patch policy

The upgrade is additive by default. No existing physics or gate file must be
changed to run it.

An optional, reversible patch is supplied through:

```bash
python3 scripts/qis/patch_run_next_gate.py --repo "$PWD"
```

It adds only an early dispatch:

```bash
scripts/qis/run_next_production_gate.sh paper-spin
```

All pre-existing branches remain byte-for-byte unchanged below the marker. The
patcher creates a timestamped backup and supports `--undo`.

This programmatic patch is used instead of a fragile line-number patch because
the gate script evolved during the sharded qualification campaign.
