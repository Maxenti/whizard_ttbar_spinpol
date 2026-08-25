# WHIZARD: Makefile for process library 'default_lib'
# Automatically generated file, do not edit

# Integrity check (don't modify the following line!)
MD5SUM = '649CDA0658CD882877BEF395D161E69A'

# Library name
BASE = default_lib

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
SOURCES += mupair_i1.f90
OBJECTS += mupair_i1.lo
mupair_i1.f90:
	@echo  "  OMEGA     mupair_i1.f90"
	@/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/local/whizard-3.1.8-mpi-omp-qualified-20260811/bin/omega_SM.opt -o mupair_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_mupair_i1 -target:md5sum 'CBEF5FEEC4B6BB9D7D6A2824867D77C3' -target:openmp -fusion:progress -scatter 'e- e+ -> mu- mu+' 
clean-mupair_i1:
	@echo  "  RM        mupair_i1.f90,.mod,.lo"
	@rm -f mupair_i1.f90
	@rm -f opr_mupair_i1.mod
	@rm -f mupair_i1.lo
CLEAN_SOURCES += mupair_i1.f90
CLEAN_OBJECTS += opr_mupair_i1.mod
CLEAN_OBJECTS += mupair_i1.lo
mupair_i1.lo: mupair_i1.f90
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
clean-mupair_i1:
.PHONY: clean-mupair_i1

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
