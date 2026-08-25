# Validation and analysis flow

1. Preflight the campaign before submission. Region preflight runs a real tiny WHIZARD integration to prove that the cut syntax is accepted by the qualified executable.
2. Submit the DAG. Never reroll physics seeds after a numerical failure.
3. `collect_campaign.py` separates technical artifacts from WHIZARD iteration rows.
4. `analyze_stability.py` computes per-node final integral/error, maximum post-first error percentage, maximum accuracy, minimum efficiency, and maximum normalized adjacent-iteration jump.
5. Restricted: `validate_restricted.py` checks 8-seed family screens and F0/F1 paired consistency. It does not replace generation-envelope qualification.
6. Regions: `analyze_regions.py` sums all nine cells and the DR/SR/NR aggregates. Run the suite stability analyzer on the old monolithic 480 collected results, then use `compare_region_to_monolithic.py`; finally `validate_regions.py` enforces closure.
7. Preserve closeout manifests and hashes. Do not select a single favorable stochastic grid for production.
