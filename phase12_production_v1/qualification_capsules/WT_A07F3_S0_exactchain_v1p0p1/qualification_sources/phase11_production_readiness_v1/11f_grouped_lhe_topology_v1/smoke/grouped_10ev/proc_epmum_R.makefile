# WHIZARD: Makefile for process library 'proc_epmum_R'
# Automatically generated file, do not edit

# Integrity check (don't modify the following line!)
MD5SUM = '6C2BBE3378286668179EBBC67D599F59'

# Library name
BASE = proc_epmum_R

# Compiler
FC = mpifort
CC = mpicc

# Included libraries
FCINCL = -I/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib/mod/whizard -I/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib/mod/omega -I/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib/mod/models  

# Compiler flags
FCFLAGS =  -fopenmp -lmpi -lmpi_usempif08 -g -O2
FCFLAGS_PIC =  -fPIC
CFLAGS = -g -O2
CFLAGS_PIC = 
LDFLAGS = -L/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib -lwhizard_main -lwhizard -lomega -I/usr/include/tirpc -ltirpc  -Wl,-rpath,/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -lHepMC3 -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -lHepMC3rootIO -Wl,-rpath,/cvmfs/sft-nightlies.cern.ch/lcg/latest/ROOT/6.40.02-41739/x86_64-el9-gcc14-opt/lib -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/ROOT/6.40.02-41739/x86_64-el9-gcc14-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/lib -Wl,-rpath,/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/lib64 -L/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/lib -L/cvmfs/sft-nightlies.cern.ch/lcg/views/devkey-head/Fri/x86_64-el9-gcc14-opt/lib64 -llcio       -lomega -L/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib/whizard/models -lwhizard

# LaTeX setup
LATEX = latex -halt-on-error
MPOST = no  -halt-on-error
DVIPS = dvips
PS2PDF = ps2pdf14
TEX_FLAGS = "/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/share/texmf/whizard:$$TEXINPUTS"
MP_FLAGS  = "/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/share/texmf/whizard:$$MPINPUTS"

# Libtool
LIBTOOL = /afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/lib/whizard/libtool
FCOMPILE = @$(LIBTOOL) --silent --tag=FC --mode=compile
CCOMPILE = @$(LIBTOOL) --silent --tag=CC --mode=compile
LINK = @$(LIBTOOL) --silent --tag=FC --mode=link

# Compile commands (default)
LTFCOMPILE = $(FCOMPILE) $(FC) -c $(FCINCL) $(FCFLAGS) $(FCFLAGS_PIC)
LTCCOMPILE = $(CCOMPILE) $(CC) -c $(CFLAGS) $(CFLAGS_PIC)

# Default target
all: link diags

# Matrix-element code files
SOURCES += proc_epmum_R1_i1.f90
OBJECTS += proc_epmum_R1_i1.lo
proc_epmum_R1_i1.f90:
	@echo  "  OMEGA     proc_epmum_R1_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R1_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R1_i1 -target:md5sum '6C9EF48D7635391C160F0350FC57EE88' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+5~t && 6+7~W- && 6+7+8~tbar' 
clean-proc_epmum_R1_i1:
	@echo  "  RM        proc_epmum_R1_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R1_i1.f90
	@rm -f opr_proc_epmum_R1_i1.mod
	@rm -f proc_epmum_R1_i1.lo
CLEAN_SOURCES += proc_epmum_R1_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R1_i1.mod
CLEAN_OBJECTS += proc_epmum_R1_i1.lo
proc_epmum_R1_i1.lo: proc_epmum_R1_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R2_i1.f90
OBJECTS += proc_epmum_R2_i1.lo
proc_epmum_R2_i1.f90:
	@echo  "  OMEGA     proc_epmum_R2_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R2_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R2_i1 -target:md5sum 'F6C584C5DD736567CD16C92D1052473B' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 6+7~W- && 6+7+8~tbar' 
clean-proc_epmum_R2_i1:
	@echo  "  RM        proc_epmum_R2_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R2_i1.f90
	@rm -f opr_proc_epmum_R2_i1.mod
	@rm -f proc_epmum_R2_i1.lo
CLEAN_SOURCES += proc_epmum_R2_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R2_i1.mod
CLEAN_OBJECTS += proc_epmum_R2_i1.lo
proc_epmum_R2_i1.lo: proc_epmum_R2_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R3_i1.f90
OBJECTS += proc_epmum_R3_i1.lo
proc_epmum_R3_i1.f90:
	@echo  "  OMEGA     proc_epmum_R3_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R3_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R3_i1 -target:md5sum '9699102CB724069FCAF886BC7DCE9677' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5~t && 6+7~W- && 6+7+8~tbar' 
clean-proc_epmum_R3_i1:
	@echo  "  RM        proc_epmum_R3_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R3_i1.f90
	@rm -f opr_proc_epmum_R3_i1.mod
	@rm -f proc_epmum_R3_i1.lo
CLEAN_SOURCES += proc_epmum_R3_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R3_i1.mod
CLEAN_OBJECTS += proc_epmum_R3_i1.lo
proc_epmum_R3_i1.lo: proc_epmum_R3_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R4_i1.f90
OBJECTS += proc_epmum_R4_i1.lo
proc_epmum_R4_i1.f90:
	@echo  "  OMEGA     proc_epmum_R4_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R4_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R4_i1 -target:md5sum '2B16CA3BB68A77A729B85CBE69B1FFBA' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+5~t && 6+7~W-' 
clean-proc_epmum_R4_i1:
	@echo  "  RM        proc_epmum_R4_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R4_i1.f90
	@rm -f opr_proc_epmum_R4_i1.mod
	@rm -f proc_epmum_R4_i1.lo
CLEAN_SOURCES += proc_epmum_R4_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R4_i1.mod
CLEAN_OBJECTS += proc_epmum_R4_i1.lo
proc_epmum_R4_i1.lo: proc_epmum_R4_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R5_i1.f90
OBJECTS += proc_epmum_R5_i1.lo
proc_epmum_R5_i1.f90:
	@echo  "  OMEGA     proc_epmum_R5_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R5_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R5_i1 -target:md5sum 'BC560D6ED8537079067C34D1A755E885' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5~t && 6+7~W-' 
clean-proc_epmum_R5_i1:
	@echo  "  RM        proc_epmum_R5_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R5_i1.f90
	@rm -f opr_proc_epmum_R5_i1.mod
	@rm -f proc_epmum_R5_i1.lo
CLEAN_SOURCES += proc_epmum_R5_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R5_i1.mod
CLEAN_OBJECTS += proc_epmum_R5_i1.lo
proc_epmum_R5_i1.lo: proc_epmum_R5_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R6_i1.f90
OBJECTS += proc_epmum_R6_i1.lo
proc_epmum_R6_i1.f90:
	@echo  "  OMEGA     proc_epmum_R6_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R6_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R6_i1 -target:md5sum '9F2CF45400ED35D6AF2FA9EE0FA556BD' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 6+7~W- && 5+8~H' 
clean-proc_epmum_R6_i1:
	@echo  "  RM        proc_epmum_R6_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R6_i1.f90
	@rm -f opr_proc_epmum_R6_i1.mod
	@rm -f proc_epmum_R6_i1.lo
CLEAN_SOURCES += proc_epmum_R6_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R6_i1.mod
CLEAN_OBJECTS += proc_epmum_R6_i1.lo
proc_epmum_R6_i1.lo: proc_epmum_R6_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R7_i1.f90
OBJECTS += proc_epmum_R7_i1.lo
proc_epmum_R7_i1.f90:
	@echo  "  OMEGA     proc_epmum_R7_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R7_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R7_i1 -target:md5sum '157B704786D7156932B676FCE68F082A' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 6+7~W- && 5+8~Z' 
clean-proc_epmum_R7_i1:
	@echo  "  RM        proc_epmum_R7_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R7_i1.f90
	@rm -f opr_proc_epmum_R7_i1.mod
	@rm -f proc_epmum_R7_i1.lo
CLEAN_SOURCES += proc_epmum_R7_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R7_i1.mod
CLEAN_OBJECTS += proc_epmum_R7_i1.lo
proc_epmum_R7_i1.lo: proc_epmum_R7_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R8_i1.f90
OBJECTS += proc_epmum_R8_i1.lo
proc_epmum_R8_i1.f90:
	@echo  "  OMEGA     proc_epmum_R8_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R8_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R8_i1 -target:md5sum 'D5FA2B65D0A24D26059ED9F7317279B9' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+6+7~Z && 5+8~H' 
clean-proc_epmum_R8_i1:
	@echo  "  RM        proc_epmum_R8_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R8_i1.f90
	@rm -f opr_proc_epmum_R8_i1.mod
	@rm -f proc_epmum_R8_i1.lo
CLEAN_SOURCES += proc_epmum_R8_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R8_i1.mod
CLEAN_OBJECTS += proc_epmum_R8_i1.lo
proc_epmum_R8_i1.lo: proc_epmum_R8_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R9_i1.f90
OBJECTS += proc_epmum_R9_i1.lo
proc_epmum_R9_i1.f90:
	@echo  "  OMEGA     proc_epmum_R9_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R9_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R9_i1 -target:md5sum '428A6D80EBDE3EF8079A19B9A6E2D7FB' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+6+7~H && 5+8~Z' 
clean-proc_epmum_R9_i1:
	@echo  "  RM        proc_epmum_R9_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R9_i1.f90
	@rm -f opr_proc_epmum_R9_i1.mod
	@rm -f proc_epmum_R9_i1.lo
CLEAN_SOURCES += proc_epmum_R9_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R9_i1.mod
CLEAN_OBJECTS += proc_epmum_R9_i1.lo
proc_epmum_R9_i1.lo: proc_epmum_R9_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R10_i1.f90
OBJECTS += proc_epmum_R10_i1.lo
proc_epmum_R10_i1.f90:
	@echo  "  OMEGA     proc_epmum_R10_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R10_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R10_i1 -target:md5sum '3F7D39A669ACB2C0DBD0CF5646A452AC' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+6+7~H' 
clean-proc_epmum_R10_i1:
	@echo  "  RM        proc_epmum_R10_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R10_i1.f90
	@rm -f opr_proc_epmum_R10_i1.mod
	@rm -f proc_epmum_R10_i1.lo
CLEAN_SOURCES += proc_epmum_R10_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R10_i1.mod
CLEAN_OBJECTS += proc_epmum_R10_i1.lo
proc_epmum_R10_i1.lo: proc_epmum_R10_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R11_i1.f90
OBJECTS += proc_epmum_R11_i1.lo
proc_epmum_R11_i1.f90:
	@echo  "  OMEGA     proc_epmum_R11_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R11_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R11_i1 -target:md5sum 'D8D8DEE2165A133B4770698E4A071053' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+5~t && 6+7+8~tbar' 
clean-proc_epmum_R11_i1:
	@echo  "  RM        proc_epmum_R11_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R11_i1.f90
	@rm -f opr_proc_epmum_R11_i1.mod
	@rm -f proc_epmum_R11_i1.lo
CLEAN_SOURCES += proc_epmum_R11_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R11_i1.mod
CLEAN_OBJECTS += proc_epmum_R11_i1.lo
proc_epmum_R11_i1.lo: proc_epmum_R11_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R12_i1.f90
OBJECTS += proc_epmum_R12_i1.lo
proc_epmum_R12_i1.f90:
	@echo  "  OMEGA     proc_epmum_R12_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R12_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R12_i1 -target:md5sum '1639240388F34214C7757A0DD57E8069' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 6+7+8~tbar' 
clean-proc_epmum_R12_i1:
	@echo  "  RM        proc_epmum_R12_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R12_i1.f90
	@rm -f opr_proc_epmum_R12_i1.mod
	@rm -f proc_epmum_R12_i1.lo
CLEAN_SOURCES += proc_epmum_R12_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R12_i1.mod
CLEAN_OBJECTS += proc_epmum_R12_i1.lo
proc_epmum_R12_i1.lo: proc_epmum_R12_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R13_i1.f90
OBJECTS += proc_epmum_R13_i1.lo
proc_epmum_R13_i1.f90:
	@echo  "  OMEGA     proc_epmum_R13_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R13_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R13_i1 -target:md5sum 'B6E11E9AD6FF68B1244629A0A9404924' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5~t && 6+7+8~tbar' 
clean-proc_epmum_R13_i1:
	@echo  "  RM        proc_epmum_R13_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R13_i1.f90
	@rm -f opr_proc_epmum_R13_i1.mod
	@rm -f proc_epmum_R13_i1.lo
CLEAN_SOURCES += proc_epmum_R13_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R13_i1.mod
CLEAN_OBJECTS += proc_epmum_R13_i1.lo
proc_epmum_R13_i1.lo: proc_epmum_R13_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R14_i1.f90
OBJECTS += proc_epmum_R14_i1.lo
proc_epmum_R14_i1.f90:
	@echo  "  OMEGA     proc_epmum_R14_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R14_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R14_i1 -target:md5sum '75A7594E8FE5645999FE2F3DD7263FCF' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+6+7~Z && 5+8~H' 
clean-proc_epmum_R14_i1:
	@echo  "  RM        proc_epmum_R14_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R14_i1.f90
	@rm -f opr_proc_epmum_R14_i1.mod
	@rm -f proc_epmum_R14_i1.lo
CLEAN_SOURCES += proc_epmum_R14_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R14_i1.mod
CLEAN_OBJECTS += proc_epmum_R14_i1.lo
proc_epmum_R14_i1.lo: proc_epmum_R14_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R15_i1.f90
OBJECTS += proc_epmum_R15_i1.lo
proc_epmum_R15_i1.f90:
	@echo  "  OMEGA     proc_epmum_R15_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R15_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R15_i1 -target:md5sum '26B64A74FC553508D2541DB11B355028' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+6+7~H && 5+8~Z' 
clean-proc_epmum_R15_i1:
	@echo  "  RM        proc_epmum_R15_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R15_i1.f90
	@rm -f opr_proc_epmum_R15_i1.mod
	@rm -f proc_epmum_R15_i1.lo
CLEAN_SOURCES += proc_epmum_R15_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R15_i1.mod
CLEAN_OBJECTS += proc_epmum_R15_i1.lo
proc_epmum_R15_i1.lo: proc_epmum_R15_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R16_i1.f90
OBJECTS += proc_epmum_R16_i1.lo
proc_epmum_R16_i1.f90:
	@echo  "  OMEGA     proc_epmum_R16_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R16_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R16_i1 -target:md5sum '21ECB3FFBDD4EFB36065C735EC279F7F' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+6+7~H' 
clean-proc_epmum_R16_i1:
	@echo  "  RM        proc_epmum_R16_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R16_i1.f90
	@rm -f opr_proc_epmum_R16_i1.mod
	@rm -f proc_epmum_R16_i1.lo
CLEAN_SOURCES += proc_epmum_R16_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R16_i1.mod
CLEAN_OBJECTS += proc_epmum_R16_i1.lo
proc_epmum_R16_i1.lo: proc_epmum_R16_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R17_i1.f90
OBJECTS += proc_epmum_R17_i1.lo
proc_epmum_R17_i1.f90:
	@echo  "  OMEGA     proc_epmum_R17_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R17_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R17_i1 -target:md5sum '1CC03361406A2638A0E482793B68EF44' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 6+7~W-' 
clean-proc_epmum_R17_i1:
	@echo  "  RM        proc_epmum_R17_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R17_i1.f90
	@rm -f opr_proc_epmum_R17_i1.mod
	@rm -f proc_epmum_R17_i1.lo
CLEAN_SOURCES += proc_epmum_R17_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R17_i1.mod
CLEAN_OBJECTS += proc_epmum_R17_i1.lo
proc_epmum_R17_i1.lo: proc_epmum_R17_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R18_i1.f90
OBJECTS += proc_epmum_R18_i1.lo
proc_epmum_R18_i1.f90:
	@echo  "  OMEGA     proc_epmum_R18_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R18_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R18_i1 -target:md5sum '05B66BFE6461AFD650684366E721E9A3' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+' 
