# 365 GeV smoke v1p2 parser correction

## Problem

The qualified ISR production source is a `.sin.in` template.  Its event-count
assignment can contain a production-renderer token rather than an integer.
The v1p1 expression required digits and therefore reported zero assignments.

## Resolution

`EVENT_PATTERN` now accepts one nonempty right-hand side, replaces only that
value with the pilot event count, and preserves a trailing comment.  The
prepared-input validator still requires the resulting executable SINDARIN to
contain exactly one literal `n_events = 200` assignment.
