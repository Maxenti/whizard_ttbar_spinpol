! WHIZARD matrix-element code interface
!
! Automatically generated file, do not edit

! Module: define library driver as an extension of the abstract driver type.
! This is used _only_ by the library dispatcher of a static executable.
! For a dynamical library, the stand-alone procedures are linked via libdl.

module proc_epmum_R_driver
  use iso_c_binding
  use iso_varying_string, string_t => varying_string
  use diagnostics
  use prclib_interfaces

  implicit none

  type, extends (prclib_driver_t) :: proc_epmum_R_driver_t
   contains
     procedure :: get_c_funptr => proc_epmum_R_driver_get_c_funptr
  end type proc_epmum_R_driver_t

contains

  function proc_epmum_R_driver_get_c_funptr (driver, feature) result (c_fptr)
    class(proc_epmum_R_driver_t), intent(inout) :: driver
    type(string_t), intent(in) :: feature
    type(c_funptr) :: c_fptr
    procedure(prc_get_n_processes) &
         :: proc_epmum_R_get_n_processes
    procedure(prc_get_stringptr) &
         :: proc_epmum_R_get_process_id_ptr
    procedure(prc_get_stringptr) &
         :: proc_epmum_R_get_model_name_ptr
    procedure(prc_get_stringptr) &
         :: proc_epmum_R_get_md5sum_ptr
    procedure(prc_get_log) &
         :: proc_epmum_R_get_openmp_status
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_in
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_out
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_flv
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_hel
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_col
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_cin
    procedure(prc_get_int) &
         :: proc_epmum_R_get_n_cf
    procedure(prc_set_int_tab1) &
         :: proc_epmum_R_set_flv_state_ptr
    procedure(prc_set_int_tab1) &
         :: proc_epmum_R_set_hel_state_ptr
    procedure(prc_set_col_state) &
         :: proc_epmum_R_set_col_state_ptr
    procedure(prc_set_color_factors) &
         :: proc_epmum_R_set_color_factors_ptr
    procedure(prc_get_fptr) &
         :: proc_epmum_R_get_fptr
    select case (char (feature))
    case ('get_n_processes')
       c_fptr = c_funloc (proc_epmum_R_get_n_processes)
    case ('get_process_id_ptr')
       c_fptr = c_funloc (proc_epmum_R_get_process_id_ptr)
    case ('get_model_name_ptr')
       c_fptr = c_funloc (proc_epmum_R_get_model_name_ptr)
    case ('get_md5sum_ptr')
       c_fptr = c_funloc (proc_epmum_R_get_md5sum_ptr)
    case ('get_openmp_status')
       c_fptr = c_funloc (proc_epmum_R_get_openmp_status)
    case ('get_n_in')
       c_fptr = c_funloc (proc_epmum_R_get_n_in)
    case ('get_n_out')
       c_fptr = c_funloc (proc_epmum_R_get_n_out)
    case ('get_n_flv')
       c_fptr = c_funloc (proc_epmum_R_get_n_flv)
    case ('get_n_hel')
       c_fptr = c_funloc (proc_epmum_R_get_n_hel)
    case ('get_n_col')
       c_fptr = c_funloc (proc_epmum_R_get_n_col)
    case ('get_n_cin')
       c_fptr = c_funloc (proc_epmum_R_get_n_cin)
    case ('get_n_cf')
       c_fptr = c_funloc (proc_epmum_R_get_n_cf)
    case ('set_flv_state_ptr')
       c_fptr = c_funloc (proc_epmum_R_set_flv_state_ptr)
    case ('set_hel_state_ptr')
       c_fptr = c_funloc (proc_epmum_R_set_hel_state_ptr)
    case ('set_col_state_ptr')
       c_fptr = c_funloc (proc_epmum_R_set_col_state_ptr)
    case ('set_color_factors_ptr')
       c_fptr = c_funloc (proc_epmum_R_set_color_factors_ptr)
    case ('get_fptr')
       c_fptr = c_funloc (proc_epmum_R_get_fptr)
    case default
       call msg_bug ('prclib2 driver setup: unknown function name')
    end select
  end function proc_epmum_R_driver_get_c_funptr

end module proc_epmum_R_driver

! Stand-alone external procedures: used for both static and dynamic linkage

! The MD5 sum of the library
function proc_epmum_R_md5sum () result (md5sum)
  implicit none
  character(32) :: md5sum
  md5sum = '6C2BBE3378286668179EBBC67D599F59'
end function proc_epmum_R_md5sum

! Return the number of processes in this library
function proc_epmum_R_get_n_processes () result (n) bind(C)
  use iso_c_binding
  implicit none
  integer(c_int) :: n
  n = 44
end function proc_epmum_R_get_n_processes

! Return the process ID of process #i (as a C pointer to a character array)
subroutine proc_epmum_R_get_process_id_ptr (i, cptr, len) bind(C)
  use iso_c_binding
  implicit none
  integer(c_int), intent(in) :: i
  type(c_ptr), intent(out) :: cptr
  integer(c_int), intent(out) :: len
  character(kind=c_char), dimension(:), allocatable, target, save :: a
  interface
     subroutine proc_epmum_R_string_to_array (string, a)
       use iso_c_binding
       implicit none
       character(*), intent(in) :: string
       character(kind=c_char), dimension(:), allocatable, intent(out) :: a
     end subroutine proc_epmum_R_string_to_array
  end interface
  select case (i)
  case (0);  if (allocated (a))  deallocate (a)
  case (1);  call proc_epmum_R_string_to_array ('proc_epmum_R1_i1', a)
  case (2);  call proc_epmum_R_string_to_array ('proc_epmum_R2_i1', a)
  case (3);  call proc_epmum_R_string_to_array ('proc_epmum_R3_i1', a)
  case (4);  call proc_epmum_R_string_to_array ('proc_epmum_R4_i1', a)
  case (5);  call proc_epmum_R_string_to_array ('proc_epmum_R5_i1', a)
  case (6);  call proc_epmum_R_string_to_array ('proc_epmum_R6_i1', a)
  case (7);  call proc_epmum_R_string_to_array ('proc_epmum_R7_i1', a)
  case (8);  call proc_epmum_R_string_to_array ('proc_epmum_R8_i1', a)
  case (9);  call proc_epmum_R_string_to_array ('proc_epmum_R9_i1', a)
  case (10);  call proc_epmum_R_string_to_array ('proc_epmum_R10_i1', a)
  case (11);  call proc_epmum_R_string_to_array ('proc_epmum_R11_i1', a)
  case (12);  call proc_epmum_R_string_to_array ('proc_epmum_R12_i1', a)
  case (13);  call proc_epmum_R_string_to_array ('proc_epmum_R13_i1', a)
  case (14);  call proc_epmum_R_string_to_array ('proc_epmum_R14_i1', a)
  case (15);  call proc_epmum_R_string_to_array ('proc_epmum_R15_i1', a)
  case (16);  call proc_epmum_R_string_to_array ('proc_epmum_R16_i1', a)
  case (17);  call proc_epmum_R_string_to_array ('proc_epmum_R17_i1', a)
  case (18);  call proc_epmum_R_string_to_array ('proc_epmum_R18_i1', a)
  case (19);  call proc_epmum_R_string_to_array ('proc_epmum_R19_i1', a)
  case (20);  call proc_epmum_R_string_to_array ('proc_epmum_R20_i1', a)
  case (21);  call proc_epmum_R_string_to_array ('proc_epmum_R21_i1', a)
  case (22);  call proc_epmum_R_string_to_array ('proc_epmum_R22_i1', a)
  case (23);  call proc_epmum_R_string_to_array ('proc_epmum_R23_i1', a)
  case (24);  call proc_epmum_R_string_to_array ('proc_epmum_R24_i1', a)
  case (25);  call proc_epmum_R_string_to_array ('proc_epmum_R25_i1', a)
  case (26);  call proc_epmum_R_string_to_array ('proc_epmum_R26_i1', a)
  case (27);  call proc_epmum_R_string_to_array ('proc_epmum_R27_i1', a)
  case (28);  call proc_epmum_R_string_to_array ('proc_epmum_R28_i1', a)
  case (29);  call proc_epmum_R_string_to_array ('proc_epmum_R29_i1', a)
  case (30);  call proc_epmum_R_string_to_array ('proc_epmum_R30_i1', a)
  case (31);  call proc_epmum_R_string_to_array ('proc_epmum_R31_i1', a)
  case (32);  call proc_epmum_R_string_to_array ('proc_epmum_R32_i1', a)
  case (33);  call proc_epmum_R_string_to_array ('proc_epmum_R33_i1', a)
  case (34);  call proc_epmum_R_string_to_array ('proc_epmum_R34_i1', a)
  case (35);  call proc_epmum_R_string_to_array ('proc_epmum_R35_i1', a)
  case (36);  call proc_epmum_R_string_to_array ('proc_epmum_R36_i1', a)
  case (37);  call proc_epmum_R_string_to_array ('proc_epmum_R37_i1', a)
  case (38);  call proc_epmum_R_string_to_array ('proc_epmum_R38_i1', a)
  case (39);  call proc_epmum_R_string_to_array ('proc_epmum_R39_i1', a)
  case (40);  call proc_epmum_R_string_to_array ('proc_epmum_R40_i1', a)
  case (41);  call proc_epmum_R_string_to_array ('proc_epmum_R41_i1', a)
  case (42);  call proc_epmum_R_string_to_array ('proc_epmum_R42_i1', a)
  case (43);  call proc_epmum_R_string_to_array ('proc_epmum_R43_i1', a)
  case (44);  call proc_epmum_R_string_to_array ('proc_epmum_R44_i1', a)
  end select
  if (allocated (a)) then
     cptr = c_loc (a)
     len = size (a)
  else
     cptr = c_null_ptr
     len = 0
  end if
end subroutine proc_epmum_R_get_process_id_ptr

! Return the model name for process #i (as a C pointer to a character array)
subroutine proc_epmum_R_get_model_name_ptr (i, cptr, len) bind(C)
  use iso_c_binding
  implicit none
  integer(c_int), intent(in) :: i
  type(c_ptr), intent(out) :: cptr
  integer(c_int), intent(out) :: len
  character(kind=c_char), dimension(:), allocatable, target, save :: a
  interface
     subroutine proc_epmum_R_string_to_array (string, a)
       use iso_c_binding
       implicit none
       character(*), intent(in) :: string
       character(kind=c_char), dimension(:), allocatable, intent(out) :: a
     end subroutine proc_epmum_R_string_to_array
  end interface
  select case (i)
  case (0);  if (allocated (a))  deallocate (a)
  case (1);  call proc_epmum_R_string_to_array ('SM', a)
  case (2);  call proc_epmum_R_string_to_array ('SM', a)
  case (3);  call proc_epmum_R_string_to_array ('SM', a)
  case (4);  call proc_epmum_R_string_to_array ('SM', a)
  case (5);  call proc_epmum_R_string_to_array ('SM', a)
  case (6);  call proc_epmum_R_string_to_array ('SM', a)
  case (7);  call proc_epmum_R_string_to_array ('SM', a)
  case (8);  call proc_epmum_R_string_to_array ('SM', a)
  case (9);  call proc_epmum_R_string_to_array ('SM', a)
  case (10);  call proc_epmum_R_string_to_array ('SM', a)
  case (11);  call proc_epmum_R_string_to_array ('SM', a)
  case (12);  call proc_epmum_R_string_to_array ('SM', a)
  case (13);  call proc_epmum_R_string_to_array ('SM', a)
  case (14);  call proc_epmum_R_string_to_array ('SM', a)
  case (15);  call proc_epmum_R_string_to_array ('SM', a)
  case (16);  call proc_epmum_R_string_to_array ('SM', a)
  case (17);  call proc_epmum_R_string_to_array ('SM', a)
  case (18);  call proc_epmum_R_string_to_array ('SM', a)
  case (19);  call proc_epmum_R_string_to_array ('SM', a)
  case (20);  call proc_epmum_R_string_to_array ('SM', a)
  case (21);  call proc_epmum_R_string_to_array ('SM', a)
  case (22);  call proc_epmum_R_string_to_array ('SM', a)
  case (23);  call proc_epmum_R_string_to_array ('SM', a)
  case (24);  call proc_epmum_R_string_to_array ('SM', a)
  case (25);  call proc_epmum_R_string_to_array ('SM', a)
  case (26);  call proc_epmum_R_string_to_array ('SM', a)
  case (27);  call proc_epmum_R_string_to_array ('SM', a)
  case (28);  call proc_epmum_R_string_to_array ('SM', a)
  case (29);  call proc_epmum_R_string_to_array ('SM', a)
  case (30);  call proc_epmum_R_string_to_array ('SM', a)
  case (31);  call proc_epmum_R_string_to_array ('SM', a)
  case (32);  call proc_epmum_R_string_to_array ('SM', a)
  case (33);  call proc_epmum_R_string_to_array ('SM', a)
  case (34);  call proc_epmum_R_string_to_array ('SM', a)
  case (35);  call proc_epmum_R_string_to_array ('SM', a)
  case (36);  call proc_epmum_R_string_to_array ('SM', a)
  case (37);  call proc_epmum_R_string_to_array ('SM', a)
  case (38);  call proc_epmum_R_string_to_array ('SM', a)
  case (39);  call proc_epmum_R_string_to_array ('SM', a)
  case (40);  call proc_epmum_R_string_to_array ('SM', a)
  case (41);  call proc_epmum_R_string_to_array ('SM', a)
  case (42);  call proc_epmum_R_string_to_array ('SM', a)
  case (43);  call proc_epmum_R_string_to_array ('SM', a)
  case (44);  call proc_epmum_R_string_to_array ('SM', a)
  end select
  if (allocated (a)) then
     cptr = c_loc (a)
     len = size (a)
  else
     cptr = c_null_ptr
     len = 0
  end if
end subroutine proc_epmum_R_get_model_name_ptr

! Return the MD5 sum for the process configuration (as a C pointer to a character array)
subroutine proc_epmum_R_get_md5sum_ptr (i, cptr, len) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_md5sum => md5sum
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_md5sum => md5sum
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_md5sum => md5sum
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_md5sum => md5sum
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_md5sum => md5sum
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_md5sum => md5sum
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_md5sum => md5sum
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_md5sum => md5sum
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_md5sum => md5sum
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_md5sum => md5sum
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_md5sum => md5sum
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_md5sum => md5sum
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_md5sum => md5sum
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_md5sum => md5sum
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_md5sum => md5sum
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_md5sum => md5sum
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_md5sum => md5sum
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_md5sum => md5sum
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_md5sum => md5sum
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_md5sum => md5sum
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_md5sum => md5sum
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_md5sum => md5sum
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_md5sum => md5sum
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_md5sum => md5sum
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_md5sum => md5sum
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_md5sum => md5sum
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_md5sum => md5sum
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_md5sum => md5sum
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_md5sum => md5sum
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_md5sum => md5sum
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_md5sum => md5sum
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_md5sum => md5sum
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_md5sum => md5sum
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_md5sum => md5sum
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_md5sum => md5sum
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_md5sum => md5sum
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_md5sum => md5sum
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_md5sum => md5sum
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_md5sum => md5sum
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_md5sum => md5sum
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_md5sum => md5sum
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_md5sum => md5sum
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_md5sum => md5sum
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_md5sum => md5sum
  implicit none
  interface
     function proc_epmum_R_md5sum () result (md5sum)
       character(32) :: md5sum
     end function proc_epmum_R_md5sum
  end interface
  integer(c_int), intent(in) :: i
  type(c_ptr), intent(out) :: cptr
  integer(c_int), intent(out) :: len
  character(kind=c_char), dimension(32), target, save :: md5sum
  select case (i)
  case (0)
     call copy (proc_epmum_R_md5sum ())
     cptr = c_loc (md5sum)
  case (1)
     call copy (proc_epmum_R1_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (2)
     call copy (proc_epmum_R2_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (3)
     call copy (proc_epmum_R3_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (4)
     call copy (proc_epmum_R4_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (5)
     call copy (proc_epmum_R5_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (6)
     call copy (proc_epmum_R6_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (7)
     call copy (proc_epmum_R7_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (8)
     call copy (proc_epmum_R8_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (9)
     call copy (proc_epmum_R9_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (10)
     call copy (proc_epmum_R10_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (11)
     call copy (proc_epmum_R11_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (12)
     call copy (proc_epmum_R12_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (13)
     call copy (proc_epmum_R13_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (14)
     call copy (proc_epmum_R14_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (15)
     call copy (proc_epmum_R15_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (16)
     call copy (proc_epmum_R16_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (17)
     call copy (proc_epmum_R17_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (18)
     call copy (proc_epmum_R18_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (19)
     call copy (proc_epmum_R19_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (20)
     call copy (proc_epmum_R20_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (21)
     call copy (proc_epmum_R21_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (22)
     call copy (proc_epmum_R22_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (23)
     call copy (proc_epmum_R23_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (24)
     call copy (proc_epmum_R24_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (25)
     call copy (proc_epmum_R25_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (26)
     call copy (proc_epmum_R26_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (27)
     call copy (proc_epmum_R27_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (28)
     call copy (proc_epmum_R28_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (29)
     call copy (proc_epmum_R29_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (30)
     call copy (proc_epmum_R30_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (31)
     call copy (proc_epmum_R31_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (32)
     call copy (proc_epmum_R32_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (33)
     call copy (proc_epmum_R33_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (34)
     call copy (proc_epmum_R34_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (35)
     call copy (proc_epmum_R35_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (36)
     call copy (proc_epmum_R36_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (37)
     call copy (proc_epmum_R37_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (38)
     call copy (proc_epmum_R38_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (39)
     call copy (proc_epmum_R39_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (40)
     call copy (proc_epmum_R40_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (41)
     call copy (proc_epmum_R41_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (42)
     call copy (proc_epmum_R42_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (43)
     call copy (proc_epmum_R43_i1_md5sum ())
     cptr = c_loc (md5sum)
  case (44)
     call copy (proc_epmum_R44_i1_md5sum ())
     cptr = c_loc (md5sum)
  case default
     cptr = c_null_ptr
  end select
  len = 32
contains
  subroutine copy (md5sum_tmp)
    character, dimension(32), intent(in) :: md5sum_tmp
    md5sum = md5sum_tmp
  end subroutine copy
end subroutine proc_epmum_R_get_md5sum_ptr

! Auxiliary: convert character string to array pointer
subroutine proc_epmum_R_string_to_array (string, a)
  use iso_c_binding
  implicit none
  character(*), intent(in) :: string
  character(kind=c_char), dimension(:), allocatable, intent(out) :: a
  integer :: i
  allocate (a (len (string)))
  do i = 1, size (a)
     a(i) = string(i:i)
  end do
end subroutine proc_epmum_R_string_to_array

! Return the OpenMP support status
function proc_epmum_R_get_openmp_status (i) result (openmp_status) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_openmp_supported => openmp_supported
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_openmp_supported => openmp_supported
  implicit none
  integer(c_int), intent(in) :: i
  logical(c_bool) :: openmp_status
  select case (i)
  case (1);  openmp_status = proc_epmum_R1_i1_openmp_supported ()
  case (2);  openmp_status = proc_epmum_R2_i1_openmp_supported ()
  case (3);  openmp_status = proc_epmum_R3_i1_openmp_supported ()
  case (4);  openmp_status = proc_epmum_R4_i1_openmp_supported ()
  case (5);  openmp_status = proc_epmum_R5_i1_openmp_supported ()
  case (6);  openmp_status = proc_epmum_R6_i1_openmp_supported ()
  case (7);  openmp_status = proc_epmum_R7_i1_openmp_supported ()
  case (8);  openmp_status = proc_epmum_R8_i1_openmp_supported ()
  case (9);  openmp_status = proc_epmum_R9_i1_openmp_supported ()
  case (10);  openmp_status = proc_epmum_R10_i1_openmp_supported ()
  case (11);  openmp_status = proc_epmum_R11_i1_openmp_supported ()
  case (12);  openmp_status = proc_epmum_R12_i1_openmp_supported ()
  case (13);  openmp_status = proc_epmum_R13_i1_openmp_supported ()
  case (14);  openmp_status = proc_epmum_R14_i1_openmp_supported ()
  case (15);  openmp_status = proc_epmum_R15_i1_openmp_supported ()
  case (16);  openmp_status = proc_epmum_R16_i1_openmp_supported ()
  case (17);  openmp_status = proc_epmum_R17_i1_openmp_supported ()
  case (18);  openmp_status = proc_epmum_R18_i1_openmp_supported ()
  case (19);  openmp_status = proc_epmum_R19_i1_openmp_supported ()
  case (20);  openmp_status = proc_epmum_R20_i1_openmp_supported ()
  case (21);  openmp_status = proc_epmum_R21_i1_openmp_supported ()
  case (22);  openmp_status = proc_epmum_R22_i1_openmp_supported ()
  case (23);  openmp_status = proc_epmum_R23_i1_openmp_supported ()
  case (24);  openmp_status = proc_epmum_R24_i1_openmp_supported ()
  case (25);  openmp_status = proc_epmum_R25_i1_openmp_supported ()
  case (26);  openmp_status = proc_epmum_R26_i1_openmp_supported ()
  case (27);  openmp_status = proc_epmum_R27_i1_openmp_supported ()
  case (28);  openmp_status = proc_epmum_R28_i1_openmp_supported ()
  case (29);  openmp_status = proc_epmum_R29_i1_openmp_supported ()
  case (30);  openmp_status = proc_epmum_R30_i1_openmp_supported ()
  case (31);  openmp_status = proc_epmum_R31_i1_openmp_supported ()
  case (32);  openmp_status = proc_epmum_R32_i1_openmp_supported ()
  case (33);  openmp_status = proc_epmum_R33_i1_openmp_supported ()
  case (34);  openmp_status = proc_epmum_R34_i1_openmp_supported ()
  case (35);  openmp_status = proc_epmum_R35_i1_openmp_supported ()
  case (36);  openmp_status = proc_epmum_R36_i1_openmp_supported ()
  case (37);  openmp_status = proc_epmum_R37_i1_openmp_supported ()
  case (38);  openmp_status = proc_epmum_R38_i1_openmp_supported ()
  case (39);  openmp_status = proc_epmum_R39_i1_openmp_supported ()
  case (40);  openmp_status = proc_epmum_R40_i1_openmp_supported ()
  case (41);  openmp_status = proc_epmum_R41_i1_openmp_supported ()
  case (42);  openmp_status = proc_epmum_R42_i1_openmp_supported ()
  case (43);  openmp_status = proc_epmum_R43_i1_openmp_supported ()
  case (44);  openmp_status = proc_epmum_R44_i1_openmp_supported ()
  end select
end function proc_epmum_R_get_openmp_status

! Return the value of n_in
function proc_epmum_R_get_n_in (pid) result (n_in) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_in => number_particles_in
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_in => number_particles_in
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_in => number_particles_in
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_in => number_particles_in
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_in => number_particles_in
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_in => number_particles_in
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_in => number_particles_in
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_in => number_particles_in
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_in => number_particles_in
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_in => number_particles_in
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_in => number_particles_in
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_in => number_particles_in
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_in => number_particles_in
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_in => number_particles_in
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_in => number_particles_in
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_in => number_particles_in
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_in => number_particles_in
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_in => number_particles_in
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_in => number_particles_in
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_in => number_particles_in
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_in => number_particles_in
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_in => number_particles_in
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_in => number_particles_in
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_in => number_particles_in
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_in => number_particles_in
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_in => number_particles_in
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_in => number_particles_in
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_in => number_particles_in
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_in => number_particles_in
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_in => number_particles_in
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_in => number_particles_in
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_in => number_particles_in
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_in => number_particles_in
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_in => number_particles_in
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_in => number_particles_in
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_in => number_particles_in
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_in => number_particles_in
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_in => number_particles_in
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_in => number_particles_in
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_in => number_particles_in
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_in => number_particles_in
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_in => number_particles_in
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_in => number_particles_in
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_in => number_particles_in
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_in
  select case (pid)
  case (1);  n_in = proc_epmum_R1_i1_n_in ()
  case (2);  n_in = proc_epmum_R2_i1_n_in ()
  case (3);  n_in = proc_epmum_R3_i1_n_in ()
  case (4);  n_in = proc_epmum_R4_i1_n_in ()
  case (5);  n_in = proc_epmum_R5_i1_n_in ()
  case (6);  n_in = proc_epmum_R6_i1_n_in ()
  case (7);  n_in = proc_epmum_R7_i1_n_in ()
  case (8);  n_in = proc_epmum_R8_i1_n_in ()
  case (9);  n_in = proc_epmum_R9_i1_n_in ()
  case (10);  n_in = proc_epmum_R10_i1_n_in ()
  case (11);  n_in = proc_epmum_R11_i1_n_in ()
  case (12);  n_in = proc_epmum_R12_i1_n_in ()
  case (13);  n_in = proc_epmum_R13_i1_n_in ()
  case (14);  n_in = proc_epmum_R14_i1_n_in ()
  case (15);  n_in = proc_epmum_R15_i1_n_in ()
  case (16);  n_in = proc_epmum_R16_i1_n_in ()
  case (17);  n_in = proc_epmum_R17_i1_n_in ()
  case (18);  n_in = proc_epmum_R18_i1_n_in ()
  case (19);  n_in = proc_epmum_R19_i1_n_in ()
  case (20);  n_in = proc_epmum_R20_i1_n_in ()
  case (21);  n_in = proc_epmum_R21_i1_n_in ()
  case (22);  n_in = proc_epmum_R22_i1_n_in ()
  case (23);  n_in = proc_epmum_R23_i1_n_in ()
  case (24);  n_in = proc_epmum_R24_i1_n_in ()
  case (25);  n_in = proc_epmum_R25_i1_n_in ()
  case (26);  n_in = proc_epmum_R26_i1_n_in ()
  case (27);  n_in = proc_epmum_R27_i1_n_in ()
  case (28);  n_in = proc_epmum_R28_i1_n_in ()
  case (29);  n_in = proc_epmum_R29_i1_n_in ()
  case (30);  n_in = proc_epmum_R30_i1_n_in ()
  case (31);  n_in = proc_epmum_R31_i1_n_in ()
  case (32);  n_in = proc_epmum_R32_i1_n_in ()
  case (33);  n_in = proc_epmum_R33_i1_n_in ()
  case (34);  n_in = proc_epmum_R34_i1_n_in ()
  case (35);  n_in = proc_epmum_R35_i1_n_in ()
  case (36);  n_in = proc_epmum_R36_i1_n_in ()
  case (37);  n_in = proc_epmum_R37_i1_n_in ()
  case (38);  n_in = proc_epmum_R38_i1_n_in ()
  case (39);  n_in = proc_epmum_R39_i1_n_in ()
  case (40);  n_in = proc_epmum_R40_i1_n_in ()
  case (41);  n_in = proc_epmum_R41_i1_n_in ()
  case (42);  n_in = proc_epmum_R42_i1_n_in ()
  case (43);  n_in = proc_epmum_R43_i1_n_in ()
  case (44);  n_in = proc_epmum_R44_i1_n_in ()
  end select
end function proc_epmum_R_get_n_in

! Return the value of n_out
function proc_epmum_R_get_n_out (pid) result (n_out) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_out => number_particles_out
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_out => number_particles_out
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_out => number_particles_out
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_out => number_particles_out
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_out => number_particles_out
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_out => number_particles_out
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_out => number_particles_out
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_out => number_particles_out
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_out => number_particles_out
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_out => number_particles_out
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_out => number_particles_out
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_out => number_particles_out
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_out => number_particles_out
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_out => number_particles_out
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_out => number_particles_out
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_out => number_particles_out
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_out => number_particles_out
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_out => number_particles_out
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_out => number_particles_out
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_out => number_particles_out
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_out => number_particles_out
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_out => number_particles_out
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_out => number_particles_out
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_out => number_particles_out
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_out => number_particles_out
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_out => number_particles_out
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_out => number_particles_out
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_out => number_particles_out
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_out => number_particles_out
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_out => number_particles_out
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_out => number_particles_out
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_out => number_particles_out
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_out => number_particles_out
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_out => number_particles_out
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_out => number_particles_out
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_out => number_particles_out
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_out => number_particles_out
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_out => number_particles_out
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_out => number_particles_out
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_out => number_particles_out
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_out => number_particles_out
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_out => number_particles_out
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_out => number_particles_out
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_out => number_particles_out
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_out
  select case (pid)
  case (1);  n_out = proc_epmum_R1_i1_n_out ()
  case (2);  n_out = proc_epmum_R2_i1_n_out ()
  case (3);  n_out = proc_epmum_R3_i1_n_out ()
  case (4);  n_out = proc_epmum_R4_i1_n_out ()
  case (5);  n_out = proc_epmum_R5_i1_n_out ()
  case (6);  n_out = proc_epmum_R6_i1_n_out ()
  case (7);  n_out = proc_epmum_R7_i1_n_out ()
  case (8);  n_out = proc_epmum_R8_i1_n_out ()
  case (9);  n_out = proc_epmum_R9_i1_n_out ()
  case (10);  n_out = proc_epmum_R10_i1_n_out ()
  case (11);  n_out = proc_epmum_R11_i1_n_out ()
  case (12);  n_out = proc_epmum_R12_i1_n_out ()
  case (13);  n_out = proc_epmum_R13_i1_n_out ()
  case (14);  n_out = proc_epmum_R14_i1_n_out ()
  case (15);  n_out = proc_epmum_R15_i1_n_out ()
  case (16);  n_out = proc_epmum_R16_i1_n_out ()
  case (17);  n_out = proc_epmum_R17_i1_n_out ()
  case (18);  n_out = proc_epmum_R18_i1_n_out ()
  case (19);  n_out = proc_epmum_R19_i1_n_out ()
  case (20);  n_out = proc_epmum_R20_i1_n_out ()
  case (21);  n_out = proc_epmum_R21_i1_n_out ()
  case (22);  n_out = proc_epmum_R22_i1_n_out ()
  case (23);  n_out = proc_epmum_R23_i1_n_out ()
  case (24);  n_out = proc_epmum_R24_i1_n_out ()
  case (25);  n_out = proc_epmum_R25_i1_n_out ()
  case (26);  n_out = proc_epmum_R26_i1_n_out ()
  case (27);  n_out = proc_epmum_R27_i1_n_out ()
  case (28);  n_out = proc_epmum_R28_i1_n_out ()
  case (29);  n_out = proc_epmum_R29_i1_n_out ()
  case (30);  n_out = proc_epmum_R30_i1_n_out ()
  case (31);  n_out = proc_epmum_R31_i1_n_out ()
  case (32);  n_out = proc_epmum_R32_i1_n_out ()
  case (33);  n_out = proc_epmum_R33_i1_n_out ()
  case (34);  n_out = proc_epmum_R34_i1_n_out ()
  case (35);  n_out = proc_epmum_R35_i1_n_out ()
  case (36);  n_out = proc_epmum_R36_i1_n_out ()
  case (37);  n_out = proc_epmum_R37_i1_n_out ()
  case (38);  n_out = proc_epmum_R38_i1_n_out ()
  case (39);  n_out = proc_epmum_R39_i1_n_out ()
  case (40);  n_out = proc_epmum_R40_i1_n_out ()
  case (41);  n_out = proc_epmum_R41_i1_n_out ()
  case (42);  n_out = proc_epmum_R42_i1_n_out ()
  case (43);  n_out = proc_epmum_R43_i1_n_out ()
  case (44);  n_out = proc_epmum_R44_i1_n_out ()
  end select
end function proc_epmum_R_get_n_out

! Return the value of n_flv
function proc_epmum_R_get_n_flv (pid) result (n_flv) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_flv => number_flavor_states
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_flv => number_flavor_states
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_flv
  select case (pid)
  case (1);  n_flv = proc_epmum_R1_i1_n_flv ()
  case (2);  n_flv = proc_epmum_R2_i1_n_flv ()
  case (3);  n_flv = proc_epmum_R3_i1_n_flv ()
  case (4);  n_flv = proc_epmum_R4_i1_n_flv ()
  case (5);  n_flv = proc_epmum_R5_i1_n_flv ()
  case (6);  n_flv = proc_epmum_R6_i1_n_flv ()
  case (7);  n_flv = proc_epmum_R7_i1_n_flv ()
  case (8);  n_flv = proc_epmum_R8_i1_n_flv ()
  case (9);  n_flv = proc_epmum_R9_i1_n_flv ()
  case (10);  n_flv = proc_epmum_R10_i1_n_flv ()
  case (11);  n_flv = proc_epmum_R11_i1_n_flv ()
  case (12);  n_flv = proc_epmum_R12_i1_n_flv ()
  case (13);  n_flv = proc_epmum_R13_i1_n_flv ()
  case (14);  n_flv = proc_epmum_R14_i1_n_flv ()
  case (15);  n_flv = proc_epmum_R15_i1_n_flv ()
  case (16);  n_flv = proc_epmum_R16_i1_n_flv ()
  case (17);  n_flv = proc_epmum_R17_i1_n_flv ()
  case (18);  n_flv = proc_epmum_R18_i1_n_flv ()
  case (19);  n_flv = proc_epmum_R19_i1_n_flv ()
  case (20);  n_flv = proc_epmum_R20_i1_n_flv ()
  case (21);  n_flv = proc_epmum_R21_i1_n_flv ()
  case (22);  n_flv = proc_epmum_R22_i1_n_flv ()
  case (23);  n_flv = proc_epmum_R23_i1_n_flv ()
  case (24);  n_flv = proc_epmum_R24_i1_n_flv ()
  case (25);  n_flv = proc_epmum_R25_i1_n_flv ()
  case (26);  n_flv = proc_epmum_R26_i1_n_flv ()
  case (27);  n_flv = proc_epmum_R27_i1_n_flv ()
  case (28);  n_flv = proc_epmum_R28_i1_n_flv ()
  case (29);  n_flv = proc_epmum_R29_i1_n_flv ()
  case (30);  n_flv = proc_epmum_R30_i1_n_flv ()
  case (31);  n_flv = proc_epmum_R31_i1_n_flv ()
  case (32);  n_flv = proc_epmum_R32_i1_n_flv ()
  case (33);  n_flv = proc_epmum_R33_i1_n_flv ()
  case (34);  n_flv = proc_epmum_R34_i1_n_flv ()
  case (35);  n_flv = proc_epmum_R35_i1_n_flv ()
  case (36);  n_flv = proc_epmum_R36_i1_n_flv ()
  case (37);  n_flv = proc_epmum_R37_i1_n_flv ()
  case (38);  n_flv = proc_epmum_R38_i1_n_flv ()
  case (39);  n_flv = proc_epmum_R39_i1_n_flv ()
  case (40);  n_flv = proc_epmum_R40_i1_n_flv ()
  case (41);  n_flv = proc_epmum_R41_i1_n_flv ()
  case (42);  n_flv = proc_epmum_R42_i1_n_flv ()
  case (43);  n_flv = proc_epmum_R43_i1_n_flv ()
  case (44);  n_flv = proc_epmum_R44_i1_n_flv ()
  end select
end function proc_epmum_R_get_n_flv

! Return the value of n_hel
function proc_epmum_R_get_n_hel (pid) result (n_hel) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_hel => number_spin_states
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_hel => number_spin_states
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_hel => number_spin_states
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_hel => number_spin_states
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_hel => number_spin_states
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_hel => number_spin_states
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_hel => number_spin_states
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_hel => number_spin_states
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_hel => number_spin_states
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_hel => number_spin_states
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_hel => number_spin_states
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_hel => number_spin_states
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_hel => number_spin_states
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_hel => number_spin_states
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_hel => number_spin_states
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_hel => number_spin_states
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_hel => number_spin_states
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_hel => number_spin_states
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_hel => number_spin_states
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_hel => number_spin_states
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_hel => number_spin_states
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_hel => number_spin_states
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_hel => number_spin_states
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_hel => number_spin_states
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_hel => number_spin_states
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_hel => number_spin_states
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_hel => number_spin_states
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_hel => number_spin_states
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_hel => number_spin_states
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_hel => number_spin_states
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_hel => number_spin_states
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_hel => number_spin_states
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_hel => number_spin_states
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_hel => number_spin_states
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_hel => number_spin_states
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_hel => number_spin_states
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_hel => number_spin_states
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_hel => number_spin_states
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_hel => number_spin_states
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_hel => number_spin_states
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_hel => number_spin_states
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_hel => number_spin_states
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_hel => number_spin_states
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_hel => number_spin_states
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_hel
  select case (pid)
  case (1);  n_hel = proc_epmum_R1_i1_n_hel ()
  case (2);  n_hel = proc_epmum_R2_i1_n_hel ()
  case (3);  n_hel = proc_epmum_R3_i1_n_hel ()
  case (4);  n_hel = proc_epmum_R4_i1_n_hel ()
  case (5);  n_hel = proc_epmum_R5_i1_n_hel ()
  case (6);  n_hel = proc_epmum_R6_i1_n_hel ()
  case (7);  n_hel = proc_epmum_R7_i1_n_hel ()
  case (8);  n_hel = proc_epmum_R8_i1_n_hel ()
  case (9);  n_hel = proc_epmum_R9_i1_n_hel ()
  case (10);  n_hel = proc_epmum_R10_i1_n_hel ()
  case (11);  n_hel = proc_epmum_R11_i1_n_hel ()
  case (12);  n_hel = proc_epmum_R12_i1_n_hel ()
  case (13);  n_hel = proc_epmum_R13_i1_n_hel ()
  case (14);  n_hel = proc_epmum_R14_i1_n_hel ()
  case (15);  n_hel = proc_epmum_R15_i1_n_hel ()
  case (16);  n_hel = proc_epmum_R16_i1_n_hel ()
  case (17);  n_hel = proc_epmum_R17_i1_n_hel ()
  case (18);  n_hel = proc_epmum_R18_i1_n_hel ()
  case (19);  n_hel = proc_epmum_R19_i1_n_hel ()
  case (20);  n_hel = proc_epmum_R20_i1_n_hel ()
  case (21);  n_hel = proc_epmum_R21_i1_n_hel ()
  case (22);  n_hel = proc_epmum_R22_i1_n_hel ()
  case (23);  n_hel = proc_epmum_R23_i1_n_hel ()
  case (24);  n_hel = proc_epmum_R24_i1_n_hel ()
  case (25);  n_hel = proc_epmum_R25_i1_n_hel ()
  case (26);  n_hel = proc_epmum_R26_i1_n_hel ()
  case (27);  n_hel = proc_epmum_R27_i1_n_hel ()
  case (28);  n_hel = proc_epmum_R28_i1_n_hel ()
  case (29);  n_hel = proc_epmum_R29_i1_n_hel ()
  case (30);  n_hel = proc_epmum_R30_i1_n_hel ()
  case (31);  n_hel = proc_epmum_R31_i1_n_hel ()
  case (32);  n_hel = proc_epmum_R32_i1_n_hel ()
  case (33);  n_hel = proc_epmum_R33_i1_n_hel ()
  case (34);  n_hel = proc_epmum_R34_i1_n_hel ()
  case (35);  n_hel = proc_epmum_R35_i1_n_hel ()
  case (36);  n_hel = proc_epmum_R36_i1_n_hel ()
  case (37);  n_hel = proc_epmum_R37_i1_n_hel ()
  case (38);  n_hel = proc_epmum_R38_i1_n_hel ()
  case (39);  n_hel = proc_epmum_R39_i1_n_hel ()
  case (40);  n_hel = proc_epmum_R40_i1_n_hel ()
  case (41);  n_hel = proc_epmum_R41_i1_n_hel ()
  case (42);  n_hel = proc_epmum_R42_i1_n_hel ()
  case (43);  n_hel = proc_epmum_R43_i1_n_hel ()
  case (44);  n_hel = proc_epmum_R44_i1_n_hel ()
  end select
end function proc_epmum_R_get_n_hel

! Return the value of n_col
function proc_epmum_R_get_n_col (pid) result (n_col) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_col => number_color_flows
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_col => number_color_flows
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_col => number_color_flows
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_col => number_color_flows
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_col => number_color_flows
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_col => number_color_flows
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_col => number_color_flows
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_col => number_color_flows
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_col => number_color_flows
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_col => number_color_flows
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_col => number_color_flows
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_col => number_color_flows
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_col => number_color_flows
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_col => number_color_flows
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_col => number_color_flows
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_col => number_color_flows
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_col => number_color_flows
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_col => number_color_flows
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_col => number_color_flows
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_col => number_color_flows
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_col => number_color_flows
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_col => number_color_flows
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_col => number_color_flows
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_col => number_color_flows
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_col => number_color_flows
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_col => number_color_flows
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_col => number_color_flows
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_col => number_color_flows
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_col => number_color_flows
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_col => number_color_flows
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_col => number_color_flows
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_col => number_color_flows
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_col => number_color_flows
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_col => number_color_flows
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_col => number_color_flows
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_col => number_color_flows
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_col => number_color_flows
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_col => number_color_flows
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_col => number_color_flows
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_col => number_color_flows
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_col => number_color_flows
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_col => number_color_flows
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_col => number_color_flows
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_col => number_color_flows
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_col
  select case (pid)
  case (1);  n_col = proc_epmum_R1_i1_n_col ()
  case (2);  n_col = proc_epmum_R2_i1_n_col ()
  case (3);  n_col = proc_epmum_R3_i1_n_col ()
  case (4);  n_col = proc_epmum_R4_i1_n_col ()
  case (5);  n_col = proc_epmum_R5_i1_n_col ()
  case (6);  n_col = proc_epmum_R6_i1_n_col ()
  case (7);  n_col = proc_epmum_R7_i1_n_col ()
  case (8);  n_col = proc_epmum_R8_i1_n_col ()
  case (9);  n_col = proc_epmum_R9_i1_n_col ()
  case (10);  n_col = proc_epmum_R10_i1_n_col ()
  case (11);  n_col = proc_epmum_R11_i1_n_col ()
  case (12);  n_col = proc_epmum_R12_i1_n_col ()
  case (13);  n_col = proc_epmum_R13_i1_n_col ()
  case (14);  n_col = proc_epmum_R14_i1_n_col ()
  case (15);  n_col = proc_epmum_R15_i1_n_col ()
  case (16);  n_col = proc_epmum_R16_i1_n_col ()
  case (17);  n_col = proc_epmum_R17_i1_n_col ()
  case (18);  n_col = proc_epmum_R18_i1_n_col ()
  case (19);  n_col = proc_epmum_R19_i1_n_col ()
  case (20);  n_col = proc_epmum_R20_i1_n_col ()
  case (21);  n_col = proc_epmum_R21_i1_n_col ()
  case (22);  n_col = proc_epmum_R22_i1_n_col ()
  case (23);  n_col = proc_epmum_R23_i1_n_col ()
  case (24);  n_col = proc_epmum_R24_i1_n_col ()
  case (25);  n_col = proc_epmum_R25_i1_n_col ()
  case (26);  n_col = proc_epmum_R26_i1_n_col ()
  case (27);  n_col = proc_epmum_R27_i1_n_col ()
  case (28);  n_col = proc_epmum_R28_i1_n_col ()
  case (29);  n_col = proc_epmum_R29_i1_n_col ()
  case (30);  n_col = proc_epmum_R30_i1_n_col ()
  case (31);  n_col = proc_epmum_R31_i1_n_col ()
  case (32);  n_col = proc_epmum_R32_i1_n_col ()
  case (33);  n_col = proc_epmum_R33_i1_n_col ()
  case (34);  n_col = proc_epmum_R34_i1_n_col ()
  case (35);  n_col = proc_epmum_R35_i1_n_col ()
  case (36);  n_col = proc_epmum_R36_i1_n_col ()
  case (37);  n_col = proc_epmum_R37_i1_n_col ()
  case (38);  n_col = proc_epmum_R38_i1_n_col ()
  case (39);  n_col = proc_epmum_R39_i1_n_col ()
  case (40);  n_col = proc_epmum_R40_i1_n_col ()
  case (41);  n_col = proc_epmum_R41_i1_n_col ()
  case (42);  n_col = proc_epmum_R42_i1_n_col ()
  case (43);  n_col = proc_epmum_R43_i1_n_col ()
  case (44);  n_col = proc_epmum_R44_i1_n_col ()
  end select
end function proc_epmum_R_get_n_col

! Return the value of n_cin
function proc_epmum_R_get_n_cin (pid) result (n_cin) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_cin => number_color_indices
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_cin => number_color_indices
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_cin => number_color_indices
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_cin => number_color_indices
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_cin => number_color_indices
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_cin => number_color_indices
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_cin => number_color_indices
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_cin => number_color_indices
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_cin => number_color_indices
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_cin => number_color_indices
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_cin => number_color_indices
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_cin => number_color_indices
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_cin => number_color_indices
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_cin => number_color_indices
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_cin => number_color_indices
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_cin => number_color_indices
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_cin => number_color_indices
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_cin => number_color_indices
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_cin => number_color_indices
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_cin => number_color_indices
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_cin => number_color_indices
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_cin => number_color_indices
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_cin => number_color_indices
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_cin => number_color_indices
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_cin => number_color_indices
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_cin => number_color_indices
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_cin => number_color_indices
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_cin => number_color_indices
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_cin => number_color_indices
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_cin => number_color_indices
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_cin => number_color_indices
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_cin => number_color_indices
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_cin => number_color_indices
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_cin => number_color_indices
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_cin => number_color_indices
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_cin => number_color_indices
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_cin => number_color_indices
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_cin => number_color_indices
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_cin => number_color_indices
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_cin => number_color_indices
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_cin => number_color_indices
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_cin => number_color_indices
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_cin => number_color_indices
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_cin => number_color_indices
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_cin
  select case (pid)
  case (1);  n_cin = proc_epmum_R1_i1_n_cin ()
  case (2);  n_cin = proc_epmum_R2_i1_n_cin ()
  case (3);  n_cin = proc_epmum_R3_i1_n_cin ()
  case (4);  n_cin = proc_epmum_R4_i1_n_cin ()
  case (5);  n_cin = proc_epmum_R5_i1_n_cin ()
  case (6);  n_cin = proc_epmum_R6_i1_n_cin ()
  case (7);  n_cin = proc_epmum_R7_i1_n_cin ()
  case (8);  n_cin = proc_epmum_R8_i1_n_cin ()
  case (9);  n_cin = proc_epmum_R9_i1_n_cin ()
  case (10);  n_cin = proc_epmum_R10_i1_n_cin ()
  case (11);  n_cin = proc_epmum_R11_i1_n_cin ()
  case (12);  n_cin = proc_epmum_R12_i1_n_cin ()
  case (13);  n_cin = proc_epmum_R13_i1_n_cin ()
  case (14);  n_cin = proc_epmum_R14_i1_n_cin ()
  case (15);  n_cin = proc_epmum_R15_i1_n_cin ()
  case (16);  n_cin = proc_epmum_R16_i1_n_cin ()
  case (17);  n_cin = proc_epmum_R17_i1_n_cin ()
  case (18);  n_cin = proc_epmum_R18_i1_n_cin ()
  case (19);  n_cin = proc_epmum_R19_i1_n_cin ()
  case (20);  n_cin = proc_epmum_R20_i1_n_cin ()
  case (21);  n_cin = proc_epmum_R21_i1_n_cin ()
  case (22);  n_cin = proc_epmum_R22_i1_n_cin ()
  case (23);  n_cin = proc_epmum_R23_i1_n_cin ()
  case (24);  n_cin = proc_epmum_R24_i1_n_cin ()
  case (25);  n_cin = proc_epmum_R25_i1_n_cin ()
  case (26);  n_cin = proc_epmum_R26_i1_n_cin ()
  case (27);  n_cin = proc_epmum_R27_i1_n_cin ()
  case (28);  n_cin = proc_epmum_R28_i1_n_cin ()
  case (29);  n_cin = proc_epmum_R29_i1_n_cin ()
  case (30);  n_cin = proc_epmum_R30_i1_n_cin ()
  case (31);  n_cin = proc_epmum_R31_i1_n_cin ()
  case (32);  n_cin = proc_epmum_R32_i1_n_cin ()
  case (33);  n_cin = proc_epmum_R33_i1_n_cin ()
  case (34);  n_cin = proc_epmum_R34_i1_n_cin ()
  case (35);  n_cin = proc_epmum_R35_i1_n_cin ()
  case (36);  n_cin = proc_epmum_R36_i1_n_cin ()
  case (37);  n_cin = proc_epmum_R37_i1_n_cin ()
  case (38);  n_cin = proc_epmum_R38_i1_n_cin ()
  case (39);  n_cin = proc_epmum_R39_i1_n_cin ()
  case (40);  n_cin = proc_epmum_R40_i1_n_cin ()
  case (41);  n_cin = proc_epmum_R41_i1_n_cin ()
  case (42);  n_cin = proc_epmum_R42_i1_n_cin ()
  case (43);  n_cin = proc_epmum_R43_i1_n_cin ()
  case (44);  n_cin = proc_epmum_R44_i1_n_cin ()
  end select
end function proc_epmum_R_get_n_cin

! Return the value of n_cf
function proc_epmum_R_get_n_cf (pid) result (n_cf) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_n_cf => number_color_factors
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_n_cf => number_color_factors
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_n_cf => number_color_factors
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_n_cf => number_color_factors
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_n_cf => number_color_factors
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_n_cf => number_color_factors
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_n_cf => number_color_factors
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_n_cf => number_color_factors
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_n_cf => number_color_factors
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_n_cf => number_color_factors
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_n_cf => number_color_factors
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_n_cf => number_color_factors
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_n_cf => number_color_factors
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_n_cf => number_color_factors
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_n_cf => number_color_factors
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_n_cf => number_color_factors
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_n_cf => number_color_factors
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_n_cf => number_color_factors
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_n_cf => number_color_factors
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_n_cf => number_color_factors
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_n_cf => number_color_factors
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_n_cf => number_color_factors
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_n_cf => number_color_factors
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_n_cf => number_color_factors
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_n_cf => number_color_factors
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_n_cf => number_color_factors
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_n_cf => number_color_factors
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_n_cf => number_color_factors
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_n_cf => number_color_factors
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_n_cf => number_color_factors
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_n_cf => number_color_factors
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_n_cf => number_color_factors
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_n_cf => number_color_factors
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_n_cf => number_color_factors
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_n_cf => number_color_factors
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_n_cf => number_color_factors
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_n_cf => number_color_factors
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_n_cf => number_color_factors
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_n_cf => number_color_factors
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_n_cf => number_color_factors
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_n_cf => number_color_factors
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_n_cf => number_color_factors
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_n_cf => number_color_factors
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_n_cf => number_color_factors
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int) :: n_cf
  select case (pid)
  case (1);  n_cf = proc_epmum_R1_i1_n_cf ()
  case (2);  n_cf = proc_epmum_R2_i1_n_cf ()
  case (3);  n_cf = proc_epmum_R3_i1_n_cf ()
  case (4);  n_cf = proc_epmum_R4_i1_n_cf ()
  case (5);  n_cf = proc_epmum_R5_i1_n_cf ()
  case (6);  n_cf = proc_epmum_R6_i1_n_cf ()
  case (7);  n_cf = proc_epmum_R7_i1_n_cf ()
  case (8);  n_cf = proc_epmum_R8_i1_n_cf ()
  case (9);  n_cf = proc_epmum_R9_i1_n_cf ()
  case (10);  n_cf = proc_epmum_R10_i1_n_cf ()
  case (11);  n_cf = proc_epmum_R11_i1_n_cf ()
  case (12);  n_cf = proc_epmum_R12_i1_n_cf ()
  case (13);  n_cf = proc_epmum_R13_i1_n_cf ()
  case (14);  n_cf = proc_epmum_R14_i1_n_cf ()
  case (15);  n_cf = proc_epmum_R15_i1_n_cf ()
  case (16);  n_cf = proc_epmum_R16_i1_n_cf ()
  case (17);  n_cf = proc_epmum_R17_i1_n_cf ()
  case (18);  n_cf = proc_epmum_R18_i1_n_cf ()
  case (19);  n_cf = proc_epmum_R19_i1_n_cf ()
  case (20);  n_cf = proc_epmum_R20_i1_n_cf ()
  case (21);  n_cf = proc_epmum_R21_i1_n_cf ()
  case (22);  n_cf = proc_epmum_R22_i1_n_cf ()
  case (23);  n_cf = proc_epmum_R23_i1_n_cf ()
  case (24);  n_cf = proc_epmum_R24_i1_n_cf ()
  case (25);  n_cf = proc_epmum_R25_i1_n_cf ()
  case (26);  n_cf = proc_epmum_R26_i1_n_cf ()
  case (27);  n_cf = proc_epmum_R27_i1_n_cf ()
  case (28);  n_cf = proc_epmum_R28_i1_n_cf ()
  case (29);  n_cf = proc_epmum_R29_i1_n_cf ()
  case (30);  n_cf = proc_epmum_R30_i1_n_cf ()
  case (31);  n_cf = proc_epmum_R31_i1_n_cf ()
  case (32);  n_cf = proc_epmum_R32_i1_n_cf ()
  case (33);  n_cf = proc_epmum_R33_i1_n_cf ()
  case (34);  n_cf = proc_epmum_R34_i1_n_cf ()
  case (35);  n_cf = proc_epmum_R35_i1_n_cf ()
  case (36);  n_cf = proc_epmum_R36_i1_n_cf ()
  case (37);  n_cf = proc_epmum_R37_i1_n_cf ()
  case (38);  n_cf = proc_epmum_R38_i1_n_cf ()
  case (39);  n_cf = proc_epmum_R39_i1_n_cf ()
  case (40);  n_cf = proc_epmum_R40_i1_n_cf ()
  case (41);  n_cf = proc_epmum_R41_i1_n_cf ()
  case (42);  n_cf = proc_epmum_R42_i1_n_cf ()
  case (43);  n_cf = proc_epmum_R43_i1_n_cf ()
  case (44);  n_cf = proc_epmum_R44_i1_n_cf ()
  end select
end function proc_epmum_R_get_n_cf

! Set table: flv_state
subroutine proc_epmum_R_set_flv_state_ptr (pid, flv_state, shape) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_flv_state => flavor_states
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_flv_state => flavor_states
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_flv_state => flavor_states
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_flv_state => flavor_states
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_flv_state => flavor_states
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_flv_state => flavor_states
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_flv_state => flavor_states
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_flv_state => flavor_states
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_flv_state => flavor_states
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_flv_state => flavor_states
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_flv_state => flavor_states
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_flv_state => flavor_states
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_flv_state => flavor_states
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_flv_state => flavor_states
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_flv_state => flavor_states
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_flv_state => flavor_states
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_flv_state => flavor_states
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_flv_state => flavor_states
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_flv_state => flavor_states
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_flv_state => flavor_states
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_flv_state => flavor_states
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_flv_state => flavor_states
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_flv_state => flavor_states
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_flv_state => flavor_states
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_flv_state => flavor_states
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_flv_state => flavor_states
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_flv_state => flavor_states
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_flv_state => flavor_states
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_flv_state => flavor_states
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_flv_state => flavor_states
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_flv_state => flavor_states
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_flv_state => flavor_states
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_flv_state => flavor_states
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_flv_state => flavor_states
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_flv_state => flavor_states
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_flv_state => flavor_states
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_flv_state => flavor_states
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_flv_state => flavor_states
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_flv_state => flavor_states
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_flv_state => flavor_states
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_flv_state => flavor_states
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_flv_state => flavor_states
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_flv_state => flavor_states
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_flv_state => flavor_states
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int), dimension(*), intent(out) :: flv_state
  integer(c_int), dimension(2), intent(in) :: shape
  integer, dimension(:,:), allocatable :: flv_state_tmp
  integer :: i, j
  select case (pid)
  case (1)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R1_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (2)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R2_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (3)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R3_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (4)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R4_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (5)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R5_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (6)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R6_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (7)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R7_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (8)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R8_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (9)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R9_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (10)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R10_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (11)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R11_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (12)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R12_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (13)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R13_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (14)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R14_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (15)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R15_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (16)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R16_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (17)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R17_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (18)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R18_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (19)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R19_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (20)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R20_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (21)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R21_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (22)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R22_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (23)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R23_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (24)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R24_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (25)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R25_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (26)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R26_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (27)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R27_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (28)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R28_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (29)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R29_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (30)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R30_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (31)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R31_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (32)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R32_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (33)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R33_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (34)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R34_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (35)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R35_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (36)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R36_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (37)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R37_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (38)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R38_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (39)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R39_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (40)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R40_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (41)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R41_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (42)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R42_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (43)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R43_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  case (44)
     allocate (flv_state_tmp (shape(1), shape(2)))
     call proc_epmum_R44_i1_flv_state (flv_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        flv_state(i + shape(1)*(j-1)) = flv_state_tmp(i,j)
     end forall
  end select
end subroutine proc_epmum_R_set_flv_state_ptr

! Set table: hel_state
subroutine proc_epmum_R_set_hel_state_ptr (pid, hel_state, shape) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_hel_state => spin_states
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_hel_state => spin_states
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_hel_state => spin_states
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_hel_state => spin_states
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_hel_state => spin_states
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_hel_state => spin_states
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_hel_state => spin_states
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_hel_state => spin_states
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_hel_state => spin_states
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_hel_state => spin_states
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_hel_state => spin_states
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_hel_state => spin_states
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_hel_state => spin_states
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_hel_state => spin_states
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_hel_state => spin_states
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_hel_state => spin_states
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_hel_state => spin_states
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_hel_state => spin_states
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_hel_state => spin_states
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_hel_state => spin_states
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_hel_state => spin_states
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_hel_state => spin_states
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_hel_state => spin_states
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_hel_state => spin_states
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_hel_state => spin_states
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_hel_state => spin_states
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_hel_state => spin_states
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_hel_state => spin_states
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_hel_state => spin_states
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_hel_state => spin_states
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_hel_state => spin_states
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_hel_state => spin_states
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_hel_state => spin_states
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_hel_state => spin_states
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_hel_state => spin_states
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_hel_state => spin_states
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_hel_state => spin_states
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_hel_state => spin_states
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_hel_state => spin_states
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_hel_state => spin_states
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_hel_state => spin_states
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_hel_state => spin_states
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_hel_state => spin_states
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_hel_state => spin_states
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int), dimension(*), intent(out) :: hel_state
  integer(c_int), dimension(2), intent(in) :: shape
  integer, dimension(:,:), allocatable :: hel_state_tmp
  integer :: i, j
  select case (pid)
  case (1)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R1_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (2)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R2_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (3)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R3_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (4)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R4_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (5)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R5_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (6)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R6_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (7)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R7_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (8)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R8_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (9)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R9_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (10)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R10_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (11)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R11_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (12)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R12_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (13)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R13_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (14)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R14_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (15)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R15_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (16)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R16_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (17)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R17_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (18)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R18_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (19)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R19_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (20)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R20_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (21)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R21_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (22)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R22_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (23)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R23_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (24)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R24_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (25)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R25_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (26)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R26_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (27)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R27_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (28)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R28_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (29)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R29_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (30)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R30_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (31)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R31_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (32)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R32_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (33)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R33_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (34)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R34_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (35)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R35_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (36)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R36_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (37)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R37_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (38)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R38_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (39)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R39_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (40)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R40_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (41)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R41_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (42)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R42_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (43)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R43_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  case (44)
     allocate (hel_state_tmp (shape(1), shape(2)))
     call proc_epmum_R44_i1_hel_state (hel_state_tmp)
     forall (i=1:shape(1), j=1:shape(2)) 
        hel_state(i + shape(1)*(j-1)) = hel_state_tmp(i,j)
     end forall
  end select
end subroutine proc_epmum_R_set_hel_state_ptr

! Set tables: col_state, ghost_flag
subroutine proc_epmum_R_set_col_state_ptr (pid, col_state, ghost_flag, shape) bind(C)
  use iso_c_binding
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_col_state => color_flows
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_col_state => color_flows
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_col_state => color_flows
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_col_state => color_flows
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_col_state => color_flows
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_col_state => color_flows
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_col_state => color_flows
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_col_state => color_flows
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_col_state => color_flows
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_col_state => color_flows
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_col_state => color_flows
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_col_state => color_flows
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_col_state => color_flows
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_col_state => color_flows
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_col_state => color_flows
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_col_state => color_flows
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_col_state => color_flows
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_col_state => color_flows
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_col_state => color_flows
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_col_state => color_flows
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_col_state => color_flows
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_col_state => color_flows
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_col_state => color_flows
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_col_state => color_flows
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_col_state => color_flows
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_col_state => color_flows
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_col_state => color_flows
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_col_state => color_flows
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_col_state => color_flows
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_col_state => color_flows
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_col_state => color_flows
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_col_state => color_flows
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_col_state => color_flows
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_col_state => color_flows
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_col_state => color_flows
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_col_state => color_flows
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_col_state => color_flows
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_col_state => color_flows
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_col_state => color_flows
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_col_state => color_flows
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_col_state => color_flows
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_col_state => color_flows
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_col_state => color_flows
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_col_state => color_flows
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int), dimension(*), intent(out) :: col_state
  logical(c_bool), dimension(*), intent(out) :: ghost_flag
  integer(c_int), dimension(3), intent(in) :: shape
  integer, dimension(:,:,:), allocatable :: col_state_tmp
  logical, dimension(:,:), allocatable :: ghost_flag_tmp
  integer :: i, j, k
  select case (pid)
  case (1)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R1_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (2)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R2_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (3)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R3_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (4)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R4_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (5)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R5_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (6)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R6_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (7)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R7_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (8)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R8_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (9)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R9_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (10)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R10_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (11)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R11_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (12)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R12_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (13)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R13_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (14)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R14_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (15)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R15_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (16)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R16_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (17)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R17_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (18)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R18_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (19)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R19_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (20)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R20_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (21)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R21_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (22)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R22_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (23)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R23_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (24)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R24_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (25)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R25_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (26)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R26_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (27)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R27_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (28)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R28_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (29)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R29_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (30)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R30_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (31)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R31_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (32)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R32_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (33)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R33_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (34)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R34_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (35)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R35_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (36)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R36_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (37)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R37_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (38)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R38_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (39)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R39_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (40)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R40_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (41)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R41_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (42)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R42_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (43)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R43_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  case (44)
  allocate (col_state_tmp (shape(1), shape(2), shape(3)))
     allocate (ghost_flag_tmp (shape(2), shape(3)))
     call proc_epmum_R44_i1_col_state (col_state_tmp, ghost_flag_tmp)
     forall (i = 1:shape(2), j = 1:shape(3))
        forall (k = 1:shape(1))
           col_state(k + shape(1) * (i + shape(2)*(j-1) - 1)) = col_state_tmp(k,i,j)
        end forall
        ghost_flag(i + shape(2)*(j-1)) = ghost_flag_tmp(i,j)
     end forall
  end select
end subroutine proc_epmum_R_set_col_state_ptr

! Set tables: color factors
subroutine proc_epmum_R_set_color_factors_ptr (pid, cf_index1, cf_index2, color_factors, shape) bind(C)
  use iso_c_binding
  use kinds
  use omega_color
  use opr_proc_epmum_R1_i1, only: proc_epmum_R1_i1_color_factors => color_factors
  use opr_proc_epmum_R2_i1, only: proc_epmum_R2_i1_color_factors => color_factors
  use opr_proc_epmum_R3_i1, only: proc_epmum_R3_i1_color_factors => color_factors
  use opr_proc_epmum_R4_i1, only: proc_epmum_R4_i1_color_factors => color_factors
  use opr_proc_epmum_R5_i1, only: proc_epmum_R5_i1_color_factors => color_factors
  use opr_proc_epmum_R6_i1, only: proc_epmum_R6_i1_color_factors => color_factors
  use opr_proc_epmum_R7_i1, only: proc_epmum_R7_i1_color_factors => color_factors
  use opr_proc_epmum_R8_i1, only: proc_epmum_R8_i1_color_factors => color_factors
  use opr_proc_epmum_R9_i1, only: proc_epmum_R9_i1_color_factors => color_factors
  use opr_proc_epmum_R10_i1, only: proc_epmum_R10_i1_color_factors => color_factors
  use opr_proc_epmum_R11_i1, only: proc_epmum_R11_i1_color_factors => color_factors
  use opr_proc_epmum_R12_i1, only: proc_epmum_R12_i1_color_factors => color_factors
  use opr_proc_epmum_R13_i1, only: proc_epmum_R13_i1_color_factors => color_factors
  use opr_proc_epmum_R14_i1, only: proc_epmum_R14_i1_color_factors => color_factors
  use opr_proc_epmum_R15_i1, only: proc_epmum_R15_i1_color_factors => color_factors
  use opr_proc_epmum_R16_i1, only: proc_epmum_R16_i1_color_factors => color_factors
  use opr_proc_epmum_R17_i1, only: proc_epmum_R17_i1_color_factors => color_factors
  use opr_proc_epmum_R18_i1, only: proc_epmum_R18_i1_color_factors => color_factors
  use opr_proc_epmum_R19_i1, only: proc_epmum_R19_i1_color_factors => color_factors
  use opr_proc_epmum_R20_i1, only: proc_epmum_R20_i1_color_factors => color_factors
  use opr_proc_epmum_R21_i1, only: proc_epmum_R21_i1_color_factors => color_factors
  use opr_proc_epmum_R22_i1, only: proc_epmum_R22_i1_color_factors => color_factors
  use opr_proc_epmum_R23_i1, only: proc_epmum_R23_i1_color_factors => color_factors
  use opr_proc_epmum_R24_i1, only: proc_epmum_R24_i1_color_factors => color_factors
  use opr_proc_epmum_R25_i1, only: proc_epmum_R25_i1_color_factors => color_factors
  use opr_proc_epmum_R26_i1, only: proc_epmum_R26_i1_color_factors => color_factors
  use opr_proc_epmum_R27_i1, only: proc_epmum_R27_i1_color_factors => color_factors
  use opr_proc_epmum_R28_i1, only: proc_epmum_R28_i1_color_factors => color_factors
  use opr_proc_epmum_R29_i1, only: proc_epmum_R29_i1_color_factors => color_factors
  use opr_proc_epmum_R30_i1, only: proc_epmum_R30_i1_color_factors => color_factors
  use opr_proc_epmum_R31_i1, only: proc_epmum_R31_i1_color_factors => color_factors
  use opr_proc_epmum_R32_i1, only: proc_epmum_R32_i1_color_factors => color_factors
  use opr_proc_epmum_R33_i1, only: proc_epmum_R33_i1_color_factors => color_factors
  use opr_proc_epmum_R34_i1, only: proc_epmum_R34_i1_color_factors => color_factors
  use opr_proc_epmum_R35_i1, only: proc_epmum_R35_i1_color_factors => color_factors
  use opr_proc_epmum_R36_i1, only: proc_epmum_R36_i1_color_factors => color_factors
  use opr_proc_epmum_R37_i1, only: proc_epmum_R37_i1_color_factors => color_factors
  use opr_proc_epmum_R38_i1, only: proc_epmum_R38_i1_color_factors => color_factors
  use opr_proc_epmum_R39_i1, only: proc_epmum_R39_i1_color_factors => color_factors
  use opr_proc_epmum_R40_i1, only: proc_epmum_R40_i1_color_factors => color_factors
  use opr_proc_epmum_R41_i1, only: proc_epmum_R41_i1_color_factors => color_factors
  use opr_proc_epmum_R42_i1, only: proc_epmum_R42_i1_color_factors => color_factors
  use opr_proc_epmum_R43_i1, only: proc_epmum_R43_i1_color_factors => color_factors
  use opr_proc_epmum_R44_i1, only: proc_epmum_R44_i1_color_factors => color_factors
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int), dimension(1), intent(in) :: shape
  integer(c_int), dimension(*), intent(out) :: cf_index1, cf_index2
  complex(c_default_complex), dimension(*), intent(out) :: color_factors
  type(omega_color_factor), dimension(:), allocatable :: cf
  select case (pid)
  case (1)
     allocate (cf (shape(1)))
     call proc_epmum_R1_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (2)
     allocate (cf (shape(1)))
     call proc_epmum_R2_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (3)
     allocate (cf (shape(1)))
     call proc_epmum_R3_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (4)
     allocate (cf (shape(1)))
     call proc_epmum_R4_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (5)
     allocate (cf (shape(1)))
     call proc_epmum_R5_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (6)
     allocate (cf (shape(1)))
     call proc_epmum_R6_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (7)
     allocate (cf (shape(1)))
     call proc_epmum_R7_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (8)
     allocate (cf (shape(1)))
     call proc_epmum_R8_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (9)
     allocate (cf (shape(1)))
     call proc_epmum_R9_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (10)
     allocate (cf (shape(1)))
     call proc_epmum_R10_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (11)
     allocate (cf (shape(1)))
     call proc_epmum_R11_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (12)
     allocate (cf (shape(1)))
     call proc_epmum_R12_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (13)
     allocate (cf (shape(1)))
     call proc_epmum_R13_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (14)
     allocate (cf (shape(1)))
     call proc_epmum_R14_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (15)
     allocate (cf (shape(1)))
     call proc_epmum_R15_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (16)
     allocate (cf (shape(1)))
     call proc_epmum_R16_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (17)
     allocate (cf (shape(1)))
     call proc_epmum_R17_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (18)
     allocate (cf (shape(1)))
     call proc_epmum_R18_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (19)
     allocate (cf (shape(1)))
     call proc_epmum_R19_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (20)
     allocate (cf (shape(1)))
     call proc_epmum_R20_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (21)
     allocate (cf (shape(1)))
     call proc_epmum_R21_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (22)
     allocate (cf (shape(1)))
     call proc_epmum_R22_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (23)
     allocate (cf (shape(1)))
     call proc_epmum_R23_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (24)
     allocate (cf (shape(1)))
     call proc_epmum_R24_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (25)
     allocate (cf (shape(1)))
     call proc_epmum_R25_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (26)
     allocate (cf (shape(1)))
     call proc_epmum_R26_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (27)
     allocate (cf (shape(1)))
     call proc_epmum_R27_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (28)
     allocate (cf (shape(1)))
     call proc_epmum_R28_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (29)
     allocate (cf (shape(1)))
     call proc_epmum_R29_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (30)
     allocate (cf (shape(1)))
     call proc_epmum_R30_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (31)
     allocate (cf (shape(1)))
     call proc_epmum_R31_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (32)
     allocate (cf (shape(1)))
     call proc_epmum_R32_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (33)
     allocate (cf (shape(1)))
     call proc_epmum_R33_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (34)
     allocate (cf (shape(1)))
     call proc_epmum_R34_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (35)
     allocate (cf (shape(1)))
     call proc_epmum_R35_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (36)
     allocate (cf (shape(1)))
     call proc_epmum_R36_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (37)
     allocate (cf (shape(1)))
     call proc_epmum_R37_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (38)
     allocate (cf (shape(1)))
     call proc_epmum_R38_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (39)
     allocate (cf (shape(1)))
     call proc_epmum_R39_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (40)
     allocate (cf (shape(1)))
     call proc_epmum_R40_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (41)
     allocate (cf (shape(1)))
     call proc_epmum_R41_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (42)
     allocate (cf (shape(1)))
     call proc_epmum_R42_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (43)
     allocate (cf (shape(1)))
     call proc_epmum_R43_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  case (44)
     allocate (cf (shape(1)))
     call proc_epmum_R44_i1_color_factors (cf)
     cf_index1(1:shape(1)) = cf%i1
     cf_index2(1:shape(1)) = cf%i2
     color_factors(1:shape(1)) = cf%factor
  end select
end subroutine proc_epmum_R_set_color_factors_ptr

! Return C pointer to a procedure:
! pid = process index;  fid = function index
subroutine proc_epmum_R_get_fptr (pid, fid, fptr) bind(C)
  use iso_c_binding
  use kinds
  implicit none
  integer(c_int), intent(in) :: pid
  integer(c_int), intent(in) :: fid
  type(c_funptr), intent(out) :: fptr
  interface
     subroutine proc_epmum_R1_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R1_i1_init
  end interface
  interface
     subroutine proc_epmum_R1_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R1_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R1_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R1_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R1_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R1_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R1_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R1_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R1_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R1_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R2_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R2_i1_init
  end interface
  interface
     subroutine proc_epmum_R2_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R2_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R2_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R2_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R2_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R2_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R2_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R2_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R2_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R2_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R3_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R3_i1_init
  end interface
  interface
     subroutine proc_epmum_R3_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R3_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R3_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R3_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R3_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R3_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R3_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R3_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R3_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R3_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R4_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R4_i1_init
  end interface
  interface
     subroutine proc_epmum_R4_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R4_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R4_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R4_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R4_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R4_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R4_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R4_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R4_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R4_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R5_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R5_i1_init
  end interface
  interface
     subroutine proc_epmum_R5_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R5_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R5_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R5_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R5_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R5_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R5_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R5_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R5_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R5_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R6_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R6_i1_init
  end interface
  interface
     subroutine proc_epmum_R6_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R6_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R6_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R6_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R6_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R6_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R6_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R6_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R6_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R6_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R7_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R7_i1_init
  end interface
  interface
     subroutine proc_epmum_R7_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R7_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R7_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R7_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R7_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R7_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R7_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R7_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R7_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R7_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R8_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R8_i1_init
  end interface
  interface
     subroutine proc_epmum_R8_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R8_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R8_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R8_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R8_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R8_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R8_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R8_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R8_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R8_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R9_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R9_i1_init
  end interface
  interface
     subroutine proc_epmum_R9_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R9_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R9_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R9_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R9_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R9_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R9_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R9_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R9_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R9_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R10_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R10_i1_init
  end interface
  interface
     subroutine proc_epmum_R10_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R10_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R10_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R10_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R10_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R10_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R10_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R10_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R10_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R10_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R11_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R11_i1_init
  end interface
  interface
     subroutine proc_epmum_R11_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R11_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R11_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R11_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R11_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R11_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R11_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R11_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R11_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R11_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R12_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R12_i1_init
  end interface
  interface
     subroutine proc_epmum_R12_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R12_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R12_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R12_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R12_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R12_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R12_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R12_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R12_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R12_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R13_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R13_i1_init
  end interface
  interface
     subroutine proc_epmum_R13_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R13_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R13_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R13_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R13_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R13_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R13_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R13_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R13_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R13_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R14_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R14_i1_init
  end interface
  interface
     subroutine proc_epmum_R14_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R14_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R14_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R14_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R14_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R14_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R14_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R14_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R14_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R14_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R15_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R15_i1_init
  end interface
  interface
     subroutine proc_epmum_R15_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R15_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R15_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R15_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R15_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R15_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R15_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R15_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R15_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R15_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R16_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R16_i1_init
  end interface
  interface
     subroutine proc_epmum_R16_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R16_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R16_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R16_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R16_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R16_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R16_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R16_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R16_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R16_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R17_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R17_i1_init
  end interface
  interface
     subroutine proc_epmum_R17_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R17_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R17_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R17_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R17_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R17_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R17_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R17_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R17_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R17_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R18_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R18_i1_init
  end interface
  interface
     subroutine proc_epmum_R18_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R18_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R18_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R18_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R18_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R18_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R18_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R18_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R18_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R18_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R19_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R19_i1_init
  end interface
  interface
     subroutine proc_epmum_R19_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R19_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R19_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R19_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R19_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R19_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R19_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R19_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R19_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R19_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R20_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R20_i1_init
  end interface
  interface
     subroutine proc_epmum_R20_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R20_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R20_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R20_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R20_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R20_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R20_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R20_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R20_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R20_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R21_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R21_i1_init
  end interface
  interface
     subroutine proc_epmum_R21_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R21_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R21_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R21_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R21_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R21_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R21_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R21_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R21_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R21_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R22_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R22_i1_init
  end interface
  interface
     subroutine proc_epmum_R22_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R22_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R22_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R22_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R22_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R22_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R22_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R22_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R22_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R22_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R23_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R23_i1_init
  end interface
  interface
     subroutine proc_epmum_R23_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R23_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R23_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R23_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R23_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R23_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R23_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R23_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R23_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R23_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R24_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R24_i1_init
  end interface
  interface
     subroutine proc_epmum_R24_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R24_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R24_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R24_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R24_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R24_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R24_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R24_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R24_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R24_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R25_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R25_i1_init
  end interface
  interface
     subroutine proc_epmum_R25_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R25_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R25_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R25_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R25_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R25_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R25_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R25_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R25_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R25_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R26_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R26_i1_init
  end interface
  interface
     subroutine proc_epmum_R26_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R26_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R26_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R26_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R26_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R26_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R26_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R26_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R26_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R26_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R27_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R27_i1_init
  end interface
  interface
     subroutine proc_epmum_R27_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R27_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R27_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R27_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R27_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R27_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R27_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R27_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R27_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R27_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R28_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R28_i1_init
  end interface
  interface
     subroutine proc_epmum_R28_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R28_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R28_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R28_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R28_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R28_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R28_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R28_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R28_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R28_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R29_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R29_i1_init
  end interface
  interface
     subroutine proc_epmum_R29_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R29_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R29_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R29_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R29_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R29_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R29_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R29_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R29_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R29_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R30_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R30_i1_init
  end interface
  interface
     subroutine proc_epmum_R30_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R30_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R30_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R30_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R30_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R30_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R30_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R30_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R30_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R30_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R31_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R31_i1_init
  end interface
  interface
     subroutine proc_epmum_R31_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R31_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R31_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R31_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R31_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R31_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R31_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R31_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R31_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R31_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R32_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R32_i1_init
  end interface
  interface
     subroutine proc_epmum_R32_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R32_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R32_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R32_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R32_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R32_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R32_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R32_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R32_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R32_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R33_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R33_i1_init
  end interface
  interface
     subroutine proc_epmum_R33_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R33_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R33_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R33_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R33_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R33_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R33_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R33_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R33_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R33_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R34_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R34_i1_init
  end interface
  interface
     subroutine proc_epmum_R34_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R34_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R34_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R34_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R34_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R34_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R34_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R34_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R34_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R34_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R35_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R35_i1_init
  end interface
  interface
     subroutine proc_epmum_R35_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R35_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R35_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R35_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R35_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R35_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R35_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R35_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R35_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R35_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R36_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R36_i1_init
  end interface
  interface
     subroutine proc_epmum_R36_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R36_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R36_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R36_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R36_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R36_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R36_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R36_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R36_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R36_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R37_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R37_i1_init
  end interface
  interface
     subroutine proc_epmum_R37_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R37_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R37_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R37_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R37_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R37_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R37_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R37_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R37_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R37_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R38_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R38_i1_init
  end interface
  interface
     subroutine proc_epmum_R38_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R38_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R38_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R38_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R38_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R38_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R38_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R38_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R38_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R38_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R39_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R39_i1_init
  end interface
  interface
     subroutine proc_epmum_R39_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R39_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R39_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R39_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R39_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R39_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R39_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R39_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R39_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R39_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R40_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R40_i1_init
  end interface
  interface
     subroutine proc_epmum_R40_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R40_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R40_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R40_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R40_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R40_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R40_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R40_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R40_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R40_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R41_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R41_i1_init
  end interface
  interface
     subroutine proc_epmum_R41_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R41_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R41_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R41_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R41_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R41_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R41_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R41_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R41_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R41_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R42_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R42_i1_init
  end interface
  interface
     subroutine proc_epmum_R42_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R42_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R42_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R42_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R42_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R42_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R42_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R42_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R42_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R42_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R43_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R43_i1_init
  end interface
  interface
     subroutine proc_epmum_R43_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R43_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R43_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R43_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R43_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R43_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R43_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R43_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R43_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R43_i1_get_amplitude
  end interface
  interface
     subroutine proc_epmum_R44_i1_init (par, scheme) bind(C)
       import
       real(c_default_float), dimension(*), intent(in) :: par
       integer(c_int), intent(in) :: scheme
     end subroutine proc_epmum_R44_i1_init
  end interface
  interface
     subroutine proc_epmum_R44_i1_update_alpha_s (alpha_s) bind(C)
       import
       real(c_default_float), intent(in) :: alpha_s
     end subroutine proc_epmum_R44_i1_update_alpha_s
  end interface
  interface
     subroutine proc_epmum_R44_i1_reset_helicity_selection (threshold, cutoff) bind(C)
       import
       real(c_default_float), intent(in) :: threshold
       integer(c_int), intent(in) :: cutoff
     end subroutine proc_epmum_R44_i1_reset_helicity_selection
  end interface
  interface
     subroutine proc_epmum_R44_i1_is_allowed (flv, hel, col, flag) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       logical(c_bool), intent(out) :: flag
     end subroutine proc_epmum_R44_i1_is_allowed
  end interface
  interface
     subroutine proc_epmum_R44_i1_new_event (p) bind(C)
       import
       real(c_default_float), dimension(0:3,*), intent(in) :: p
     end subroutine proc_epmum_R44_i1_new_event
  end interface
  interface
     subroutine proc_epmum_R44_i1_get_amplitude (flv, hel, col, amp) bind(C)
       import
       integer(c_int), intent(in) :: flv, hel, col
       complex(c_default_complex), intent(out) :: amp
     end subroutine proc_epmum_R44_i1_get_amplitude
  end interface
  select case (pid)
  case (1)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R1_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R1_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R1_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R1_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R1_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R1_i1_get_amplitude)
     end select
  case (2)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R2_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R2_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R2_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R2_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R2_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R2_i1_get_amplitude)
     end select
  case (3)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R3_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R3_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R3_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R3_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R3_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R3_i1_get_amplitude)
     end select
  case (4)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R4_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R4_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R4_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R4_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R4_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R4_i1_get_amplitude)
     end select
  case (5)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R5_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R5_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R5_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R5_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R5_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R5_i1_get_amplitude)
     end select
  case (6)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R6_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R6_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R6_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R6_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R6_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R6_i1_get_amplitude)
     end select
  case (7)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R7_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R7_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R7_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R7_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R7_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R7_i1_get_amplitude)
     end select
  case (8)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R8_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R8_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R8_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R8_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R8_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R8_i1_get_amplitude)
     end select
  case (9)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R9_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R9_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R9_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R9_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R9_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R9_i1_get_amplitude)
     end select
  case (10)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R10_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R10_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R10_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R10_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R10_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R10_i1_get_amplitude)
     end select
  case (11)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R11_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R11_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R11_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R11_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R11_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R11_i1_get_amplitude)
     end select
  case (12)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R12_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R12_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R12_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R12_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R12_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R12_i1_get_amplitude)
     end select
  case (13)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R13_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R13_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R13_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R13_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R13_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R13_i1_get_amplitude)
     end select
  case (14)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R14_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R14_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R14_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R14_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R14_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R14_i1_get_amplitude)
     end select
  case (15)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R15_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R15_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R15_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R15_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R15_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R15_i1_get_amplitude)
     end select
  case (16)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R16_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R16_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R16_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R16_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R16_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R16_i1_get_amplitude)
     end select
  case (17)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R17_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R17_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R17_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R17_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R17_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R17_i1_get_amplitude)
     end select
  case (18)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R18_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R18_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R18_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R18_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R18_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R18_i1_get_amplitude)
     end select
  case (19)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R19_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R19_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R19_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R19_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R19_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R19_i1_get_amplitude)
     end select
  case (20)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R20_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R20_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R20_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R20_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R20_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R20_i1_get_amplitude)
     end select
  case (21)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R21_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R21_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R21_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R21_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R21_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R21_i1_get_amplitude)
     end select
  case (22)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R22_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R22_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R22_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R22_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R22_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R22_i1_get_amplitude)
     end select
  case (23)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R23_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R23_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R23_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R23_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R23_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R23_i1_get_amplitude)
     end select
  case (24)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R24_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R24_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R24_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R24_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R24_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R24_i1_get_amplitude)
     end select
  case (25)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R25_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R25_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R25_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R25_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R25_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R25_i1_get_amplitude)
     end select
  case (26)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R26_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R26_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R26_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R26_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R26_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R26_i1_get_amplitude)
     end select
  case (27)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R27_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R27_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R27_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R27_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R27_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R27_i1_get_amplitude)
     end select
  case (28)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R28_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R28_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R28_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R28_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R28_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R28_i1_get_amplitude)
     end select
  case (29)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R29_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R29_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R29_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R29_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R29_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R29_i1_get_amplitude)
     end select
  case (30)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R30_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R30_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R30_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R30_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R30_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R30_i1_get_amplitude)
     end select
  case (31)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R31_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R31_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R31_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R31_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R31_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R31_i1_get_amplitude)
     end select
  case (32)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R32_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R32_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R32_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R32_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R32_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R32_i1_get_amplitude)
     end select
  case (33)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R33_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R33_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R33_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R33_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R33_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R33_i1_get_amplitude)
     end select
  case (34)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R34_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R34_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R34_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R34_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R34_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R34_i1_get_amplitude)
     end select
  case (35)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R35_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R35_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R35_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R35_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R35_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R35_i1_get_amplitude)
     end select
  case (36)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R36_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R36_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R36_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R36_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R36_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R36_i1_get_amplitude)
     end select
  case (37)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R37_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R37_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R37_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R37_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R37_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R37_i1_get_amplitude)
     end select
  case (38)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R38_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R38_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R38_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R38_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R38_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R38_i1_get_amplitude)
     end select
  case (39)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R39_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R39_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R39_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R39_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R39_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R39_i1_get_amplitude)
     end select
  case (40)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R40_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R40_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R40_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R40_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R40_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R40_i1_get_amplitude)
     end select
  case (41)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R41_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R41_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R41_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R41_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R41_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R41_i1_get_amplitude)
     end select
  case (42)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R42_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R42_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R42_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R42_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R42_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R42_i1_get_amplitude)
     end select
  case (43)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R43_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R43_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R43_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R43_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R43_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R43_i1_get_amplitude)
     end select
  case (44)
     select case (fid)
     case (1);  fptr = c_funloc (proc_epmum_R44_i1_init)
     case (2);  fptr = c_funloc (proc_epmum_R44_i1_update_alpha_s)
     case (3);  fptr = c_funloc (proc_epmum_R44_i1_reset_helicity_selection)
     case (4);  fptr = c_funloc (proc_epmum_R44_i1_is_allowed)
     case (5);  fptr = c_funloc (proc_epmum_R44_i1_new_event)
     case (6);  fptr = c_funloc (proc_epmum_R44_i1_get_amplitude)
     end select
  end select
end subroutine proc_epmum_R_get_fptr

subroutine proc_epmum_R1_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R1_i1_init

subroutine proc_epmum_R1_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R1_i1_update_alpha_s

subroutine proc_epmum_R1_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R1_i1_reset_helicity_selection

subroutine proc_epmum_R1_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R1_i1_is_allowed

subroutine proc_epmum_R1_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R1_i1_new_event

subroutine proc_epmum_R1_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R1_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R1_i1_get_amplitude

subroutine proc_epmum_R2_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R2_i1_init

subroutine proc_epmum_R2_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R2_i1_update_alpha_s

subroutine proc_epmum_R2_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R2_i1_reset_helicity_selection

subroutine proc_epmum_R2_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R2_i1_is_allowed

subroutine proc_epmum_R2_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R2_i1_new_event

subroutine proc_epmum_R2_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R2_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R2_i1_get_amplitude

subroutine proc_epmum_R3_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R3_i1_init

subroutine proc_epmum_R3_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R3_i1_update_alpha_s

subroutine proc_epmum_R3_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R3_i1_reset_helicity_selection

subroutine proc_epmum_R3_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R3_i1_is_allowed

subroutine proc_epmum_R3_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R3_i1_new_event

subroutine proc_epmum_R3_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R3_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R3_i1_get_amplitude

