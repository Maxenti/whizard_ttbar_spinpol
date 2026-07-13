WHIZARD ttbar spin/polarization EOS-output migration helpers

Files:
  migrate_whizard_outputs_to_eos.sh
    Copies runs/lhe/logs/metadata/validation from the AFS repository to the
    canonical EOS output root, verifies checksums, preserves timestamped AFS
    backups, and replaces the AFS directories with EOS symlinks.

  run_one_eos.sh
    Full replacement for scripts/run_one.sh. Runs WHIZARD in local/Condor
    scratch and stages the complete workspace plus LHE/logs to EOS.

  check_whizard_eos_layout.sh
    Verifies that every persistent output tree in the AFS repository resolves
    to the expected EOS destination.

Canonical paths:
  AFS code: /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
  EOS data: /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol
