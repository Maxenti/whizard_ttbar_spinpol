Phase-11E P6 100k validation false-negative record
===================================================

The first 100k metadata/preparation validator reported FAIL on all
four shards solely because it required a top-level metadata field:

  hepmc_events

The shower metadata schema does not provide that field.

The valid metadata event contract is represented by:
  requested_events
  attempted_events
  accepted_events
  failed_events

The actual HepMC serialized event count is independently and more
directly validated by opening each HepMC file with pyhepmc.

The independent HepMC validation returned:
  4 HepMC files
  25000 events per file
  100000 total events
  0 bad-weight events
  P6_100K_HEPMC_GATE=PASS

Therefore the original metadata/preparation FAIL is classified as a
validation-script false negative, not a simulation, worker, shower,
HepMC, or physics failure.

No physics jobs were rerun and no frozen production code was changed.
