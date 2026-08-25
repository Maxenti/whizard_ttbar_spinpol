# WHIZARD: Makefile for process library 'default_lib'
# Automatically generated file, do not edit

# Integrity check (don't modify the following line!)
MD5SUM = '4274B9A91C5AD31FB0B21100D1E65EAE'

# Library name
BASE = default_lib

# Compiler
FC = /cvmfs/sft.cern.ch/lcg/releases/gcc/14.3.0-c8dfb/x86_64-el9/bin/gfortran
CC = /cvmfs/sft.cern.ch/lcg/releases/gcc/14.3.0-c8dfb/x86_64-el9/bin/gcc

# Included libraries
FCINCL = -I/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib/mod/whizard -I/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib/mod/omega -I/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib/mod/models -I/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/openloops/2.1.4.250729/x86_64-el9-gcc14-opt/lib_src/openloops/mod 

# Compiler flags
FCFLAGS =    -g -O2
FCFLAGS_PIC =  -fPIC
CFLAGS = -g -O2
CFLAGS_PIC = 
LDFLAGS = -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib -lwhizard_main -lwhizard -lomega -I/usr/include/tirpc  -ltirpc   -Wl,-rpath,/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -lHepMC3 -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/hepmc3/3.3.1-69c77/x86_64-el9-gcc14-opt/lib64 -lHepMC3rootIO -Wl,-rpath,/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/ROOT/6.40.02/x86_64-el9-gcc14-opt/lib -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/ROOT/6.40.02/x86_64-el9-gcc14-opt/lib -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/LCIO/HEAD/x86_64-el9-gcc14-opt/lib -Wl,-rpath,/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/LCIO/HEAD/x86_64-el9-gcc14-opt/lib64 -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/LCIO/HEAD/x86_64-el9-gcc14-opt/lib -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/LCIO/HEAD/x86_64-el9-gcc14-opt/lib64 -llcio -L/cvmfs/sft.cern.ch/lcg/releases/MCGenerators/hoppet/1.2.0-49d63/x86_64-el9-gcc14-opt/lib -L/cvmfs/sft.cern.ch/lcg/releases/MCGenerators/hoppet/1.2.0-49d63/x86_64-el9-gcc14-opt/lib64 -lhoppet_v1 -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/looptools/2.15/x86_64-el9-gcc14-opt/lib64 -looptools -Wl,-rpath,/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/openloops/2.1.4.250729/x86_64-el9-gcc14-opt/lib -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/openloops/2.1.4.250729/x86_64-el9-gcc14-opt/lib -Wl,-rpath,/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/openloops/2.1.4.250729/x86_64-el9-gcc14-opt/lib64 -L/build/jenkins/workspace/lcg_nightly_pipeline/install/devkey-head/MCGenerators/openloops/2.1.4.250729/x86_64-el9-gcc14-opt/lib64 -lopenloops    -lomega -L/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib/whizard/models -lwhizard

# LaTeX setup
LATEX = latex -halt-on-error
MPOST = mpost --math=scaled -halt-on-error
DVIPS = dvips
PS2PDF = ps2pdf14
TEX_FLAGS = "/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/share/texmf/whizard:$$TEXINPUTS"
MP_FLAGS  = "/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/share/texmf/whizard:$$MPINPUTS"

# Libtool
LIBTOOL = /cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/lib/whizard/libtool
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
	@/cvmfs/sft-nightlies.cern.ch/lcg/latest/whizard/3.1.8-5a48d/x86_64-el9-gcc14-opt/bin/omega_SM.opt -o mupair_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_mupair_i1 -target:md5sum '1846556C6F90E86B98E752EE60A4DF18' -fusion:progress -scatter 'e- e+ -> mu- mu+' 
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
