#!/usr/bin/env bash

set -Eeuo pipefail
set -o pipefail

##############################################################################
# WHIZARD 3.1.8 MPI/OpenMP
# clean build -> full check -> persistent install
##############################################################################

export REPO=/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol

export SOURCE_TARBALL=/eos/user/c/cglenn/FCCWork/whizard/packages/whizard-3.1.8-cern-lcg-source.tar.gz
export EXPECTED_SOURCE_SHA256=96bfdf2ec4476ab7945e50550a3294634af6bc0f472cf7848b5903887629ce55

export BUILD_PARENT=/tmp/${USER}/whizard-3.1.8-mpi-omp-qualified-build
export BUILD_SOURCE=$BUILD_PARENT/whizard-3.1.8

export INSTALL_ROOT=$REPO/local/whizard-3.1.8-mpi-omp-qualified-20260811

export LOG_ROOT=$REPO/build_logs/whizard-3.1.8-mpi-omp-qualified-20260811

export COMPAT_ROOT=$REPO/local/el9-link-compat
export COMPAT_LIB=$COMPAT_ROOT/lib

export BASE_ENV=$REPO/environments/setup_lcg_devkey_head_fri_ttsp.sh

export JOBS=${JOBS:-8}

mkdir -p \
    "$LOG_ROOT" \
    "$COMPAT_LIB"

STATUS_FILE="$LOG_ROOT/QUALIFICATION_STATUS.txt"

write_failure() {
    local stage="$1"
    local rc="$2"

    {
        echo "QUALIFICATION=FAIL"
        echo "FAILED_STAGE=$stage"
        echo "RC=$rc"
        echo "HOST=$(hostname)"
        echo "UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$STATUS_FILE"
}

run_logged() {
    local stage="$1"
    shift

    local logfile="$LOG_ROOT/${stage}.log"

    echo
    echo "================================================================"
    echo "STAGE: $stage"
    echo "================================================================"

    set +e
    "$@" 2>&1 | tee "$logfile"
    local rc=${PIPESTATUS[0]}
    set -e

    echo "${stage}_RC=$rc" | tee -a "$logfile"

    if [[ $rc -ne 0 ]]; then
        write_failure "$stage" "$rc"
        return "$rc"
    fi
}

##############################################################################
# Runtime environment
##############################################################################

cd "$REPO"
source "$BASE_ENV"

export OCAML_ROOT=/cvmfs/sft.cern.ch/lcg/releases/ocaml/4.14.2-7a890/x86_64-el9-gcc14-opt
export PATH="$OCAML_ROOT/bin:$PATH"

export OMP_NUM_THREADS=1

##############################################################################
# Provenance
##############################################################################

{
    echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "HOST=$(hostname)"
    echo "REPO=$REPO"
    echo "SOURCE_TARBALL=$SOURCE_TARBALL"
    echo "BUILD_SOURCE=$BUILD_SOURCE"
    echo "INSTALL_ROOT=$INSTALL_ROOT"
    echo
    echo "gcc=$(command -v gcc || true)"
    gcc --version | head -1 || true
    echo
    echo "mpicc=$(command -v mpicc || true)"
    mpicc --showme:command || true
    echo
    echo "mpicxx=$(command -v mpicxx || true)"
    mpicxx --showme:command || true
    echo
    echo "mpifort=$(command -v mpifort || true)"
    mpifort --showme:command || true
    echo
    echo "ocaml=$(command -v ocaml || true)"
    ocaml -version || true
} > "$LOG_ROOT/provenance.txt"

##############################################################################
# Verify source
##############################################################################

gzip -t "$SOURCE_TARBALL"

ACTUAL_SOURCE_SHA256="$(
    sha256sum "$SOURCE_TARBALL" | awk '{print $1}'
)"

{
    echo "EXPECTED_SOURCE_SHA256=$EXPECTED_SOURCE_SHA256"
    echo "ACTUAL_SOURCE_SHA256=$ACTUAL_SOURCE_SHA256"
} | tee "$LOG_ROOT/source_sha256.txt"

if [[ "$ACTUAL_SOURCE_SHA256" != "$EXPECTED_SOURCE_SHA256" ]]; then
    write_failure SOURCE_SHA256 1
    echo "ERROR: source SHA256 mismatch"
    exit 1
fi

##############################################################################
# Fresh temporary build
##############################################################################

rm -rf "$BUILD_PARENT"
mkdir -p "$BUILD_PARENT"

tar -xzf "$SOURCE_TARBALL" \
    -C "$BUILD_PARENT"

test -x "$BUILD_SOURCE/configure"
test -s "$BUILD_SOURCE/Makefile.in"
test -s "$BUILD_SOURCE/circe1/src/circe1.f90"

##############################################################################
# EL9/OpenMPI libudev compatibility shim
##############################################################################

UDEV_REAL="$(readlink -f /lib64/libudev.so.1)"

ln -sfn \
    "$UDEV_REAL" \
    "$COMPAT_LIB/libudev.so"

test -e "$COMPAT_LIB/libudev.so"

##############################################################################
# Refuse to overwrite a persistent qualified installation
##############################################################################

if [[ -e "$INSTALL_ROOT" ]]; then
    write_failure INSTALL_PREFIX_ALREADY_EXISTS 1
    echo "ERROR: persistent install already exists:"
    echo "  $INSTALL_ROOT"
    exit 1
fi

##############################################################################
# Configure
#
# IMPORTANT:
# Compiler/linker values belong here.
# Do NOT pass them later as make command-line overrides.
##############################################################################

cd "$BUILD_SOURCE"

