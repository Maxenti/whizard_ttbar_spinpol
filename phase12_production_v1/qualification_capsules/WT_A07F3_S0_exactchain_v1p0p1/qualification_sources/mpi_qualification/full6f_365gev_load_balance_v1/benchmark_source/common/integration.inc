! Full-6f 365 GeV MPI/VAMP2 scaling benchmark.
!
! Physics configuration is copied unchanged from:
! full6f_365gev_ee_ttbar_spinpol_v1 / LR100 / epmum
!
! The benchmark deliberately changes only the integration backend,
! RNG required by VAMP2/MPI, OpenMP usage, and integration schedule.

$integration_method = "vamp2"
$rng_method = "rng_stream"
$vamp_parallel_method = "load"

?omega_openmp = false
openmp_num_threads = 1

! Preserve the canonical hard-process seed.
seed = 672175147

! Moderate representative scaling workload:
! 2 x 100k grid-building/adaptation calls
! 2 x 200k final integration calls
iterations = 2:100000:"gw", 2:200000:""

integrate (proc_epmum)