subroutine proc_epmum_R4_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R4_i1_init

subroutine proc_epmum_R4_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R4_i1_update_alpha_s

subroutine proc_epmum_R4_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R4_i1_reset_helicity_selection

subroutine proc_epmum_R4_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R4_i1_is_allowed

subroutine proc_epmum_R4_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R4_i1_new_event

subroutine proc_epmum_R4_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R4_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R4_i1_get_amplitude

subroutine proc_epmum_R5_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R5_i1_init

subroutine proc_epmum_R5_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R5_i1_update_alpha_s

subroutine proc_epmum_R5_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R5_i1_reset_helicity_selection

subroutine proc_epmum_R5_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R5_i1_is_allowed

subroutine proc_epmum_R5_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R5_i1_new_event

subroutine proc_epmum_R5_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R5_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R5_i1_get_amplitude

subroutine proc_epmum_R6_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R6_i1_init

subroutine proc_epmum_R6_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R6_i1_update_alpha_s

subroutine proc_epmum_R6_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R6_i1_reset_helicity_selection

subroutine proc_epmum_R6_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R6_i1_is_allowed

subroutine proc_epmum_R6_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R6_i1_new_event

subroutine proc_epmum_R6_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R6_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R6_i1_get_amplitude

subroutine proc_epmum_R7_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R7_i1_init

