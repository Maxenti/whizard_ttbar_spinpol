# 365 GeV smoke v1p2 corrective overlay

This overlay fixes preparation from the authoritative version-controlled
`*.sin.in` production source.  Such sources may use a renderer placeholder as
the right-hand side of `n_events`; v1p1 accepted only decimal literals.

The replacement remains strict: exactly one nonempty `n_events = VALUE`
assignment is required, only VALUE is replaced, and any trailing SINDARIN
comment is preserved.  A regression test covers a production placeholder.
