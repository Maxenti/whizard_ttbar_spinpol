! File generated automatically by O'Mega 3.1.8 release Mar 03 2026
!
!   /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R44_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R44_i1 -target:md5sum 6C81D0068F192DC5A272B5F6678BC93D -fusion:progress -scatter "e- e+ -> e+ nue b mu- numubar bbar" -cascade 3+4+5~t
!
! with all scattering amplitudes for the process(es)
!
!   flavor combinations:
!
!       1: e- e+ -> e+ nue b mu- numubar bbar
!
!   color flows:
!
!       1: (  0,  0) (  0,  0) -> (  0,  0) (  0,  0) (  1,  0) (  0,  0) (  0,  0) (  0, -1)
!
!     NB: i.g. not all color flows contribute to all flavor
!     combinations.  Consult the array FLV_COL_IS_ALLOWED
!     below for the allowed combinations.
!
!   Color Factors:
!
!     (  1,  1): + N
!
!   vanishing or redundant flavor combinations:
!
!
!   diagram selection (MIGHT BREAK GAUGE INVARIANCE!!!):
!
!     3+4+5 ~ t  grouping {{3,4,5}}
!
!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Amplitude computation module
! NOT to be USEd by application programs
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_proc_epmum_R44_i1_computation
  use kinds
  use omega95
  use omega_color, OCF => omega_color_factor
  use parameters_SM
  implicit none
  private
  public :: number_particles_in, number_particles_out, number_color_indices, &
    reset_helicity_selection, new_event, is_allowed, get_amplitude, &
    color_sum, external_masses, openmp_supported, table_coupling_orders, &
    table_coupling_powers, amp_by_orders, table_spin_states, &
    table_flavor_states, number_spin_states, spin_states, &
    number_flavor_states, flavor_states, number_color_flows, color_flows, &
    number_color_factors, color_factors, init, final, update_alpha_s, md5sum
  ! DON'T EVEN THINK of removing the following!
  ! If the compiler complains about undeclared
  ! or undefined variables, you are compiling
  ! against an incompatible omega95 module!
  integer, dimension(7), parameter, private :: require = &
    (/ omega_spinors_2010_01_A, omega_spinor_cpls_2010_01_A, &
       omega_vectors_2010_01_A, omega_polarizations_2010_01_A, &
       omega_couplings_2010_01_A, omega_color_2010_01_A, &
       omega_utils_2010_01_A /)

  integer, parameter :: n_prt = 8
  integer, parameter :: n_in = 2
  integer, parameter :: n_out = 6
  integer, parameter :: n_cflow = 1
  integer, parameter :: n_cindex = 2
  integer, parameter :: n_flv = 1
  integer, parameter :: n_hel = 256
  integer, parameter :: n_co = 0
  integer, parameter :: n_co_len = 0
  integer, parameter :: n_cp = 1

  ! NB: you MUST NOT change the value of N_ here!!!
  !     It is defined here for convenience only and must be
  !     compatible with hardcoded values in the amplitude!
  real(kind=default), parameter :: N_ = 3
  logical, parameter :: F = .false.
  logical, parameter :: T = .true.

  character(len=0), dimension(n_co), save, protected :: table_coupling_orders

  integer, dimension(n_co,n_cp), save, protected :: table_coupling_powers

  integer, dimension(n_prt,n_hel), save, protected :: table_spin_states
  data table_spin_states(:,   1) / -1, -1, -1, -1, -1, -1, -1, -1 /
  data table_spin_states(:,   2) / -1, -1, -1, -1, -1, -1, -1,  1 /
  data table_spin_states(:,   3) / -1, -1, -1, -1, -1, -1,  1, -1 /
  data table_spin_states(:,   4) / -1, -1, -1, -1, -1, -1,  1,  1 /
  data table_spin_states(:,   5) / -1, -1, -1, -1, -1,  1, -1, -1 /
  data table_spin_states(:,   6) / -1, -1, -1, -1, -1,  1, -1,  1 /
  data table_spin_states(:,   7) / -1, -1, -1, -1, -1,  1,  1, -1 /
  data table_spin_states(:,   8) / -1, -1, -1, -1, -1,  1,  1,  1 /
  data table_spin_states(:,   9) / -1, -1, -1, -1,  1, -1, -1, -1 /
  data table_spin_states(:,  10) / -1, -1, -1, -1,  1, -1, -1,  1 /
  data table_spin_states(:,  11) / -1, -1, -1, -1,  1, -1,  1, -1 /
  data table_spin_states(:,  12) / -1, -1, -1, -1,  1, -1,  1,  1 /
  data table_spin_states(:,  13) / -1, -1, -1, -1,  1,  1, -1, -1 /
  data table_spin_states(:,  14) / -1, -1, -1, -1,  1,  1, -1,  1 /
  data table_spin_states(:,  15) / -1, -1, -1, -1,  1,  1,  1, -1 /
  data table_spin_states(:,  16) / -1, -1, -1, -1,  1,  1,  1,  1 /
  data table_spin_states(:,  17) / -1, -1, -1,  1, -1, -1, -1, -1 /
  data table_spin_states(:,  18) / -1, -1, -1,  1, -1, -1, -1,  1 /
  data table_spin_states(:,  19) / -1, -1, -1,  1, -1, -1,  1, -1 /
  data table_spin_states(:,  20) / -1, -1, -1,  1, -1, -1,  1,  1 /
  data table_spin_states(:,  21) / -1, -1, -1,  1, -1,  1, -1, -1 /
  data table_spin_states(:,  22) / -1, -1, -1,  1, -1,  1, -1,  1 /
  data table_spin_states(:,  23) / -1, -1, -1,  1, -1,  1,  1, -1 /
  data table_spin_states(:,  24) / -1, -1, -1,  1, -1,  1,  1,  1 /
  data table_spin_states(:,  25) / -1, -1, -1,  1,  1, -1, -1, -1 /
  data table_spin_states(:,  26) / -1, -1, -1,  1,  1, -1, -1,  1 /
  data table_spin_states(:,  27) / -1, -1, -1,  1,  1, -1,  1, -1 /
  data table_spin_states(:,  28) / -1, -1, -1,  1,  1, -1,  1,  1 /
  data table_spin_states(:,  29) / -1, -1, -1,  1,  1,  1, -1, -1 /
  data table_spin_states(:,  30) / -1, -1, -1,  1,  1,  1, -1,  1 /
  data table_spin_states(:,  31) / -1, -1, -1,  1,  1,  1,  1, -1 /
  data table_spin_states(:,  32) / -1, -1, -1,  1,  1,  1,  1,  1 /
  data table_spin_states(:,  33) / -1, -1,  1, -1, -1, -1, -1, -1 /
  data table_spin_states(:,  34) / -1, -1,  1, -1, -1, -1, -1,  1 /
  data table_spin_states(:,  35) / -1, -1,  1, -1, -1, -1,  1, -1 /
  data table_spin_states(:,  36) / -1, -1,  1, -1, -1, -1,  1,  1 /
  data table_spin_states(:,  37) / -1, -1,  1, -1, -1,  1, -1, -1 /
  data table_spin_states(:,  38) / -1, -1,  1, -1, -1,  1, -1,  1 /
  data table_spin_states(:,  39) / -1, -1,  1, -1, -1,  1,  1, -1 /
  data table_spin_states(:,  40) / -1, -1,  1, -1, -1,  1,  1,  1 /
  data table_spin_states(:,  41) / -1, -1,  1, -1,  1, -1, -1, -1 /
  data table_spin_states(:,  42) / -1, -1,  1, -1,  1, -1, -1,  1 /
  data table_spin_states(:,  43) / -1, -1,  1, -1,  1, -1,  1, -1 /
  data table_spin_states(:,  44) / -1, -1,  1, -1,  1, -1,  1,  1 /
  data table_spin_states(:,  45) / -1, -1,  1, -1,  1,  1, -1, -1 /
  data table_spin_states(:,  46) / -1, -1,  1, -1,  1,  1, -1,  1 /
  data table_spin_states(:,  47) / -1, -1,  1, -1,  1,  1,  1, -1 /
  data table_spin_states(:,  48) / -1, -1,  1, -1,  1,  1,  1,  1 /
  data table_spin_states(:,  49) / -1, -1,  1,  1, -1, -1, -1, -1 /
  data table_spin_states(:,  50) / -1, -1,  1,  1, -1, -1, -1,  1 /
  data table_spin_states(:,  51) / -1, -1,  1,  1, -1, -1,  1, -1 /
  data table_spin_states(:,  52) / -1, -1,  1,  1, -1, -1,  1,  1 /
  data table_spin_states(:,  53) / -1, -1,  1,  1, -1,  1, -1, -1 /
  data table_spin_states(:,  54) / -1, -1,  1,  1, -1,  1, -1,  1 /
  data table_spin_states(:,  55) / -1, -1,  1,  1, -1,  1,  1, -1 /
  data table_spin_states(:,  56) / -1, -1,  1,  1, -1,  1,  1,  1 /
  data table_spin_states(:,  57) / -1, -1,  1,  1,  1, -1, -1, -1 /
  data table_spin_states(:,  58) / -1, -1,  1,  1,  1, -1, -1,  1 /
  data table_spin_states(:,  59) / -1, -1,  1,  1,  1, -1,  1, -1 /
  data table_spin_states(:,  60) / -1, -1,  1,  1,  1, -1,  1,  1 /
  data table_spin_states(:,  61) / -1, -1,  1,  1,  1,  1, -1, -1 /
  data table_spin_states(:,  62) / -1, -1,  1,  1,  1,  1, -1,  1 /
  data table_spin_states(:,  63) / -1, -1,  1,  1,  1,  1,  1, -1 /
  data table_spin_states(:,  64) / -1, -1,  1,  1,  1,  1,  1,  1 /
  data table_spin_states(:,  65) / -1,  1, -1, -1, -1, -1, -1, -1 /
  data table_spin_states(:,  66) / -1,  1, -1, -1, -1, -1, -1,  1 /
  data table_spin_states(:,  67) / -1,  1, -1, -1, -1, -1,  1, -1 /
  data table_spin_states(:,  68) / -1,  1, -1, -1, -1, -1,  1,  1 /
  data table_spin_states(:,  69) / -1,  1, -1, -1, -1,  1, -1, -1 /
  data table_spin_states(:,  70) / -1,  1, -1, -1, -1,  1, -1,  1 /
  data table_spin_states(:,  71) / -1,  1, -1, -1, -1,  1,  1, -1 /
  data table_spin_states(:,  72) / -1,  1, -1, -1, -1,  1,  1,  1 /
  data table_spin_states(:,  73) / -1,  1, -1, -1,  1, -1, -1, -1 /
  data table_spin_states(:,  74) / -1,  1, -1, -1,  1, -1, -1,  1 /
  data table_spin_states(:,  75) / -1,  1, -1, -1,  1, -1,  1, -1 /
  data table_spin_states(:,  76) / -1,  1, -1, -1,  1, -1,  1,  1 /
  data table_spin_states(:,  77) / -1,  1, -1, -1,  1,  1, -1, -1 /
  data table_spin_states(:,  78) / -1,  1, -1, -1,  1,  1, -1,  1 /
  data table_spin_states(:,  79) / -1,  1, -1, -1,  1,  1,  1, -1 /
  data table_spin_states(:,  80) / -1,  1, -1, -1,  1,  1,  1,  1 /
  data table_spin_states(:,  81) / -1,  1, -1,  1, -1, -1, -1, -1 /
  data table_spin_states(:,  82) / -1,  1, -1,  1, -1, -1, -1,  1 /
  data table_spin_states(:,  83) / -1,  1, -1,  1, -1, -1,  1, -1 /
  data table_spin_states(:,  84) / -1,  1, -1,  1, -1, -1,  1,  1 /
  data table_spin_states(:,  85) / -1,  1, -1,  1, -1,  1, -1, -1 /
  data table_spin_states(:,  86) / -1,  1, -1,  1, -1,  1, -1,  1 /
  data table_spin_states(:,  87) / -1,  1, -1,  1, -1,  1,  1, -1 /
  data table_spin_states(:,  88) / -1,  1, -1,  1, -1,  1,  1,  1 /
  data table_spin_states(:,  89) / -1,  1, -1,  1,  1, -1, -1, -1 /
  data table_spin_states(:,  90) / -1,  1, -1,  1,  1, -1, -1,  1 /
  data table_spin_states(:,  91) / -1,  1, -1,  1,  1, -1,  1, -1 /
  data table_spin_states(:,  92) / -1,  1, -1,  1,  1, -1,  1,  1 /
  data table_spin_states(:,  93) / -1,  1, -1,  1,  1,  1, -1, -1 /
  data table_spin_states(:,  94) / -1,  1, -1,  1,  1,  1, -1,  1 /
  data table_spin_states(:,  95) / -1,  1, -1,  1,  1,  1,  1, -1 /
  data table_spin_states(:,  96) / -1,  1, -1,  1,  1,  1,  1,  1 /
  data table_spin_states(:,  97) / -1,  1,  1, -1, -1, -1, -1, -1 /
  data table_spin_states(:,  98) / -1,  1,  1, -1, -1, -1, -1,  1 /
  data table_spin_states(:,  99) / -1,  1,  1, -1, -1, -1,  1, -1 /
  data table_spin_states(:, 100) / -1,  1,  1, -1, -1, -1,  1,  1 /
  data table_spin_states(:, 101) / -1,  1,  1, -1, -1,  1, -1, -1 /
  data table_spin_states(:, 102) / -1,  1,  1, -1, -1,  1, -1,  1 /
  data table_spin_states(:, 103) / -1,  1,  1, -1, -1,  1,  1, -1 /
  data table_spin_states(:, 104) / -1,  1,  1, -1, -1,  1,  1,  1 /
  data table_spin_states(:, 105) / -1,  1,  1, -1,  1, -1, -1, -1 /
  data table_spin_states(:, 106) / -1,  1,  1, -1,  1, -1, -1,  1 /
  data table_spin_states(:, 107) / -1,  1,  1, -1,  1, -1,  1, -1 /
  data table_spin_states(:, 108) / -1,  1,  1, -1,  1, -1,  1,  1 /
  data table_spin_states(:, 109) / -1,  1,  1, -1,  1,  1, -1, -1 /
  data table_spin_states(:, 110) / -1,  1,  1, -1,  1,  1, -1,  1 /
  data table_spin_states(:, 111) / -1,  1,  1, -1,  1,  1,  1, -1 /
  data table_spin_states(:, 112) / -1,  1,  1, -1,  1,  1,  1,  1 /
  data table_spin_states(:, 113) / -1,  1,  1,  1, -1, -1, -1, -1 /
  data table_spin_states(:, 114) / -1,  1,  1,  1, -1, -1, -1,  1 /
  data table_spin_states(:, 115) / -1,  1,  1,  1, -1, -1,  1, -1 /
  data table_spin_states(:, 116) / -1,  1,  1,  1, -1, -1,  1,  1 /
  data table_spin_states(:, 117) / -1,  1,  1,  1, -1,  1, -1, -1 /
  data table_spin_states(:, 118) / -1,  1,  1,  1, -1,  1, -1,  1 /
  data table_spin_states(:, 119) / -1,  1,  1,  1, -1,  1,  1, -1 /
  data table_spin_states(:, 120) / -1,  1,  1,  1, -1,  1,  1,  1 /
  data table_spin_states(:, 121) / -1,  1,  1,  1,  1, -1, -1, -1 /
  data table_spin_states(:, 122) / -1,  1,  1,  1,  1, -1, -1,  1 /
  data table_spin_states(:, 123) / -1,  1,  1,  1,  1, -1,  1, -1 /
  data table_spin_states(:, 124) / -1,  1,  1,  1,  1, -1,  1,  1 /
  data table_spin_states(:, 125) / -1,  1,  1,  1,  1,  1, -1, -1 /
  data table_spin_states(:, 126) / -1,  1,  1,  1,  1,  1, -1,  1 /
  data table_spin_states(:, 127) / -1,  1,  1,  1,  1,  1,  1, -1 /
  data table_spin_states(:, 128) / -1,  1,  1,  1,  1,  1,  1,  1 /
  data table_spin_states(:, 129) /  1, -1, -1, -1, -1, -1, -1, -1 /
  data table_spin_states(:, 130) /  1, -1, -1, -1, -1, -1, -1,  1 /
  data table_spin_states(:, 131) /  1, -1, -1, -1, -1, -1,  1, -1 /
  data table_spin_states(:, 132) /  1, -1, -1, -1, -1, -1,  1,  1 /
  data table_spin_states(:, 133) /  1, -1, -1, -1, -1,  1, -1, -1 /
  data table_spin_states(:, 134) /  1, -1, -1, -1, -1,  1, -1,  1 /
  data table_spin_states(:, 135) /  1, -1, -1, -1, -1,  1,  1, -1 /
  data table_spin_states(:, 136) /  1, -1, -1, -1, -1,  1,  1,  1 /
  data table_spin_states(:, 137) /  1, -1, -1, -1,  1, -1, -1, -1 /
  data table_spin_states(:, 138) /  1, -1, -1, -1,  1, -1, -1,  1 /
  data table_spin_states(:, 139) /  1, -1, -1, -1,  1, -1,  1, -1 /
  data table_spin_states(:, 140) /  1, -1, -1, -1,  1, -1,  1,  1 /
  data table_spin_states(:, 141) /  1, -1, -1, -1,  1,  1, -1, -1 /
  data table_spin_states(:, 142) /  1, -1, -1, -1,  1,  1, -1,  1 /
  data table_spin_states(:, 143) /  1, -1, -1, -1,  1,  1,  1, -1 /
  data table_spin_states(:, 144) /  1, -1, -1, -1,  1,  1,  1,  1 /
  data table_spin_states(:, 145) /  1, -1, -1,  1, -1, -1, -1, -1 /
  data table_spin_states(:, 146) /  1, -1, -1,  1, -1, -1, -1,  1 /
  data table_spin_states(:, 147) /  1, -1, -1,  1, -1, -1,  1, -1 /
  data table_spin_states(:, 148) /  1, -1, -1,  1, -1, -1,  1,  1 /
  data table_spin_states(:, 149) /  1, -1, -1,  1, -1,  1, -1, -1 /
  data table_spin_states(:, 150) /  1, -1, -1,  1, -1,  1, -1,  1 /
  data table_spin_states(:, 151) /  1, -1, -1,  1, -1,  1,  1, -1 /
  data table_spin_states(:, 152) /  1, -1, -1,  1, -1,  1,  1,  1 /
  data table_spin_states(:, 153) /  1, -1, -1,  1,  1, -1, -1, -1 /
  data table_spin_states(:, 154) /  1, -1, -1,  1,  1, -1, -1,  1 /
  data table_spin_states(:, 155) /  1, -1, -1,  1,  1, -1,  1, -1 /
  data table_spin_states(:, 156) /  1, -1, -1,  1,  1, -1,  1,  1 /
  data table_spin_states(:, 157) /  1, -1, -1,  1,  1,  1, -1, -1 /
  data table_spin_states(:, 158) /  1, -1, -1,  1,  1,  1, -1,  1 /
  data table_spin_states(:, 159) /  1, -1, -1,  1,  1,  1,  1, -1 /
  data table_spin_states(:, 160) /  1, -1, -1,  1,  1,  1,  1,  1 /
  data table_spin_states(:, 161) /  1, -1,  1, -1, -1, -1, -1, -1 /
  data table_spin_states(:, 162) /  1, -1,  1, -1, -1, -1, -1,  1 /
  data table_spin_states(:, 163) /  1, -1,  1, -1, -1, -1,  1, -1 /
  data table_spin_states(:, 164) /  1, -1,  1, -1, -1, -1,  1,  1 /
  data table_spin_states(:, 165) /  1, -1,  1, -1, -1,  1, -1, -1 /
  data table_spin_states(:, 166) /  1, -1,  1, -1, -1,  1, -1,  1 /
  data table_spin_states(:, 167) /  1, -1,  1, -1, -1,  1,  1, -1 /
  data table_spin_states(:, 168) /  1, -1,  1, -1, -1,  1,  1,  1 /
  data table_spin_states(:, 169) /  1, -1,  1, -1,  1, -1, -1, -1 /
  data table_spin_states(:, 170) /  1, -1,  1, -1,  1, -1, -1,  1 /
  data table_spin_states(:, 171) /  1, -1,  1, -1,  1, -1,  1, -1 /
  data table_spin_states(:, 172) /  1, -1,  1, -1,  1, -1,  1,  1 /
  data table_spin_states(:, 173) /  1, -1,  1, -1,  1,  1, -1, -1 /
  data table_spin_states(:, 174) /  1, -1,  1, -1,  1,  1, -1,  1 /
  data table_spin_states(:, 175) /  1, -1,  1, -1,  1,  1,  1, -1 /
  data table_spin_states(:, 176) /  1, -1,  1, -1,  1,  1,  1,  1 /
  data table_spin_states(:, 177) /  1, -1,  1,  1, -1, -1, -1, -1 /
  data table_spin_states(:, 178) /  1, -1,  1,  1, -1, -1, -1,  1 /
  data table_spin_states(:, 179) /  1, -1,  1,  1, -1, -1,  1, -1 /
  data table_spin_states(:, 180) /  1, -1,  1,  1, -1, -1,  1,  1 /
  data table_spin_states(:, 181) /  1, -1,  1,  1, -1,  1, -1, -1 /
  data table_spin_states(:, 182) /  1, -1,  1,  1, -1,  1, -1,  1 /
  data table_spin_states(:, 183) /  1, -1,  1,  1, -1,  1,  1, -1 /
  data table_spin_states(:, 184) /  1, -1,  1,  1, -1,  1,  1,  1 /
  data table_spin_states(:, 185) /  1, -1,  1,  1,  1, -1, -1, -1 /
  data table_spin_states(:, 186) /  1, -1,  1,  1,  1, -1, -1,  1 /
  data table_spin_states(:, 187) /  1, -1,  1,  1,  1, -1,  1, -1 /
  data table_spin_states(:, 188) /  1, -1,  1,  1,  1, -1,  1,  1 /
  data table_spin_states(:, 189) /  1, -1,  1,  1,  1,  1, -1, -1 /
  data table_spin_states(:, 190) /  1, -1,  1,  1,  1,  1, -1,  1 /
  data table_spin_states(:, 191) /  1, -1,  1,  1,  1,  1,  1, -1 /
  data table_spin_states(:, 192) /  1, -1,  1,  1,  1,  1,  1,  1 /
  data table_spin_states(:, 193) /  1,  1, -1, -1, -1, -1, -1, -1 /
  data table_spin_states(:, 194) /  1,  1, -1, -1, -1, -1, -1,  1 /
  data table_spin_states(:, 195) /  1,  1, -1, -1, -1, -1,  1, -1 /
  data table_spin_states(:, 196) /  1,  1, -1, -1, -1, -1,  1,  1 /
  data table_spin_states(:, 197) /  1,  1, -1, -1, -1,  1, -1, -1 /
  data table_spin_states(:, 198) /  1,  1, -1, -1, -1,  1, -1,  1 /
  data table_spin_states(:, 199) /  1,  1, -1, -1, -1,  1,  1, -1 /
  data table_spin_states(:, 200) /  1,  1, -1, -1, -1,  1,  1,  1 /
  data table_spin_states(:, 201) /  1,  1, -1, -1,  1, -1, -1, -1 /
  data table_spin_states(:, 202) /  1,  1, -1, -1,  1, -1, -1,  1 /
  data table_spin_states(:, 203) /  1,  1, -1, -1,  1, -1,  1, -1 /
  data table_spin_states(:, 204) /  1,  1, -1, -1,  1, -1,  1,  1 /
  data table_spin_states(:, 205) /  1,  1, -1, -1,  1,  1, -1, -1 /
  data table_spin_states(:, 206) /  1,  1, -1, -1,  1,  1, -1,  1 /
  data table_spin_states(:, 207) /  1,  1, -1, -1,  1,  1,  1, -1 /
  data table_spin_states(:, 208) /  1,  1, -1, -1,  1,  1,  1,  1 /
  data table_spin_states(:, 209) /  1,  1, -1,  1, -1, -1, -1, -1 /
  data table_spin_states(:, 210) /  1,  1, -1,  1, -1, -1, -1,  1 /
  data table_spin_states(:, 211) /  1,  1, -1,  1, -1, -1,  1, -1 /
  data table_spin_states(:, 212) /  1,  1, -1,  1, -1, -1,  1,  1 /
  data table_spin_states(:, 213) /  1,  1, -1,  1, -1,  1, -1, -1 /
  data table_spin_states(:, 214) /  1,  1, -1,  1, -1,  1, -1,  1 /
  data table_spin_states(:, 215) /  1,  1, -1,  1, -1,  1,  1, -1 /
  data table_spin_states(:, 216) /  1,  1, -1,  1, -1,  1,  1,  1 /
  data table_spin_states(:, 217) /  1,  1, -1,  1,  1, -1, -1, -1 /
  data table_spin_states(:, 218) /  1,  1, -1,  1,  1, -1, -1,  1 /
  data table_spin_states(:, 219) /  1,  1, -1,  1,  1, -1,  1, -1 /
  data table_spin_states(:, 220) /  1,  1, -1,  1,  1, -1,  1,  1 /
  data table_spin_states(:, 221) /  1,  1, -1,  1,  1,  1, -1, -1 /
  data table_spin_states(:, 222) /  1,  1, -1,  1,  1,  1, -1,  1 /
  data table_spin_states(:, 223) /  1,  1, -1,  1,  1,  1,  1, -1 /
  data table_spin_states(:, 224) /  1,  1, -1,  1,  1,  1,  1,  1 /
  data table_spin_states(:, 225) /  1,  1,  1, -1, -1, -1, -1, -1 /
  data table_spin_states(:, 226) /  1,  1,  1, -1, -1, -1, -1,  1 /
  data table_spin_states(:, 227) /  1,  1,  1, -1, -1, -1,  1, -1 /
  data table_spin_states(:, 228) /  1,  1,  1, -1, -1, -1,  1,  1 /
  data table_spin_states(:, 229) /  1,  1,  1, -1, -1,  1, -1, -1 /
  data table_spin_states(:, 230) /  1,  1,  1, -1, -1,  1, -1,  1 /
  data table_spin_states(:, 231) /  1,  1,  1, -1, -1,  1,  1, -1 /
  data table_spin_states(:, 232) /  1,  1,  1, -1, -1,  1,  1,  1 /
  data table_spin_states(:, 233) /  1,  1,  1, -1,  1, -1, -1, -1 /
  data table_spin_states(:, 234) /  1,  1,  1, -1,  1, -1, -1,  1 /
  data table_spin_states(:, 235) /  1,  1,  1, -1,  1, -1,  1, -1 /
  data table_spin_states(:, 236) /  1,  1,  1, -1,  1, -1,  1,  1 /
  data table_spin_states(:, 237) /  1,  1,  1, -1,  1,  1, -1, -1 /
  data table_spin_states(:, 238) /  1,  1,  1, -1,  1,  1, -1,  1 /
  data table_spin_states(:, 239) /  1,  1,  1, -1,  1,  1,  1, -1 /
  data table_spin_states(:, 240) /  1,  1,  1, -1,  1,  1,  1,  1 /
  data table_spin_states(:, 241) /  1,  1,  1,  1, -1, -1, -1, -1 /
  data table_spin_states(:, 242) /  1,  1,  1,  1, -1, -1, -1,  1 /
  data table_spin_states(:, 243) /  1,  1,  1,  1, -1, -1,  1, -1 /
  data table_spin_states(:, 244) /  1,  1,  1,  1, -1, -1,  1,  1 /
  data table_spin_states(:, 245) /  1,  1,  1,  1, -1,  1, -1, -1 /
  data table_spin_states(:, 246) /  1,  1,  1,  1, -1,  1, -1,  1 /
  data table_spin_states(:, 247) /  1,  1,  1,  1, -1,  1,  1, -1 /
  data table_spin_states(:, 248) /  1,  1,  1,  1, -1,  1,  1,  1 /
  data table_spin_states(:, 249) /  1,  1,  1,  1,  1, -1, -1, -1 /
  data table_spin_states(:, 250) /  1,  1,  1,  1,  1, -1, -1,  1 /
  data table_spin_states(:, 251) /  1,  1,  1,  1,  1, -1,  1, -1 /
  data table_spin_states(:, 252) /  1,  1,  1,  1,  1, -1,  1,  1 /
  data table_spin_states(:, 253) /  1,  1,  1,  1,  1,  1, -1, -1 /
  data table_spin_states(:, 254) /  1,  1,  1,  1,  1,  1, -1,  1 /
  data table_spin_states(:, 255) /  1,  1,  1,  1,  1,  1,  1, -1 /
  data table_spin_states(:, 256) /  1,  1,  1,  1,  1,  1,  1,  1 /

  integer, dimension(n_prt,n_flv), save, protected :: table_flavor_states
  data table_flavor_states(:,   1) /  11, -11, -11,  12,   5,  13, -14,  -5 / ! e- e+ e+ nue b mu- numubar bbar

  integer, dimension(n_cindex,n_prt,n_cflow), save, protected :: table_color_flows
  data table_color_flows(:,:,   1) / 0,0,  0,0,  0,0,  0,0,  1,0,  0,0,  0,0, &
     0,-1 /

  logical, dimension(n_prt,n_cflow), save, protected :: table_ghost_flags
  data table_ghost_flags(:,   1) / F,  F,  F,  F,  F,  F,  F,  F /

  integer, parameter :: n_cfactors = 1
  type(OCF), dimension(n_cfactors), save, protected :: table_color_factors
  real(kind=default), parameter, private :: color_factor_000001 = +N_
  data table_color_factors(     1) / OCF(1,1,color_factor_000001) /

  logical, dimension(n_flv,n_cflow), save, protected ::  flv_col_is_allowed
  data flv_col_is_allowed(:,   1) / T /

  logical, dimension(n_cp,n_flv,n_cflow), save, protected ::  &
    co_flv_col_is_allowed
  data co_flv_col_is_allowed(:,   1,   1) / T /

  complex(kind=default), dimension(n_flv,n_cflow,n_hel), save :: amp_all_orders
  complex(kind=default), dimension(n_cp,n_flv,n_cflow,n_hel), save :: amp_by_orders

  logical, dimension(n_hel), save :: hel_is_allowed = T
  real(kind=default), dimension(n_hel), save :: hel_max_abs = 0
  real(kind=default), save :: hel_sum_abs = 0, hel_threshold = 1E10_default
  integer, save :: hel_count = 0, hel_cutoff = 100
  integer :: i
  integer, save, dimension(n_hel) :: hel_map = (/(i, i = 1, n_hel)/)
  integer, save :: hel_finite = n_hel

    type(momentum) :: p1, p2, p3, p4, p5, p6, p7, p8
    type(momentum) :: p12, p126, p1267, p127, p128, p167, p34, p345, p67, &
      p678
    type(spinor) :: owf_fd3_i1_p8, owf_fn2_p7, owf_fl1_p3, owf_fl1_p1
    type(conjspinor) :: owf_fd3b_o1_p5, owf_fn1b_p4, owf_fl1b_p2, owf_fl2b_p6
    type(spinor) :: owf_fd3_i1_p128, owf_fu3_i1_p678, owf_fn2_p127, &
      owf_fn1_p167
    type(conjspinor) :: owf_fu3b_o1_p345, owf_fl2b_p126
    type(vector) :: owf_fa_p12, owf_fz_p12, owf_fwm_p34, owf_fwp_p1267, &
      owf_fwp_p67
    complex(kind=default) :: oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1