subroutine proc_epmum_R7_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R7_i1_update_alpha_s

subroutine proc_epmum_R7_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R7_i1_reset_helicity_selection

subroutine proc_epmum_R7_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R7_i1_is_allowed

subroutine proc_epmum_R7_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R7_i1_new_event

subroutine proc_epmum_R7_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R7_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R7_i1_get_amplitude

subroutine proc_epmum_R8_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R8_i1_init

subroutine proc_epmum_R8_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R8_i1_update_alpha_s

subroutine proc_epmum_R8_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R8_i1_reset_helicity_selection

subroutine proc_epmum_R8_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R8_i1_is_allowed

subroutine proc_epmum_R8_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R8_i1_new_event

subroutine proc_epmum_R8_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R8_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R8_i1_get_amplitude

subroutine proc_epmum_R9_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R9_i1_init

subroutine proc_epmum_R9_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R9_i1_update_alpha_s

subroutine proc_epmum_R9_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R9_i1_reset_helicity_selection

subroutine proc_epmum_R9_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R9_i1_is_allowed

subroutine proc_epmum_R9_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R9_i1_new_event

subroutine proc_epmum_R9_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R9_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R9_i1_get_amplitude

subroutine proc_epmum_R10_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R10_i1_init

subroutine proc_epmum_R10_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R10_i1_update_alpha_s