clean-proc_epmum_R18_i1:
	@echo  "  RM        proc_epmum_R18_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R18_i1.f90
	@rm -f opr_proc_epmum_R18_i1.mod
	@rm -f proc_epmum_R18_i1.lo
CLEAN_SOURCES += proc_epmum_R18_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R18_i1.mod
CLEAN_OBJECTS += proc_epmum_R18_i1.lo
proc_epmum_R18_i1.lo: proc_epmum_R18_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R19_i1.f90
OBJECTS += proc_epmum_R19_i1.lo
proc_epmum_R19_i1.f90:
	@echo  "  OMEGA     proc_epmum_R19_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R19_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R19_i1 -target:md5sum 'AAA3DD4ED39159BEBBFCFFE84DB37611' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+5+6+7+8~Z' 
clean-proc_epmum_R19_i1:
	@echo  "  RM        proc_epmum_R19_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R19_i1.f90
	@rm -f opr_proc_epmum_R19_i1.mod
	@rm -f proc_epmum_R19_i1.lo
CLEAN_SOURCES += proc_epmum_R19_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R19_i1.mod
CLEAN_OBJECTS += proc_epmum_R19_i1.lo
proc_epmum_R19_i1.lo: proc_epmum_R19_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R20_i1.f90
OBJECTS += proc_epmum_R20_i1.lo
proc_epmum_R20_i1.f90:
	@echo  "  OMEGA     proc_epmum_R20_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R20_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R20_i1 -target:md5sum 'F3FD6EB01DE5A2BA239BC8CB200AA366' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+5+8~W+' 
clean-proc_epmum_R20_i1:
	@echo  "  RM        proc_epmum_R20_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R20_i1.f90
	@rm -f opr_proc_epmum_R20_i1.mod
	@rm -f proc_epmum_R20_i1.lo
CLEAN_SOURCES += proc_epmum_R20_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R20_i1.mod
CLEAN_OBJECTS += proc_epmum_R20_i1.lo
proc_epmum_R20_i1.lo: proc_epmum_R20_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R21_i1.f90
OBJECTS += proc_epmum_R21_i1.lo
proc_epmum_R21_i1.f90:
	@echo  "  OMEGA     proc_epmum_R21_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R21_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R21_i1 -target:md5sum 'E4F5C5841E687BC80869177C3ECA0A84' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 5+6+7+8~W-' 
clean-proc_epmum_R21_i1:
	@echo  "  RM        proc_epmum_R21_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R21_i1.f90
	@rm -f opr_proc_epmum_R21_i1.mod
	@rm -f proc_epmum_R21_i1.lo
CLEAN_SOURCES += proc_epmum_R21_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R21_i1.mod
CLEAN_OBJECTS += proc_epmum_R21_i1.lo
proc_epmum_R21_i1.lo: proc_epmum_R21_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R22_i1.f90
OBJECTS += proc_epmum_R22_i1.lo
proc_epmum_R22_i1.f90:
	@echo  "  OMEGA     proc_epmum_R22_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R22_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R22_i1 -target:md5sum '9B81EF4F8C2E1B305F4FD3A554C06F03' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5+8~W+' 
clean-proc_epmum_R22_i1:
	@echo  "  RM        proc_epmum_R22_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R22_i1.f90
	@rm -f opr_proc_epmum_R22_i1.mod
	@rm -f proc_epmum_R22_i1.lo
CLEAN_SOURCES += proc_epmum_R22_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R22_i1.mod
CLEAN_OBJECTS += proc_epmum_R22_i1.lo
proc_epmum_R22_i1.lo: proc_epmum_R22_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R23_i1.f90
OBJECTS += proc_epmum_R23_i1.lo
proc_epmum_R23_i1.f90:
	@echo  "  OMEGA     proc_epmum_R23_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R23_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R23_i1 -target:md5sum '870DDAEA610433F04934AC682687088B' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5+8~W+ && 3+4+5+6+7+8~Z' 
clean-proc_epmum_R23_i1:
	@echo  "  RM        proc_epmum_R23_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R23_i1.f90
	@rm -f opr_proc_epmum_R23_i1.mod
	@rm -f proc_epmum_R23_i1.lo
CLEAN_SOURCES += proc_epmum_R23_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R23_i1.mod
CLEAN_OBJECTS += proc_epmum_R23_i1.lo
proc_epmum_R23_i1.lo: proc_epmum_R23_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R24_i1.f90
OBJECTS += proc_epmum_R24_i1.lo
proc_epmum_R24_i1.f90:
	@echo  "  OMEGA     proc_epmum_R24_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R24_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R24_i1 -target:md5sum 'CAD0BE0C878A6DBF592ACC9D10E9A3C8' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+5+6+7+8~Z' 
clean-proc_epmum_R24_i1:
	@echo  "  RM        proc_epmum_R24_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R24_i1.f90
	@rm -f opr_proc_epmum_R24_i1.mod
	@rm -f proc_epmum_R24_i1.lo
CLEAN_SOURCES += proc_epmum_R24_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R24_i1.mod
CLEAN_OBJECTS += proc_epmum_R24_i1.lo
proc_epmum_R24_i1.lo: proc_epmum_R24_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R25_i1.f90
OBJECTS += proc_epmum_R25_i1.lo
proc_epmum_R25_i1.f90:
	@echo  "  OMEGA     proc_epmum_R25_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R25_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R25_i1 -target:md5sum '8BBA285903F00BB0C667600E4B741988' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '5+6+7+8~W- && 3+4+5+6+7+8~Z' 
