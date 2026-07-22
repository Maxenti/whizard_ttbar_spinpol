# Paper-spin 365 GeV smoke v1p3 fix

This corrective overlay extends the strict 365 GeV smoke preparer to accept
production `.sin.in` placeholders for `seed`, `n_events`, and `$sample`.
It also canonicalizes `campaign_id` metadata and validates that no controlled
production placeholders or 500 GeV campaign tokens remain before WHIZARD runs.

Install this archive over the original v1 package plus the v1p1 and v1p2
overlays. Then rerun the package tests and prepare-only gate.