subroutine proc_epmum_R10_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R10_i1_reset_helicity_selection

subroutine proc_epmum_R10_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R10_i1_is_allowed

subroutine proc_epmum_R10_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R10_i1_new_event

subroutine proc_epmum_R10_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R10_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R10_i1_get_amplitude

subroutine proc_epmum_R11_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R11_i1_init

subroutine proc_epmum_R11_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R11_i1_update_alpha_s

subroutine proc_epmum_R11_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R11_i1_reset_helicity_selection

subroutine proc_epmum_R11_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R11_i1_is_allowed

subroutine proc_epmum_R11_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R11_i1_new_event

subroutine proc_epmum_R11_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R11_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R11_i1_get_amplitude

subroutine proc_epmum_R12_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R12_i1_init

subroutine proc_epmum_R12_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R12_i1_update_alpha_s

subroutine proc_epmum_R12_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R12_i1_reset_helicity_selection

subroutine proc_epmum_R12_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R12_i1_is_allowed

subroutine proc_epmum_R12_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R12_i1_new_event

subroutine proc_epmum_R12_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R12_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R12_i1_get_amplitude

subroutine proc_epmum_R13_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R13_i1_init

subroutine proc_epmum_R13_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R13_i1_update_alpha_s

subroutine proc_epmum_R13_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R13_i1_reset_helicity_selection