clean-proc_epmum_R25_i1:
	@echo  "  RM        proc_epmum_R25_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R25_i1.f90
	@rm -f opr_proc_epmum_R25_i1.mod
	@rm -f proc_epmum_R25_i1.lo
CLEAN_SOURCES += proc_epmum_R25_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R25_i1.mod
CLEAN_OBJECTS += proc_epmum_R25_i1.lo
proc_epmum_R25_i1.lo: proc_epmum_R25_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R26_i1.f90
OBJECTS += proc_epmum_R26_i1.lo
proc_epmum_R26_i1.f90:
	@echo  "  OMEGA     proc_epmum_R26_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R26_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R26_i1 -target:md5sum 'DA4153020300487C75E0C7C41E6088C3' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W-' 
clean-proc_epmum_R26_i1:
	@echo  "  RM        proc_epmum_R26_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R26_i1.f90
	@rm -f opr_proc_epmum_R26_i1.mod
	@rm -f proc_epmum_R26_i1.lo
CLEAN_SOURCES += proc_epmum_R26_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R26_i1.mod
CLEAN_OBJECTS += proc_epmum_R26_i1.lo
proc_epmum_R26_i1.lo: proc_epmum_R26_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R27_i1.f90
OBJECTS += proc_epmum_R27_i1.lo
proc_epmum_R27_i1.f90:
	@echo  "  OMEGA     proc_epmum_R27_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R27_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R27_i1 -target:md5sum '7E9388E43D5973492ECB733F1BAB8845' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '5+6+7+8~W-' 
clean-proc_epmum_R27_i1:
	@echo  "  RM        proc_epmum_R27_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R27_i1.f90
	@rm -f opr_proc_epmum_R27_i1.mod
	@rm -f proc_epmum_R27_i1.lo
CLEAN_SOURCES += proc_epmum_R27_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R27_i1.mod
CLEAN_OBJECTS += proc_epmum_R27_i1.lo
proc_epmum_R27_i1.lo: proc_epmum_R27_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R28_i1.f90
OBJECTS += proc_epmum_R28_i1.lo
proc_epmum_R28_i1.f90:
	@echo  "  OMEGA     proc_epmum_R28_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R28_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R28_i1 -target:md5sum 'DDF1F4998B5DBAA5835E7DD41185AD6F' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+6+7~Z && 5+8~H' 
clean-proc_epmum_R28_i1:
	@echo  "  RM        proc_epmum_R28_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R28_i1.f90
	@rm -f opr_proc_epmum_R28_i1.mod
	@rm -f proc_epmum_R28_i1.lo
CLEAN_SOURCES += proc_epmum_R28_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R28_i1.mod
CLEAN_OBJECTS += proc_epmum_R28_i1.lo
proc_epmum_R28_i1.lo: proc_epmum_R28_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R29_i1.f90
OBJECTS += proc_epmum_R29_i1.lo
proc_epmum_R29_i1.f90:
	@echo  "  OMEGA     proc_epmum_R29_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R29_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R29_i1 -target:md5sum '0939E78042C201E86EFA43E45AAA2612' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+6+7~Z' 
clean-proc_epmum_R29_i1:
	@echo  "  RM        proc_epmum_R29_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R29_i1.f90
	@rm -f opr_proc_epmum_R29_i1.mod
	@rm -f proc_epmum_R29_i1.lo
CLEAN_SOURCES += proc_epmum_R29_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R29_i1.mod
CLEAN_OBJECTS += proc_epmum_R29_i1.lo
proc_epmum_R29_i1.lo: proc_epmum_R29_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R30_i1.f90
OBJECTS += proc_epmum_R30_i1.lo
proc_epmum_R30_i1.f90:
	@echo  "  OMEGA     proc_epmum_R30_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R30_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R30_i1 -target:md5sum 'CCFFEF0856B854B2C7127D0C7F681170' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+6+7~Z' 
clean-proc_epmum_R30_i1:
	@echo  "  RM        proc_epmum_R30_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R30_i1.f90
	@rm -f opr_proc_epmum_R30_i1.mod
	@rm -f proc_epmum_R30_i1.lo
CLEAN_SOURCES += proc_epmum_R30_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R30_i1.mod
CLEAN_OBJECTS += proc_epmum_R30_i1.lo
proc_epmum_R30_i1.lo: proc_epmum_R30_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R31_i1.f90
OBJECTS += proc_epmum_R31_i1.lo
proc_epmum_R31_i1.f90:
	@echo  "  OMEGA     proc_epmum_R31_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R31_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R31_i1 -target:md5sum '48A68320916E66598EA7556C00458143' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+6+7~Z' 
clean-proc_epmum_R31_i1:
	@echo  "  RM        proc_epmum_R31_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R31_i1.f90
	@rm -f opr_proc_epmum_R31_i1.mod
	@rm -f proc_epmum_R31_i1.lo
CLEAN_SOURCES += proc_epmum_R31_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R31_i1.mod
CLEAN_OBJECTS += proc_epmum_R31_i1.lo
proc_epmum_R31_i1.lo: proc_epmum_R31_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R32_i1.f90
OBJECTS += proc_epmum_R32_i1.lo
proc_epmum_R32_i1.f90:
	@echo  "  OMEGA     proc_epmum_R32_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R32_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R32_i1 -target:md5sum '921695AFEE7704EDA6095126FD1C3E22' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 5+8~Z' 