run_logged configure \
    env \
    CC=mpicc \
    CXX=mpicxx \
    FC=mpifort \
    F77=mpifort \
    TIRPC_CFLAGS="-I/usr/include/tirpc" \
    TIRPC_LIBS="-ltirpc" \
    LDFLAGS="-L$COMPAT_LIB -Wl,--enable-new-dtags" \
    ./configure \
        --prefix="$INSTALL_ROOT" \
        --enable-fc-mpi \
        --with-mpi-lib=openmpi \
        --enable-fc-openmp \
        --disable-dependency-tracking

##############################################################################
# Record configured values
##############################################################################

grep -E \
    '^(CC|CXX|FC|F77|LDFLAGS|prefix)[[:space:]]*=' \
    "$BUILD_SOURCE/Makefile" \
    > "$LOG_ROOT/configured_make_variables.txt"

##############################################################################
# Critical: no GNU Make command-line build-variable overrides
##############################################################################

unset CC
unset CXX
unset FC
unset F77
unset LDFLAGS
unset MFLAGS
unset MAKEFLAGS

env | grep -E \
    '^(CC|CXX|FC|F77|LDFLAGS|MFLAGS|MAKEFLAGS)=' \
    > "$LOG_ROOT/unexpected_make_environment.txt" \
    && {
        cat "$LOG_ROOT/unexpected_make_environment.txt"
        write_failure EXTERNAL_MAKE_OVERRIDES 1
        exit 1
    } \
    || true

##############################################################################
# Build
##############################################################################

cd "$BUILD_SOURCE"

run_logged make \
    make -j"$JOBS"

##############################################################################
# Build-tree runtime library isolation
##############################################################################

BASE_LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}"

export LD_LIBRARY_PATH="$BUILD_SOURCE/src/.libs:$BUILD_SOURCE/src/prebuilt/.libs:$BUILD_SOURCE/vamp/src/.libs:$BUILD_SOURCE/circe1/src/.libs:$BUILD_SOURCE/circe2/src/.libs${BASE_LD_LIBRARY_PATH:+:$BASE_LD_LIBRARY_PATH}"

{
    echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
    echo
    ldd "$BUILD_SOURCE/src/.libs/whizard" || true
} > "$LOG_ROOT/build_runtime_linkage.txt"

##############################################################################
# FULL top-level qualification
##############################################################################

cd "$BUILD_SOURCE"

run_logged make_check_full_serial \
    make -j1 check

##############################################################################
# Capture all test summaries
##############################################################################

grep -nE \
    'Testsuite summary|# TOTAL:|# PASS:|# SKIP:|# XFAIL:|# FAIL:|# XPASS:|# ERROR:' \
    "$LOG_ROOT/make_check_full_serial.log" \
    > "$LOG_ROOT/test_summaries.txt" \
    || true

grep -nE \
    '^FAIL:|^ERROR:' \
    "$LOG_ROOT/make_check_full_serial.log" \
    > "$LOG_ROOT/test_failures.txt" \
    || true

if [[ -s "$LOG_ROOT/test_failures.txt" ]]; then
    cat "$LOG_ROOT/test_failures.txt"
    write_failure TEST_FAILURE_LINES_FOUND 1
    exit 1
fi

##############################################################################
# Persistent installation
##############################################################################

# Avoid the harmless missing-document-directory issue observed previously.
mkdir -p "$INSTALL_ROOT/share/doc/whizard"

cd "$BUILD_SOURCE"

run_logged make_install \
    make -j1 install

##############################################################################
# Installed runtime verification
##############################################################################

test -x "$INSTALL_ROOT/bin/whizard"

INSTALL_BASE_LD="${LD_LIBRARY_PATH:-}"

export LD_LIBRARY_PATH="$INSTALL_ROOT/lib${INSTALL_BASE_LD:+:$INSTALL_BASE_LD}"

"$INSTALL_ROOT/bin/whizard" --version \
    > "$LOG_ROOT/installed_whizard_version.txt" \
    2>&1

"$INSTALL_ROOT/bin/whizard" --help \
    > "$LOG_ROOT/installed_whizard_help.txt" \
    2>&1

if ldd "$INSTALL_ROOT/bin/whizard" \
    | grep 'not found' \
    > "$LOG_ROOT/installed_missing_libraries.txt"
then
    cat "$LOG_ROOT/installed_missing_libraries.txt"
    write_failure INSTALLED_LIBRARY_CLOSURE 1
    exit 1
else
    : > "$LOG_ROOT/installed_missing_libraries.txt"
fi

ldd "$INSTALL_ROOT/bin/whizard" \
    > "$LOG_ROOT/installed_ldd.txt"

readelf -d "$INSTALL_ROOT/bin/whizard" \
    > "$LOG_ROOT/installed_readelf_dynamic.txt"

##############################################################################
# Checksums
##############################################################################

sha256sum \
    "$INSTALL_ROOT/bin/whizard" \
    "$INSTALL_ROOT/lib/libwhizard.so.2.0.2" \
    > "$LOG_ROOT/installed_core_sha256.txt"

##############################################################################
# Final status
##############################################################################

{
    echo "QUALIFICATION=PASS"
    echo "WHIZARD_VERSION=3.1.8"
    echo "MPI=OPENMPI"
    echo "OPENMP=ON"
    echo "INSTALL_ROOT=$INSTALL_ROOT"
    echo "HOST=$(hostname)"
    echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo
    echo "FULL_TEST_SUMMARIES:"
    cat "$LOG_ROOT/test_summaries.txt"
} | tee "$STATUS_FILE"

echo
echo "================================================================"
echo "QUALIFIED WHIZARD BUILD COMPLETE"
echo "================================================================"
echo "INSTALL_ROOT=$INSTALL_ROOT"
echo "STATUS_FILE=$STATUS_FILE"
