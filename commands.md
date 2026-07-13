/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/whizard_eos_output_migration_v1



cp /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/whizard_eos_output_migration_v1/migrate_whizard_outputs_to_eos.sh \
  scripts/

cp /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/whizard_eos_output_migration_v1/check_whizard_eos_layout.sh \
  scripts/

cp /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/whizard_eos_output_migration_v1/run_one_eos.sh \
  scripts/run_one.sh

chmod +x \
  scripts/migrate_whizard_outputs_to_eos.sh \
  scripts/check_whizard_eos_layout.sh \
  scripts/run_one.sh