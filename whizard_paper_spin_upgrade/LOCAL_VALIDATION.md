# Local bundle validation

Validation date: 2026-07-21

The additive overlay was checked with:

- Python byte-code compilation of all new package and CLI modules;
- `bash -n` over all new shell scripts;
- isolated pytest suite: **16 passed**;
- clean installation into a temporary repository;
- post-install isolated pytest suite: **16 passed**;
- independent gamma/Z benchmark smoke calculation;
- synthetic moment and physical-shape closure smoke calculation.

The local runtime does not contain `pyarrow`, so the full EOS Parquet pipeline
cannot be executed inside this artifact container. The Key4HEP environment used
by the project is expected to supply the Parquet backend; the included preflight
checks this explicitly before production.