clean-proc_epmum_R32_i1:
	@echo  "  RM        proc_epmum_R32_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R32_i1.f90
	@rm -f opr_proc_epmum_R32_i1.mod
	@rm -f proc_epmum_R32_i1.lo
CLEAN_SOURCES += proc_epmum_R32_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R32_i1.mod
CLEAN_OBJECTS += proc_epmum_R32_i1.lo
proc_epmum_R32_i1.lo: proc_epmum_R32_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R33_i1.f90
OBJECTS += proc_epmum_R33_i1.lo
proc_epmum_R33_i1.f90:
	@echo  "  OMEGA     proc_epmum_R33_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R33_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R33_i1 -target:md5sum '718439FED094D24ABACF01DF68557009' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 5+8~H' 
clean-proc_epmum_R33_i1:
	@echo  "  RM        proc_epmum_R33_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R33_i1.f90
	@rm -f opr_proc_epmum_R33_i1.mod
	@rm -f proc_epmum_R33_i1.lo
CLEAN_SOURCES += proc_epmum_R33_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R33_i1.mod
CLEAN_OBJECTS += proc_epmum_R33_i1.lo
proc_epmum_R33_i1.lo: proc_epmum_R33_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R34_i1.f90
OBJECTS += proc_epmum_R34_i1.lo
proc_epmum_R34_i1.f90:
	@echo  "  OMEGA     proc_epmum_R34_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R34_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R34_i1 -target:md5sum '7D80DB9B5D25E4D52ADD9B8995DD1005' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 6+7+8~tbar' 
clean-proc_epmum_R34_i1:
	@echo  "  RM        proc_epmum_R34_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R34_i1.f90
	@rm -f opr_proc_epmum_R34_i1.mod
	@rm -f proc_epmum_R34_i1.lo
CLEAN_SOURCES += proc_epmum_R34_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R34_i1.mod
CLEAN_OBJECTS += proc_epmum_R34_i1.lo
proc_epmum_R34_i1.lo: proc_epmum_R34_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R35_i1.f90
OBJECTS += proc_epmum_R35_i1.lo
proc_epmum_R35_i1.f90:
	@echo  "  OMEGA     proc_epmum_R35_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R35_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R35_i1 -target:md5sum '668D516FED0E56ECD1BF23F698328CD7' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7+8~tbar' 
clean-proc_epmum_R35_i1:
	@echo  "  RM        proc_epmum_R35_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R35_i1.f90
	@rm -f opr_proc_epmum_R35_i1.mod
	@rm -f proc_epmum_R35_i1.lo
CLEAN_SOURCES += proc_epmum_R35_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R35_i1.mod
CLEAN_OBJECTS += proc_epmum_R35_i1.lo
proc_epmum_R35_i1.lo: proc_epmum_R35_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R36_i1.f90
OBJECTS += proc_epmum_R36_i1.lo
proc_epmum_R36_i1.f90:
	@echo  "  OMEGA     proc_epmum_R36_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R36_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R36_i1 -target:md5sum '4F54529B7593F74A628C81F035D8CC7C' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 5+8~Z' 
clean-proc_epmum_R36_i1:
	@echo  "  RM        proc_epmum_R36_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R36_i1.f90
	@rm -f opr_proc_epmum_R36_i1.mod
	@rm -f proc_epmum_R36_i1.lo
CLEAN_SOURCES += proc_epmum_R36_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R36_i1.mod
CLEAN_OBJECTS += proc_epmum_R36_i1.lo
proc_epmum_R36_i1.lo: proc_epmum_R36_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R37_i1.f90
OBJECTS += proc_epmum_R37_i1.lo
proc_epmum_R37_i1.f90:
	@echo  "  OMEGA     proc_epmum_R37_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R37_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R37_i1 -target:md5sum '9AD6B5AE8A8EC8BF226F218828DA0416' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 5+8~H' 
clean-proc_epmum_R37_i1:
	@echo  "  RM        proc_epmum_R37_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R37_i1.f90
	@rm -f opr_proc_epmum_R37_i1.mod
	@rm -f proc_epmum_R37_i1.lo
CLEAN_SOURCES += proc_epmum_R37_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R37_i1.mod
CLEAN_OBJECTS += proc_epmum_R37_i1.lo
proc_epmum_R37_i1.lo: proc_epmum_R37_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R38_i1.f90
OBJECTS += proc_epmum_R38_i1.lo
proc_epmum_R38_i1.f90:
	@echo  "  OMEGA     proc_epmum_R38_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R38_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R38_i1 -target:md5sum 'B77E69D828F465215CDBE1A7918D3082' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '6+7~W- && 3+4+6+7~Z && 5+8~Z' 
clean-proc_epmum_R38_i1:
	@echo  "  RM        proc_epmum_R38_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R38_i1.f90
	@rm -f opr_proc_epmum_R38_i1.mod
	@rm -f proc_epmum_R38_i1.lo
CLEAN_SOURCES += proc_epmum_R38_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R38_i1.mod
CLEAN_OBJECTS += proc_epmum_R38_i1.lo
proc_epmum_R38_i1.lo: proc_epmum_R38_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R39_i1.f90
OBJECTS += proc_epmum_R39_i1.lo
proc_epmum_R39_i1.f90:
	@echo  "  OMEGA     proc_epmum_R39_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R39_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R39_i1 -target:md5sum '7EE2742648837FD5AF73923F67A058AA' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+6+7~Z && 5+8~Z' 