subroutine proc_epmum_R13_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R13_i1_is_allowed

subroutine proc_epmum_R13_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R13_i1_new_event

subroutine proc_epmum_R13_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R13_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R13_i1_get_amplitude

subroutine proc_epmum_R14_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R14_i1_init

subroutine proc_epmum_R14_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R14_i1_update_alpha_s

subroutine proc_epmum_R14_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R14_i1_reset_helicity_selection

subroutine proc_epmum_R14_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R14_i1_is_allowed

subroutine proc_epmum_R14_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R14_i1_new_event

subroutine proc_epmum_R14_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R14_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R14_i1_get_amplitude

subroutine proc_epmum_R15_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R15_i1_init

subroutine proc_epmum_R15_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R15_i1_update_alpha_s

subroutine proc_epmum_R15_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R15_i1_reset_helicity_selection

subroutine proc_epmum_R15_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R15_i1_is_allowed

subroutine proc_epmum_R15_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R15_i1_new_event

subroutine proc_epmum_R15_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R15_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R15_i1_get_amplitude

subroutine proc_epmum_R16_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R16_i1_init

subroutine proc_epmum_R16_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R16_i1_update_alpha_s

subroutine proc_epmum_R16_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R16_i1_reset_helicity_selection

subroutine proc_epmum_R16_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R16_i1_is_allowed