contains

  pure function md5sum ()
    character(len=32) :: md5sum
    ! DON'T EVEN THINK of modifying the following line!
    md5sum = "6C81D0068F192DC5A272B5F6678BC93D"
  end function md5sum

  subroutine init (par, scheme)
    real(kind=default), dimension(*), intent(in) :: par
    integer, intent(in) :: scheme
    call import_from_whizard (par, scheme)
  end subroutine init

  subroutine final ()
  end subroutine final

  subroutine update_alpha_s (alpha_s)
    real(kind=default), intent(in) :: alpha_s
    call model_update_alpha_s (alpha_s)
  end subroutine update_alpha_s

  pure function number_particles_in () result (n)
    integer :: n
    n = n_in
  end function number_particles_in

  pure function number_particles_out () result (n)
    integer :: n
    n = n_out
  end function number_particles_out

  pure function number_spin_states () result (n)
    integer :: n
    n = size (table_spin_states, dim=2)
  end function number_spin_states

  pure subroutine spin_states (a)
    integer, dimension(:,:), intent(out) :: a
    a = table_spin_states
  end subroutine spin_states

  pure function number_flavor_states () result (n)
    integer :: n
    n = size (table_flavor_states, dim=2)
  end function number_flavor_states

  pure subroutine flavor_states (a)
    integer, dimension(:,:), intent(out) :: a
    a = table_flavor_states
  end subroutine flavor_states

  pure subroutine external_masses (m, flv)
    real(kind=default), dimension(:), intent(out) :: m
    integer, intent(in) :: flv
    select case (flv)
    case (  1)
      m( 1) = mass(11)
      m( 2) = mass(11)
      m( 3) = mass(11)
      m( 4) = mass(12)
      m( 5) = mass(5)
      m( 6) = mass(13)
      m( 7) = mass(14)
      m( 8) = mass(5)
    end select
  end subroutine external_masses

  pure function openmp_supported () result (status)
    logical :: status
    status = .false.
  end function openmp_supported

  pure function number_color_indices () result (n)
    integer :: n
    n = size (table_color_flows, dim=1)
  end function number_color_indices

  pure function number_color_flows () result (n)
    integer :: n
    n = size (table_color_flows, dim=3)
  end function number_color_flows

  pure subroutine color_flows (a, g)
    integer, dimension(:,:,:), intent(out) :: a
    logical, dimension(:,:), intent(out) :: g
    a = table_color_flows
    g = table_ghost_flags
  end subroutine color_flows

  pure function number_color_factors () result (n)
    integer :: n
    n = size (table_color_factors)
  end function number_color_factors

  pure subroutine color_factors (cf)
    type(OCF), dimension(:), intent(out) :: cf
    cf = table_color_factors
  end subroutine color_factors

  function color_sum (flv, hel) result (amp2)
    integer, intent(in) :: flv, hel
    real(kind=default) :: amp2
    amp2 = real (omega_color_sum (flv, hel, amp_all_orders, table_color_factors))
  end function color_sum

  subroutine new_event (p)
    real(kind=default), dimension(0:3,*), intent(in) :: p
    logical :: mask_dirty
    integer :: hel
    call calculate_amplitudes (amp_by_orders, p, hel_is_allowed)
    amp_all_orders = sum (amp_by_orders, dim=1)
    if ((hel_threshold .gt. 0) .and. (hel_count .le. hel_cutoff)) then
      call omega_update_helicity_selection (hel_count, amp_all_orders, &
              hel_max_abs, hel_sum_abs, hel_is_allowed, hel_threshold, &
              hel_cutoff, mask_dirty)
      if (mask_dirty) then
        hel_finite = 0
        do hel = 1, n_hel
          if (hel_is_allowed(hel)) then
            hel_finite = hel_finite + 1
            hel_map(hel_finite) = hel
          end if
        end do
      end if
    end if
  end subroutine new_event

  subroutine reset_helicity_selection (threshold, cutoff)
    real(kind=default), intent(in) :: threshold
    integer, intent(in) :: cutoff
    integer :: i
    hel_is_allowed = T
    hel_max_abs = 0
    hel_sum_abs = 0
    hel_count = 0
    hel_threshold = threshold
    hel_cutoff = cutoff
    hel_map = (/(i, i = 1, n_hel)/)
    hel_finite = n_hel
  end subroutine reset_helicity_selection

  pure function is_allowed (flv, hel, col) result (yorn)
    logical :: yorn
    integer, intent(in) :: flv, hel, col
    yorn = hel_is_allowed(hel) .and. flv_col_is_allowed(flv,col)
  end function is_allowed

  pure function get_amplitude (flv, hel, col) result (amp)
    complex(kind=default) :: amp
    integer, intent(in) :: flv, hel, col
    amp = amp_all_orders(flv, col, hel)
  end function get_amplitude



  subroutine calculate_amplitudes (amp, k, mask)
    complex(kind=default), dimension(:,:,:,:), intent(out) :: amp
    real(kind=default), dimension(0:3,*), intent(in) :: k
    logical, dimension(:), intent(in) :: mask
    integer, dimension(n_prt) :: s
    integer :: h, hi
    p1 = - k(:,1) ! incoming
    p2 = - k(:,2) ! incoming
    p3 =   k(:,3) ! outgoing
    p4 =   k(:,4) ! outgoing
    p5 =   k(:,5) ! outgoing
    p6 =   k(:,6) ! outgoing
    p7 =   k(:,7) ! outgoing
    p8 =   k(:,8) ! outgoing
    p12 = p1 + p2
    p34 = p3 + p4
    p67 = p6 + p7
    p345 = p5 + p34
    p126 = p6 + p12
    p127 = p7 + p12
    p167 = p1 + p67
    p128 = p8 + p12
    p678 = p8 + p67
    p1267 = p2 + p167
    amp = 0
    if (hel_finite == 0) return
    do hi = 1, hel_finite
      h = hel_map(hi)
      s = table_spin_states(:,h)
      owf_fl1_p1 = u (mass(11), - p1, s(1))
      owf_fl1b_p2 = vbar (mass(11), - p2, s(2))
      owf_fl1_p3 = v (mass(11), p3, s(3))
      owf_fn1b_p4 = ubar (mass(12), p4, s(4))
      owf_fd3b_o1_p5 = ubar (mass(5), p5, s(5))
      owf_fl2b_p6 = ubar (mass(13), p6, s(6))
      owf_fn2_p7 = v (mass(14), p7, s(7))
      owf_fd3_i1_p8 = v (mass(5), p8, s(8))
      call compute_fusions_0001 ()
      call compute_fusions_0002 ()
      call compute_brakets_0001 ()
      amp(1,1,1,h) = oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1
    end do
  end subroutine calculate_amplitudes
  subroutine compute_fusions_0001 ()
      owf_fa_p12 = pr_feynman(p12, + v_ff(qlep,owf_fl1b_p2,owf_fl1_p1))
      owf_fz_p12 = pr_unitarity(p12,mass(23),wd_tl(p12,width(23)),.false., &
         + va_ff(gnclep(1),gnclep(2),owf_fl1b_p2,owf_fl1_p1))
      owf_fwm_p34 = pr_unitarity(p34,mass(24),wd_tl(p34,width(24)),.false., &
         + vl_ff(gcc,owf_fn1b_p4,owf_fl1_p3))
      owf_fwp_p67 = pr_unitarity(p67,mass(24),wd_tl(p67,width(24)),.false., &
         + vl_ff(gcc,owf_fl2b_p6,owf_fn2_p7))
      owf_fu3b_o1_p345 = pr_psibar(p345,mass(6),wd_tl(p345,width(6)),.false., &
         - f_fvl(gcc,owf_fd3b_o1_p5,owf_fwm_p34))
      owf_fl2b_p126 = pr_psibar(p126,mass(13),wd_tl(p126,width(13)),.false., &
         - f_fv(qlep,owf_fl2b_p6,owf_fa_p12) &
         - f_fva(gnclep(1),gnclep(2),owf_fl2b_p6,owf_fz_p12))
      owf_fn2_p127 = pr_psi(p127,mass(14),wd_tl(p127,width(14)),.false., &
         - f_vaf(gncneu(1),gncneu(2),owf_fz_p12,owf_fn2_p7))
      owf_fn1_p167 = pr_psi(p167,mass(12),wd_tl(p167,width(12)),.false., &
         + f_vlf(gcc,owf_fwp_p67,owf_fl1_p1))
      owf_fd3_i1_p128 = pr_psi(p128,mass(5),wd_tl(p128,width(5)),.false., &
         - f_vf(qdwn,owf_fa_p12,owf_fd3_i1_p8) &
         - f_vaf(gncdwn(1),gncdwn(2),owf_fz_p12,owf_fd3_i1_p8))
      owf_fu3_i1_p678 = pr_psi(p678,mass(6),wd_tl(p678,width(6)),.false., &
         - f_vlf(gcc,owf_fwp_p67,owf_fd3_i1_p8))
  end subroutine compute_fusions_0001
  subroutine compute_fusions_0002 ()
      owf_fwp_p1267 = &
         pr_unitarity(p1267,mass(24),wd_tl(p1267,width(24)),.false., &
         + vl_ff(gcc,owf_fl1b_p2,owf_fn1_p167) &
         - vl_ff(gcc,owf_fl2b_p6,owf_fn2_p127) &
         - vl_ff(gcc,owf_fl2b_p126,owf_fn2_p7) &
         + g_gg(iqw,owf_fwp_p67,p67,owf_fa_p12,p12) &
         + g_gg(igzww,owf_fwp_p67,p67,owf_fz_p12,p12))
  end subroutine compute_fusions_0002
  subroutine compute_brakets_0001 ()
      oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 = 0
      oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 = &
        oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 + owf_fu3b_o1_p345*( &
         - f_vaf(gncup(1),gncup(2),owf_fz_p12,owf_fu3_i1_p678) &
         - f_vf(qup,owf_fa_p12,owf_fu3_i1_p678))
      oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 = &
        oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 + ( &
         - f_fvl(gcc,owf_fu3b_o1_p345,owf_fwp_p67))*owf_fd3_i1_p128
      oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 = &
        oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 + owf_fwp_p1267*( &
         + vl_ff(gcc,owf_fu3b_o1_p345,owf_fd3_i1_p8))
      oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 = &
         - oks_fl1_fl1b_fl1b_fn1_fd3_i1_fl2_fn2b_fd3b_o1 ! 6 vertices, 5 propagators
      ! unit symmetry factor
  end subroutine compute_brakets_0001