clean-proc_epmum_R39_i1:
	@echo  "  RM        proc_epmum_R39_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R39_i1.f90
	@rm -f opr_proc_epmum_R39_i1.mod
	@rm -f proc_epmum_R39_i1.lo
CLEAN_SOURCES += proc_epmum_R39_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R39_i1.mod
CLEAN_OBJECTS += proc_epmum_R39_i1.lo
proc_epmum_R39_i1.lo: proc_epmum_R39_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R40_i1.f90
OBJECTS += proc_epmum_R40_i1.lo
proc_epmum_R40_i1.f90:
	@echo  "  OMEGA     proc_epmum_R40_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R40_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R40_i1 -target:md5sum '63FB4B6FAEDAC7D23525638F5DE0C46B' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+6+7~Z && 5+8~Z' 
clean-proc_epmum_R40_i1:
	@echo  "  RM        proc_epmum_R40_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R40_i1.f90
	@rm -f opr_proc_epmum_R40_i1.mod
	@rm -f proc_epmum_R40_i1.lo
CLEAN_SOURCES += proc_epmum_R40_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R40_i1.mod
CLEAN_OBJECTS += proc_epmum_R40_i1.lo
proc_epmum_R40_i1.lo: proc_epmum_R40_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R41_i1.f90
OBJECTS += proc_epmum_R41_i1.lo
proc_epmum_R41_i1.f90:
	@echo  "  OMEGA     proc_epmum_R41_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R41_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R41_i1 -target:md5sum 'F607135FC406BA17590DEDEFC53B0A8F' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '5+8~Z' 
clean-proc_epmum_R41_i1:
	@echo  "  RM        proc_epmum_R41_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R41_i1.f90
	@rm -f opr_proc_epmum_R41_i1.mod
	@rm -f proc_epmum_R41_i1.lo
CLEAN_SOURCES += proc_epmum_R41_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R41_i1.mod
CLEAN_OBJECTS += proc_epmum_R41_i1.lo
proc_epmum_R41_i1.lo: proc_epmum_R41_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R42_i1.f90
OBJECTS += proc_epmum_R42_i1.lo
proc_epmum_R42_i1.f90:
	@echo  "  OMEGA     proc_epmum_R42_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R42_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R42_i1 -target:md5sum '4C985E22D9D427C69CF045DAF2C4AF40' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '5+8~H' 
clean-proc_epmum_R42_i1:
	@echo  "  RM        proc_epmum_R42_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R42_i1.f90
	@rm -f opr_proc_epmum_R42_i1.mod
	@rm -f proc_epmum_R42_i1.lo
CLEAN_SOURCES += proc_epmum_R42_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R42_i1.mod
CLEAN_OBJECTS += proc_epmum_R42_i1.lo
proc_epmum_R42_i1.lo: proc_epmum_R42_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R43_i1.f90
OBJECTS += proc_epmum_R43_i1.lo
proc_epmum_R43_i1.f90:
	@echo  "  OMEGA     proc_epmum_R43_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R43_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R43_i1 -target:md5sum '5547B4D65CF723BF22085BB6DD28D538' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4~W+ && 3+4+5~t' 
clean-proc_epmum_R43_i1:
	@echo  "  RM        proc_epmum_R43_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R43_i1.f90
	@rm -f opr_proc_epmum_R43_i1.mod
	@rm -f proc_epmum_R43_i1.lo
CLEAN_SOURCES += proc_epmum_R43_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R43_i1.mod
CLEAN_OBJECTS += proc_epmum_R43_i1.lo
proc_epmum_R43_i1.lo: proc_epmum_R43_i1.f90
	$(LTFCOMPILE) $<
SOURCES += proc_epmum_R44_i1.f90
OBJECTS += proc_epmum_R44_i1.lo
proc_epmum_R44_i1.f90:
	@echo  "  OMEGA     proc_epmum_R44_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o proc_epmum_R44_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_proc_epmum_R44_i1 -target:md5sum '6C81D0068F192DC5A272B5F6678BC93D' -fusion:progress -scatter 'e- e+ -> e+ nue b mu- numubar bbar' -cascade '3+4+5~t' 
clean-proc_epmum_R44_i1:
	@echo  "  RM        proc_epmum_R44_i1.f90,.mod,.lo"
	@rm -f proc_epmum_R44_i1.f90
	@rm -f opr_proc_epmum_R44_i1.mod
	@rm -f proc_epmum_R44_i1.lo
CLEAN_SOURCES += proc_epmum_R44_i1.f90
CLEAN_OBJECTS += opr_proc_epmum_R44_i1.mod
CLEAN_OBJECTS += proc_epmum_R44_i1.lo
proc_epmum_R44_i1.lo: proc_epmum_R44_i1.f90
	$(LTFCOMPILE) $<

# Library driver
$(BASE).lo: $(BASE).f90 $(OBJECTS)
	$(LTFCOMPILE) $<
	@echo  "  FC       " $@

# Library
$(BASE).la: $(BASE).lo $(OBJECTS)
	@echo  "  FCLD     " $@
	$(LINK) $(FC) -module -rpath /dev/null $(FCFLAGS) $(LDFLAGS) -o $(BASE).la $^