subroutine proc_epmum_R16_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R16_i1_new_event

subroutine proc_epmum_R16_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R16_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R16_i1_get_amplitude

subroutine proc_epmum_R17_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R17_i1_init

subroutine proc_epmum_R17_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R17_i1_update_alpha_s

subroutine proc_epmum_R17_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R17_i1_reset_helicity_selection

subroutine proc_epmum_R17_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R17_i1_is_allowed

subroutine proc_epmum_R17_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R17_i1_new_event

subroutine proc_epmum_R17_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R17_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R17_i1_get_amplitude

subroutine proc_epmum_R18_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R18_i1_init

subroutine proc_epmum_R18_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R18_i1_update_alpha_s

subroutine proc_epmum_R18_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R18_i1_reset_helicity_selection

subroutine proc_epmum_R18_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R18_i1_is_allowed

subroutine proc_epmum_R18_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R18_i1_new_event

subroutine proc_epmum_R18_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R18_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R18_i1_get_amplitude

subroutine proc_epmum_R19_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R19_i1_init

subroutine proc_epmum_R19_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R19_i1_update_alpha_s

subroutine proc_epmum_R19_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R19_i1_reset_helicity_selection

subroutine proc_epmum_R19_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R19_i1_is_allowed

subroutine proc_epmum_R19_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R19_i1_new_event

subroutine proc_epmum_R19_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R19_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R19_i1_get_amplitude

subroutine proc_epmum_R20_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R20_i1_init

subroutine proc_epmum_R20_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R20_i1_update_alpha_s

subroutine proc_epmum_R20_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R20_i1_reset_helicity_selection

subroutine proc_epmum_R20_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R20_i1_is_allowed

subroutine proc_epmum_R20_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R20_i1_new_event

subroutine proc_epmum_R20_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R20_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R20_i1_get_amplitude

subroutine proc_epmum_R21_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R21_i1_init

subroutine proc_epmum_R21_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R21_i1_update_alpha_s

subroutine proc_epmum_R21_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R21_i1_reset_helicity_selection

subroutine proc_epmum_R21_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R21_i1_is_allowed

subroutine proc_epmum_R21_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R21_i1_new_event

subroutine proc_epmum_R21_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R21_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R21_i1_get_amplitude

subroutine proc_epmum_R22_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R22_i1_init

subroutine proc_epmum_R22_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R22_i1_update_alpha_s

subroutine proc_epmum_R22_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R22_i1_reset_helicity_selection

subroutine proc_epmum_R22_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R22_i1_is_allowed

subroutine proc_epmum_R22_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R22_i1_new_event

subroutine proc_epmum_R22_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R22_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R22_i1_get_amplitude

subroutine proc_epmum_R23_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R23_i1_init

subroutine proc_epmum_R23_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R23_i1_update_alpha_s

subroutine proc_epmum_R23_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R23_i1_reset_helicity_selection

subroutine proc_epmum_R23_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R23_i1_is_allowed

subroutine proc_epmum_R23_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R23_i1_new_event

subroutine proc_epmum_R23_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R23_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R23_i1_get_amplitude

subroutine proc_epmum_R24_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R24_i1_init

subroutine proc_epmum_R24_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R24_i1_update_alpha_s

subroutine proc_epmum_R24_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R24_i1_reset_helicity_selection

subroutine proc_epmum_R24_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R24_i1_is_allowed

subroutine proc_epmum_R24_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R24_i1_new_event

subroutine proc_epmum_R24_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R24_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R24_i1_get_amplitude

subroutine proc_epmum_R25_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R25_i1_init

subroutine proc_epmum_R25_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R25_i1_update_alpha_s

subroutine proc_epmum_R25_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R25_i1_reset_helicity_selection

subroutine proc_epmum_R25_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R25_i1_is_allowed

subroutine proc_epmum_R25_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R25_i1_new_event

subroutine proc_epmum_R25_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R25_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R25_i1_get_amplitude

subroutine proc_epmum_R26_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R26_i1_init

subroutine proc_epmum_R26_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R26_i1_update_alpha_s

subroutine proc_epmum_R26_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R26_i1_reset_helicity_selection

subroutine proc_epmum_R26_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R26_i1_is_allowed

subroutine proc_epmum_R26_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R26_i1_new_event

subroutine proc_epmum_R26_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R26_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R26_i1_get_amplitude

subroutine proc_epmum_R27_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R27_i1_init

subroutine proc_epmum_R27_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R27_i1_update_alpha_s

subroutine proc_epmum_R27_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R27_i1_reset_helicity_selection

subroutine proc_epmum_R27_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R27_i1_is_allowed

subroutine proc_epmum_R27_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R27_i1_new_event

subroutine proc_epmum_R27_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R27_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R27_i1_get_amplitude

subroutine proc_epmum_R28_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R28_i1_init

subroutine proc_epmum_R28_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R28_i1_update_alpha_s

subroutine proc_epmum_R28_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R28_i1_reset_helicity_selection

subroutine proc_epmum_R28_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R28_i1_is_allowed

subroutine proc_epmum_R28_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R28_i1_new_event

subroutine proc_epmum_R28_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R28_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R28_i1_get_amplitude

subroutine proc_epmum_R29_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R29_i1_init

subroutine proc_epmum_R29_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R29_i1_update_alpha_s

subroutine proc_epmum_R29_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R29_i1_reset_helicity_selection

subroutine proc_epmum_R29_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R29_i1_is_allowed

subroutine proc_epmum_R29_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R29_i1_new_event

subroutine proc_epmum_R29_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R29_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R29_i1_get_amplitude

subroutine proc_epmum_R30_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R30_i1_init

subroutine proc_epmum_R30_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R30_i1_update_alpha_s

subroutine proc_epmum_R30_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R30_i1_reset_helicity_selection

subroutine proc_epmum_R30_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R30_i1_is_allowed

subroutine proc_epmum_R30_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R30_i1_new_event

subroutine proc_epmum_R30_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R30_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R30_i1_get_amplitude

subroutine proc_epmum_R31_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R31_i1_init

subroutine proc_epmum_R31_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R31_i1_update_alpha_s

subroutine proc_epmum_R31_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R31_i1_reset_helicity_selection

subroutine proc_epmum_R31_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R31_i1_is_allowed

subroutine proc_epmum_R31_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R31_i1_new_event

subroutine proc_epmum_R31_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R31_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R31_i1_get_amplitude

subroutine proc_epmum_R32_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R32_i1_init

subroutine proc_epmum_R32_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R32_i1_update_alpha_s

subroutine proc_epmum_R32_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R32_i1_reset_helicity_selection

subroutine proc_epmum_R32_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R32_i1_is_allowed

subroutine proc_epmum_R32_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R32_i1_new_event

subroutine proc_epmum_R32_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R32_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R32_i1_get_amplitude

subroutine proc_epmum_R33_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R33_i1_init

subroutine proc_epmum_R33_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R33_i1_update_alpha_s

subroutine proc_epmum_R33_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R33_i1_reset_helicity_selection

subroutine proc_epmum_R33_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R33_i1_is_allowed

subroutine proc_epmum_R33_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R33_i1_new_event

subroutine proc_epmum_R33_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R33_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R33_i1_get_amplitude

subroutine proc_epmum_R34_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R34_i1_init

subroutine proc_epmum_R34_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R34_i1_update_alpha_s

subroutine proc_epmum_R34_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R34_i1_reset_helicity_selection

subroutine proc_epmum_R34_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R34_i1_is_allowed

subroutine proc_epmum_R34_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R34_i1_new_event

subroutine proc_epmum_R34_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R34_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R34_i1_get_amplitude

subroutine proc_epmum_R35_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R35_i1_init

subroutine proc_epmum_R35_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R35_i1_update_alpha_s

subroutine proc_epmum_R35_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R35_i1_reset_helicity_selection

subroutine proc_epmum_R35_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R35_i1_is_allowed

subroutine proc_epmum_R35_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R35_i1_new_event

subroutine proc_epmum_R35_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R35_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R35_i1_get_amplitude

subroutine proc_epmum_R36_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R36_i1_init

subroutine proc_epmum_R36_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R36_i1_update_alpha_s

subroutine proc_epmum_R36_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R36_i1_reset_helicity_selection

subroutine proc_epmum_R36_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R36_i1_is_allowed

subroutine proc_epmum_R36_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R36_i1_new_event

subroutine proc_epmum_R36_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R36_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R36_i1_get_amplitude

subroutine proc_epmum_R37_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R37_i1_init

subroutine proc_epmum_R37_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R37_i1_update_alpha_s

subroutine proc_epmum_R37_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R37_i1_reset_helicity_selection

subroutine proc_epmum_R37_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R37_i1_is_allowed

subroutine proc_epmum_R37_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R37_i1_new_event

subroutine proc_epmum_R37_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R37_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R37_i1_get_amplitude

subroutine proc_epmum_R38_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R38_i1_init

subroutine proc_epmum_R38_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R38_i1_update_alpha_s

subroutine proc_epmum_R38_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R38_i1_reset_helicity_selection

subroutine proc_epmum_R38_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R38_i1_is_allowed

subroutine proc_epmum_R38_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R38_i1_new_event

subroutine proc_epmum_R38_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R38_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R38_i1_get_amplitude

subroutine proc_epmum_R39_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R39_i1_init

subroutine proc_epmum_R39_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R39_i1_update_alpha_s

subroutine proc_epmum_R39_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R39_i1_reset_helicity_selection

subroutine proc_epmum_R39_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R39_i1_is_allowed

subroutine proc_epmum_R39_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R39_i1_new_event

subroutine proc_epmum_R39_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R39_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R39_i1_get_amplitude

subroutine proc_epmum_R40_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R40_i1_init

subroutine proc_epmum_R40_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R40_i1_update_alpha_s

subroutine proc_epmum_R40_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R40_i1_reset_helicity_selection

subroutine proc_epmum_R40_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R40_i1_is_allowed

subroutine proc_epmum_R40_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R40_i1_new_event

subroutine proc_epmum_R40_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R40_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R40_i1_get_amplitude

subroutine proc_epmum_R41_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R41_i1_init

subroutine proc_epmum_R41_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R41_i1_update_alpha_s

subroutine proc_epmum_R41_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R41_i1_reset_helicity_selection

subroutine proc_epmum_R41_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R41_i1_is_allowed

subroutine proc_epmum_R41_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R41_i1_new_event

subroutine proc_epmum_R41_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R41_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R41_i1_get_amplitude

subroutine proc_epmum_R42_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R42_i1_init

subroutine proc_epmum_R42_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R42_i1_update_alpha_s

subroutine proc_epmum_R42_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R42_i1_reset_helicity_selection

subroutine proc_epmum_R42_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R42_i1_is_allowed

subroutine proc_epmum_R42_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R42_i1_new_event

subroutine proc_epmum_R42_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R42_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R42_i1_get_amplitude

subroutine proc_epmum_R43_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R43_i1_init

subroutine proc_epmum_R43_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R43_i1_update_alpha_s

subroutine proc_epmum_R43_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R43_i1_reset_helicity_selection

subroutine proc_epmum_R43_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R43_i1_is_allowed

subroutine proc_epmum_R43_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R43_i1_new_event

subroutine proc_epmum_R43_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R43_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R43_i1_get_amplitude

subroutine proc_epmum_R44_i1_init (par, scheme) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  real(c_default_float), dimension(*), intent(in) :: par
  integer(c_int), intent(in) :: scheme
  call init (par, scheme)
end subroutine proc_epmum_R44_i1_init

subroutine proc_epmum_R44_i1_update_alpha_s (alpha_s) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  real(c_default_float), intent(in) :: alpha_s
  call update_alpha_s (alpha_s)
end subroutine proc_epmum_R44_i1_update_alpha_s

subroutine proc_epmum_R44_i1_reset_helicity_selection (threshold, cutoff) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  real(c_default_float), intent(in) :: threshold
  integer(c_int), intent(in) :: cutoff
  call reset_helicity_selection (threshold, int (cutoff))
end subroutine proc_epmum_R44_i1_reset_helicity_selection

subroutine proc_epmum_R44_i1_is_allowed (flv, hel, col, flag) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  integer(c_int), intent(in) :: flv, hel, col
  logical(c_bool), intent(out) :: flag
  flag = is_allowed (int (flv), int (hel), int (col))
end subroutine proc_epmum_R44_i1_is_allowed

subroutine proc_epmum_R44_i1_new_event (p) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  real(c_default_float), dimension(0:3,*), intent(in) :: p
  call new_event (p)
end subroutine proc_epmum_R44_i1_new_event

subroutine proc_epmum_R44_i1_get_amplitude (flv, hel, col, amp) bind(C)
  use iso_c_binding
  use kinds
  use opr_proc_epmum_R44_i1
  integer(c_int), intent(in) :: flv, hel, col
  complex(c_default_complex), intent(out) :: amp
  amp = get_amplitude (int (flv), int (hel), int (col))
end subroutine proc_epmum_R44_i1_get_amplitude
