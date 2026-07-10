! File generated automatically by O'Mega 3.1.5 release Sep 13 2024
!
!   /cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/bin/omega_SM.opt -o tbar_decay_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_tbar_decay_i1 -target:md5sum BDDABF8794DB4CD885F2F27AF45DE4D7 -target:openmp -fusion:progress -decay "tbar -> bbar mu- numubar"
!
! with all scattering amplitudes for the process(es)
!
!   flavor combinations:
!
!       1: tbar -> bbar mu- numubar
!
!   color flows:
!
!       1: (  0, -1) -> (  0, -1) (  0,  0) (  0,  0)
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
!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Amplitude computation module
! NOT to be USEd by application programs
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_tbar_decay_i1_computation
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

  integer, parameter :: n_prt = 4
  integer, parameter :: n_in = 1
  integer, parameter :: n_out = 3
  integer, parameter :: n_cflow = 1
  integer, parameter :: n_cindex = 2
  integer, parameter :: n_flv = 1
  integer, parameter :: n_hel = 16
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
  data table_spin_states(:,   1) / -1, -1, -1, -1 /
  data table_spin_states(:,   2) / -1, -1, -1,  1 /
  data table_spin_states(:,   3) / -1, -1,  1, -1 /
  data table_spin_states(:,   4) / -1, -1,  1,  1 /
  data table_spin_states(:,   5) / -1,  1, -1, -1 /
  data table_spin_states(:,   6) / -1,  1, -1,  1 /
  data table_spin_states(:,   7) / -1,  1,  1, -1 /
  data table_spin_states(:,   8) / -1,  1,  1,  1 /
  data table_spin_states(:,   9) /  1, -1, -1, -1 /
  data table_spin_states(:,  10) /  1, -1, -1,  1 /
  data table_spin_states(:,  11) /  1, -1,  1, -1 /
  data table_spin_states(:,  12) /  1, -1,  1,  1 /
  data table_spin_states(:,  13) /  1,  1, -1, -1 /
  data table_spin_states(:,  14) /  1,  1, -1,  1 /
  data table_spin_states(:,  15) /  1,  1,  1, -1 /
  data table_spin_states(:,  16) /  1,  1,  1,  1 /

  integer, dimension(n_prt,n_flv), save, protected :: table_flavor_states
  data table_flavor_states(:,   1) /  -6,  -5,  13, -14 / ! tbar bbar mu- numubar

  integer, dimension(n_cindex,n_prt,n_cflow), save, protected :: table_color_flows
  data table_color_flows(:,:,   1) / 0,-1,  0,-1,  0,0,  0,0 /

  logical, dimension(n_prt,n_cflow), save, protected :: table_ghost_flags
  data table_ghost_flags(:,   1) / F,  F,  F,  F /

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

    type(momentum) :: p1, p2, p3, p4
    type(momentum) :: p12
  type thread_local_data
    type(spinor) :: owf_fd3_i1_p2, owf_fn2_p4
    type(conjspinor) :: owf_fu3b_o1_p1, owf_fl2b_p3
    type(vector) :: owf_fwm_p12
    complex(kind=default) :: oks_fu3b_o1_fd3b_o1_fl2_fn2b
  end type thread_local_data
  type(thread_local_data) :: tld

contains

  pure function md5sum ()
    character(len=32) :: md5sum
    ! DON'T EVEN THINK of modifying the following line!
    md5sum = "BDDABF8794DB4CD885F2F27AF45DE4D7"
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
      m( 1) = mass(6)
      m( 2) = mass(5)
      m( 3) = mass(13)
      m( 4) = mass(14)
    end select
  end subroutine external_masses

  pure function openmp_supported () result (status)
    logical :: status
    status = .true.
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
    p2 =   k(:,2) ! outgoing
    p3 =   k(:,3) ! outgoing
    p4 =   k(:,4) ! outgoing
    p12 = p1 + p2
    amp = 0
    if (hel_finite == 0) return
!$OMP PARALLEL DO DEFAULT(SHARED) PRIVATE(s, h, tld) SCHEDULE(STATIC)
    do hi = 1, hel_finite
      h = hel_map(hi)
      s = table_spin_states(:,h)
      tld%owf_fu3b_o1_p1 = vbar (mass(6), - p1, s(1))
      tld%owf_fd3_i1_p2 = v (mass(5), p2, s(2))
      tld%owf_fl2b_p3 = ubar (mass(13), p3, s(3))
      tld%owf_fn2_p4 = v (mass(14), p4, s(4))
      call compute_fusions_0001 (tld)
      call compute_brakets_0001 (tld)
      amp(1,1,1,h) = tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b
    end do
!$OMP END PARALLEL DO
  end subroutine calculate_amplitudes
  subroutine compute_fusions_0001 (tld)
  type(thread_local_data), intent(inout) :: tld
      tld%owf_fwm_p12 = &
         pr_unitarity(p12,mass(24),wd_tl(p12,width(24)),.false., &
         + vl_ff(gcc,tld%owf_fu3b_o1_p1,tld%owf_fd3_i1_p2))
  end subroutine compute_fusions_0001
  subroutine compute_brakets_0001 (tld)
  type(thread_local_data), intent(inout) :: tld
      tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b = 0
      tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b = tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b &
         + tld%owf_fwm_p12*( + vl_ff(gcc,tld%owf_fl2b_p3,tld%owf_fn2_p4))
      tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b = &
         - tld%oks_fu3b_o1_fd3b_o1_fl2_fn2b ! 2 vertices, 1 propagators
      ! unit symmetry factor
  end subroutine compute_brakets_0001

end module opr_tbar_decay_i1_computation
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! O'Mega API Version 1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_tbar_decay_i1_api_v1
  use opr_tbar_decay_i1_computation, only: number_particles_in, &
       number_particles_out, number_color_indices, reset_helicity_selection, &
       new_event, is_allowed, get_amplitude, color_sum, external_masses, &
       openmp_supported, table_coupling_orders, table_coupling_powers, &
       amp_by_orders, table_spin_states, table_flavor_states, &
       number_spin_states, spin_states, number_flavor_states, flavor_states, &
       number_color_flows, color_flows, number_color_factors, color_factors, &
       init, final, update_alpha_s, md5sum
  implicit none
  public
end module opr_tbar_decay_i1_api_v1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Backward compatible alias for O'Mega API Version 1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_tbar_decay_i1
  use opr_tbar_decay_i1_api_v1
  implicit none
  public
end module opr_tbar_decay_i1
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! O'Mega API Version 3
! WORK IN PROCESS !!!!
! NOT FOR PRODUCTION !
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
module opr_tbar_decay_i1_api_v3
  use omega_birdtracks
  use omega_api_v3
  use opr_tbar_decay_i1_computation
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

end module opr_tbar_decay_i1_api_v3