# Main targets
link: compile $(BASE).la
compile: source $(OBJECTS) $(TEX_OBJECTS) $(BASE).lo
compile_tex: $(TEX_OBJECTS)
source: $(SOURCES) $(BASE).f90 $(TEX_SOURCES)
.PHONY: link diags compile compile_tex source

# Specific cleanup targets
clean-proc_epmum_R1_i1:
.PHONY: clean-proc_epmum_R1_i1
clean-proc_epmum_R2_i1:
.PHONY: clean-proc_epmum_R2_i1
clean-proc_epmum_R3_i1:
.PHONY: clean-proc_epmum_R3_i1
clean-proc_epmum_R4_i1:
.PHONY: clean-proc_epmum_R4_i1
clean-proc_epmum_R5_i1:
.PHONY: clean-proc_epmum_R5_i1
clean-proc_epmum_R6_i1:
.PHONY: clean-proc_epmum_R6_i1
clean-proc_epmum_R7_i1:
.PHONY: clean-proc_epmum_R7_i1
clean-proc_epmum_R8_i1:
.PHONY: clean-proc_epmum_R8_i1
clean-proc_epmum_R9_i1:
.PHONY: clean-proc_epmum_R9_i1
clean-proc_epmum_R10_i1:
.PHONY: clean-proc_epmum_R10_i1
clean-proc_epmum_R11_i1:
.PHONY: clean-proc_epmum_R11_i1
clean-proc_epmum_R12_i1:
.PHONY: clean-proc_epmum_R12_i1
clean-proc_epmum_R13_i1:
.PHONY: clean-proc_epmum_R13_i1
clean-proc_epmum_R14_i1:
.PHONY: clean-proc_epmum_R14_i1
clean-proc_epmum_R15_i1:
.PHONY: clean-proc_epmum_R15_i1
clean-proc_epmum_R16_i1:
.PHONY: clean-proc_epmum_R16_i1
clean-proc_epmum_R17_i1:
.PHONY: clean-proc_epmum_R17_i1
clean-proc_epmum_R18_i1:
.PHONY: clean-proc_epmum_R18_i1
clean-proc_epmum_R19_i1:
.PHONY: clean-proc_epmum_R19_i1
clean-proc_epmum_R20_i1:
.PHONY: clean-proc_epmum_R20_i1
clean-proc_epmum_R21_i1:
.PHONY: clean-proc_epmum_R21_i1
clean-proc_epmum_R22_i1:
.PHONY: clean-proc_epmum_R22_i1
clean-proc_epmum_R23_i1:
.PHONY: clean-proc_epmum_R23_i1
clean-proc_epmum_R24_i1:
.PHONY: clean-proc_epmum_R24_i1
clean-proc_epmum_R25_i1:
.PHONY: clean-proc_epmum_R25_i1
clean-proc_epmum_R26_i1:
.PHONY: clean-proc_epmum_R26_i1
clean-proc_epmum_R27_i1:
.PHONY: clean-proc_epmum_R27_i1
clean-proc_epmum_R28_i1:
.PHONY: clean-proc_epmum_R28_i1
clean-proc_epmum_R29_i1:
.PHONY: clean-proc_epmum_R29_i1
clean-proc_epmum_R30_i1:
.PHONY: clean-proc_epmum_R30_i1
clean-proc_epmum_R31_i1:
.PHONY: clean-proc_epmum_R31_i1
clean-proc_epmum_R32_i1:
.PHONY: clean-proc_epmum_R32_i1
clean-proc_epmum_R33_i1:
.PHONY: clean-proc_epmum_R33_i1
clean-proc_epmum_R34_i1:
.PHONY: clean-proc_epmum_R34_i1
clean-proc_epmum_R35_i1:
.PHONY: clean-proc_epmum_R35_i1
clean-proc_epmum_R36_i1:
.PHONY: clean-proc_epmum_R36_i1
clean-proc_epmum_R37_i1:
.PHONY: clean-proc_epmum_R37_i1
clean-proc_epmum_R38_i1:
.PHONY: clean-proc_epmum_R38_i1
clean-proc_epmum_R39_i1:
.PHONY: clean-proc_epmum_R39_i1
clean-proc_epmum_R40_i1:
.PHONY: clean-proc_epmum_R40_i1
clean-proc_epmum_R41_i1:
.PHONY: clean-proc_epmum_R41_i1
clean-proc_epmum_R42_i1:
.PHONY: clean-proc_epmum_R42_i1
clean-proc_epmum_R43_i1:
.PHONY: clean-proc_epmum_R43_i1
clean-proc_epmum_R44_i1:
.PHONY: clean-proc_epmum_R44_i1

# Generic cleanup targets
clean-library:
	@echo  "  RM        $(BASE).la"
	@rm -f $(BASE).la
clean-objects:
	@echo  "  RM        $(BASE).lo $(BASE)_driver.mod $(CLEAN_OBJECTS)"
	@rm -f $(BASE).lo $(BASE)_driver.mod $(CLEAN_OBJECTS)
clean-source:
	@echo  "  RM        $(CLEAN_SOURCES)"
	@rm -f $(CLEAN_SOURCES)
clean-driver:
	@echo  "  RM        $(BASE).f90"
	@rm -f $(BASE).f90
clean-makefile:
	@echo  "  RM        $(BASE).makefile"
	@rm -f $(BASE).makefile
.PHONY: clean-library clean-objects clean-source clean-driver clean-makefile

clean: clean-library clean-objects clean-source
distclean: clean clean-driver clean-makefile
.PHONY: clean distclean