end module opr_proc_epmum_R44_i1_computation
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! O'Mega API Version 1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_proc_epmum_R44_i1_api_v1
  use opr_proc_epmum_R44_i1_computation, only: number_particles_in, &
       number_particles_out, number_color_indices, reset_helicity_selection, &
       new_event, is_allowed, get_amplitude, color_sum, external_masses, &
       openmp_supported, table_coupling_orders, table_coupling_powers, &
       amp_by_orders, table_spin_states, table_flavor_states, &
       number_spin_states, spin_states, number_flavor_states, flavor_states, &
       number_color_flows, color_flows, number_color_factors, color_factors, &
       init, final, update_alpha_s, md5sum
  implicit none
  public
end module opr_proc_epmum_R44_i1_api_v1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Backward compatible alias for O'Mega API Version 1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_proc_epmum_R44_i1
  use opr_proc_epmum_R44_i1_api_v1
  implicit none
  public
end module opr_proc_epmum_R44_i1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! O'Mega API Version 3
! WORK IN PROCESS !!!!
! NOT FOR PRODUCTION !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_proc_epmum_R44_i1_api_v3
  use omega_birdtracks
  use omega_api_v3
  use opr_proc_epmum_R44_i1_computation
  implicit none
  private
  public :: load_amplidude
! DUMMY DECLARATIONS FOR TESTING!
  integer, parameter, public :: n_incoming = 2
  integer, parameter, public :: n_outgoing = 2
  integer, parameter, public :: n_particles = 4
  integer, parameter, public :: n_colorflows = 2
  integer, parameter :: max_rank_inflowing = 1
  integer, parameter :: max_rank_outflowing = 1
  integer, parameter :: max_n_eps = 0
  integer, parameter :: max_n_eps_bar = 0
  integer, dimension(n_particles,n_colorflows), save :: rank_inflowing, rank_outflowing
  integer, dimension(n_colorflows), save :: n_eps, n_eps_bar
  integer, dimension(max_rank_inflowing,n_particles,n_colorflows), save :: inflowing, outflowing
  logical, dimension(n_particles,n_colorflows), save :: is_ghost
  integer, dimension(3,max_n_eps,n_colorflows), save :: eps
  integer, dimension(3,max_n_eps_bar,n_colorflows), save :: eps_bar

contains

  pure subroutine load_amplidude (a)
   type(amplitude), intent(inout) :: a
   call copy_amplitude &
      (a, n_incoming, table_flavor_states, table_spin_states, &
       rank_inflowing, inflowing, rank_outflowing, outflowing, is_ghost, &
       n_eps, eps, n_eps_bar, eps_bar, &
       table_coupling_orders, table_coupling_powers, amp_by_orders)
  end subroutine load_amplidude

end module opr_proc_epmum_R44_i1_api_v3
