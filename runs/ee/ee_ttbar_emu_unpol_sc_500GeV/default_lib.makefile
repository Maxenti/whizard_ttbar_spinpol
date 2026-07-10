# WHIZARD: Makefile for process library 'default_lib'
# Automatically generated file, do not edit

# Integrity check (don't modify the following line!)
MD5SUM = 'DD69C791D90A686B2CF9B6D3323D5818'

# Library name
BASE = default_lib

# Compiler
FC = /cvmfs/sw.hsf.org/contrib/x86_64-almalinux9-gcc11.4.1-opt/gcc/14.2.0-yuyjov/bin/gfortran
CC = /cvmfs/sw.hsf.org/contrib/x86_64-almalinux9-gcc11.4.1-opt/gcc/14.2.0-yuyjov/bin/gcc

# Included libraries
FCINCL = -I/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib/mod/whizard -I/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib/mod/omega -I/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib/mod/models -I/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openloops/2.1.4-trhgkp/lib_src/openloops/mod 

# Compiler flags
FCFLAGS =  -fopenmp  -g -O2
FCFLAGS_PIC =  -fPIC
CFLAGS = -g -O2
CFLAGS_PIC = 
LDFLAGS = -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib -lwhizard_main -lwhizard -lomega -I/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/libtirpc/1.3.7-fkurbs/include/tirpc -L/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/libtirpc/1.3.7-fkurbs/lib -ltirpc  -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-5ee2bd/lib64 -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-5ee2bd/lib64 -lHepMC3 -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-5ee2bd/lib64 -lHepMC3rootIO -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/root/6.38.04-pbcgqf/lib/root -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/root/6.38.04-pbcgqf/lib/root -lCore -lImt -lRIO -lNet -lHist -lGraf -lGraf3d -lGpad -lROOTVecOps -lTree -lTreePlayer -lRint -lPostscript -lMatrix -lPhysics -lMathCore -lThread -lROOTNTuple -lROOTNTupleUtil -lMultiProc -lROOTDataFrame -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/lcio/2.23.2-m2hwgz/lib -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/lcio/2.23.2-m2hwgz/lib64 -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/lcio/2.23.2-m2hwgz/lib -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/lcio/2.23.2-m2hwgz/lib64 -llcio   -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openloops/2.1.4-trhgkp/lib -L/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openloops/2.1.4-trhgkp/lib -Wl,-rpath,/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openloops/2.1.4-trhgkp/lib64 -L/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openloops/2.1.4-trhgkp/lib64 -lopenloops    -lomega -L/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib/whizard/models -lwhizard

# LaTeX setup
LATEX = no -halt-on-error
MPOST = no  -halt-on-error
DVIPS = no
PS2PDF = no
TEX_FLAGS = "/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/share/texmf/whizard:$$TEXINPUTS"
MP_FLAGS  = "/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/share/texmf/whizard:$$MPINPUTS"

# Libtool
LIBTOOL = /cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/lib/whizard/libtool
FCOMPILE = @$(LIBTOOL) --silent --tag=FC --mode=compile
CCOMPILE = @$(LIBTOOL) --silent --tag=CC --mode=compile
LINK = @$(LIBTOOL) --silent --tag=FC --mode=link

# Compile commands (default)
LTFCOMPILE = $(FCOMPILE) $(FC) -c $(FCINCL) $(FCFLAGS) $(FCFLAGS_PIC)
LTCCOMPILE = $(CCOMPILE) $(CC) -c $(CFLAGS) $(CFLAGS_PIC)

# Default target
all: link diags

# Matrix-element code files
SOURCES += tt_prod_i1.f90
OBJECTS += tt_prod_i1.lo
tt_prod_i1.f90:
	@echo  "  OMEGA     tt_prod_i1.f90"
	@/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/bin/omega_SM.opt -o tt_prod_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_tt_prod_i1 -target:md5sum '9E60235DE8274793A2E2C15C0C1F38C8' -target:openmp -fusion:progress -scatter 'e- e+ -> t tbar' 
clean-tt_prod_i1:
	@echo  "  RM        tt_prod_i1.f90,.mod,.lo"
	@rm -f tt_prod_i1.f90
	@rm -f opr_tt_prod_i1.mod
	@rm -f tt_prod_i1.lo
CLEAN_SOURCES += tt_prod_i1.f90
CLEAN_OBJECTS += opr_tt_prod_i1.mod
CLEAN_OBJECTS += tt_prod_i1.lo
tt_prod_i1.lo: tt_prod_i1.f90
	$(LTFCOMPILE) $<
SOURCES += t_decay_i1.f90
OBJECTS += t_decay_i1.lo
t_decay_i1.f90:
	@echo  "  OMEGA     t_decay_i1.f90"
	@/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/bin/omega_SM.opt -o t_decay_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_t_decay_i1 -target:md5sum '6497DE63A45797FA8C6BF24EBAA9C66C' -target:openmp -fusion:progress -decay 't -> b e+ nue' 
clean-t_decay_i1:
	@echo  "  RM        t_decay_i1.f90,.mod,.lo"
	@rm -f t_decay_i1.f90
	@rm -f opr_t_decay_i1.mod
	@rm -f t_decay_i1.lo
CLEAN_SOURCES += t_decay_i1.f90
CLEAN_OBJECTS += opr_t_decay_i1.mod
CLEAN_OBJECTS += t_decay_i1.lo
t_decay_i1.lo: t_decay_i1.f90
	$(LTFCOMPILE) $<
SOURCES += tbar_decay_i1.f90
OBJECTS += tbar_decay_i1.lo
tbar_decay_i1.f90:
	@echo  "  OMEGA     tbar_decay_i1.f90"
	@/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/whizard/3.1.5-nmagsz/bin/omega_SM.opt -o tbar_decay_i1.f90 -target:whizard -target:parameter_module parameters_SM -target:module opr_tbar_decay_i1 -target:md5sum 'BDDABF8794DB4CD885F2F27AF45DE4D7' -target:openmp -fusion:progress -decay 'tbar -> bbar mu- numubar' 
clean-tbar_decay_i1:
	@echo  "  RM        tbar_decay_i1.f90,.mod,.lo"
	@rm -f tbar_decay_i1.f90
	@rm -f opr_tbar_decay_i1.mod
	@rm -f tbar_decay_i1.lo
CLEAN_SOURCES += tbar_decay_i1.f90
CLEAN_OBJECTS += opr_tbar_decay_i1.mod
CLEAN_OBJECTS += tbar_decay_i1.lo
tbar_decay_i1.lo: tbar_decay_i1.f90
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
clean-tt_prod_i1:
.PHONY: clean-tt_prod_i1
clean-t_decay_i1:
.PHONY: clean-t_decay_i1
clean-tbar_decay_i1:
.PHONY: clean-tbar_decay_i1

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
